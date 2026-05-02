import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

import predict
import calibrate
from predict import (
    blend_predictions,
    days_to_weekend,
    polymarket_expected_value,
    predict_movie,
    record_actual,
    reference_amc_theatre_count,
)


class PredictionNormalizationTest(unittest.TestCase):
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

    def test_blend_predictions_keeps_seat_primary_with_liquid_market(self):
        poly_result = {
            "ev": 40.0,
            "low": 35.0,
            "high": 45.0,
            "total_volume": 1_000_000,
        }

        _, _, _, w_seat, w_poly = blend_predictions(
            100.0,
            80.0,
            120.0,
            poly_result,
            n_theatres=400,
            n_days=1,
            coverage_ratio=1.0,
        )

        self.assertGreaterEqual(w_seat, 0.75)
        self.assertLessEqual(w_poly, 0.25)

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

    def test_blend_predictions_uses_coverage_when_available(self):
        poly_result = {
            "ev": 80.0,
            "low": 70.0,
            "high": 90.0,
            "total_volume": 500_000,
        }

        _, _, _, full_w_seat, _ = blend_predictions(
            100.0,
            90.0,
            110.0,
            poly_result,
            n_theatres=400,
            n_days=1,
            coverage_ratio=1.0,
        )
        _, _, _, sparse_w_seat, _ = blend_predictions(
            100.0,
            90.0,
            110.0,
            poly_result,
            n_theatres=400,
            n_days=1,
            coverage_ratio=0.25,
        )

        self.assertLess(sparse_w_seat, full_w_seat)

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


if __name__ == "__main__":
    unittest.main()
