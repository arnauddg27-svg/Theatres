import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402
import calibrate  # noqa: E402


class SnapshotWeekendWiringTest(unittest.TestCase):
    """apply_regression_snapshot_weekend: gated OFF, behavior pinned.

    The wiring feeds snapshot per-day estimates into the fitted weekend
    assembly (the shape the LOO/band are fitted on). Adversarial testing
    2026-08-31 found it (a) masked at the live Thu/Fri stage by the
    complete-snapshot exception path and (b) harmful on full-observation
    replays (snap_coef inflation, The Dog Stars 14.3 -> 17.9 vs actual 8.0),
    so it ships DISABLED. These tests pin the default and the mechanics so a
    future split-case backtest can enable it deliberately, not accidentally.
    """

    def setUp(self):
        self._flag = P.REGRESSION_USE_SNAPSHOT_DAYS
        self.cal = calibrate.load_calibration()

    def tearDown(self):
        P.REGRESSION_USE_SNAPSHOT_DAYS = self._flag

    def _pred(self):
        return {
            "daily_estimates": {"Thursday": 2.4e6, "Friday": 3.6e6},
            "daily_details": {
                "Thursday": {"coverage_ratio": 0.95},
                "Friday": {"coverage_ratio": 0.90},
            },
            "snapshot_all_daily_details": {
                "Saturday": {"raw_domestic_mid": 3.5e6, "lead_bucket": "same_day",
                             "coverage_ratio": 0.8},
                "Sunday": {"raw_domestic_mid": 2.6e6, "lead_bucket": "same_day",
                           "coverage_ratio": 0.8},
            },
            "seat_mid_m": 20.0, "seat_low_m": 14.0, "seat_high_m": 28.0,
            "seat_empirical_regression_applied": True,
            "blended_m": 20.0, "blend_low_m": 14.0, "blend_high_m": 28.0,
        }

    def test_flag_ships_off(self):
        self.assertFalse(P.REGRESSION_USE_SNAPSHOT_DAYS)

    def test_noop_when_disabled(self):
        P.REGRESSION_USE_SNAPSHOT_DAYS = False
        pred = self._pred()
        P.apply_regression_snapshot_weekend(pred, self.cal)
        self.assertEqual(20.0, pred["seat_mid_m"])
        self.assertNotIn("regression_snapshot_days", pred)

    def test_replaces_weekend_and_keeps_blended_in_step_when_enabled(self):
        P.REGRESSION_USE_SNAPSHOT_DAYS = True
        pred = self._pred()
        P.apply_regression_snapshot_weekend(pred, self.cal)
        self.assertIn("regression_snapshot_days", pred)
        self.assertEqual(["Saturday", "Sunday"], pred["regression_snapshot_days"])
        self.assertNotEqual(20.0, pred["seat_mid_m"])
        self.assertEqual(20.0, pred["pre_snapshot_regression_seat_mid_m"])
        self.assertEqual(pred["blended_m"], pred["seat_mid_m"])
        self.assertLessEqual(pred["seat_low_m"], pred["seat_mid_m"])
        self.assertLessEqual(pred["seat_mid_m"], pred["seat_high_m"])

    def test_noop_without_snapshot_details_even_when_enabled(self):
        P.REGRESSION_USE_SNAPSHOT_DAYS = True
        pred = self._pred()
        pred["snapshot_all_daily_details"] = {}
        P.apply_regression_snapshot_weekend(pred, self.cal)
        self.assertEqual(20.0, pred["seat_mid_m"])


if __name__ == "__main__":
    unittest.main()
