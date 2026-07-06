import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import import_thenumbers_daily as T  # noqa: E402


class OpeningDaysTests(unittest.TestCase):
    def test_preview_thursday_is_subtracted_from_friday(self):
        # the-numbers rolls Thursday previews (rank 'P') into the Friday gross.
        # Supergirl: Thu(P) 7.8, Fri 18.4 -> model Friday = 18.4 - 7.8 = 10.6,
        # and Thu+Fri+Sat+Sun == the reported 3-day (37.1).
        daily = {
            date(2026, 6, 25): ("P", 7.8),
            date(2026, 6, 26): ("2", 18.4),
            date(2026, 6, 27): ("2", 10.8),
            date(2026, 6, 28): ("2", 7.9),
        }
        od = T.opening_days(daily, "2026-06-26")
        self.assertAlmostEqual(od["Thursday"], 7.8)
        self.assertAlmostEqual(od["Friday"], 10.6)      # 18.4 - 7.8
        self.assertAlmostEqual(sum(od.values()), 37.1, places=2)

    def test_wednesday_opener_thursday_not_subtracted(self):
        # Minions: Thursday is a ranked regular day (not 'P'), so no subtraction.
        daily = {
            date(2026, 7, 2): ("1", 10.81),
            date(2026, 7, 3): ("1", 16.51),
            date(2026, 7, 4): ("1", 9.47),
            date(2026, 7, 5): ("1", 10.42),
        }
        od = T.opening_days(daily, "2026-07-03")
        self.assertAlmostEqual(od["Thursday"], 10.81)
        self.assertAlmostEqual(od["Friday"], 16.51)     # unchanged
        self.assertAlmostEqual(sum(od.values()), 47.21, places=2)

    def test_missing_thursday_is_fine(self):
        daily = {
            date(2026, 5, 15): ("1", 1.17),
            date(2026, 5, 16): ("1", 1.03),
            date(2026, 5, 17): ("1", 0.72),
        }
        od = T.opening_days(daily, "2026-05-15")
        self.assertNotIn("Thursday", od)
        self.assertEqual(set(od), {"Friday", "Saturday", "Sunday"})


class SlugTests(unittest.TestCase):
    def test_ampersand_and_year(self):
        cands = T.slug_candidates("Minions & Monsters", 2026)
        self.assertIn("Minions-and-Monsters-(2026)", cands[0])

    def test_punctuation_dropped(self):
        cands = T.slug_candidates("Jackass: Best and Last", 2026)
        self.assertIn("Jackass-Best-and-Last-(2026)", cands[0])


if __name__ == "__main__":
    unittest.main()
