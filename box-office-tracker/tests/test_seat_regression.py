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


if __name__ == "__main__":
    unittest.main()
