# tests/test_seat_regression.py
import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

from math import log

import seat_regression as sr


class TestConstants(unittest.TestCase):
    def test_constants_present(self):
        self.assertEqual(sr.COVERAGE_FLOOR, 0.60)
        self.assertEqual(sr.OPENING_DAYS, ("Thursday", "Friday", "Saturday", "Sunday"))
        self.assertEqual(sr.MIN_WEEKEND_CV_DAYS, 2)
        # t_{0.95, df} table for two-sided 90% interval
        self.assertAlmostEqual(sr.t_quantile_95(5), 2.015, places=3)
        self.assertAlmostEqual(sr.t_quantile_95(1), 6.314, places=3)
        self.assertAlmostEqual(sr.t_quantile_95(100), 1.660, places=2)  # ~normal


class TestRidge(unittest.TestCase):
    def test_solve_identity(self):
        # 2x2 solve: [[2,0],[0,4]] x = [2,8] -> [1,2]
        x = sr._solve([[2.0, 0.0], [0.0, 4.0]], [2.0, 8.0])
        self.assertAlmostEqual(x[0], 1.0, places=9)
        self.assertAlmostEqual(x[1], 2.0, places=9)

    def test_ridge_recovers_line_with_unit_slope_prior(self):
        # y = 0.5 + 1.0*x exactly; intercept unpenalized, slope prior=1.
        # With perfect data and any lambda, slope should stay ~1, intercept ~0.5.
        X = [[1.0, 0.0], [1.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
        y = [0.5, 1.5, 2.5, 3.5]
        w = [1.0, 1.0, 1.0, 1.0]
        beta = sr.weighted_ridge(X, y, w, prior=[0.0, 1.0],
                                 penalize=[0, 1], l2=1.0)
        self.assertAlmostEqual(beta[1], 1.0, places=6)
        self.assertAlmostEqual(beta[0], 0.5, places=6)

    def test_ridge_shrinks_slope_toward_one_when_noisy(self):
        # Slope of raw OLS would be ~2; with strong prior=1 + big lambda it shrinks toward 1.
        X = [[1.0, 0.0], [1.0, 1.0]]
        y = [0.0, 2.0]   # OLS slope = 2
        beta = sr.weighted_ridge(X, y, [1.0, 1.0], prior=[0.0, 1.0],
                                 penalize=[0, 1], l2=100.0)
        self.assertLess(beta[1], 1.5)   # pulled toward prior 1
        self.assertGreater(beta[1], 1.0)


class TestTrainingRows(unittest.TestCase):
    def _history(self):
        return [
            {  # good movie: 2 admissible seat-days (Thu, Sun), Fri below floor
                "movie": "A", "weekend_of": "2026-01-02", "actual_total": 40.0,
                "raw_daily_predictions": {"Thursday": 5.0, "Friday": 10.0, "Sunday": 8.0},
                "daily_actuals": {"Thursday": 6.0, "Friday": 9.0, "Sunday": 9.0},
                "daily_coverage_ratios": {"Thursday": 1.0, "Friday": 0.40, "Sunday": 0.90},
                "snapshot_daily_predictions": {"Sunday": 7.5},
                "snapshot_daily_lead_buckets": {"Sunday": "same_day"},
            },
            {  # unusable: 1 admissible day only
                "movie": "B", "weekend_of": "2026-01-09", "actual_total": 2.0,
                "raw_daily_predictions": {"Sunday": 2.0},
                "daily_actuals": {"Sunday": 1.5},
                "daily_coverage_ratios": {"Sunday": 0.03},
            },
        ]

    def test_seat_rows_respect_coverage_floor(self):
        rows = sr.build_seat_rows(self._history())
        # A: Thu(1.0) and Sun(0.90) pass; Fri(0.40) excluded. B: Sun(0.03) excluded.
        keys = {(r["movie"], r["day"]) for r in rows}
        self.assertEqual(keys, {("A", "Thursday"), ("A", "Sunday")})

    def test_seat_row_fields_and_weight(self):
        rows = sr.build_seat_rows(self._history())
        thu = next(r for r in rows if r["day"] == "Thursday")
        self.assertAlmostEqual(thu["log_seat"], log(5.0))
        self.assertAlmostEqual(thu["log_actual"], log(6.0))
        self.assertAlmostEqual(thu["coverage"], 1.0)
        self.assertAlmostEqual(thu["weight"], 1.0)   # weight == coverage

    def test_snapshot_rows(self):
        rows = sr.build_snapshot_rows(self._history())
        keys = {(r["movie"], r["day"]) for r in rows}
        self.assertEqual(keys, {("A", "Sunday")})
        r = rows[0]
        self.assertAlmostEqual(r["log_snap"], log(7.5))
        self.assertEqual(r["lead_bucket"], "same_day")

    def test_weekend_cv_movies(self):
        movies = sr.weekend_cv_movies(self._history())
        self.assertEqual(movies, ["A"])   # B has <2 admissible days


class TestFeatures(unittest.TestCase):
    def test_seat_features(self):
        # [intercept, log_seat, is_thu, is_fri, is_sat, one_minus_cov]; Sunday baseline
        v = sr.seat_features(log_seat=2.0, day="Friday", coverage=0.8)
        self.assertEqual(v, [1.0, 2.0, 0.0, 1.0, 0.0, 0.2])
        v2 = sr.seat_features(log_seat=1.0, day="Sunday", coverage=1.0)
        self.assertEqual(v2, [1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(sr.SEAT_PRIOR, [0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(sr.SEAT_PENALIZE, [0, 1, 1, 1, 1, 1])

    def test_snapshot_features(self):
        # [intercept, log_snap, is_thu, is_fri, is_sat, lead_next, lead_multi, lead_long]
        # same_day is the lead baseline
        v = sr.snapshot_features(log_snap=1.5, day="Thursday", lead_bucket="next_day")
        self.assertEqual(v, [1.0, 1.5, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        v2 = sr.snapshot_features(log_snap=1.5, day="Sunday", lead_bucket="same_day")
        self.assertEqual(v2, [1.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
