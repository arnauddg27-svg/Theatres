"""Authoritative-empty listings count as fresh Phase 1 coverage (2026-10-27).

2026-10-26: five small openers, ~45% of AMC theatres booked none of them, so
their cleanly-read dates were never saved and the 90% fresh-link gate failed
23 collect-links runs in a row on a market fact."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper  # noqa: E402

V = scraper.SHOWTIME_WINDOW_VERSION
LINK = {"showtime": "7:00pm", "showtime_id": "1", "format": "Digital"}


class SavedDateEntryTest(unittest.TestCase):
    def test_links_saved(self):
        p = scraper.phase1_saved_date_entry(scraper.phase1_result({"Fjord": [LINK]}), now_iso="t")
        self.assertEqual(p, {"movies": {"Fjord": [LINK]}, "collected_at": "t", "showtime_window_version": V})

    def test_empty_listing_saved_with_marker(self):
        p = scraper.phase1_saved_date_entry(scraper.phase1_result({}, "empty"), now_iso="t")
        self.assertEqual(p["movies"], {})
        self.assertTrue(p["empty"])

    def test_unsettled_reads_not_saved(self):
        for reason in ("blocked", "challenge", "queue", "timeout", "nav_error", "aborted"):
            self.assertIsNone(scraper.phase1_saved_date_entry(scraper.phase1_result({}, reason)), reason)


class FreshnessTest(unittest.TestCase):
    def entry(self, **dates):
        return {"tz": "PT", "showtime_window_version": V, "dates": dates}

    def test_empty_date_is_fresh_and_absent_date_is_not(self):
        e = self.entry(**{"2026-10-29": {"movies": {}, "empty": True, "showtime_window_version": V},
                          "2026-10-30": {"movies": {"Fjord": [LINK]}, "showtime_window_version": V}})
        self.assertTrue(scraper.phase1_date_entry(e, "2026-10-29"))
        self.assertTrue(scraper.phase1_date_entry(e, "2026-10-30"))
        self.assertIsNone(scraper.phase1_date_entry(e, "2026-10-31"))
        # movies={} with no marker (never read cleanly) stays stale
        e2 = self.entry(**{"2026-10-29": {"movies": {}, "showtime_window_version": V}})
        self.assertIsNone(scraper.phase1_date_entry(e2, "2026-10-29"))

    def test_coverage_counts_empty_dates(self):
        theatres = {"PT": [{"name": "AMC Otay Ranch 12", "cohort": "core"}, {"name": "AMC Kabuki 8", "cohort": "core"}]}
        saved = {
            "AMC Otay Ranch 12": self.entry(**{
                "2026-10-29": {"movies": {}, "empty": True, "showtime_window_version": V},
                "2026-10-30": {"movies": {"Fjord": [LINK]}, "showtime_window_version": V}}),
            "AMC Kabuki 8": self.entry(**{"2026-10-29": {"movies": {"Fjord": [LINK]}, "showtime_window_version": V}}),
        }
        report = scraper.phase1_link_coverage_for_date_sets(
            saved, theatres, ["PT"], {"PT": ["2026-10-29", "2026-10-30"]}, required_cohorts=None)
        self.assertEqual((report["fresh_count"], report["expected_total"]), (3, 4))
        self.assertEqual(report["by_date"]["2026-10-29"]["fresh"], 2)

    def test_merge_keeps_links_and_clears_marker(self):
        old = {"movies": {"Fjord": [LINK]}, "showtime_window_version": V}
        new = {"movies": {}, "empty": True, "collected_at": "t2", "showtime_window_version": V}
        merged = scraper.merge_phase1_date_entries(old, new)
        self.assertEqual(merged["movies"], {"Fjord": [LINK]})
        self.assertFalse(merged["empty"])
        self.assertEqual(scraper.merge_phase1_date_entries(None, new)["empty"], True)


if __name__ == "__main__":
    unittest.main()
