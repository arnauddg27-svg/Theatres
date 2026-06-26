import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import import_wiki_pageviews as W  # noqa: E402


class OpeningFridayFromPeakTests(unittest.TestCase):
    def _friday(self, datestr):
        return W.opening_friday_from_peak(datetime.strptime(datestr, "%Y-%m-%d")).strftime("%Y-%m-%d")

    def test_saturday_peak_maps_to_that_friday(self):
        # 2023-07-22 is the Sat of Oppenheimer's opening weekend -> Fri 07-21
        self.assertEqual(self._friday("2023-07-22"), "2023-07-21")

    def test_friday_peak_is_itself(self):
        self.assertEqual(self._friday("2023-07-21"), "2023-07-21")

    def test_sunday_peak_maps_back_to_friday(self):
        self.assertEqual(self._friday("2023-07-23"), "2023-07-21")

    def test_monday_after_weekend_maps_to_prior_friday(self):
        self.assertEqual(self._friday("2023-07-24"), "2023-07-21")

    def test_result_is_always_a_friday(self):
        base = datetime(2024, 1, 1)
        for k in range(60):
            f = W.opening_friday_from_peak(base + timedelta(days=k))
            self.assertEqual(f.weekday(), 4)  # Friday


class WindowSumTests(unittest.TestCase):
    def test_leak_free_mon_thu_window_only(self):
        # Build a week of views; the Mon-Thu sum must exclude Fri/Sat/Sun.
        mon = datetime(2026, 6, 22)  # Mon before the 2026-06-26 Friday
        items = []
        for k in range(7):
            day = mon + timedelta(days=k)
            items.append({"timestamp": day.strftime("%Y%m%d") + "00", "views": (k + 1) * 100})
        # Mon..Thu = 100+200+300+400 = 1000; Fri/Sat/Sun (500/600/700) excluded
        self.assertEqual(W._window_sum(items, mon, days=4), 1000)

    def test_missing_days_count_as_zero(self):
        mon = datetime(2026, 6, 22)
        items = [{"timestamp": mon.strftime("%Y%m%d") + "00", "views": 100}]  # only Monday
        self.assertEqual(W._window_sum(items, mon, days=4), 100)


if __name__ == "__main__":
    unittest.main()
