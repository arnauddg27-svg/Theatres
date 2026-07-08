import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


def _cal(ratios):
    return {"history": [
        {"movie": f"F{i}", "predicted_mid": 10.0, "actual_total": 10.0 * r}
        for i, r in enumerate(ratios)
    ]}


class ConformalRatioBandTests(unittest.TestCase):
    def test_needs_min_history(self):
        self.assertIsNone(P.conformal_ratio_band(_cal([1.0] * 9), "New"))
        self.assertIsNone(P.conformal_ratio_band(None, "New"))

    def test_band_is_trimmed_extremes(self):
        ratios = [0.5, 0.8, 0.9, 0.95, 1.0, 1.0, 1.05, 1.1, 1.2, 1.5, 3.0]
        r_lo, r_hi = P.conformal_ratio_band(_cal(ratios), "New")
        # k=1 at n=11 (11//8=1): min/max... k=min(2, max(1, 11//8))=1
        self.assertAlmostEqual(r_lo, 0.5)
        self.assertAlmostEqual(r_hi, 3.0)

    def test_k2_trim_at_larger_n(self):
        ratios = [0.5] + [1.0] * 17 + [3.0]   # n=19 -> k=2 trims the extremes
        r_lo, r_hi = P.conformal_ratio_band(_cal(ratios), "New")
        self.assertAlmostEqual(r_lo, 1.0)
        self.assertAlmostEqual(r_hi, 1.0)

    def test_loo_excludes_own_movie(self):
        cal = _cal([1.0] * 16)
        cal["history"].append({"movie": "Target", "predicted_mid": 10.0, "actual_total": 90.0})
        r_lo, r_hi = P.conformal_ratio_band(cal, "Target")
        self.assertLess(r_hi, 2.0)   # own 9.0x ratio must not widen its own band

    def test_floor_widens_never_narrows(self):
        cal = _cal([0.7, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.4, 2.0])
        pred = {"movie": "New", "daily_details": {},
                "snapshot_mid_m": 40.0, "snapshot_low_m": 38.0, "snapshot_high_m": 42.0,
                "seat_mid_m": 40.0, "seat_low_m": 38.0, "seat_high_m": 42.0,
                "snapshot_days": [], "audience_type": ""}
        orig = P.complete_snapshot_covers_missing_days
        P.complete_snapshot_covers_missing_days = lambda p: True
        try:
            P.select_regression_prediction(pred, cal=cal)
        finally:
            P.complete_snapshot_covers_missing_days = orig
        self.assertLessEqual(pred["regression_low_m"], 38.0)
        self.assertGreaterEqual(pred["regression_high_m"], 42.0)
        self.assertEqual(pred["regression_mid_m"], 40.0)   # mid untouched
        self.assertIn("conformal", pred["regression_basis"])


class SupplyConstraintGateTests(unittest.TestCase):
    def _seat(self, showings_per_day):
        return {"2026-07-03": [
            {"theatre_name": "T1", "showtime": f"{10+i}:00"} for i in range(showings_per_day)
        ]}

    def test_showings_per_cinema_day(self):
        self.assertAlmostEqual(P._seat_showings_per_cinema_day(self._seat(2)), 2.0)
        self.assertAlmostEqual(P._seat_showings_per_cinema_day(self._seat(6)), 6.0)
        self.assertIsNone(P._seat_showings_per_cinema_day({}))

    def test_floor_constant_separates_yw_from_wide_films(self):
        # Young Washington opened at 2.2-2.4 showings/cinema (gated);
        # Supergirl/Jackass/Minions ran 5.8-6.8+ (pass).
        self.assertGreater(P.CROSS_CHAIN_MIN_SHOWINGS_PER_CINEMA, 2.5)
        self.assertLess(P.CROSS_CHAIN_MIN_SHOWINGS_PER_CINEMA, 5.5)


if __name__ == "__main__":
    unittest.main()
