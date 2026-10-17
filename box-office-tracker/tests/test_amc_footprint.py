"""Sub-fleet AMC releases (2026-10-17, You Can See Everything)."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict as P  # noqa: E402


class AmcFootprintTest(unittest.TestCase):
    def test_footprint_from_links_only(self):
        profiles = {"2026-10-15": {"n_theatres": 245}, "2026-10-16": {"n_theatres": 241},
                    "2026-10-20": {"n_theatres": 400}}
        self.assertEqual(245, P.film_amc_footprint(profiles, ["2026-10-15", "2026-10-16"]))
        self.assertEqual(0, P.film_amc_footprint({}, ["2026-10-15"]))

    def test_reference_switches_only_for_sub_fleet(self):
        self.assertEqual(245, P.footprint_reference_amc_theatres(425, 245))
        self.assertEqual(425, P.footprint_reference_amc_theatres(425, 400))   # wide: unchanged
        self.assertEqual(425, P.footprint_reference_amc_theatres(425, 0))     # unknown
        self.assertEqual(425, P.footprint_reference_amc_theatres(425, 10))    # implausibly small
        with mock.patch.object(P, "AMC_FOOTPRINT_MODE", "off"):
            self.assertEqual(425, P.footprint_reference_amc_theatres(425, 245))

    def test_chain_skew(self):
        with mock.patch.object(P, "cinemark_pool_size", return_value=306), \
             mock.patch.object(P, "cinemark_film_footprint", return_value=132):
            skew = P.amc_chain_footprint_skew("X", 240, 425, "2026-10-16")
            self.assertAlmostEqual((240 / 425) / (132 / 306), skew["multiplier"], places=6)
            self.assertIsNone(P.amc_chain_footprint_skew("X", 420, 425, "2026-10-16"))  # wide
            with mock.patch.object(P, "CHAIN_SKEW_MODE", "off"):
                self.assertIsNone(P.amc_chain_footprint_skew("X", 240, 425, "2026-10-16"))
        with mock.patch.object(P, "cinemark_pool_size", return_value=306), \
             mock.patch.object(P, "cinemark_film_footprint", return_value=300):
            skew = P.amc_chain_footprint_skew("X", 100, 425, "2026-10-16")
            self.assertEqual(P.CHAIN_SKEW_BOUNDS[0], skew["multiplier"])     # bounded
        with mock.patch.object(P, "cinemark_pool_size", return_value=306), \
             mock.patch.object(P, "cinemark_film_footprint", return_value=3):
            self.assertIsNone(P.amc_chain_footprint_skew("X", 240, 425, "2026-10-16"))  # too few


if __name__ == "__main__":
    unittest.main()
