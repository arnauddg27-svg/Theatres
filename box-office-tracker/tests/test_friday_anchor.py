import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


class FridayWeekendMultiplierTests(unittest.TestCase):
    def test_global_multiplier_is_reasonable(self):
        m = P.audience_friday_weekend_multiplier(None)
        self.assertIsNotNone(m)
        self.assertTrue(2.0 < m < 3.2, m)   # Friday(incl previews)->weekend ~2.4x

    def test_fan_driven_more_frontloaded_family_leggier(self):
        glob = P.audience_friday_weekend_multiplier(None)
        fan = P.audience_friday_weekend_multiplier("fan_driven")
        fam = P.audience_friday_weekend_multiplier("broad_family")
        self.assertLess(fan, glob)      # front-loaded -> smaller weekend per Friday
        self.assertGreater(fam, glob)   # leggy -> larger

    def test_unknown_audience_falls_back_to_global(self):
        self.assertEqual(
            P.audience_friday_weekend_multiplier("not_a_real_type"),
            P.audience_friday_weekend_multiplier(None),
        )


class FridayAnchoredWeekendTests(unittest.TestCase):
    def test_none_until_friday_observed(self):
        # Thursday only -> inert (the as-of-Thursday path must be unchanged)
        self.assertIsNone(P.friday_anchored_weekend_m(
            {"daily_details": {"Thursday": {"domestic_mid": 8_700_000}}}))
        self.assertIsNone(P.friday_anchored_weekend_m({"daily_details": {}}))
        self.assertIsNone(P.friday_anchored_weekend_m({}))

    def test_value_once_thu_and_fri_observed(self):
        pred = {"daily_details": {"Thursday": {"domestic_mid": 8_700_000},
                                  "Friday": {"domestic_mid": 10_000_000}},
                "audience_type": "fan_driven"}
        res = P.friday_anchored_weekend_m(pred)
        self.assertIsNotNone(res)
        weekend_m, front_m, mult = res
        self.assertAlmostEqual(front_m, 18.7, places=1)          # dollars -> $M
        self.assertAlmostEqual(weekend_m, front_m * mult, places=4)
        # fan_driven is more front-loaded than the global average
        self.assertLess(mult, P.audience_friday_weekend_multiplier(None))

    def test_blend_constant_is_interior(self):
        self.assertTrue(0.0 < P.FRIDAY_ANCHOR_BLEND_WEIGHT < 1.0)


if __name__ == "__main__":
    unittest.main()
