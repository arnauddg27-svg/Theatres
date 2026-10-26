"""Lognormal bracket probabilities from graded stage errors (2026-10-26)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bracket_model as B  # noqa: E402

BR = [("<22m", None, 22.0), ("22m-25m", 22.0, 25.0), ("25m-28m", 25.0, 28.0), ("28m+", 28.0, None)]


class BracketModelTest(unittest.TestCase):
    def test_probabilities_sum_to_one_and_centre_on_mid(self):
        p = B.bracket_probabilities(23.5, BR, 0.0, 0.08)
        self.assertAlmostEqual(sum(p.values()), 1.0, places=9)
        self.assertEqual(max(p, key=p.get), "22m-25m")
        self.assertGreater(p["<22m"], p["28m+"])  # 23.5 sits nearer 22 than 28
        # A 3M bracket is narrow against an after-friday-sized error (sigma
        # 0.15): the model should NOT be confident in it.
        self.assertLess(B.bracket_probabilities(23.5, BR, 0.0, 0.15)["22m-25m"], 0.4)

    def test_wider_sigma_spreads_mass(self):
        tight = B.bracket_probabilities(23.5, BR, 0.0, 0.03)["22m-25m"]
        wide = B.bracket_probabilities(23.5, BR, 0.0, 0.40)["22m-25m"]
        self.assertGreater(tight, 0.9)
        self.assertLess(wide, 0.35)

    def test_bias_shifts_the_centre(self):
        up = B.bracket_probabilities(21.0, BR, math.log(1.2), 0.10)
        self.assertEqual(max(up, key=up.get), "25m-28m")

    def test_degenerate_inputs(self):
        self.assertEqual(B.bracket_probabilities(0, BR, 0, 0.1), {})
        self.assertEqual(B.bracket_probabilities(10, BR, 0, 0), {})

    def test_fit_uses_only_earlier_weekends_and_other_films(self):
        ratios = {"after-friday": [("2026-09-18", "a", 0.10), ("2026-09-25", "b", -0.10),
                                   ("2026-10-02", "c", 0.05), ("2026-10-09", "d", -0.05),
                                   ("2026-10-16", "e", 0.00), ("2026-10-23", "f", 2.0),   # future: excluded
                                   ("2026-10-09", "x", 3.0)]}                            # the film itself
        bias, sigma, n = B.fit_stage("after-friday", "2026-10-23", "X", ratios=ratios)
        self.assertEqual(n, 5)
        self.assertLess(sigma, 0.2)
        self.assertAlmostEqual(bias, 0.0, places=6)
        _, prior, n0 = B.fit_stage("after-friday", "2026-09-01", ratios=ratios)
        self.assertEqual((n0, prior), (0, B.PRIOR_SIGMA["after-friday"]))

    def test_sigma_never_collapses(self):
        ratios = {"complete": [("2026-09-%02d" % d, "m%d" % d, 0.0) for d in range(1, 12)]}
        _, sigma, _ = B.fit_stage("complete", "2026-10-23", ratios=ratios)
        self.assertGreaterEqual(sigma, 0.5 * B.PRIOR_SIGMA["complete"])


if __name__ == "__main__":
    unittest.main()
