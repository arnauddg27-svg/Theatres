import copy
import csv
import importlib.util
from math import log
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import actuals_quality as aq
import forecast_evaluation as fe
import model_calibration as mc
import predict as p
import seat_regression as sr

spec = importlib.util.spec_from_file_location("calibration_backtest", ROOT / "scripts/calibration_backtest.py")
backtest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backtest)


def history_row(movie="Film", weekend="2026-01-02", recorded="2026-01-05"):
    return {"movie": movie, "weekend_of": weekend, "date": recorded,
            "actual_total": 100, "predicted_mid": 100,
            "daily_actuals": {"Thursday": 10, "Friday": 30, "Saturday": 35, "Sunday": 25},
            "raw_daily_predictions": {"Thursday": 10, "Friday": 30, "Saturday": 35, "Sunday": 25},
            "daily_coverage_ratios": dict.fromkeys(sr.OPENING_DAYS, 1.0),
            "snapshot_daily_predictions": dict.fromkeys(sr.OPENING_DAYS, 10),
            "snapshot_daily_lead_buckets": dict.fromkeys(sr.OPENING_DAYS, "next_day"),
            "snapshot_daily_coverage_ratios": dict.fromkeys(sr.OPENING_DAYS, 1.0)}


class ActualQualityTests(unittest.TestCase):
    def test_legacy_seat_derived_split_keeps_reported_preview_and_original_record(self):
        row = history_row()
        row["actual_source"] = "user report total; Fri/Sat/Sun split derived from captured seat proportions"
        original = copy.deepcopy(row)
        self.assertEqual({"Thursday": 10}, aq.independent_daily_actuals(row))
        self.assertEqual(["Thursday"], [r["day"] for r in sr.build_seat_rows([row])])
        self.assertEqual(["Thursday"], [r["day"] for r in sr.build_snapshot_rows([row])])
        self.assertEqual((0, 0), mc.snapshot_calibration_actual_for_day(row, "Saturday"))
        self.assertEqual(0, mc.snapshot_calibration_support([row])["days"]["Saturday"]["n"])
        self.assertEqual(original, row)

    def test_explicit_estimated_day_is_excluded_from_all_daily_calibration(self):
        row = history_row()
        row["estimated_daily_actual_days"] = ["Friday"]
        self.assertNotIn("Friday", aq.independent_daily_actuals(row))
        self.assertIn("Friday", mc.excluded_calibration_days(row))
        self.assertNotIn("Friday", p._history_daily_actuals(row))

    def test_history_day_aliases_still_normalize_before_quality_filtering(self):
        row = history_row()
        row["daily_actuals"] = {"Thu": 10, "fri": 30}
        row["estimated_daily_actual_days"] = ["Friday"]
        self.assertEqual({"Thursday": 10}, p._history_daily_actuals(row))

    def test_reported_preview_subtraction_remains_usable(self):
        self.assertTrue(aq.independent_daily_override({
            "source": "derived from reported Friday incl previews", "status": "reported",
            "notes": "Reported Friday minus Thursday previews"}))
        self.assertFalse(aq.independent_daily_override({
            "source": "derived from captured AMC seat proportions", "status": "reported"}))

    def test_estimated_overrides_cannot_anchor_live_forecasts(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "actuals.csv"
            rows = [{"weekend_of": "2026-01-02", "movie_title": "Film", "day_of_week": "Friday",
                     "gross_m": "30", "source": "trade report", "status": "reported",
                     "as_of_date": "2026-01-03"},
                    {"weekend_of": "2026-01-02", "movie_title": "Film", "day_of_week": "Friday",
                     "gross_m": "60", "source": "derived from seat proportions", "status": "reported",
                     "as_of_date": "2026-01-04"}]
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
            with patch.object(p, "DAILY_ACTUALS_CSV", str(path)):
                self.assertEqual(30, p.load_daily_actual_overrides("2026-01-02")["Film"]["Friday"]["gross_m"])

    def test_day_shape_rejects_holidays_partial_and_folded_previews(self):
        good = history_row()
        variants = []
        for flag in ("exclude_from_day_weights", "previews_folded_into_friday", "data_outage"):
            bad = history_row(); bad[flag] = True; bad["daily_actuals"]["Friday"] = 1000
            variants.append(bad)
        estimated = history_row(); estimated["estimated_daily_actual_days"] = ["Saturday"]
        partial = history_row(); partial["daily_actuals"].pop("Thursday")
        self.assertEqual(sr.learn_day_shares([good]), sr.learn_day_shares([good] + variants + [estimated, partial]))

    def test_missing_daily_targets_are_not_invented_from_snapshot_proportions(self):
        row = history_row(); row["daily_actuals"] = {"Thursday": 10, "WeekendRemainder": 90}
        self.assertEqual((0, 0), mc.snapshot_calibration_actual_for_day(row, "Sunday"))
        self.assertEqual(1.0, mc.recalibrate_snapshot_day_scale_factors([row])["Sunday"])

    def test_outage_cannot_increase_snapshot_training_support(self):
        row = history_row(); row["data_outage"] = True
        self.assertEqual((0, 0), mc.snapshot_calibration_actual_for_day(row, "Friday"))

    def test_load_replaces_stale_shape_weights_from_the_same_clean_history(self):
        cal = {"history": [history_row()], "calibration_factors": {"day_weights": dict.fromkeys(sr.OPENING_DAYS, .25)}}
        clean = mc.sanitize_calibration(cal, p.DAY_WEIGHTS_DEFAULT, .25)
        self.assertEqual(clean["calibration_factors"]["regression"]["day_shares"], clean["calibration_factors"]["day_weights"])
        self.assertAlmostEqual(.1, p.get_day_weights(clean)["Thursday"])

    def test_sellout_feature_is_learned_and_used_at_prediction(self):
        rows = [{"day": "Sunday", "movie": str(i), "log_seat": log(10),
                 "log_actual": log(10) + 1.5 * sellout, "coverage": 1, "weight": 1,
                 "sellout": sellout} for i, sellout in enumerate([0, .2, .4, .6, .8, 1] * 4)]
        coef = sr.fit_seat(rows, .03)
        low = sr.predict_log(coef, sr.seat_features(log(10), "Sunday", 1, 0))
        high = sr.predict_log(coef, sr.seat_features(log(10), "Sunday", 1, .8))
        self.assertAlmostEqual(1.2, high - low, delta=.05)


class ForecastEvaluationTests(unittest.TestCase):
    def test_chronological_training_excludes_same_weekend_future_and_late_actuals(self):
        before = history_row("Earlier")
        same = history_row("Same", "2026-01-09", "2026-01-12")
        late = history_row("Late", recorded="2026-01-10")
        future = history_row("Future", "2026-01-16", "2026-01-19")
        missing = history_row("Unknown"); missing.pop("date")
        self.assertEqual([before], backtest.earlier_history([before, same, late, future, missing], "2026-01-09"))

    def test_all_films_on_a_weekend_share_one_training_fold(self):
        history = [history_row("Earlier"), history_row("A", "2026-01-09", "2026-01-12"),
                   history_row("B", "2026-01-09", "2026-01-12")]
        with patch.object(sr, "fit_regression_calibration", wraps=sr.fit_regression_calibration) as fit:
            report = backtest.evaluate(history, min_training_movies=1)
        self.assertEqual(1, fit.call_count)
        self.assertEqual([history[0]], fit.call_args.args[0])
        self.assertEqual(2, report["all_scored"]["n"])
        self.assertEqual(1, report["unscored"])

    def test_checkpoint_ignores_later_run_and_normalizes_offsets(self):
        rows = [{"weekend_of": "2026-09-18", "logged_at": stamp, "headline_mid_m": value}
                for stamp, value in [("2026-09-18T15:59:00Z", 40),
                                     ("2026-09-18T12:00:00-04:00", 45),
                                     ("2026-09-18T16:00:01Z", 90),
                                     ("not-a-date", 100)]]
        out = fe.select_forecast_checkpoints(rows, "2026-09-18")
        self.assertEqual(45, out["friday_noon_et"]["mid_m"])
        self.assertNotIn("thursday_noon_et", out)
        self.assertNotIn("sunday_noon_et", out)

    def test_checkpoint_uses_eastern_winter_time(self):
        row = {"weekend_of": "2026-01-02", "logged_at": "2026-01-02T16:45:00Z", "headline_mid_m": 30}
        self.assertEqual("2026-01-02T17:00:00Z", fe.select_forecast_checkpoints([row], "2026-01-02")["friday_noon_et"]["cutoff"])

    def test_live_grading_retains_fixed_checkpoints(self):
        rows = [{"weekend_of": "2026-09-18", "logged_at": "2026-09-18T15:59:00Z",
                 "headline_mid_m": "45", "seat_days": "Thursday"}]
        self.assertEqual(45, p.select_live_headline(rows, "2026-09-18")["checkpoints"]["friday_noon_et"]["mid_m"])

    def test_each_checkpoint_is_graded_against_actual_without_mutating_log(self):
        checkpoints = {"friday_noon_et": {"mid_m": 40, "low_m": 30, "high_m": 60},
                       "saturday_noon_et": {"mid_m": 55}}
        result = fe.grade_forecast_checkpoints(checkpoints, 50)
        self.assertEqual(-20, result["friday_noon_et"]["error_pct"])
        self.assertTrue(result["friday_noon_et"]["in_range"])
        self.assertEqual(10, result["saturday_noon_et"]["error_pct"])
        self.assertIsNone(result["saturday_noon_et"]["in_range"])
        self.assertNotIn("error_pct", checkpoints["friday_noon_et"])

    def test_interval_excludes_future_and_late_recorded_results(self):
        past = [history_row(str(i)) for i in range(10)]
        future = history_row("Later", "2026-02-06", "2026-02-09"); future["actual_total"] = 10000
        late = history_row("Late", recorded="2026-03-01"); late["actual_total"] = 10000
        self.assertEqual((.85, 1.15), p.conformal_ratio_band({"history": past + [future, late]}, "New", weekend_of="2026-01-30"))

    def test_tentpole_interval_never_has_negative_lower_bound(self):
        rows = [dict(history_row(str(i)), actual_total=1) for i in range(10)]
        low, high = p.conformal_ratio_band({"history": rows}, "New", predicted_mid=100)
        self.assertEqual(0, low)
        self.assertGreaterEqual(high, 1.15)


if __name__ == "__main__":
    unittest.main()
