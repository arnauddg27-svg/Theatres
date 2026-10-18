"""Sunday = Saturday x historical ratio once Fri+Sat are reported (2026-10-18)."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict as P  # noqa: E402


def _cal(ratios):
    return {"history": [
        {"weekend_of": f"2026-01-{i + 1:02d}", "movie": f"M{i}",
         "daily_actuals": {"Saturday": 10.0, "Sunday": 10.0 * r}}
        for i, r in enumerate(ratios)]}


class SundayRatioTest(unittest.TestCase):
    def setUp(self):
        self.meta = mock.patch.object(P, "load_movie_metadata", return_value={})
        self.meta.start()
        self.addCleanup(self.meta.stop)

    def test_global_median_and_band(self):
        ratios = [0.66, 0.68, 0.70, 0.72, 0.74, 0.74, 0.76, 0.78, 0.80, 0.85, 0.88]
        out = P.sunday_saturday_ratio(_cal(ratios))
        self.assertAlmostEqual(0.74, out["ratio"], places=6)
        self.assertLessEqual(out["low"], out["ratio"])
        self.assertGreaterEqual(out["high"], out["ratio"])
        self.assertEqual(11, out["n"])

    def test_too_few_films(self):
        self.assertIsNone(P.sunday_saturday_ratio(_cal([0.7] * 5)))

    def test_exclude_replayed_film(self):
        ratios = [0.7] * 10 + [5.0]
        with_it = P.sunday_saturday_ratio(_cal(ratios))
        without = P.sunday_saturday_ratio(_cal(ratios), exclude=("2026-01-11", "M10"))
        self.assertEqual(11, with_it["n"])
        self.assertEqual(10, without["n"])
        self.assertAlmostEqual(0.7, without["ratio"], places=6)


if __name__ == "__main__":
    unittest.main()


class SundaySeatRatioTest(unittest.TestCase):
    def test_seat_ratio_used_when_plausible(self):
        sat = {"sold_seats": 130000, "n_theatres": 416}
        sun = {"sold_seats": 101000, "n_theatres": 423}
        out = P.sunday_seat_ratio(sat, sun, 0.74)
        self.assertAlmostEqual(101000 / 130000 * P.SUNDAY_SEAT_PRICE_K, out["ratio"], places=6)

    def test_implausible_or_incomplete_falls_back(self):
        sat = {"sold_seats": 100000, "n_theatres": 420}
        self.assertIsNone(P.sunday_seat_ratio(sat, {"sold_seats": 160000, "n_theatres": 420}, 0.72))  # 1.49x norm
        self.assertIsNone(P.sunday_seat_ratio(sat, {"sold_seats": 70000, "n_theatres": 200}, 0.72))   # half the theatres
        self.assertIsNone(P.sunday_seat_ratio(sat, None, 0.72))
