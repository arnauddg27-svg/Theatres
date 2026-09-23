import copy
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import predict as P


class EvidenceIntegrityTests(unittest.TestCase):
    def test_calibration_shift_keeps_midpoint_inside_range_and_original_range(self):
        for target in (5_000_000, 20_000_000):
            day = dict(domestic_mid=10_000_000, domestic_low=8_000_000,
                       domestic_high=12_000_000)
            P.apply_calibrated_day_detail(day, {"mid": target})
            self.assertEqual(target, day["domestic_mid"])
            self.assertLessEqual(day["domestic_low"], min(8_000_000, target))
            self.assertGreaterEqual(day["domestic_high"], max(12_000_000, target))

    def test_reported_gross_cannot_be_rewritten_by_regression(self):
        day = dict(domestic_mid=10_000_000, domestic_low=10_000_000,
                   domestic_high=10_000_000, actual_override=True)
        P.apply_calibrated_day_detail(day, {"mid": 20_000_000})
        self.assertEqual(10_000_000, day["domestic_mid"])
        self.assertEqual(10_000_000, day["domestic_low"])
        self.assertEqual(10_000_000, day["domestic_high"])
        # Legacy per-day scaling must not replace the explicitly reported value.
        day.update(domestic_mid=8_000_000, actual_override_m=10)
        P.apply_calibrated_day_detail(day, {"mid": 20_000_000})
        self.assertEqual(10_000_000, day["domestic_mid"])

    def test_excluded_gross_cannot_reenter_empirical_weekend_sum(self):
        days = {"Thursday": {"domestic_mid": 1_000_000},
                "Friday": {"domestic_mid": 100_000_000, "excluded_from_weekend": True}}
        cal = {"calibration_factors": {"day_weights": {"Thursday": .1, "Friday": .9}}}
        result = P._recompute_weekend_from_daily_detail_m(days, cal)
        self.assertEqual(["Thursday"], result["days"])
        self.assertAlmostEqual(10, result["mid_m"])

    def test_complete_reported_weekend_is_not_adjusted_by_reviews_or_regression(self):
        pred = {"movie": "X", "seat_mid_m": 50, "seat_low_m": 25, "seat_high_m": 90,
                "review_weekend_factor": 1.1,
                "daily_details": {d: {"domestic_mid": 10_000_000, "actual_override": True}
                                  for d in P.OPENING_WEEKEND_DAYS}}
        P.select_regression_prediction(pred)
        self.assertEqual(40, pred["regression_mid_m"])
        self.assertEqual(40, pred["regression_low_m"])
        self.assertEqual(40, pred["regression_high_m"])
        self.assertEqual("reported-actuals", pred["regression_source"])
        pred["daily_details"]["Sunday"]["actual_override_status"] = "provisional"
        P.select_regression_prediction(pred)
        self.assertTrue(pred["forecast_provisional"])

    def test_forecast_cannot_fall_below_already_reported_revenue(self):
        pred = {"movie": "X", "seat_mid_m": 5, "seat_low_m": 3, "seat_high_m": 8,
                "daily_details": {"Thursday": {"domestic_mid": 10_000_000, "actual_override": True}}}
        P.select_regression_prediction(pred)
        self.assertEqual(10, pred["regression_mid_m"])
        self.assertEqual(10, pred["regression_low_m"])
        self.assertEqual(10, pred["regression_high_m"])

    def test_excluded_day_does_not_receive_empirical_correction(self):
        pred = {"daily_details": {"Friday": {"domestic_mid": 100_000_000,
                                             "excluded_from_weekend": True}}}
        before = copy.deepcopy(pred)
        with patch.object(P, "empirical_daily_residual_regression", side_effect=AssertionError("excluded input")):
            self.assertIsNone(P.apply_empirical_seat_regression(pred, [], {}))
        self.assertEqual(before, pred)

    def row(self, theatre, date, day):
        return dict(movie_title="Sample Movie", date=date, day_of_week=day,
                    theatre_name=theatre, auditorium_type="Standard", showtime="7:00 PM",
                    has_seat_map="true", seats_sold="50", total_seats="100",
                    adult_ticket_price="10", minutes_after_showtime="0")

    def cal(self):
        return {"history": [], "calibration_factors": {"amc_market_share": .25,
                "reference_amc_theatres": 2, "reference_amc_theatres_by_cohort": {"core,expansion": 2}}}

    def test_rejected_friday_cannot_become_an_observed_friday_anchor(self):
        seats = {"2026-05-07": [self.row(t, "2026-05-07", "Thursday") for t in ("One", "Two")],
                 "2026-05-08": [self.row("One", "2026-05-08", "Friday")]}
        pred = P.predict_movie("Sample Movie", seats, [], self.cal())
        self.assertIsNotNone(pred)
        self.assertEqual({"Thursday"}, set(pred["daily_details"]))
        self.assertIn("Friday", pred["excluded_daily_details"])
        self.assertEqual("after-previews", pred["forecast_stage"])
        self.assertIsNone(pred.get("friday_anchored_mid_m"))
        self.assertEqual(1, pred["n_days"])

    def test_only_rejected_data_abstains_instead_of_publishing_zero_or_bad_extrapolation(self):
        seats = {"2026-05-08": [self.row("One", "2026-05-08", "Friday")]}
        self.assertIsNone(P.predict_movie("Sample Movie", seats, [], self.cal()))


class DashboardInputTests(unittest.TestCase):
    def run_dashboard(self, prediction):
        import dashboard
        inputs = {
            "load_calibration": {}, "load_seat_data": {"Sample: Movie": {}},
            "load_polymarket_data": {"Sample Movie": [{"market_question": "market"}]},
            "load_pre_reservation_data": {}, "load_social_signal_data": {"signal": 1},
            "load_reviews_data": {"reviews": 2}, "load_cross_chain_occupancy": {"chains": 3},
            "load_daily_actual_overrides": {"actuals": 4},
            "load_showtime_link_daypart_profiles": {"Sample Movie": {"schedule": 5}},
            "load_theatre_counts": {}, "load_movie_metadata": {},
        }
        with ExitStack() as stack:
            loaders = {name: stack.enter_context(patch.object(P, name, return_value=value))
                       for name, value in inputs.items()}
            forecast = stack.enter_context(patch.object(P, "predict_movie", return_value=prediction))
            result = dashboard.build_prediction_map("2026-09-18", dashboard.DATA_DIR)
        for name in ("load_reviews_data", "load_cross_chain_occupancy",
                     "load_daily_actual_overrides", "load_showtime_link_daypart_profiles"):
            loaders[name].assert_called_once_with(weekend_of="2026-09-18")
        return result, forecast.call_args

    def test_dashboard_passes_all_live_inputs_and_normalizes_movie_aliases(self):
        result, call = self.run_dashboard({"regression_mid_m": 20, "regression_low_m": 10,
                                           "regression_high_m": 30})
        self.assertEqual(20, result["Sample: Movie"]["mid_m"])
        self.assertEqual({"reviews": 2}, call.kwargs["reviews_data"])
        self.assertEqual({"chains": 3}, call.kwargs["cross_chain_data"])
        self.assertEqual({"actuals": 4}, call.kwargs["daily_actual_overrides"])
        self.assertEqual({"schedule": 5}, call.kwargs["showtime_link_profiles"])
        self.assertEqual([{"market_question": "market"}], call.args[2])

    def test_dashboard_explains_abstention(self):
        result, _ = self.run_dashboard(None)
        self.assertIn("Insufficient usable", result["Sample: Movie"]["error"])


if __name__ == "__main__":
    unittest.main()
