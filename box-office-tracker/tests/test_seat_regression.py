# tests/test_seat_regression.py
import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

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


if __name__ == "__main__":
    unittest.main()
