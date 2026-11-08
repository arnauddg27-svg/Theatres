"""finalize refreshes theatre-counts.json from Sat 18Z so the opening-count
sync has a post-Friday chart (2026-11-08)."""
import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("rtc", ROOT / "scripts" / "refresh_theatre_counts.py")
rtc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rtc)


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


class WindowTest(unittest.TestCase):
    def test_window(self):
        self.assertFalse(rtc.window_open(utc(2026, 11, 6, 23, 0)))   # Friday
        self.assertFalse(rtc.window_open(utc(2026, 11, 7, 17, 59)))  # Sat before 18Z
        self.assertTrue(rtc.window_open(utc(2026, 11, 7, 18, 0)))
        self.assertTrue(rtc.window_open(utc(2026, 11, 8, 2, 30)))    # Sunday
        self.assertTrue(rtc.window_open(utc(2026, 11, 9, 23, 0)))    # Monday
        self.assertFalse(rtc.window_open(utc(2026, 11, 10, 1, 0)))   # Tuesday

    def test_main_skips_outside_window_and_fetches_openers_inside(self):
        with mock.patch.object(rtc, "window_open", return_value=False):
            self.assertEqual(rtc.main([]), 0)
        import holdover
        import scraper
        with mock.patch.object(rtc, "window_open", return_value=True), \
                mock.patch.object(scraper, "opening_weekend_friday", return_value="2026-11-06"), \
                mock.patch.object(scraper, "tracked_movie_titles_from_state", return_value=["Godzilla Minus Zero", "Wildwood"]), \
                mock.patch.object(holdover, "without_holdovers", return_value=["Godzilla Minus Zero"]), \
                mock.patch.object(scraper, "fetch_bom_theatre_counts") as fetch:
            self.assertEqual(rtc.main([]), 0)
            fetch.assert_called_once_with(["Godzilla Minus Zero"])

    def test_finalize_runs_refresh_before_sync(self):
        yml = (ROOT.parent / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        self.assertLess(yml.index("scripts/refresh_theatre_counts.py"), yml.index("scripts/sync_opening_theatre_counts.py --write"))


if __name__ == "__main__":
    unittest.main()
