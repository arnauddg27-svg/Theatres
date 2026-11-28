"""A film forecast from reservation snapshots alone must still be graded.

2026-11-20: I Play Rocky had no AMC seat-count rows (AMC lane blocked), was
forecast all weekend from snapshots, and never reached calibration.json —
auto_calibrate walked seat_data only.
"""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calibrate as C
import seat_regression


def pending_item(movie, actual, reason=None):
    return {"movie": movie,
            "pred": {"n_theatres_total": 0, "n_days": 0, "reference_amc_theatres": 400,
                     "model_cohort_key": "core,expansion", "model_version": "test"},
            "regression_prediction": (6.8, 2.0, 17.8),
            "daily_actuals": dict(actual), "daily_predictions": {},
            "graded_only_reason": reason}


class SnapshotOnlyGradingTests(unittest.TestCase):
    def test_snapshot_only_film_is_in_the_grading_list(self):
        seat = {"Seat Film": {"2026-11-20": [{}]}}
        snapshots = {"Seat Film": {"2026-11-21": [{}]}, "Snapshot Only": {"2026-11-21": [{}]}}
        with patch.object(C.small_film_gate, "filter_titles", side_effect=lambda t, *a: list(t)), \
                patch.object(C.holdover, "without_holdovers", side_effect=lambda t, *a: list(t)):
            names = C.calibration_movie_names(seat, snapshots, "2026-11-20")
            self.assertEqual(["Seat Film", "Snapshot Only"], names)
        # The gates still apply to it.
        with patch.object(C.small_film_gate, "filter_titles", side_effect=lambda t, *a: ["Seat Film"]), \
                patch.object(C.holdover, "without_holdovers", side_effect=lambda t, *a: list(t)):
            self.assertEqual(["Seat Film"], C.calibration_movie_names(seat, snapshots, "2026-11-20"))

    def test_graded_only_entry_is_recorded_without_touching_the_fits(self):
        prior = {"movie": "Seat Film", "weekend_of": "2026-11-20", "predicted_mid": 100.0,
                 "actual_total": 119.3, "daily_actuals": {"Friday": 119.3}, "daily_predictions": {}}
        cal = {"history": [prior],
               "calibration_factors": {"amc_market_share": 0.24, "day_weights": {"Friday": 1.0},
                                       "reference_amc_theatres_by_cohort": {"core,expansion": 425},
                                       "historical_accuracy": [{"movie": "Seat Film"}],
                                       "regression": {"active_tier": "regression"}}}
        factors_before = copy.deepcopy(cal["calibration_factors"])
        stale_baseline = {"calibration_factors": {"amc_market_share": 0.99}}
        reported = {"Friday": 3.8, "Saturday": 3.25, "Sunday": 2.28}
        with patch.object(C, "save_calibration"), \
                patch.object(C, "_live_headline", return_value={"mid_m": 9.39, "logged_at": "2026-11-23T10:47:53Z"}):
            entries = C.record_pending_calibrations(
                cal, stale_baseline, "2026-11-20",
                [pending_item("I Play Rocky", reported, C.NO_SEAT_ROWS_REASON)])
        entry = entries[0]
        self.assertEqual(2, len(cal["history"]))
        self.assertAlmostEqual(9.33, entry["actual_total"])
        self.assertAlmostEqual(0.6, entry["live_error_pct"], places=1)
        self.assertTrue(entry["data_outage"])
        self.assertEqual(C.NO_SEAT_ROWS_REASON, entry["data_outage_reason"])
        self.assertTrue(entry["previews_folded_into_friday"])
        self.assertEqual([prior], seat_regression.fitting_history(cal["history"]))
        self.assertEqual(factors_before, cal["calibration_factors"])
        json.dumps(cal)

    def test_live_headline_stands_in_when_the_model_cannot_replay(self):
        # Rocky's live headline was the outage fallback and then reported days;
        # with no seat rows and no overrides the replay returns None.
        self.assertIsNone(C.live_headline_stand_in(None))
        self.assertIsNone(C.live_headline_stand_in({"mid_m": 0}))
        stub, values = C.live_headline_stand_in({"mid_m": 9.39, "low_m": 9.12, "high_m": 9.89})
        self.assertEqual((9.39, 9.12, 9.89), values)
        cal = {"history": [], "calibration_factors": {"historical_accuracy": []}}
        item = pending_item("I Play Rocky", {"Friday": 3.8, "Saturday": 3.25, "Sunday": 2.28},
                            C.NO_SEAT_ROWS_REASON)
        item.update(pred=stub, regression_prediction=values)
        with patch.object(C, "save_calibration"), \
                patch.object(C, "_live_headline", return_value={"mid_m": 9.39}):
            entry = C.record_pending_calibrations(cal, {}, "2026-11-20", [item])[0]
        self.assertTrue(entry["replay_unavailable"])
        self.assertEqual(9.39, entry["predicted_mid"])
        # A stand-in is not a model accuracy row for the trading confidence.
        self.assertIsNone(C.accuracy_entry_from_history(entry))
        self.assertEqual([], C.rebuild_historical_accuracy(cal))

    def test_cli_weekend_reaches_auto_calibrate(self):
        import inspect
        self.assertIn("weekend_of", inspect.signature(C.auto_calibrate).parameters)


if __name__ == "__main__":
    unittest.main()
