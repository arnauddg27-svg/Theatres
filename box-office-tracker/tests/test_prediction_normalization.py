import unittest
from pathlib import Path
import sys
import tempfile
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

import predict
import calibrate
from model_calibration import recalibrate_snapshot_day_scale_factors
from predict import (
    days_to_weekend,
    polymarket_expected_value,
    predict_movie,
    record_actual,
    reference_amc_theatre_count,
)


class PredictionNormalizationTest(unittest.TestCase):
    def test_parse_manual_daily_actuals(self):
        parsed = calibrate.parse_daily_actuals_arg(
            "Thursday=10.0,Friday=22.5,Saturday=25.9,Sunday=18.6"
        )

        self.assertEqual(
            {
                "Thursday": 10.0,
                "Friday": 22.5,
                "Saturday": 25.9,
                "Sunday": 18.6,
            },
            parsed,
        )

    def test_polymarket_expected_value_normalizes_interval_prices(self):
        result = polymarket_expected_value([
            {
                "market_question": "Will Sample Opening Weekend Box Office be between 50m and 60m?",
                "outcome_prices": "[\"0.6\", \"0.4\"]",
                "volume": "1000",
            },
            {
                "market_question": "Will Sample Opening Weekend Box Office be between 60m and 70m?",
                "outcome_prices": "[\"0.6\", \"0.4\"]",
                "volume": "1000",
            },
        ])

        self.assertAlmostEqual(60.0, result["ev"], places=6)
        self.assertAlmostEqual(1.2, result["raw_probability_sum"], places=6)
        self.assertAlmostEqual(1.0, sum(b["p_norm"] for b in result["brackets"]), places=6)

    def test_low_coverage_widens_weekend_interval(self):
        cal = {
            "calibration_factors": {
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
            },
        }

        full_mid, full_low, full_high, _ = days_to_weekend(
            {"Thursday": 10_000_000},
            cal,
            daily_coverage_ratios={"Thursday": 1.0},
        )
        sparse_mid, sparse_low, sparse_high, _ = days_to_weekend(
            {"Thursday": 10_000_000},
            cal,
            daily_coverage_ratios={"Thursday": 0.5},
        )

        self.assertEqual(full_mid, sparse_mid)
        self.assertLess(sparse_low, full_low)
        self.assertGreater(sparse_high, full_high)

    def test_prediction_normalizes_sampled_amc_total_to_reference_theatre_count(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "reference_amc_theatres": 4,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 4,
                },
            },
        }
        rows = [
            self._row("AMC One"),
            self._row("AMC Two"),
        ]

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-07": rows},
            [],
            cal,
        )

        thursday = pred["daily_details"]["Thursday"]
        self.assertEqual(2, thursday["n_theatres"])
        self.assertEqual(4, thursday["expected_theatres"])
        self.assertAlmostEqual(0.5, thursday["coverage_ratio"], places=6)
        self.assertAlmostEqual(1000.0, thursday["sampled_amc_total"], places=6)
        self.assertAlmostEqual(2000.0, thursday["amc_total"], places=6)
        self.assertLess(pred["seat_data_quality"], 1.0)
        self.assertAlmostEqual(0.008, pred["seat_mid_m"], places=6)

    def test_prediction_keeps_polymarket_ev_out_of_forecast_math(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
            },
        }
        rows = [self._row("AMC One")]
        markets = [
            {
                "market_question": "Will Sample Movie Opening Weekend Box Office be between 100m and 110m?",
                "outcome_prices": "[\"1.0\", \"0.0\"]",
                "volume": "1000000",
            },
        ]

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-07": rows},
            markets,
            cal,
        )

        self.assertIsNotNone(pred["poly_result"])
        self.assertGreater(pred["poly_result"]["ev"], pred["seat_mid_m"])
        self.assertAlmostEqual(pred["seat_mid_m"], pred["blended_m"], places=6)
        self.assertAlmostEqual(1.0, pred["w_seat"], places=6)
        self.assertAlmostEqual(0.0, pred["w_poly"], places=6)

    def test_prediction_penalizes_missing_full_timezone_bucket(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Friday": 1.0},
                "day_scale_factors": {"Friday": 1.0},
                "reference_amc_theatres": 6,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 6,
                },
            },
        }
        rows = [
            self._row("AMC East", date="2026-05-08", day="Friday", timezone="ET"),
            self._row("AMC West", date="2026-05-08", day="Friday", timezone="PT"),
        ]

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-08": rows},
            [],
            cal,
        )

        friday = pred["daily_details"]["Friday"]
        naive_factor = friday["expected_theatres"] / friday["n_theatres"]
        self.assertEqual(["CT"], friday["missing_timezones"])
        self.assertLess(friday["sample_normalization_factor"], naive_factor)
        self.assertGreater(friday["sample_normalization_factor"], 1.0)
        self.assertLess(
            friday["amc_total"],
            friday["sampled_amc_total"] * naive_factor,
        )
        self.assertLess(friday["effective_coverage_ratio"], friday["coverage_ratio"])

    def test_prediction_reports_weighted_missing_data_profile(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {
                    "Thursday": 0.10,
                    "Friday": 0.30,
                    "Saturday": 0.35,
                    "Sunday": 0.25,
                },
                "day_scale_factors": {"Thursday": 1.0},
                "reference_amc_theatres": 1,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 1,
                },
            },
        }

        pred = predict_movie(
            "Sample Movie",
            {
                "2026-05-07": [
                    self._row(
                        "AMC One",
                        date="2026-05-07",
                        day="Thursday",
                        timezone="ET",
                    )
                ]
            },
            [],
            cal,
        )

        profile = pred["missing_data_profile"]
        self.assertEqual(["Friday", "Saturday", "Sunday"], profile["missing_days"])
        self.assertAlmostEqual(0.10, pred["seat_observed_day_share"], places=6)
        self.assertAlmostEqual(0.90, pred["seat_missing_day_share"], places=6)
        self.assertGreater(pred["seat_weighted_coverage_ratio"], 0)
        self.assertLessEqual(pred["seat_weighted_coverage_ratio"], 0.10)
        self.assertLess(pred["seat_data_quality"], 0.50)

    def test_missing_day_share_raises_partial_data_prior_weight(self):
        pred = {
            "n_days": 3,
            "seat_data_quality": 0.92,
            "daily_details": {
                "Thursday": {},
                "Friday": {},
                "Saturday": {},
            },
            "missing_data_profile": {
                "missing_day_share": 0.25,
                "missing_days": ["Sunday"],
                "missing_timezone_days": [],
            },
        }

        self.assertGreaterEqual(predict.missing_data_prior_weight(pred), 0.15)

    def test_snapshot_layer_estimates_missing_future_days_only(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {
                    "Thursday": 0.25,
                    "Friday": 0.25,
                    "Saturday": 0.25,
                    "Sunday": 0.25,
                },
                "day_scale_factors": {
                    "Thursday": 1.0,
                    "Friday": 1.0,
                    "Saturday": 1.0,
                    "Sunday": 1.0,
                },
                "snapshot_to_day_scale_factors": {
                    "Friday": 1.0,
                },
                "reference_amc_theatres": 4,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 4,
                },
            },
        }
        seat_rows = [
            self._row("AMC One", date="2026-05-07", day="Thursday", timezone="ET"),
            self._row("AMC Two", date="2026-05-07", day="Thursday", timezone="CT"),
        ]
        snapshot_rows = [
            self._snapshot_row("AMC One", "Friday", "2026-05-08", timezone="ET"),
            self._snapshot_row("AMC Two", "Friday", "2026-05-08", timezone="CT"),
        ]

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-07": seat_rows},
            [],
            cal,
            snapshot_data={"2026-05-08": snapshot_rows},
        )

        self.assertIn("Thursday", pred["daily_details"])
        self.assertIn("Friday", pred["snapshot_daily_details"])
        self.assertNotIn("Friday", pred["daily_details"])
        self.assertIsNotNone(pred["snapshot_mid_m"])
        self.assertNotEqual(pred["snapshot_mid_m"], pred["seat_mid_m"])
        self.assertGreater(pred["snapshot_model_weight"], 0)
        self.assertEqual(
            "seat+snapshot-regression",
            pred["regression_source"],
        )

    def test_snapshot_layer_never_overrides_actual_seat_count_day(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 0.5, "Friday": 0.5},
                "day_scale_factors": {"Thursday": 1.0, "Friday": 1.0},
                "reference_amc_theatres": 4,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 4,
                },
            },
        }
        seat_rows = [
            self._row("AMC One", date="2026-05-07", day="Thursday", timezone="ET"),
        ]
        snapshot_rows = [
            self._snapshot_row("AMC One", "Thursday", "2026-05-07", timezone="ET"),
            self._snapshot_row("AMC Two", "Friday", "2026-05-08", timezone="CT"),
        ]

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-07": seat_rows},
            [],
            cal,
            snapshot_data={
                "2026-05-07": [snapshot_rows[0]],
                "2026-05-08": [snapshot_rows[1]],
            },
        )

        self.assertEqual(["Thursday"], sorted(pred["daily_details"]))
        self.assertEqual(["Friday"], sorted(pred["snapshot_daily_details"]))
        self.assertIn("Thursday", pred["snapshot_ignored_days"])

    def test_snapshot_layer_calibrates_future_days_from_same_week_overlap(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Friday": 0.5, "Saturday": 0.5},
                "snapshot_to_day_scale_factors": {"Friday": 1.0, "Saturday": 1.0},
            },
        }
        friday_rows = [
            self._snapshot_row("AMC One", "Friday", "2026-05-08", timezone="ET"),
            self._snapshot_row("AMC Two", "Friday", "2026-05-08", timezone="CT"),
        ]
        saturday_rows = [
            self._snapshot_row("AMC One", "Saturday", "2026-05-09", timezone="ET"),
            self._snapshot_row("AMC Two", "Saturday", "2026-05-09", timezone="CT"),
        ]
        uncalibrated_sat = predict.estimate_snapshot_day(
            saturday_rows,
            "2026-05-09",
            cal,
            expected_amc_theatres=2,
            expected_timezone_counts={"ET": 1, "CT": 1},
            theatre_timezone_map={"AMC One": "ET", "AMC Two": "CT"},
        )
        friday_actual = uncalibrated_sat["domestic_mid"] * 2.0

        layer = predict.build_snapshot_future_layer(
            {
                "2026-05-08": friday_rows,
                "2026-05-09": saturday_rows,
            },
            {
                "Friday": {
                    "domestic_mid": friday_actual,
                    "coverage_ratio": 1.0,
                    "effective_coverage_ratio": 1.0,
                }
            },
            cal,
            expected_amc_theatres=2,
            expected_timezone_counts={"ET": 1, "CT": 1},
            theatre_timezone_map={"AMC One": "ET", "AMC Two": "CT"},
        )

        saturday = layer["snapshot_daily_details"]["Saturday"]
        self.assertIn("Friday", layer["snapshot_ignored_days"])
        self.assertGreater(layer["snapshot_same_week_scale"], 1.0)
        self.assertAlmostEqual(friday_actual, saturday["domestic_mid"], delta=1)
        self.assertGreater(saturday["domestic_mid"], uncalibrated_sat["domestic_mid"])

    def test_snapshot_day_ignores_rows_beyond_day_plus_one_window(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
            },
        }
        near_row = self._snapshot_row(
            "AMC Near",
            "Saturday",
            "2026-05-09",
            timezone="ET",
        )
        far_row = self._snapshot_row(
            "AMC Far",
            "Saturday",
            "2026-05-09",
            timezone="CT",
        )
        far_row["minutes_until_showtime"] = str(72 * 60)

        details = predict.estimate_snapshot_day(
            [near_row, far_row],
            "2026-05-09",
            cal,
            expected_amc_theatres=2,
            expected_timezone_counts={"ET": 1, "CT": 1},
        )

        self.assertEqual(1, details["n_theatres"])
        self.assertEqual(["ET"], details["observed_timezones"])
        self.assertEqual(["CT"], details["missing_timezones"])
        self.assertEqual(1, details["n_lead_window_ignored"])

    def test_partial_snapshot_future_days_anchor_to_regular_day_shape(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Friday": 0.5, "Saturday": 0.25, "Sunday": 0.25},
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
            },
        }
        rows = [
            self._snapshot_row("AMC One", "Saturday", "2026-05-09", timezone="ET"),
            self._snapshot_row("AMC Two", "Saturday", "2026-05-09", timezone="ET"),
        ]
        for row in rows:
            row["reserved_seats"] = "1"
        raw = predict.estimate_snapshot_day(
            rows,
            "2026-05-09",
            cal,
            expected_amc_theatres=4,
            expected_timezone_counts={"ET": 2, "CT": 2},
        )
        layer = predict.build_snapshot_future_layer(
            {"2026-05-09": rows},
            {
                "Friday": {
                    "domestic_mid": 20_000_000,
                    "coverage_ratio": 1.0,
                    "effective_coverage_ratio": 1.0,
                }
            },
            cal,
            expected_amc_theatres=4,
            expected_timezone_counts={"ET": 2, "CT": 2},
        )

        saturday = layer["snapshot_daily_details"]["Saturday"]
        self.assertGreater(saturday["domestic_mid"], raw["domestic_mid"])
        self.assertGreater(saturday["snapshot_day_shape_prior_weight"], 0.70)
        self.assertGreater(saturday["domestic_mid"], 7_000_000)

    def test_snapshot_day_ignores_stale_timezone_slice(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "snapshot_to_day_scale_factors": {"Friday": 1.0},
            },
        }
        rows = [
            self._snapshot_row(
                "AMC ET",
                "Friday",
                "2026-05-08",
                timezone="ET",
                snapshot_time="2026-05-09T04:00:00+00:00",
            ),
            self._snapshot_row(
                "AMC CT",
                "Friday",
                "2026-05-08",
                timezone="CT",
                snapshot_time="2026-05-09T05:00:00+00:00",
            ),
            self._snapshot_row(
                "AMC PT Stale",
                "Friday",
                "2026-05-08",
                timezone="PT",
                snapshot_time="2026-05-08T05:00:00+00:00",
            ),
        ]

        details = predict.estimate_snapshot_day(
            rows,
            "2026-05-08",
            cal,
            expected_amc_theatres=3,
            expected_timezone_counts={"ET": 1, "CT": 1, "PT": 1},
        )

        self.assertEqual(2, details["n_theatres"])
        self.assertEqual(["CT", "ET"], details["observed_timezones"])
        self.assertEqual(["PT"], details["missing_timezones"])
        self.assertLess(details["effective_coverage_ratio"], details["coverage_ratio"])

    def test_snapshot_day_scale_calibration_uses_all_reliable_movie_days(self):
        history = [
            {
                "movie": "Movie One",
                "daily_actuals": {"Friday": 12.0},
                "snapshot_daily_predictions": {"Friday": 10.0},
                "snapshot_daily_coverage_ratios": {"Friday": 0.9},
            },
            {
                "movie": "Movie Two",
                "daily_actuals": {"Friday": 8.0},
                "snapshot_daily_predictions": {"Friday": 10.0},
                "snapshot_daily_coverage_ratios": {"Friday": 0.9},
            },
        ]

        scales = recalibrate_snapshot_day_scale_factors(history, alpha=0.5)

        self.assertIn("Friday", scales)
        self.assertNotEqual(1.0, scales["Friday"])

    def test_snapshot_calibration_uses_raw_unscaled_snapshot_mid(self):
        snapshot_predictions, snapshot_coverage = (
            calibrate.snapshot_calibration_fields_from_prediction({
                "snapshot_daily_details": {
                    "Friday": {
                        "raw_domestic_mid": 10_000_000,
                        "domestic_mid": 20_000_000,
                        "effective_coverage_ratio": 0.9,
                    },
                },
            })
        )

        self.assertEqual({"Friday": 10.0}, snapshot_predictions)
        self.assertEqual({"Friday": 0.9}, snapshot_coverage)

    def test_predict_actual_snapshot_calibration_uses_raw_unscaled_snapshot_mid(self):
        snapshot_predictions, snapshot_coverage = (
            predict.snapshot_calibration_fields_from_prediction({
                "snapshot_daily_details": {
                    "Saturday": {
                        "raw_domestic_mid": 8_000_000,
                        "domestic_mid": 16_000_000,
                        "coverage_ratio": 0.5,
                    },
                },
            })
        )

        self.assertEqual({"Saturday": 8.0}, snapshot_predictions)
        self.assertEqual({"Saturday": 0.5}, snapshot_coverage)

    def test_load_pre_reservation_data_requires_weekend_and_snapshot_date_for_replay(self):
        old_snapshot_csv = predict.PRE_RESERVATION_CSV
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_csv = Path(tmpdir) / "pre-reservation-snapshots.csv"
            snapshot_csv.write_text(
                "\n".join([
                    "weekend_of,movie_title,show_date,snapshot_time,theatre_name",
                    ",Blank Weekend Leak,2026-05-08,2026-05-07T12:00:00+00:00,Unknown AMC",
                    "2026-05-08,Blank Snapshot Time,2026-05-08,,Unknown AMC",
                    "2026-05-08,Fresh Snapshot,2026-05-08,2026-05-07T12:00:00+00:00,Unknown AMC",
                ]),
                encoding="utf-8",
            )
            predict.PRE_RESERVATION_CSV = str(snapshot_csv)
            try:
                loaded = predict.load_pre_reservation_data(
                    weekend_of="2026-05-08",
                    through_date="2026-05-07",
                )
            finally:
                predict.PRE_RESERVATION_CSV = old_snapshot_csv

        self.assertNotIn("Blank Weekend Leak", loaded)
        self.assertNotIn("Blank Snapshot Time", loaded)
        self.assertIn("Fresh Snapshot", loaded)

    def test_record_result_stores_snapshot_layer_and_recalibrates_it(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Friday": 1.0},
                "day_scale_factors": {"Friday": 1.0},
                "snapshot_to_day_scale_factors": {"Friday": 1.0},
                "historical_accuracy": [],
            },
        }
        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            entry = calibrate.record_result(
                cal,
                "Sample Movie",
                "2026-05-08",
                predicted_mid=10.0,
                predicted_low=8.0,
                predicted_high=12.0,
                daily_actuals={"Friday": 12.0},
                daily_predictions={"Friday": 10.0},
                n_theatres=425,
                n_days=1,
                snapshot_daily_predictions={"Friday": 10.0},
                snapshot_daily_coverage_ratios={"Friday": 0.9},
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        self.assertEqual({"Friday": 10.0}, entry["snapshot_daily_predictions"])
        self.assertEqual({"Friday": 0.9}, entry["snapshot_daily_coverage_ratios"])
        self.assertNotEqual(
            1.0,
            cal["calibration_factors"]["snapshot_to_day_scale_factors"]["Friday"],
        )

    def test_reference_count_prefers_recorded_prediction_reference(self):
        cal = {
            "history": [
                {
                    "movie": "Expansion Era Movie",
                    "reference_amc_theatres": 376,
                    "daily_theatre_counts": {"Thursday": 425},
                    "daily_coverage_ratios": {"Thursday": 1.0},
                }
            ],
            "calibration_factors": {},
        }

        self.assertEqual(376, reference_amc_theatre_count(cal, fallback=425))

    def test_reference_count_uses_cohort_specific_baseline(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "reference_amc_theatres": 376,
                "reference_amc_theatres_by_cohort": {
                    "core": 376,
                    "core,expansion": 425,
                },
            },
        }

        self.assertEqual(
            425,
            reference_amc_theatre_count(
                cal,
                fallback=425,
                model_cohort_key="core,expansion",
            ),
        )
        self.assertEqual(
            376,
            reference_amc_theatre_count(
                cal,
                fallback=425,
                model_cohort_key="core",
            ),
        )

    def test_expanded_model_does_not_fall_back_to_core_reference(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "reference_amc_theatres": 376,
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
            },
        }
        rows = [self._row(f"Unknown AMC {idx}") for idx in range(1, 6)]

        old_env = predict.os.environ.get("THEATRE_MODEL_COHORTS")
        predict.os.environ["THEATRE_MODEL_COHORTS"] = "core,expansion"
        try:
            pred = predict_movie(
                "Sample Movie",
                {"2026-05-07": rows},
                [],
                cal,
            )
        finally:
            if old_env is None:
                predict.os.environ.pop("THEATRE_MODEL_COHORTS", None)
            else:
                predict.os.environ["THEATRE_MODEL_COHORTS"] = old_env

        thursday = pred["daily_details"]["Thursday"]
        self.assertEqual("core,expansion", pred["model_cohort_key"])
        self.assertEqual(5, pred["reference_amc_theatres"])
        self.assertEqual(5, thursday["expected_theatres"])
        self.assertAlmostEqual(1.0, thursday["sample_normalization_factor"], places=6)
        self.assertAlmostEqual(2500.0, thursday["amc_total"], places=6)

    def test_record_actual_stores_prediction_cohort_reference(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "historical_accuracy": [],
            },
        }
        old_save_calibration = predict.save_calibration
        predict.save_calibration = lambda _cal: None
        try:
            record_actual(
                cal,
                "Sample Movie",
                10.0,
                8.0,
                12.0,
                2.0,
                0.0,
                11.0,
                425,
                ["Thursday"],
                reference_amc_theatres=425,
                model_cohort_key="core,expansion",
            )
        finally:
            predict.save_calibration = old_save_calibration

        entry = cal["history"][-1]
        self.assertEqual("core,expansion", entry["model_cohort_key"])
        self.assertEqual(425, entry["reference_amc_theatres"])
        self.assertEqual(
            425,
            cal["calibration_factors"]["reference_amc_theatres_by_cohort"]["core,expansion"],
        )

    def test_record_result_stores_prediction_cohort_reference(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "historical_accuracy": [],
            },
        }
        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            entry = calibrate.record_result(
                cal,
                "Sample Movie",
                "2026-05-08",
                predicted_mid=10.0,
                predicted_low=8.0,
                predicted_high=12.0,
                daily_actuals={"Thursday": 11.0},
                daily_predictions={"Thursday": 10.0},
                n_theatres=425,
                n_days=1,
                reference_amc_theatres=425,
                model_cohort_key="core,expansion",
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        self.assertEqual("core,expansion", entry["model_cohort_key"])
        self.assertEqual(425, entry["reference_amc_theatres"])
        self.assertEqual(
            425,
            cal["calibration_factors"]["reference_amc_theatres_by_cohort"]["core,expansion"],
        )
        self.assertEqual(
            "core,expansion",
            cal["calibration_factors"]["historical_accuracy"][-1]["model_cohort_key"],
        )

    def test_record_result_can_replace_existing_manual_actual(self):
        cal = {
            "history": [
                {
                    "movie": "Sample Movie",
                    "weekend_of": "2026-05-08",
                    "predicted_mid": 8.0,
                    "actual_total": 9.0,
                }
            ],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "historical_accuracy": [
                    {
                        "movie": "Sample Movie",
                        "weekend_of": "2026-05-08",
                        "abs_error_pct": 10.0,
                    }
                ],
            },
        }
        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            entry = calibrate.record_result(
                cal,
                "Sample Movie",
                "2026-05-08",
                predicted_mid=10.0,
                predicted_low=8.0,
                predicted_high=12.0,
                daily_actuals={"Thursday": 11.0},
                daily_predictions={"Thursday": 10.0},
                n_theatres=425,
                n_days=1,
                actual_source="manual test",
                actual_status="provisional",
                replace_existing=True,
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        matching_history = [
            h for h in cal["history"]
            if h["movie"] == "Sample Movie" and h["weekend_of"] == "2026-05-08"
        ]
        matching_accuracy = [
            h for h in cal["calibration_factors"]["historical_accuracy"]
            if h["movie"] == "Sample Movie" and h["weekend_of"] == "2026-05-08"
        ]
        self.assertEqual(1, len(matching_history))
        self.assertEqual(1, len(matching_accuracy))
        self.assertEqual("manual test", entry["actual_source"])
        self.assertEqual("provisional", entry["actual_status"])
        self.assertEqual(11.0, entry["actual_total"])

    def test_final_calibrated_movies_ignores_provisional_actuals(self):
        cal = {
            "history": [
                {
                    "movie": "Provisional Movie",
                    "weekend_of": "2026-05-08",
                    "actual_status": "provisional",
                },
                {
                    "movie": "Final Movie",
                    "weekend_of": "2026-05-08",
                    "actual_status": "final",
                },
                {
                    "movie": "Legacy Final Movie",
                    "weekend_of": "2026-05-08",
                },
            ],
            "calibration_factors": {},
        }

        done = calibrate.final_calibrated_movies(cal, "2026-05-08")

        self.assertNotIn("Provisional Movie", done)
        self.assertIn("Final Movie", done)
        self.assertIn("Legacy Final Movie", done)

    def test_load_prediction_calibration_requires_freeze_when_requested(self):
        fallback = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Thursday": 1.0},
            },
        }

        old_data_dir = calibrate.DATA_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            calibrate.DATA_DIR = tmpdir
            try:
                with self.assertRaises(FileNotFoundError):
                    calibrate.load_prediction_calibration(
                        "2026-05-08",
                        fallback,
                        require_freeze=True,
                    )
            finally:
                calibrate.DATA_DIR = old_data_dir

    def test_record_pending_calibrations_keeps_all_same_run_accuracy_entries(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "historical_accuracy": [
                    {
                        "movie": "Older Movie",
                        "weekend_of": "2026-05-01",
                        "abs_error_pct": 5.0,
                    }
                ],
            },
        }
        prediction_cal = {
            "calibration_factors": dict(cal["calibration_factors"]),
        }
        pending = [
            self._pending_calibration("Movie One", predicted=10.0, actual=11.0),
            self._pending_calibration("Movie Two", predicted=20.0, actual=18.0),
        ]

        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            entries = calibrate.record_pending_calibrations(
                cal,
                prediction_cal,
                "2026-05-08",
                pending,
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        self.assertEqual(2, len(entries))
        accuracy_movies = [
            entry["movie"]
            for entry in cal["calibration_factors"]["historical_accuracy"]
        ]
        self.assertIn("Movie One", accuracy_movies)
        self.assertIn("Movie Two", accuracy_movies)

    def test_record_pending_calibrations_preserves_prior_same_weekend_accuracy(self):
        prior_entry = {
            "movie": "Already Final Movie",
            "weekend_of": "2026-05-08",
            "predicted_mid": 15.0,
            "actual_total": 12.0,
            "daily_actuals": {"Thursday": 12.0},
            "daily_predictions": {"Thursday": 15.0},
            "n_theatres": 425,
            "n_days": 1,
            "model_cohort_key": "core,expansion",
            "reference_amc_theatres": 425,
        }
        cal = {
            "history": [prior_entry],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "historical_accuracy": [],
            },
        }
        prediction_cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "historical_accuracy": [],
            },
        }
        pending = [
            self._pending_calibration("Movie Two", predicted=20.0, actual=18.0),
        ]

        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            calibrate.record_pending_calibrations(
                cal,
                prediction_cal,
                "2026-05-08",
                pending,
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        accuracy_movies = [
            entry["movie"]
            for entry in cal["calibration_factors"]["historical_accuracy"]
        ]
        self.assertIn("Already Final Movie", accuracy_movies)
        self.assertIn("Movie Two", accuracy_movies)

    def test_record_actual_stores_numeric_days_and_reference_count(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "historical_accuracy": [],
            },
        }
        old_save_calibration = predict.save_calibration
        predict.save_calibration = lambda _cal: None
        try:
            record_actual(
                cal,
                "Sample Movie",
                10.0,
                8.0,
                12.0,
                2.0,
                0.0,
                11.0,
                425,
                ["Thursday", "Friday"],
                reference_amc_theatres=376,
            )
        finally:
            predict.save_calibration = old_save_calibration

        entry = cal["history"][-1]
        self.assertEqual(2, entry["days_collected"])
        self.assertEqual(2, entry["n_days"])
        self.assertEqual(376, entry["reference_amc_theatres"])

    def _pending_calibration(self, movie, predicted, actual):
        return {
            "movie": movie,
            "pred": {
                "n_theatres_total": 425,
                "n_days": 1,
                "reference_amc_theatres": 425,
                "model_cohort_key": "core,expansion",
            },
            "regression_prediction": (predicted, predicted * 0.9, predicted * 1.1),
            "daily_actuals": {"Thursday": actual},
            "daily_predictions": {"Thursday": predicted},
            "raw_daily_predictions": {"Thursday": predicted},
            "daily_theatre_counts": {"Thursday": 425},
            "daily_coverage_ratios": {"Thursday": 1.0},
        }

    def _row(self, theatre_name, date="2026-05-07", day="Thursday", timezone=None):
        row = {
            "movie_title": "Sample Movie",
            "date": date,
            "day_of_week": day,
            "theatre_name": theatre_name,
            "auditorium_type": "Standard",
            "showtime": "7:00 PM",
            "has_seat_map": "true",
            "seats_sold": "50",
            "total_seats": "100",
            "adult_ticket_price": "10",
            "minutes_after_showtime": "0",
        }
        if timezone:
            row["timezone"] = timezone
        return row

    def _snapshot_row(self, theatre_name, day, show_date, timezone=None,
                      snapshot_time="2026-05-07T12:00:00+00:00"):
        row = {
            "weekend_of": "2026-05-08",
            "movie_title": "Sample Movie",
            "show_date": show_date,
            "day_of_week": day,
            "theatre_name": theatre_name,
            "auditorium_type": "Standard",
            "showtime": "7:00 PM",
            "showtime_id": f"{theatre_name}-{show_date}",
            "reserved_seats": "20",
            "total_seats": "100",
            "minutes_until_showtime": "180",
            "snapshot_time": snapshot_time,
            "snapshot_bucket": snapshot_time[:13] + ":00Z",
        }
        if timezone:
            row["timezone"] = timezone
        return row


if __name__ == "__main__":
    unittest.main()
