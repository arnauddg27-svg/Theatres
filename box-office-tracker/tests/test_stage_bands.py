"""Per-stage headline bands from graded live calls (2026-10-18)."""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict as P  # noqa: E402

LOG = "logged_at,weekend_of,movie,headline_mid_m,forecast_stage\n" + "\n".join(
    f"2026-09-{10+i:02d}T00:00:00Z,2026-09-{10+i:02d},Film{i},{10.0},after-friday" for i in range(7)) + "\n"


class StageBandTest(unittest.TestCase):
    def _cal(self, ratios):
        return {"history": [{"weekend_of": f"2026-09-{10+i:02d}", "movie": f"Film{i}", "actual_total": 10.0 * r}
                            for i, r in enumerate(ratios)]}

    def test_stage_band_from_live_log(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(LOG)
        try:
            with mock.patch.object(P, "PREDICTION_LOG_CSV", f.name):
                P._STAGE_BAND_CACHE.clear()
                cal = self._cal([0.9, 0.95, 1.0, 1.02, 1.05, 1.1, 1.15])
                lo, hi = P.stage_ratio_band(cal, "after-friday", movie="Other")
                # low side: 1 - 0.10*1.3 = 0.87 is narrower than the 15% floor -> 0.85
                self.assertAlmostEqual(1 - P.CONFORMAL_MIN_HALF_WIDTH, lo, places=6)
                self.assertAlmostEqual(1 + 0.15 * 1.3, hi, places=6)
                # LOO: the film itself is excluded, min half width enforced
                P._STAGE_BAND_CACHE.clear()
                lo2, hi2 = P.stage_ratio_band(cal, "after-friday", movie="Film0")
                self.assertAlmostEqual(1 - P.CONFORMAL_MIN_HALF_WIDTH, lo2, places=6)
                self.assertIsNone(P.stage_ratio_band(cal, "presales"))          # no graded calls
                P._STAGE_BAND_CACHE.clear()
                self.assertIsNone(P.stage_ratio_band(self._cal([1.0] * 3), "after-friday"))  # n < 6
        finally:
            os.unlink(f.name)
            P._STAGE_BAND_CACHE.clear()


if __name__ == "__main__":
    unittest.main()
