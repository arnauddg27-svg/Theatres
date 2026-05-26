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


class TestFitOne(unittest.TestCase):
    def test_recovers_planted_relationship(self):
        # actual = exp(0.3) * seat^1.0 exactly, across days -> intercept 0.3, slope 1.
        rows = []
        for day, s in [("Thursday", 2.0), ("Friday", 10.0), ("Saturday", 12.0),
                       ("Sunday", 8.0), ("Friday", 5.0), ("Sunday", 20.0)]:
            rows.append({"day": day, "log_seat": log(s),
                         "log_actual": 0.3 + log(s), "coverage": 1.0, "weight": 1.0})
        coef = sr.fit_seat(rows, l2=0.1)
        # predicted log-mean for a Sunday with log_seat=log(10) ~ 0.3 + log(10)
        pred = sr.predict_log(coef, sr.seat_features(log(10.0), "Sunday", 1.0))
        self.assertAlmostEqual(pred, 0.3 + log(10.0), places=2)

    def test_fit_seat_handles_empty(self):
        self.assertIsNone(sr.fit_seat([], l2=1.0))


class TestLOO(unittest.TestCase):
    def _rows(self):
        # 3 movies, clean unit-slope relationship with intercept 0.2
        rows = []
        plan = {"A": [("Thursday", 3.0), ("Sunday", 9.0)],
                "B": [("Friday", 8.0), ("Saturday", 11.0)],
                "C": [("Thursday", 2.0), ("Sunday", 7.0)]}
        for movie, days in plan.items():
            for day, s in days:
                rows.append({"movie": movie, "day": day, "log_seat": log(s),
                             "log_actual": 0.2 + log(s), "coverage": 1.0, "weight": 1.0})
        return rows

    def test_loo_returns_lambda_and_resid_sd(self):
        best_l2, resid_sd, n = sr.loo_select(
            self._rows(), sr.fit_seat,
            lambda coef, r: sr.predict_log(coef, sr.seat_features(r["log_seat"], r["day"], r["coverage"])),
        )
        self.assertIn(best_l2, sr.LAMBDA_GRID)
        self.assertLess(resid_sd, 0.05)   # near-perfect data -> tiny residuals
        self.assertEqual(n, 6)

    def test_loo_handles_single_movie(self):
        rows = [r for r in self._rows() if r["movie"] == "A"]
        out = sr.loo_select(rows, sr.fit_seat,
                            lambda coef, r: sr.predict_log(coef, sr.seat_features(r["log_seat"], r["day"], r["coverage"])))
        self.assertIsNotNone(out)   # degrades gracefully, no crash


class TestCombine(unittest.TestCase):
    def test_inverse_variance_combine(self):
        # two sources: logmean 1.0 (var 0.04) and 2.0 (var 0.01)
        mean, var = sr.combine_sources([(1.0, 0.04), (2.0, 0.01)])
        # precision-weighted: w1=25, w2=100 -> (25*1+100*2)/125 = 1.8 ; var=1/125
        self.assertAlmostEqual(mean, 1.8, places=6)
        self.assertAlmostEqual(var, 1.0 / 125.0, places=6)

    def test_single_source(self):
        self.assertEqual(sr.combine_sources([(1.5, 0.04)]), (1.5, 0.04))

    def test_no_source(self):
        self.assertIsNone(sr.combine_sources([]))

    def test_seat_variance_inflated_by_coverage(self):
        base = 0.09
        # lower coverage -> larger variance
        v_full = sr.inflate_variance(base, coverage=1.0)
        v_partial = sr.inflate_variance(base, coverage=0.6)
        self.assertAlmostEqual(v_full, base, places=9)
        self.assertGreater(v_partial, v_full)


if __name__ == "__main__":
    unittest.main()
