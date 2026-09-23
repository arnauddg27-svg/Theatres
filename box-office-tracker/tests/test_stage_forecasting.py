import copy
import csv
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import predict as P
import stage_forecasting as S
import stage_backtest as B
import forecast_evaluation as F


def prediction():
    return {"movie": "Example", "seat_mid_m": 20, "seat_low_m": 10, "seat_high_m": 30,
            "snapshot_mid_m": 28, "snapshot_low_m": 23, "snapshot_high_m": 33,
            "snapshot_model_coverage_ratio": .8, "snapshot_calibration_support_factor": .7,
            "snapshot_days": ["Saturday", "Sunday"],
            "daily_details": {"Thursday": {"domestic_mid": 3e6}, "Friday": {"domestic_mid": 7e6}},
            "missing_data_profile": {"missing_days": ["Saturday", "Sunday"]}}


class StageForecastTests(unittest.TestCase):
    def test_daily_evidence_is_not_pulled_back_by_generic_friday_anchor(self):
        pred = prediction()
        with patch.object(P, "friday_anchored_weekend_m", return_value=(20, 10, 2)):
            old = copy.deepcopy(pred)
            P.select_regression_prediction(old, apply_stage_model=False)
            P.select_regression_prediction(pred)
        self.assertEqual(28, pred["regression_mid_m"])
        self.assertEqual(old["regression_mid_m"], pred["stage_baseline_mid_m"])
        self.assertEqual(0, pred["friday_anchor_blend_weight"])
        self.assertEqual("after-friday", pred["forecast_stage"])
        self.assertLessEqual(pred["regression_low_m"], old["regression_low_m"])
        self.assertGreaterEqual(pred["regression_high_m"], old["regression_high_m"])

    def test_partial_reservations_can_fill_a_coverage_gap(self):
        pred = prediction()
        pred["snapshot_days"] = ["Saturday"]
        self.assertFalse(P.complete_snapshot_covers_missing_days(pred))
        P.select_regression_prediction(pred)
        self.assertEqual("stage-daily-evidence", pred["regression_source"])
        self.assertEqual(28, pred["regression_mid_m"])

    def test_completed_weekend_keeps_original_model(self):
        pred = prediction()
        pred["daily_details"].update({"Saturday": {}, "Sunday": {}})
        old = copy.deepcopy(pred)
        P.select_regression_prediction(old, apply_stage_model=False)
        P.select_regression_prediction(pred)
        self.assertEqual(old["regression_mid_m"], pred["regression_mid_m"])
        self.assertFalse(pred["stage_daily_evidence_applied"])
        self.assertEqual("complete", S.forecast_stage(pred))

    def test_sparse_or_unsupported_snapshots_preserve_fallback(self):
        for field, value in (("snapshot_model_coverage_ratio", .49),
                             ("snapshot_calibration_support_factor", .19),
                             ("snapshot_mid_m", float("nan")),
                             ("snapshot_low_m", 40), ("snapshot_high_m", None)):
            pred = prediction(); pred[field] = value
            self.assertIsNone(S.daily_evidence_candidate(pred), field)

    def test_no_regular_seats_or_no_snapshot_does_not_invent_forecast(self):
        self.assertIsNone(S.daily_evidence_candidate({}))
        pred = prediction(); pred["daily_details"] = {}
        self.assertIsNone(S.daily_evidence_candidate(pred))

    def test_review_factor_is_applied_exactly_once(self):
        pred = prediction(); pred["review_weekend_factor"] = 1.1
        P.select_regression_prediction(pred)
        self.assertAlmostEqual(30.8, pred["regression_mid_m"])
        P.select_regression_prediction(pred)
        self.assertAlmostEqual(30.8, pred["regression_mid_m"])

    def test_old_historical_error_band_survives_a_lower_new_forecast(self):
        pred = prediction(); old = copy.deepcopy(pred)
        cal = {"history": [{"movie": str(i), "predicted_mid": 10, "actual_total": 20} for i in range(20)]}
        with patch.object(P, "friday_anchored_weekend_m", return_value=(100, 10, 10)):
            P.select_regression_prediction(old, cal, apply_stage_model=False)
            P.select_regression_prediction(pred, cal)
        self.assertLess(pred["regression_mid_m"], old["regression_mid_m"])
        self.assertGreaterEqual(pred["regression_high_m"], old["regression_high_m"])
        self.assertLessEqual(pred["regression_low_m"], old["regression_low_m"])

    def test_missing_saturday_does_not_label_sunday_sample_complete(self):
        pred = prediction(); pred["daily_details"]["Sunday"] = {}
        self.assertEqual("after-sunday", S.forecast_stage(pred))

    def test_legacy_log_preserves_rows_and_extra_columns_when_adding_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.csv"
            path.write_text("logged_at,movie,headline_mid_m,custom_note\n2026-09-18T10:00:00Z,Earlier,12,keep me\n")
            pred = prediction(); P.select_regression_prediction(pred)
            self.assertTrue(P.append_prediction_log(pred, path=str(path), weekend_of="2026-09-18"))
            with path.open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual("keep me", rows[0]["custom_note"])
            self.assertEqual("12", rows[0]["headline_mid_m"])
            self.assertEqual("", rows[0]["baseline_mid_m"])
            self.assertEqual(str(round(pred["stage_baseline_mid_m"], 2)), rows[1]["baseline_mid_m"])
            self.assertNotIn(None, rows[1])

    def test_fixed_checkpoint_grades_new_and_old_models_from_the_same_run(self):
        rows = [{"weekend_of": "2026-09-18", "logged_at": "2026-09-18T15:59:00Z",
                 "headline_mid_m": "12", "baseline_mid_m": "15", "model_version": "v29"}]
        checkpoints = F.select_forecast_checkpoints(rows, "2026-09-18")
        grade = F.grade_forecast_checkpoints(checkpoints, 10)["friday_noon_et"]
        self.assertEqual(30, grade["absolute_error_improvement_pp"])
        self.assertEqual("v29", grade["model_version"])


class StageReplayTests(unittest.TestCase):
    def test_capture_clock_rejects_future_same_day_data_and_unknown_times(self):
        cutoff = B.checkpoint_time("2026-09-18", 0)
        rows = [{"check_time": v} for v in ["2026-09-18T11:59:00-04:00", "2026-09-18T16:00:01Z", "", "2026-09-18T10:00:00"]]
        data = {"Film": {"2026-09-17": rows}}
        self.assertEqual([rows[0]], B.filter_captured(data, cutoff, "check_time")["Film"]["2026-09-17"])
        self.assertEqual(4, len(rows))

    def test_cutoff_respects_dst(self):
        self.assertEqual(16, B.checkpoint_time("2026-09-18", 0).hour)
        self.assertEqual(17, B.checkpoint_time("2026-01-02", 0).hour)

    def test_metrics_report_independent_films_and_all_checkpoints(self):
        rows = [{"movie": "A", "weekend_of": "2026-09-18", "actual_m": 10,
                 "baseline_m": 20, "updated_m": 15}] * 3
        metrics = B.summarize(rows)
        self.assertEqual(3, metrics["forecasts"])
        self.assertEqual(1, metrics["films"])
        self.assertEqual(50, metrics["updated"]["mape_pct"])


if __name__ == "__main__":
    unittest.main()
