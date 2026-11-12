"""Drift guard metric (2026-11-12): budget-capped lanes are judged on rows per
weekend, slate-scaled lanes on rows per film."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("capture_completeness", ROOT / "scripts" / "capture_completeness.py")
CC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CC)


class DriftMetricTest(unittest.TestCase):
    def test_fandango_is_judged_on_rows_per_weekend(self):
        # steady ~2,400 rows a weekend; the slate doubled from 3 to 7 films
        prior = [{0: 1200, 1: 1250}, {0: 1200, 1: 1300}, {0: 1100, 1: 1300}, {0: 1250, 1: 1200}]
        recent = [{0: 1200, 1: 1220}, {0: 1150, 1: 1250}, {0: 1100, 1: 1050}, {0: 1200, 1: 1200}]
        r, p, unit = CC.drift_medians("fandango", recent, [7, 8, 7, 6], prior, [3, 2, 4, 3])
        self.assertEqual("rows/weekend", unit)
        self.assertGreater(r, 0.5 * p)                      # no drift
        # the same counts on a slate-scaled lane would (rightly) read as a halving per film
        r2, p2, unit2 = CC.drift_medians("cinemark", recent, [7, 8, 7, 6], prior, [3, 2, 4, 3])
        self.assertEqual("rows/film", unit2)
        self.assertLess(r2, 0.5 * p2)

    def test_a_real_fandango_bleed_still_warns(self):
        prior = [{0: 2400}] * 4
        recent = [{0: 1000}] * 4
        r, p, _ = CC.drift_medians("fandango", recent, [3] * 4, prior, [3] * 4)
        self.assertLess(r, 0.5 * p)


if __name__ == "__main__":
    unittest.main()
