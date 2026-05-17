import unittest
from pathlib import Path
import sys
import tempfile
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

import predict
import calibrate
from historical_comps import (
    HistoricalComp,
    TargetMetadata,
    estimate_opening_weekend_from_thursday,
    release_footprint_factor,
)
from model_calibration import (
    recalibrate_snapshot_day_scale_factors,
    recalibrate_snapshot_lead_scale_factors,
    snapshot_calibration_support,
)
from predict import (
    days_to_weekend,
    national_theatre_count_for_movie,
    national_release_footprint_factor,
    polymarket_expected_value,
    predict_movie,
    record_actual,
    reference_amc_theatre_count,
    select_regression_prediction,
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

    def test_weekend_daypart_gap_reduces_effective_coverage(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Saturday": 1.0},
                "day_scale_factors": {"Saturday": 1.0},
                "reference_amc_theatres": 2,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 2,
                },
            },
        }
        evening_rows = [
            self._row("AMC One", date="2026-05-09", day="Saturday"),
            self._row("AMC Two", date="2026-05-09", day="Saturday"),
        ]
        full_day_rows = []
        for theatre in ("AMC One", "AMC Two"):
            early = self._row(theatre, date="2026-05-09", day="Saturday")
            early["showtime"] = "10:00 AM"
            evening = self._row(theatre, date="2026-05-09", day="Saturday")
            evening["showtime"] = "7:00 PM"
            full_day_rows.extend([early, evening])

        partial = predict_movie(
            "Sample Movie",
            {"2026-05-09": evening_rows},
            [],
            cal,
        )
        full = predict_movie(
            "Sample Movie",
            {"2026-05-09": full_day_rows},
            [],
            cal,
        )

        partial_sat = partial["daily_details"]["Saturday"]
        full_sat = full["daily_details"]["Saturday"]
        self.assertAlmostEqual(1.0, partial_sat["coverage_ratio"], places=6)
        self.assertAlmostEqual(0.0, partial_sat["full_day_window_coverage_ratio"], places=6)
        self.assertLess(partial_sat["effective_coverage_ratio"], 0.50)
        self.assertLess(partial["seat_data_quality"], full["seat_data_quality"])
        self.assertAlmostEqual(1.0, full_sat["effective_coverage_ratio"], places=6)

    def test_late_skew_horror_weekend_schedule_is_not_treated_as_missing_matinees(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Saturday": 1.0},
                "day_scale_factors": {"Saturday": 1.0},
                "reference_amc_theatres": 2,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 2,
                },
            },
        }
        rows = []
        for theatre in ("AMC One", "AMC Two"):
            for showtime in ("4:00 PM", "7:00 PM", "10:00 PM"):
                row = self._row(theatre, date="2026-05-09", day="Saturday")
                row["showtime"] = showtime
                rows.append(row)
        metadata = {
            "sample movie": TargetMetadata(
                movie="Sample Movie",
                genre="horror",
                audience_type="horror_fan",
                franchise_type="original",
                rating="R",
            )
        }

        old_loader = predict.load_movie_metadata
        try:
            predict.load_movie_metadata = lambda: metadata
            pred = predict_movie(
                "Sample Movie",
                {"2026-05-09": rows},
                [],
                cal,
            )
        finally:
            predict.load_movie_metadata = old_loader

        saturday = pred["daily_details"]["Saturday"]
        self.assertAlmostEqual(0.0, saturday["full_day_window_coverage_ratio"], places=6)
        self.assertAlmostEqual(1.0, saturday["daypart_coverage_factor"], places=6)
        self.assertAlmostEqual(1.0, saturday["effective_coverage_ratio"], places=6)

    def test_snapshot_supports_partial_weekend_regular_day(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Saturday": 1.0},
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
            },
        }
        rows = [self._snapshot_row("AMC One", "Saturday", "2026-05-09")]
        layer = predict.build_snapshot_future_layer(
            {"2026-05-09": rows},
            {
                "Saturday": {
                    "domestic_mid": 4_000_000,
                    "coverage_ratio": 1.0,
                    "effective_coverage_ratio": 0.45,
                    "daypart_coverage_factor": 0.45,
                    "actual_override": False,
                }
            },
            cal,
            expected_amc_theatres=1,
        )

        self.assertIn("Saturday", layer["snapshot_days"])
        self.assertEqual([], layer["snapshot_ignored_days"])
        self.assertTrue(
            layer["snapshot_daily_details"]["Saturday"]["supports_partial_regular_day"]
        )

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

    def test_national_theatre_count_is_footprint_drag_for_sub_wide_release(self):
        factor = national_release_footprint_factor(2615)
        self.assertLess(factor, 1.0)
        self.assertGreater(factor, 0.90)
        self.assertAlmostEqual(release_footprint_factor(2615), factor, places=12)
        self.assertEqual(1.0, national_release_footprint_factor(None))

        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "reference_amc_theatres": 2,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 2,
                },
            },
        }
        rows = [
            self._row("AMC One"),
            self._row("AMC Two"),
        ]

        no_count = predict_movie(
            "Sample Movie",
            {"2026-05-07": rows},
            [],
            cal,
        )
        sub_wide = predict_movie(
            "Sample Movie",
            {"2026-05-07": rows},
            [],
            cal,
            national_theatre_count=2615,
        )

        self.assertLess(sub_wide["seat_mid_m"], no_count["seat_mid_m"])
        self.assertLess(
            sub_wide["daily_details"]["Thursday"]["national_footprint_factor"],
            1.0,
        )
        self.assertGreater(
            sub_wide["daily_details"]["Thursday"]["national_footprint_factor"],
            0.90,
        )

    def test_comp_prior_theatre_count_drag_is_chain_adjusted(self):
        target = TargetMetadata(
            movie="Sample Movie",
            genre="horror",
            audience_type="horror_fan",
            franchise_type="original",
            rating="R",
            national_theatre_count=2615,
        )
        comp = HistoricalComp(
            movie="Wide Horror Comp",
            genre="horror",
            audience_type="horror_fan",
            franchise_type="original",
            rating="R",
            thursday_preview_m=10.0,
            opening_weekend_m=100.0,
            national_theatre_count=4000,
        )

        estimate = estimate_opening_weekend_from_thursday(2.6, target, [comp])

        self.assertLess(estimate.prior_footprint_factor, 1.0)
        self.assertGreater(estimate.prior_footprint_factor, 0.90)

    def test_national_theatre_count_falls_back_to_movie_metadata(self):
        metadata = {
            "sample movie": TargetMetadata(
                movie="Sample Movie",
                genre="horror",
                audience_type="horror_fan",
                franchise_type="original",
                rating="R",
                national_theatre_count=2615,
            )
        }

        self.assertEqual(
            2615,
            national_theatre_count_for_movie("Sample Movie", {}, metadata=metadata),
        )

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

    def test_regression_selector_uses_seat_primary_line_when_available(self):
        pred = {
            "seat_mid_m": 30.0,
            "seat_low_m": 24.0,
            "seat_high_m": 36.0,
            "seat_comp_adjusted_mid_m": 18.0,
            "seat_comp_adjusted_low_m": 15.0,
            "seat_comp_adjusted_high_m": 22.0,
            "seat_comp_adjusted_basis": "Thursday comp prior",
            "seat_primary_mid_m": 22.8,
            "seat_primary_low_m": 18.6,
            "seat_primary_high_m": 26.2,
            "seat_primary_w_direct": 0.40,
            "seat_primary_w_comp": 0.60,
        }

        select_regression_prediction(pred, {"history": []})

        self.assertAlmostEqual(22.8, pred["regression_mid_m"], places=6)
        self.assertEqual("seat-primary-regression", pred["regression_source"])
        self.assertIn("direct seats", pred["regression_basis"])
        self.assertFalse(pred["regression_uses_polymarket"])

    def test_seat_primary_dampens_direct_weight_for_sparse_partial_data(self):
        pred = {
            "seat_mid_m": 30.0,
            "seat_low_m": 24.0,
            "seat_high_m": 36.0,
            "seat_comp_adjusted_mid_m": 15.0,
            "seat_comp_adjusted_low_m": 12.0,
            "seat_comp_adjusted_high_m": 18.0,
            "seat_comp_mid_m": 15.0,
            "seat_comp_low_m": 12.0,
            "seat_comp_high_m": 18.0,
            "n_days": 1,
            "seat_data_quality": 0.10,
        }

        primary = predict.seat_primary_ensemble(pred)

        self.assertLess(primary["w_direct"], 0.30)
        self.assertGreater(primary["w_comp"], 0.70)
        self.assertLess(primary["mid_m"], 19.5)
        self.assertGreater(primary["mid_m"], 15.0)

    def test_reported_actual_days_raise_direct_weight_in_seat_primary(self):
        sparse_pred = {
            "seat_mid_m": 20.0,
            "seat_low_m": 16.0,
            "seat_high_m": 24.0,
            "seat_comp_adjusted_mid_m": 12.0,
            "seat_comp_adjusted_low_m": 10.0,
            "seat_comp_adjusted_high_m": 14.0,
            "seat_comp_mid_m": 12.0,
            "seat_comp_low_m": 10.0,
            "seat_comp_high_m": 14.0,
            "n_days": 2,
            "seat_data_quality": 0.42,
        }
        actual_anchored = dict(sparse_pred)
        actual_anchored["reported_actual_day_share"] = 0.38

        sparse = predict.seat_primary_ensemble(sparse_pred)
        anchored = predict.seat_primary_ensemble(actual_anchored)

        self.assertGreater(anchored["w_direct"], sparse["w_direct"])
        self.assertGreaterEqual(anchored["w_direct"], 0.45)
        self.assertGreater(anchored["mid_m"], sparse["mid_m"])

    def test_actual_anchor_reduces_metadata_prior_weight(self):
        pred = {
            "n_days": 2,
            "seat_data_quality": 0.42,
            "reported_actual_day_share": 0.38,
            "missing_data_profile": {
                "missing_day_share": 0.62,
            },
        }

        self.assertLess(predict.missing_data_prior_weight(pred), 0.45)

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

    def test_family_daypart_adjustment_boosts_low_evening_show_count(self):
        metadata = types.SimpleNamespace(audience_type="broad_family", rating="PG")

        adjusted = predict.daypart_adjusted_evening_to_daily(
            1.7,
            "Saturday",
            avg_showings=2.1,
            target_metadata=metadata,
        )

        self.assertGreater(adjusted, 3.0)
        self.assertLessEqual(adjusted, 3.8)

    def test_daypart_adjustment_does_not_boost_non_family_movies(self):
        metadata = types.SimpleNamespace(audience_type="fan_driven", rating="R")

        adjusted = predict.daypart_adjusted_evening_to_daily(
            1.7,
            "Saturday",
            avg_showings=2.1,
            target_metadata=metadata,
        )

        self.assertAlmostEqual(1.7, adjusted)

    def test_saturday_full_day_window_removes_evening_multiplier(self):
        metadata = types.SimpleNamespace(audience_type="broad_family", rating="PG")

        adjusted = predict.daypart_adjusted_evening_to_daily(
            1.7,
            "Saturday",
            avg_showings=5.5,
            target_metadata=metadata,
            earliest_showtime_hour=10.0,
            full_day_window_coverage_ratio=0.80,
        )

        self.assertAlmostEqual(1.0, adjusted)

    def test_single_early_showtime_does_not_make_weekend_sample_full_day(self):
        metadata = types.SimpleNamespace(audience_type="broad_family", rating="PG")

        adjusted = predict.daypart_adjusted_evening_to_daily(
            1.7,
            "Saturday",
            avg_showings=2.1,
            target_metadata=metadata,
            earliest_showtime_hour=10.0,
            full_day_window_coverage_ratio=0.05,
        )

        self.assertGreater(adjusted, 3.0)

    def test_showtime_window_marker_without_daytime_rows_does_not_count_full_day(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Saturday": 1.0},
                "day_scale_factors": {"Saturday": 1.0},
                "reference_amc_theatres": 2,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 2,
                },
            },
        }
        rows = [
            self._row("AMC One", date="2026-05-09", day="Saturday"),
            self._row("AMC Two", date="2026-05-09", day="Saturday"),
        ]
        for row in rows:
            row["notes"] = "Standard @ 7:00 PM; showtime_window=sat-sun-10-23-v1"

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-09": rows},
            [],
            cal,
        )

        saturday = pred["daily_details"]["Saturday"]
        self.assertAlmostEqual(0.0, saturday["full_day_window_coverage_ratio"])
        self.assertAlmostEqual(1.7, saturday["evening_to_daily"])

    def test_showtime_window_with_observed_daytime_rows_counts_full_day(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Saturday": 1.0},
                "day_scale_factors": {"Saturday": 1.0},
                "reference_amc_theatres": 2,
                "reference_amc_theatres_by_cohort": {
                    "core,expansion": 2,
                },
            },
        }
        rows = []
        for theatre in ("AMC One", "AMC Two"):
            early = self._row(theatre, date="2026-05-09", day="Saturday")
            early["showtime"] = "11:00 AM"
            early["amc_seat_map_url"] = f"https://example.test/{theatre}/early"
            early["notes"] = "Standard @ 11:00 AM; showtime_window=sat-sun-10-23-v1"
            evening = self._row(theatre, date="2026-05-09", day="Saturday")
            evening["showtime"] = "7:00 PM"
            evening["amc_seat_map_url"] = f"https://example.test/{theatre}/evening"
            evening["notes"] = "Standard @ 7:00 PM; showtime_window=sat-sun-10-23-v1"
            rows.extend([early, evening])

        pred = predict_movie(
            "Sample Movie",
            {"2026-05-09": rows},
            [],
            cal,
        )

        saturday = pred["daily_details"]["Saturday"]
        self.assertAlmostEqual(1.0, saturday["full_day_window_coverage_ratio"])
        self.assertAlmostEqual(1.0, saturday["evening_to_daily"])

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
        self.assertIsNotNone(pred["snapshot_calibration_support_factor"])
        self.assertEqual(
            "seat+snapshot-regression",
            pred["regression_source"],
        )

    def test_snapshot_layer_weight_is_capped_by_untrained_lead_bucket(self):
        def cal_with_next_day_support(next_day_support):
            return {
                "history": [],
                "calibration_factors": {
                    "amc_market_share": 0.25,
                    "overall_scale_factor": 1.0,
                    "day_weights": {"Friday": 0.5, "Saturday": 0.5},
                    "snapshot_to_day_scale_factors": {"Friday": 1.0, "Saturday": 1.0},
                    "snapshot_to_lead_scale_factors": {
                        "same_day": 1.0,
                        "next_day": 1.0,
                        "multi_day": 1.0,
                        "long_lead": 1.0,
                    },
                    "snapshot_calibration_support": {
                        "days": {
                            "Friday": {"n": 8, "support": 8.0},
                            "Saturday": {"n": 8, "support": 8.0},
                        },
                        "leads": {
                            "same_day": {"n": 8, "support": 8.0},
                            "next_day": {"n": int(next_day_support), "support": next_day_support},
                        },
                    },
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
        for row in saturday_rows:
            row["minutes_until_showtime"] = str(25 * 60)

        untrained = predict.build_snapshot_future_layer(
            {"2026-05-08": friday_rows, "2026-05-09": saturday_rows},
            {},
            cal_with_next_day_support(0.0),
            expected_amc_theatres=2,
            expected_timezone_counts={"ET": 1, "CT": 1},
            theatre_timezone_map={"AMC One": "ET", "AMC Two": "CT"},
        )
        trained = predict.build_snapshot_future_layer(
            {"2026-05-08": friday_rows, "2026-05-09": saturday_rows},
            {},
            cal_with_next_day_support(8.0),
            expected_amc_theatres=2,
            expected_timezone_counts={"ET": 1, "CT": 1},
            theatre_timezone_map={"AMC One": "ET", "AMC Two": "CT"},
        )

        self.assertLess(
            untrained["snapshot_model_weight"],
            trained["snapshot_model_weight"],
        )
        self.assertAlmostEqual(
            0.575,
            untrained["snapshot_calibration_support_factor"],
            places=6,
        )
        self.assertAlmostEqual(
            0.8,
            trained["snapshot_calibration_support_factor"],
            places=6,
        )
        self.assertAlmostEqual(
            0.35,
            untrained["snapshot_daily_details"]["Saturday"][
                "snapshot_calibration_support_factor"
            ],
            places=6,
        )
        self.assertGreater(
            trained["snapshot_daily_details"]["Saturday"][
                "snapshot_calibration_support_factor"
            ],
            0.75,
        )

    def test_same_week_calibrated_partial_snapshot_gets_meaningful_weight(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {
                    "Thursday": 0.12,
                    "Friday": 0.32,
                    "Saturday": 0.33,
                    "Sunday": 0.23,
                },
                "snapshot_to_day_scale_factors": {
                    "Thursday": 1.0,
                    "Friday": 1.0,
                    "Saturday": 1.0,
                    "Sunday": 1.0,
                },
                "snapshot_to_lead_scale_factors": {
                    "same_day": 1.0,
                    "next_day": 1.0,
                    "multi_day": 1.0,
                },
            },
        }
        theatre_names = [f"AMC Signal {idx:02d}" for idx in range(24)]
        snapshot_data = {}
        for day, date_str in (
            ("Thursday", "2026-05-07"),
            ("Friday", "2026-05-08"),
            ("Saturday", "2026-05-09"),
            ("Sunday", "2026-05-10"),
        ):
            snapshot_data[date_str] = [
                self._snapshot_row(name, day, date_str, timezone="ET")
                for name in theatre_names
            ]
        regular_daily_details = {
            "Thursday": {"domestic_mid": 2_600_000, "coverage_ratio": 0.8},
            "Friday": {"domestic_mid": 7_500_000, "coverage_ratio": 0.6},
        }

        layer = predict.build_snapshot_future_layer(
            snapshot_data,
            regular_daily_details,
            cal,
            expected_amc_theatres=100,
        )

        self.assertEqual(
            ["Friday", "Thursday"],
            sorted(anchor["day"] for anchor in layer["snapshot_same_week_anchors"]),
        )
        self.assertAlmostEqual(0.24, layer["snapshot_coverage_ratio"], places=6)
        self.assertAlmostEqual(0.70, layer["snapshot_same_week_support_floor"], places=6)
        self.assertGreaterEqual(layer["snapshot_model_weight"], 0.12)

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

    def test_snapshot_day_accepts_rest_of_weekend_lead_window(self):
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
        too_far_row = self._snapshot_row(
            "AMC Too Far",
            "Saturday",
            "2026-05-09",
            timezone="PT",
        )
        too_far_row["minutes_until_showtime"] = str(120 * 60)
        stale_row = self._snapshot_row(
            "AMC Stale",
            "Saturday",
            "2026-05-09",
            timezone="PT",
        )
        stale_row["minutes_until_showtime"] = "-30"
        missing_lead_row = self._snapshot_row(
            "AMC Missing Lead",
            "Saturday",
            "2026-05-09",
            timezone="PT",
        )
        missing_lead_row["minutes_until_showtime"] = ""

        details = predict.estimate_snapshot_day(
            [near_row, far_row, too_far_row, stale_row, missing_lead_row],
            "2026-05-09",
            cal,
            expected_amc_theatres=3,
            expected_timezone_counts={"ET": 1, "CT": 1, "PT": 1},
        )

        self.assertEqual(2, details["n_theatres"])
        self.assertEqual(["CT", "ET"], details["observed_timezones"])
        self.assertEqual(["PT"], details["missing_timezones"])
        self.assertEqual(3, details["n_lead_window_ignored"])

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
                "daily_actuals": {"Friday": 14.0},
                "snapshot_daily_predictions": {"Friday": 10.0},
                "snapshot_daily_coverage_ratios": {"Friday": 0.9},
            },
        ]

        scales = recalibrate_snapshot_day_scale_factors(history, alpha=0.5)

        self.assertIn("Friday", scales)
        self.assertNotEqual(1.0, scales["Friday"])

    def test_snapshot_calibration_uses_raw_unscaled_snapshot_mid(self):
        snapshot_predictions, snapshot_coverage, snapshot_leads = (
            calibrate.snapshot_calibration_fields_from_prediction({
                "snapshot_daily_details": {
                    "Friday": {
                        "raw_domestic_mid": 10_000_000,
                        "domestic_mid": 20_000_000,
                        "effective_coverage_ratio": 0.9,
                        "lead_bucket": "next_day",
                    },
                },
            })
        )

        self.assertEqual({"Friday": 10.0}, snapshot_predictions)
        self.assertEqual({"Friday": 0.9}, snapshot_coverage)
        self.assertEqual({"Friday": "next_day"}, snapshot_leads)

    def test_predict_actual_snapshot_calibration_uses_raw_unscaled_snapshot_mid(self):
        snapshot_predictions, snapshot_coverage, snapshot_leads = (
            predict.snapshot_calibration_fields_from_prediction({
                "snapshot_daily_details": {
                    "Saturday": {
                        "raw_domestic_mid": 8_000_000,
                        "domestic_mid": 16_000_000,
                        "coverage_ratio": 0.5,
                        "lead_bucket": "multi_day",
                    },
                },
            })
        )

        self.assertEqual({"Saturday": 8.0}, snapshot_predictions)
        self.assertEqual({"Saturday": 0.5}, snapshot_coverage)
        self.assertEqual({"Saturday": "multi_day"}, snapshot_leads)

    def test_snapshot_calibration_keeps_ignored_regular_days(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Friday": 1.0},
                "snapshot_to_day_scale_factors": {"Friday": 1.0},
            },
        }
        rows = [
            self._snapshot_row(
                "AMC Snapshot",
                "Friday",
                "2026-05-08",
                timezone="ET",
                snapshot_time="2026-05-07T12:00:00+00:00",
            )
        ]

        layer = predict.build_snapshot_future_layer(
            {"2026-05-08": rows},
            {
                "Friday": {
                    "domestic_mid": 12_000_000,
                    "coverage_ratio": 1.0,
                    "effective_coverage_ratio": 1.0,
                }
            },
            cal,
            expected_amc_theatres=1,
            expected_timezone_counts={"ET": 1},
        )

        self.assertEqual({}, layer["snapshot_daily_details"])
        self.assertIn("Friday", layer["snapshot_all_daily_details"])
        snapshot_predictions, snapshot_coverage, snapshot_leads = (
            calibrate.snapshot_calibration_fields_from_prediction(layer)
        )
        self.assertIn("Friday", snapshot_predictions)
        self.assertEqual({"Friday": 1.0}, snapshot_coverage)
        self.assertEqual({"Friday": "same_day"}, snapshot_leads)

    def test_snapshot_lead_scale_learns_residual_after_day_scale(self):
        history = [
            {
                "movie": "Same Day Snapshot",
                "daily_actuals": {"Friday": 15.0},
                "snapshot_daily_predictions": {"Friday": 10.0},
                "snapshot_daily_coverage_ratios": {"Friday": 1.0},
                "snapshot_daily_lead_buckets": {"Friday": "same_day"},
            }
        ]

        scales = recalibrate_snapshot_lead_scale_factors(
            history,
            day_scales={"Friday": 1.0},
            alpha=0.5,
        )

        self.assertGreater(scales["same_day"], 1.0)

    def test_snapshot_pickup_profile_matches_final_seat_rows(self):
        snapshot_row = self._snapshot_row(
            "AMC One",
            "Friday",
            "2026-05-08",
            snapshot_time="2026-05-08T20:00:00+00:00",
        )
        snapshot_row["reserved_seats"] = "20"
        snapshot_row["minutes_until_showtime"] = "180"
        snapshot_row["amc_seat_map_url"] = "https://www.amctheatres.com/showtimes/123/seats"
        seat_row = self._row("AMC One", date="2026-05-08", day="Friday")
        seat_row["seats_sold"] = "54"
        seat_row["amc_seat_map_url"] = "https://www.amctheatres.com/showtimes/123/seats"

        profile = predict.snapshot_pickup_profile([snapshot_row], [seat_row], {})

        self.assertEqual(1, profile["n_matched_showtimes"])
        self.assertEqual(20, profile["reserved_seats_at_snapshot"])
        self.assertEqual(54, profile["final_sold_seats"])
        self.assertEqual(34, profile["post_snapshot_pickup_seats"])
        self.assertAlmostEqual(2.0, profile["projected_revenue_scale"], places=6)
        self.assertAlmostEqual(0.6296, profile["post_snapshot_pickup_share"], places=4)

    def test_snapshot_future_layer_uses_matched_pickup_scale(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "overall_scale_factor": 1.0,
                "day_weights": {"Friday": 0.5, "Saturday": 0.5},
                "day_scale_factors": {"Friday": 1.0, "Saturday": 1.0},
                "snapshot_to_day_scale_factors": {"Friday": 1.0, "Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
                "reference_amc_theatres": 1,
                "reference_amc_theatres_by_cohort": {"core,expansion": 1},
            },
        }
        friday_snapshot = self._snapshot_row(
            "AMC One",
            "Friday",
            "2026-05-08",
            snapshot_time="2026-05-08T20:00:00+00:00",
        )
        friday_snapshot["reserved_seats"] = "20"
        friday_snapshot["minutes_until_showtime"] = "180"
        friday_snapshot["amc_seat_map_url"] = "https://www.amctheatres.com/showtimes/123/seats"
        saturday_snapshot = self._snapshot_row(
            "AMC One",
            "Saturday",
            "2026-05-09",
            snapshot_time="2026-05-09T20:00:00+00:00",
        )
        saturday_snapshot["reserved_seats"] = "20"
        saturday_snapshot["minutes_until_showtime"] = "180"
        saturday_snapshot["amc_seat_map_url"] = "https://www.amctheatres.com/showtimes/456/seats"
        friday_seat = self._row("AMC One", date="2026-05-08", day="Friday")
        friday_seat["seats_sold"] = "54"
        friday_seat["amc_seat_map_url"] = "https://www.amctheatres.com/showtimes/123/seats"

        raw_saturday = predict.estimate_snapshot_day(
            [saturday_snapshot],
            "2026-05-09",
            cal,
            expected_amc_theatres=1,
        )
        layer = predict.build_snapshot_future_layer(
            {
                "2026-05-08": [friday_snapshot],
                "2026-05-09": [saturday_snapshot],
            },
            {
                "Friday": {
                    "date": "2026-05-08",
                    "domestic_mid": 540,
                    "coverage_ratio": 1.0,
                    "effective_coverage_ratio": 1.0,
                }
            },
            cal,
            expected_amc_theatres=1,
            regular_seat_data={"2026-05-08": [friday_seat]},
        )

        self.assertAlmostEqual(2.0, layer["snapshot_same_week_scale"], places=6)
        self.assertEqual("matched_showtime_pickup", layer["snapshot_same_week_scale_source"])
        self.assertEqual(1, layer["snapshot_pickup_profile"]["n_matched_showtimes"])
        self.assertAlmostEqual(
            raw_saturday["domestic_mid"] * 2.0,
            layer["snapshot_daily_details"]["Saturday"]["pre_day_shape_domestic_mid"],
            places=6,
        )

    def test_snapshot_pickup_scale_for_weekend_days_prefers_friday_anchor(self):
        anchors = [
            {"day": "Thursday", "scale": 0.80, "weight": 1.0},
            {"day": "Friday", "scale": 1.20, "weight": 1.0},
        ]

        saturday_scale = predict.snapshot_pickup_scale_for_day(
            "Saturday",
            anchors,
            fallback_scale=1.0,
        )
        sunday_scale = predict.snapshot_pickup_scale_for_day(
            "Sunday",
            anchors,
            fallback_scale=1.0,
        )

        self.assertGreater(saturday_scale, 1.08)
        self.assertGreater(sunday_scale, 1.05)
        self.assertLess(saturday_scale, 1.20)

    def test_snapshot_day_shape_signal_uses_strategic_sample_confidence(self):
        details = {
            "domestic_mid": 12_000_000,
            "domestic_low": 10_000_000,
            "domestic_high": 14_000_000,
            "effective_coverage_ratio": 0.25,
            "effective_strategic_coverage_ratio": 1.0,
            "snapshot_calibration_support_factor": 0.70,
        }

        adjusted = predict.apply_snapshot_day_shape_prior(
            details,
            8_000_000,
        )

        self.assertGreater(adjusted["snapshot_day_shape_signal_weight"], 0.40)
        self.assertLess(adjusted["snapshot_day_shape_prior_weight"], 0.60)

    def test_snapshot_day_tracks_raw_and_strategic_coverage(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
            },
        }
        rows = [
            self._snapshot_row(f"AMC {idx}", "Saturday", "2026-05-16")
            for idx in range(100)
        ]

        details = predict.estimate_snapshot_day(
            rows,
            "2026-05-16",
            cal,
            expected_amc_theatres=425,
        )

        self.assertAlmostEqual(100 / 425, details["coverage_ratio"], places=6)
        self.assertEqual(100, details["strategic_expected_theatres"])
        self.assertAlmostEqual(1.0, details["strategic_coverage_ratio"], places=6)
        self.assertAlmostEqual(
            1.0,
            details["effective_strategic_coverage_ratio"],
            places=6,
        )

    def test_snapshot_layer_weight_uses_strategic_coverage_not_raw_amc_share(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {
                    "Thursday": 0.12,
                    "Friday": 0.32,
                    "Saturday": 0.33,
                    "Sunday": 0.23,
                },
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
                "snapshot_calibration_support": {
                    "days": {"Saturday": {"support": 10.0, "n": 2}},
                    "leads": {"same_day": {"support": 10.0, "n": 2}},
                },
            },
        }
        rows = [
            self._snapshot_row(f"AMC {idx}", "Saturday", "2026-05-16")
            for idx in range(100)
        ]

        layer = predict.build_snapshot_future_layer(
            {"2026-05-16": rows},
            {},
            cal,
            expected_amc_theatres=425,
        )

        self.assertLess(layer["snapshot_coverage_ratio"], 0.30)
        self.assertAlmostEqual(1.0, layer["snapshot_model_coverage_ratio"], places=6)
        self.assertAlmostEqual(1.0, layer["snapshot_weight_coverage_signal"], places=6)
        self.assertGreater(layer["snapshot_model_weight"], 0.30)

    def test_snapshot_layer_uses_same_week_actual_amc_share_anchor(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Saturday": 1.0},
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
            },
        }
        rows = [self._snapshot_row("AMC One", "Saturday", "2026-05-16")]

        prior_layer = predict.build_snapshot_future_layer(
            {"2026-05-16": rows},
            {},
            cal,
            expected_amc_theatres=1,
        )
        anchored_layer = predict.build_snapshot_future_layer(
            {"2026-05-16": rows},
            {},
            cal,
            expected_amc_theatres=1,
            amc_share_anchor={"day": "Friday", "blended_share": 0.20},
        )

        prior_mid = prior_layer["snapshot_daily_details"]["Saturday"]["raw_domestic_mid"]
        anchored_details = anchored_layer["snapshot_daily_details"]["Saturday"]
        self.assertAlmostEqual(0.20, anchored_details["amc_market_share_used"])
        self.assertEqual(
            "same_week_actual_anchor",
            anchored_details["amc_market_share_source"],
        )
        self.assertGreater(anchored_details["raw_domestic_mid"], prior_mid * 1.20)

    def test_snapshot_layer_weights_multiple_same_week_amc_share_anchors_by_day(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Saturday": 1.0},
                "snapshot_to_day_scale_factors": {"Saturday": 1.0},
                "snapshot_to_lead_scale_factors": {"same_day": 1.0},
            },
        }
        rows = [self._snapshot_row("AMC One", "Saturday", "2026-05-16")]

        layer = predict.build_snapshot_future_layer(
            {"2026-05-16": rows},
            {},
            cal,
            expected_amc_theatres=1,
            amc_share_anchors=[
                {"day": "Thursday", "blended_share": 0.10, "anchor_weight": 1.0},
                {"day": "Friday", "blended_share": 0.20, "anchor_weight": 1.0},
            ],
        )

        details = layer["snapshot_daily_details"]["Saturday"]
        anchor = details["amc_market_share_anchor"]
        self.assertEqual(["Thursday", "Friday"], anchor["days"])
        self.assertGreater(details["amc_market_share_used"], 0.19)
        self.assertLess(details["amc_market_share_used"], 0.20)
        self.assertEqual(
            "same_week_actual_anchor",
            details["amc_market_share_source"],
        )

    def test_snapshot_calibration_support_tracks_day_and_lead_history(self):
        history = [
            {
                "movie": "Reliable Snapshot",
                "daily_actuals": {"Saturday": 12.0},
                "snapshot_daily_predictions": {"Saturday": 10.0},
                "snapshot_daily_coverage_ratios": {"Saturday": 0.8},
                "snapshot_daily_lead_buckets": {"Saturday": "next_day"},
            },
            {
                "movie": "Too Sparse Snapshot",
                "daily_actuals": {"Saturday": 12.0},
                "snapshot_daily_predictions": {"Saturday": 10.0},
                "snapshot_daily_coverage_ratios": {"Saturday": 0.05},
                "snapshot_daily_lead_buckets": {"Saturday": "next_day"},
            },
        ]

        support = snapshot_calibration_support(history)

        self.assertEqual(1, support["days"]["Saturday"]["n"])
        self.assertAlmostEqual(0.8, support["days"]["Saturday"]["support"])
        self.assertEqual(1, support["leads"]["next_day"]["n"])
        self.assertAlmostEqual(0.8, support["leads"]["next_day"]["support"])

    def test_sparse_snapshot_lead_scale_is_shrunk_toward_prior(self):
        history = [
            {
                "movie": "Extreme Sparse Snapshot",
                "daily_actuals": {"Friday": 50.0},
                "snapshot_daily_predictions": {"Friday": 10.0},
                "snapshot_daily_coverage_ratios": {"Friday": 1.0},
                "snapshot_daily_lead_buckets": {"Friday": "same_day"},
            }
        ]

        scales = recalibrate_snapshot_lead_scale_factors(
            history,
            day_scales={"Friday": 1.0},
            alpha=1.0,
        )

        self.assertLess(scales["same_day"], 1.5)

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

    def test_calibration_record_result_stores_model_version(self):
        cal = {
            "history": [],
            "calibration_factors": {
                "historical_accuracy": [],
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
            },
        }
        old_save_calibration = calibrate.save_calibration
        calibrate.save_calibration = lambda _cal: None
        try:
            entry = calibrate.record_result(
                cal,
                "Sample Movie",
                "2026-05-15",
                predicted_mid=10.0,
                predicted_low=8.0,
                predicted_high=12.0,
                daily_actuals={"Thursday": 10.0},
                daily_predictions={"Thursday": 10.0},
                n_theatres=425,
                n_days=1,
                model_version=predict.MODEL_VERSION,
            )
        finally:
            calibrate.save_calibration = old_save_calibration

        self.assertEqual(predict.MODEL_VERSION, entry["model_version"])

    def test_regression_uses_shrunk_historical_residuals(self):
        pred = {
            "movie": "Future Movie",
            "seat_comp_mid_m": 100.0,
            "seat_comp_low_m": 90.0,
            "seat_comp_high_m": 110.0,
            "n_theatres_total": 425,
            "n_days": 4,
            "coverage_ratio": 1.0,
            "seat_weighted_coverage_ratio": 1.0,
            "seat_data_quality": 1.0,
            "model_cohort_key": "core,expansion",
        }
        cal = {
            "history": [
                {
                    "movie": "Settled One",
                    "predicted_mid": 100.0,
                    "actual_total": 80.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                },
                {
                    "movie": "Settled Two",
                    "predicted_mid": 50.0,
                    "actual_total": 40.0,
                    "n_theatres": 420,
                    "n_days": 4,
                    "coverage_ratio": 0.95,
                    "model_cohort_key": "core,expansion",
                },
            ],
        }

        select_regression_prediction(pred, cal)

        self.assertLess(pred["regression_mid_m"], 100.0)
        self.assertGreater(pred["regression_mid_m"], 80.0)
        self.assertLess(pred["historical_residual_factor"], 1.0)
        self.assertEqual(2, pred["historical_residual_n"])
        self.assertIn("historical-residual", pred["regression_source"])
        self.assertFalse(pred["regression_uses_polymarket"])

    def test_legacy_model_residuals_are_downweighted(self):
        def prediction():
            return {
                "movie": "Future Movie",
                "seat_comp_mid_m": 100.0,
                "seat_comp_low_m": 90.0,
                "seat_comp_high_m": 110.0,
                "n_theatres_total": 425,
                "n_days": 4,
                "coverage_ratio": 1.0,
                "seat_weighted_coverage_ratio": 1.0,
                "seat_data_quality": 1.0,
                "model_cohort_key": "core,expansion",
                "model_version": predict.MODEL_VERSION,
            }

        base_entries = [
            {
                "movie": "Settled One",
                "predicted_mid": 100.0,
                "actual_total": 80.0,
                "n_theatres": 425,
                "n_days": 4,
                "coverage_ratio": 1.0,
                "model_cohort_key": "core,expansion",
            },
            {
                "movie": "Settled Two",
                "predicted_mid": 50.0,
                "actual_total": 40.0,
                "n_theatres": 420,
                "n_days": 4,
                "coverage_ratio": 0.95,
                "model_cohort_key": "core,expansion",
            },
        ]
        legacy_pred = prediction()
        current_pred = prediction()
        current_entries = [
            {**entry, "model_version": predict.MODEL_VERSION}
            for entry in base_entries
        ]

        select_regression_prediction(legacy_pred, {"history": base_entries})
        select_regression_prediction(current_pred, {"history": current_entries})

        self.assertLess(
            legacy_pred["historical_residual_strength"],
            current_pred["historical_residual_strength"],
        )
        self.assertGreater(
            legacy_pred["historical_residual_factor"],
            current_pred["historical_residual_factor"],
        )

    def test_historical_residual_weights_metadata_similar_movies(self):
        pred = {
            "movie": "Target Horror",
            "seat_comp_mid_m": 100.0,
            "seat_comp_low_m": 90.0,
            "seat_comp_high_m": 110.0,
            "n_theatres_total": 425,
            "n_days": 4,
            "coverage_ratio": 1.0,
            "seat_weighted_coverage_ratio": 1.0,
            "seat_data_quality": 1.0,
            "model_cohort_key": "core,expansion",
            "model_version": predict.MODEL_VERSION,
        }
        cal = {
            "history": [
                {
                    "movie": "Similar Horror",
                    "predicted_mid": 100.0,
                    "actual_total": 60.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                    "model_version": predict.MODEL_VERSION,
                },
                {
                    "movie": "Different Comedy",
                    "predicted_mid": 100.0,
                    "actual_total": 150.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                    "model_version": predict.MODEL_VERSION,
                },
            ],
        }
        metadata = {
            "target horror": TargetMetadata(
                "Target Horror", "horror", "horror_fan", "original", "R",
            ),
            "similar horror": TargetMetadata(
                "Similar Horror", "horror", "horror_fan", "original", "R",
            ),
            "different comedy": TargetMetadata(
                "Different Comedy", "comedy", "female_skewing", "sequel", "PG-13",
            ),
        }
        old_loader = predict.load_movie_metadata
        predict.load_movie_metadata = lambda: metadata
        try:
            select_regression_prediction(pred, cal)
        finally:
            predict.load_movie_metadata = old_loader

        weights = {
            item["movie"]: item["weight"]
            for item in pred["historical_residual_examples"]
        }
        self.assertGreater(weights["Similar Horror"], weights["Different Comedy"])
        self.assertLess(pred["regression_mid_m"], 100.0)

    def test_historical_residual_weights_similar_release_footprints(self):
        pred = {
            "movie": "Target Horror",
            "seat_comp_mid_m": 100.0,
            "seat_comp_low_m": 90.0,
            "seat_comp_high_m": 110.0,
            "n_theatres_total": 425,
            "n_days": 4,
            "coverage_ratio": 1.0,
            "seat_weighted_coverage_ratio": 1.0,
            "seat_data_quality": 1.0,
            "model_cohort_key": "core,expansion",
            "model_version": predict.MODEL_VERSION,
        }
        cal = {
            "history": [
                {
                    "movie": "Same Footprint Horror",
                    "predicted_mid": 100.0,
                    "actual_total": 80.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                    "model_version": predict.MODEL_VERSION,
                },
                {
                    "movie": "Ultra Wide Horror",
                    "predicted_mid": 100.0,
                    "actual_total": 80.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                    "model_version": predict.MODEL_VERSION,
                },
            ],
        }
        metadata = {
            "target horror": TargetMetadata(
                "Target Horror", "horror", "horror_fan", "original", "R",
                national_theatre_count=2600,
            ),
            "same footprint horror": TargetMetadata(
                "Same Footprint Horror", "horror", "horror_fan", "original", "R",
                national_theatre_count=2550,
            ),
            "ultra wide horror": TargetMetadata(
                "Ultra Wide Horror", "horror", "horror_fan", "original", "R",
                national_theatre_count=4300,
            ),
        }
        old_loader = predict.load_movie_metadata
        predict.load_movie_metadata = lambda: metadata
        try:
            select_regression_prediction(pred, cal)
        finally:
            predict.load_movie_metadata = old_loader

        weights = {
            item["movie"]: item["weight"]
            for item in pred["historical_residual_examples"]
        }
        self.assertGreater(
            weights["Same Footprint Horror"],
            weights["Ultra Wide Horror"],
        )

    def test_regression_residual_skips_target_and_provisional_actuals(self):
        pred = {
            "movie": "Future Movie",
            "seat_comp_mid_m": 100.0,
            "seat_comp_low_m": 90.0,
            "seat_comp_high_m": 110.0,
            "n_theatres_total": 425,
            "n_days": 4,
            "coverage_ratio": 1.0,
            "seat_weighted_coverage_ratio": 1.0,
            "seat_data_quality": 1.0,
            "model_cohort_key": "core,expansion",
        }
        cal = {
            "history": [
                {
                    "movie": "Future Movie",
                    "predicted_mid": 100.0,
                    "actual_total": 50.0,
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                },
                {
                    "movie": "Other Provisional",
                    "predicted_mid": 100.0,
                    "actual_total": 50.0,
                    "actual_status": "provisional",
                    "n_theatres": 425,
                    "n_days": 4,
                    "coverage_ratio": 1.0,
                    "model_cohort_key": "core,expansion",
                },
            ],
        }

        select_regression_prediction(pred, cal)

        self.assertAlmostEqual(100.0, pred["regression_mid_m"], places=6)
        self.assertNotIn("historical_residual_factor", pred)

    def test_social_signal_layer_is_capped_and_excludes_polymarket(self):
        pred = {
            "movie": "Future Movie",
            "seat_comp_mid_m": 100.0,
            "seat_comp_low_m": 90.0,
            "seat_comp_high_m": 110.0,
            "n_theatres_total": 425,
            "n_days": 4,
            "coverage_ratio": 1.0,
            "seat_weighted_coverage_ratio": 1.0,
            "seat_data_quality": 1.0,
            "model_cohort_key": "core,expansion",
            "social_signal": {
                "factor": 1.50,
                "adjustment_pct": 50.0,
                "sentiment_score": 1.0,
                "buzz_score": 1.0,
                "signal_quality": 1.0,
                "reach": 1000000,
                "rows": 2,
                "platforms": ["TikTok", "X"],
            },
        }

        select_regression_prediction(pred, {})

        self.assertAlmostEqual(108.0, pred["regression_mid_m"], places=6)
        self.assertEqual(8.0, pred["social_adjustment_pct"])
        self.assertIn("social", pred["regression_source"])
        self.assertFalse(pred["regression_uses_polymarket"])

    def test_build_social_signal_layer_is_neutral_without_quality(self):
        layer = predict.build_social_signal_layer(
            "Future Movie",
            {
                "Future Movie": {
                    "sentiment_score": 1.0,
                    "buzz_score": 1.0,
                    "signal_quality": 0.0,
                    "reach": 0,
                    "rows": 1,
                    "platforms": ["manual"],
                }
            },
        )

        self.assertEqual(1.0, layer["factor"])
        self.assertEqual(0.0, layer["adjustment_pct"])

    def test_social_signal_loader_uses_latest_platform_snapshot(self):
        old_path = predict.SOCIAL_SIGNALS_CSV
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                path = Path(tmpdir) / "social-signals.csv"
                path.write_text(
                    "\n".join([
                        "weekend_of,as_of_date,movie_title,platform,source,mentions,engagement,views,positive_mentions,negative_mentions,neutral_mentions,sentiment_score,buzz_score",
                        "2026-05-15,2026-05-13,Sample Movie,TikTok,manual,100,0,0,80,20,0,,",
                        "2026-05-15,2026-05-14,Sample Movie,TikTok,manual,400,0,0,300,50,50,,",
                        "2026-05-15,2026-05-14,Other Movie,TikTok,manual,100,0,0,40,40,20,,",
                    ])
                    + "\n"
                )
                predict.SOCIAL_SIGNALS_CSV = str(path)

                loaded = predict.load_social_signal_data(weekend_of="2026-05-15")
        finally:
            predict.SOCIAL_SIGNALS_CSV = old_path

        self.assertEqual(400, loaded["Sample Movie"]["reach"])
        self.assertAlmostEqual(0.625, loaded["Sample Movie"]["sentiment_score"])
        self.assertGreater(loaded["Sample Movie"]["buzz_score"], 0)
        self.assertEqual("relative-volume", loaded["Sample Movie"]["buzz_source"])

    def test_social_signal_loader_preserves_relishmix_smu(self):
        old_path = predict.SOCIAL_SIGNALS_CSV
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                path = Path(tmpdir) / "social-signals.csv"
                path.write_text(
                    "\n".join([
                        "weekend_of,as_of_date,movie_title,platform,source,social_media_universe_m,sentiment_score,buzz_score",
                        "2026-05-15,2026-05-14,Sample Movie,RelishMix,manual,500,0.25,0.4",
                    ])
                    + "\n"
                )
                predict.SOCIAL_SIGNALS_CSV = str(path)

                loaded = predict.load_social_signal_data(weekend_of="2026-05-15")
                layer = predict.build_social_signal_layer("Sample Movie", loaded)
        finally:
            predict.SOCIAL_SIGNALS_CSV = old_path

        self.assertEqual(500.0, loaded["Sample Movie"]["social_media_universe_m"])
        self.assertEqual(500.0, layer["social_media_universe_m"])
        self.assertGreater(loaded["Sample Movie"]["reach"], 0)

    def test_daily_actual_override_loader_uses_latest_report(self):
        old_path = predict.DAILY_ACTUALS_CSV
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                path = Path(tmpdir) / "daily-actual-overrides.csv"
                path.write_text(
                    "\n".join([
                        "weekend_of,movie_title,day_of_week,gross_m,source,status,as_of_date,notes",
                        "2026-05-15,Sample Movie,Thu,2.4,early,reported,2026-05-15,old report",
                        "2026-05-15,Sample Movie,Thursday,2.6,manual,reported,2026-05-15,final preview",
                        "2026-05-15,Sample Movie,Friday,8.0,manual,reported,2026-05-16,future",
                        "2026-05-08,Sample Movie,Thursday,1.0,manual,reported,2026-05-08,old weekend",
                    ])
                    + "\n"
                )
                predict.DAILY_ACTUALS_CSV = str(path)

                loaded = predict.load_daily_actual_overrides(
                    weekend_of="2026-05-15",
                    through_date="2026-05-15",
                )
        finally:
            predict.DAILY_ACTUALS_CSV = old_path

        self.assertEqual(2.6, loaded["Sample Movie"]["Thursday"]["gross_m"])
        self.assertEqual("manual", loaded["Sample Movie"]["Thursday"]["source"])
        self.assertNotIn("Friday", loaded["Sample Movie"])

    def test_daily_actual_override_replaces_seat_implied_day(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "reference_amc_theatres": 2,
            }
        }
        seat_data = {
            "2026-05-14": [
                self._row("AMC One", date="2026-05-14", day="Thursday"),
                self._row("AMC Two", date="2026-05-14", day="Thursday"),
            ]
        }

        seat_only = predict_movie(
            "Sample Movie",
            seat_data,
            [],
            cal,
            daily_actual_overrides={},
        )
        overridden = predict_movie(
            "Sample Movie",
            seat_data,
            [],
            cal,
            daily_actual_overrides={
                "Sample Movie": {
                    "Thursday": {
                        "gross_m": 2.6,
                        "source": "manual",
                        "status": "reported",
                        "as_of_date": "2026-05-15",
                    }
                }
            },
        )

        self.assertNotAlmostEqual(2.6, seat_only["seat_mid_m"], places=3)
        self.assertAlmostEqual(2.6, overridden["seat_mid_m"], places=6)
        self.assertAlmostEqual(2_600_000, overridden["daily_details"]["Thursday"]["domestic_mid"])
        self.assertTrue(overridden["daily_details"]["Thursday"]["actual_override"])
        self.assertGreater(
            overridden["daily_details"]["Thursday"]["seat_implied_domestic_mid"],
            0,
        )
        daily_predictions, raw_daily_predictions, _, _ = (
            predict.daily_calibration_fields_from_prediction(overridden)
        )
        self.assertNotAlmostEqual(
            daily_predictions["Thursday"],
            overridden["daily_details"]["Thursday"]["actual_override_m"],
            places=3,
        )
        self.assertAlmostEqual(
            overridden["daily_details"]["Thursday"]["seat_implied_domestic_mid"] / 1_000_000,
            raw_daily_predictions["Thursday"],
            places=6,
        )

    def test_daily_actual_override_calibrates_future_day_amc_share(self):
        cal = {
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Thursday": 0.5, "Friday": 0.5},
                "day_scale_factors": {"Thursday": 1.0, "Friday": 1.0},
                "reference_amc_theatres": 2,
            }
        }
        seat_data = {
            "2026-05-14": [
                self._row("AMC One", date="2026-05-14", day="Thursday"),
                self._row("AMC Two", date="2026-05-14", day="Thursday"),
            ],
            "2026-05-15": [
                self._row("AMC One", date="2026-05-15", day="Friday"),
                self._row("AMC Two", date="2026-05-15", day="Friday"),
            ],
        }

        pred = predict_movie(
            "Sample Movie",
            seat_data,
            [],
            cal,
            daily_actual_overrides={
                "Sample Movie": {
                    "Thursday": {
                        "gross_m": 0.008,
                        "source": "manual",
                        "status": "reported",
                        "as_of_date": "2026-05-15",
                    }
                }
            },
        )

        anchor = pred["dynamic_amc_share_anchor"]
        friday = pred["daily_details"]["Friday"]
        self.assertAlmostEqual(0.125, anchor["implied_share"], places=6)
        self.assertAlmostEqual(0.14375, anchor["blended_share"], places=6)
        self.assertEqual("Thursday", anchor["day"])
        self.assertEqual("same_week_actual_anchor", friday["amc_market_share_source"])
        self.assertAlmostEqual(0.14375, friday["amc_market_share_used"], places=6)
        self.assertAlmostEqual(1700 / 0.14375, friday["domestic_mid"], places=6)
        self.assertGreater(friday["domestic_mid"], 1700 / 0.25)

    def test_thursday_preview_residual_learns_from_local_history(self):
        cal = {
            "history": [
                {
                    "movie": "Sample Horror Comp",
                    "actual_status": "final",
                    "model_version": predict.MODEL_VERSION,
                    "daily_actuals": {"Thursday": 2.0},
                    "daily_predictions": {"Thursday": 1.0},
                    "daily_coverage_ratios": {"Thursday": 1.0},
                    "n_theatres": 425,
                    "n_days": 1,
                }
            ],
            "calibration_factors": {
                "amc_market_share": 0.25,
                "day_weights": {"Thursday": 1.0},
                "day_scale_factors": {"Thursday": 1.0},
                "reference_amc_theatres": 2,
            },
        }
        metadata = {
            "sample movie": TargetMetadata(
                movie="Sample Movie",
                genre="horror",
                audience_type="horror_fan",
                franchise_type="original",
                rating="R",
            ),
            "sample horror comp": TargetMetadata(
                movie="Sample Horror Comp",
                genre="horror",
                audience_type="horror_fan",
                franchise_type="original",
                rating="R",
            ),
        }
        rows = [
            self._row("AMC One"),
            self._row("AMC Two"),
        ]

        old_load_metadata = predict.load_movie_metadata
        predict.load_movie_metadata = lambda: metadata
        try:
            baseline = predict_movie(
                "Sample Movie",
                {"2026-05-07": rows},
                [],
                {**cal, "history": []},
                daily_actual_overrides={},
            )
            adjusted = predict_movie(
                "Sample Movie",
                {"2026-05-07": rows},
                [],
                cal,
                daily_actual_overrides={},
            )
            self_leak = predict_movie(
                "Sample Horror Comp",
                {"2026-05-07": rows},
                [],
                cal,
                daily_actual_overrides={},
            )
        finally:
            predict.load_movie_metadata = old_load_metadata

        thursday = adjusted["daily_details"]["Thursday"]
        self.assertGreater(thursday["preview_seat_residual_factor"], 1.0)
        self.assertGreater(
            thursday["domestic_mid"],
            baseline["daily_details"]["Thursday"]["domestic_mid"],
        )
        self.assertAlmostEqual(
            1.0,
            self_leak["daily_details"]["Thursday"]["preview_seat_residual_factor"],
        )

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
