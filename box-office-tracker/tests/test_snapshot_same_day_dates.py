"""Snapshot-only Phase 2 must read the current show date during the day.

2026-10-10: Saturday's call for Other Mommy rested on Friday-midnight
reservations because SNAPSHOT_SAME_DAY_CUTOFF_HOUR=6 dropped today from the
14:30Z/22:30Z slots (and left the Sunday daytime slots with nothing to read).
"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper  # noqa: E402


class SnapshotSameDayDatesTest(unittest.TestCase):
    def _with_cutoff(self, hour):
        old = scraper.SNAPSHOT_SAME_DAY_CUTOFF_HOUR
        scraper.SNAPSHOT_SAME_DAY_CUTOFF_HOUR = hour
        self.addCleanup(setattr, scraper, "SNAPSHOT_SAME_DAY_CUTOFF_HOUR", old)

    def test_default_keeps_today_all_day(self):
        self.assertEqual(24, scraper.SNAPSHOT_SAME_DAY_CUTOFF_HOUR)

    def test_saturday_morning_reads_saturday_and_sunday(self):
        self._with_cutoff(24)
        dates = scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 10, 10, 30))
        self.assertEqual(["2026-10-10", "2026-10-11"], dates)

    def test_saturday_evening_still_reads_saturday(self):
        self._with_cutoff(24)
        dates = scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 10, 18, 35))
        self.assertEqual(["2026-10-10", "2026-10-11"], dates)

    def test_sunday_daytime_reads_sunday(self):
        self._with_cutoff(24)
        dates = scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 11, 14, 0))
        self.assertEqual(["2026-10-11"], dates)

    def test_legacy_cutoff_drops_today_after_six(self):
        self._with_cutoff(6)
        self.assertEqual(["2026-10-11"],
                         scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 10, 10, 30)))
        self.assertEqual([], scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 11, 14, 0)))

    def test_max_dates_keeps_nearest(self):
        self._with_cutoff(24)
        dates = scraper.phase2_snapshot_collection_dates(datetime(2026, 10, 9, 10, 30), max_dates=2)
        self.assertEqual(["2026-10-09", "2026-10-10"], dates)


if __name__ == "__main__":
    unittest.main()
