"""Release-calendar seeding (2026-10-18)."""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import release_calendar as RC  # noqa: E402
import scraper  # noqa: E402

PAGE = """
<table>
<tr><th>Release</th><th>Distributor</th><th>Scale</th></tr>
<tr><th colspan="3">October 22, 2026</th></tr>
<tr><td><a>Early Bird</a> Comedy With: Someone 1 hr 30 min Cast, Crew, and Company Info</td><td>Neon</td><td>Wide</td></tr>
<tr><th colspan="3">October 23, 2026</th></tr>
<tr><td><a>Clayface</a> Horror Sci-Fi Thriller With: Tom Rhys Harries 1 hr 48 min Cast, Crew, and Company Info</td><td>Warner Bros.</td><td>Wide</td></tr>
<tr><td><a>Love Language</a> Comedy Romance With: Chloe 1 hr 44 min Cast, Crew, and Company Info</td><td>Vertical</td><td>Limited</td></tr>
<tr><td><a>You Can See Everything</a> Documentary With: Nathan Fielder 2 hr 54 min Cast, Crew, and Company Info</td><td>A24</td><td>Wide</td></tr>
<tr><td><a>Rocky (50th Anniversary)</a> Drama With: Sylvester 2 hr Cast, Crew, and Company Info</td><td>Fathom</td><td>Wide</td></tr>
<tr><th colspan="3">October 30, 2026</th></tr>
<tr><td><a>Next Week Film</a> Action With: X 1 hr Cast, Crew, and Company Info</td><td>Sony</td><td>Wide</td></tr>
</table>
"""


class ReleaseCalendarParseTest(unittest.TestCase):
    def test_parse_keeps_wide_wed_to_fri_and_skips_expansions_and_rereleases(self):
        with mock.patch.object(RC, "earlier_tracked_titles", return_value={RC._key("You Can See Everything")}):
            rows = RC.parse_calendar(PAGE, "2026-10-23")
        titles = [r["title"] for r in rows]
        self.assertEqual(["Clayface", "Early Bird"], titles)      # major first, Thursday opener kept
        self.assertEqual("Warner Bros.", rows[0]["distributor"])
        self.assertIn("Horror", rows[0]["genres"])

    def test_parse_live_bom_header_format(self):
        # Live BOM headers read "Fri Oct 30, 2026"; the first parser only
        # matched "October 30, 2026" and wrote 0 titles on 2026-10-23/24.
        page = (PAGE.replace("October 22, 2026", "Thu Oct 22, 2026")
                    .replace("October 23, 2026", "Fri Oct 23, 2026")
                    .replace("October 30, 2026", "Fri Oct 30, 2026"))
        page = page.replace("</table>", '<tr><td><a>Show Live!</a> Musical With: X 2 hr Cast, Crew, and '
                            'Company Info</td><td>Roadside</td><td>Wide</td></tr></table>')
        with mock.patch.object(RC, "earlier_tracked_titles", return_value=set()):
            titles = [r["title"] for r in RC.parse_calendar(page, "2026-10-23")]
        self.assertEqual(["Clayface", "Early Bird", "You Can See Everything"], titles)
        with mock.patch.object(RC, "earlier_tracked_titles", return_value=set()):
            live = RC.parse_calendar(page.replace("Fri Oct 30, 2026", "Wed Oct 21, 2026"), "2026-10-23")
        self.assertNotIn("Show Live!", [r["title"] for r in live])

    def test_calendar_page_starts_on_wednesday(self):
        self.assertEqual("2026-10-28", RC.calendar_start_date("2026-10-30"))

    def test_earlier_tracked_titles(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("movie,weekend_of\nYou Can See Everything,2026-10-16\nClayface,2026-10-23\n")
        try:
            keys = RC.earlier_tracked_titles("2026-10-23", metadata_csv=f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual({RC._key("You Can See Everything")}, keys)


class ScraperCalendarMergeTest(unittest.TestCase):
    def test_merge_adds_missing_calendar_titles(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "release-calendar.json")
            with open(path, "w") as f:
                json.dump({"weekend_of": "2026-10-23", "fetched_at": "2026-10-19T12:00:00+00:00",
                           "titles": [{"title": "Clayface"}, {"title": "Wildwood"}]}, f)
            with mock.patch.object(scraper, "RELEASE_CALENDAR_JSON", scraper.Path(path)), \
                 mock.patch.object(scraper, "latest_market_urls_from_csv", return_value={}):
                merged = scraper.merge_calendar_titles(
                    [{"movie_title": "Clayface", "market_url": "u"}], "2026-10-23", "Phase 1")
                self.assertEqual(["Clayface", "Wildwood"], [m["movie_title"] for m in merged])
                self.assertEqual([], scraper.calendar_titles_for_weekend("2026-10-30"))
                stale = dict(json.load(open(path)), fetched_at="2026-09-01T00:00:00+00:00")
                json.dump(stale, open(path, "w"))
                self.assertEqual([], scraper.calendar_titles_for_weekend("2026-10-23"))


if __name__ == "__main__":
    unittest.main()


class TrackedStateIncludesCalendarTest(unittest.TestCase):
    def test_tracked_titles_include_calendar(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "release-calendar.json")
            with open(path, "w") as f:
                json.dump({"weekend_of": "2026-10-23", "fetched_at": "2026-10-19T12:00:00+00:00",
                           "titles": [{"title": "Clayface"}, {"title": "The Clayface"}]}, f)
            with mock.patch.object(scraper, "RELEASE_CALENDAR_JSON", scraper.Path(path)), \
                 mock.patch.object(scraper, "LINKS_JSON", scraper.Path(os.path.join(td, "none.json"))), \
                 mock.patch.object(scraper, "THEATRE_COUNTS_JSON", scraper.Path(os.path.join(td, "none2.json"))):
                self.assertEqual(["Clayface"], scraper.tracked_movie_titles_from_state("2026-10-23"))
                self.assertEqual([], scraper.tracked_movie_titles_from_state("2026-10-30"))


class DedupGuardCalendarTest(unittest.TestCase):
    def test_guard_counts_calendar_titles_as_active(self):
        import importlib.util
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "guard", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "scripts", "collect_links_dedup_guard.py"))
        guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "box-office-tracker" / "data").mkdir(parents=True)
            (root / "box-office-tracker" / "data" / "release-calendar.json").write_text(json.dumps(
                {"weekend_of": "2026-10-23", "titles": [{"title": "Clayface"}, {"title": "Wildwood"}]}))
            self.assertEqual(["Clayface", "Wildwood"], guard._calendar_titles(root, "2026-10-23"))
            self.assertEqual([], guard._calendar_titles(root, "2026-10-30"))


class DedupGuardCalendarDemandTest(unittest.TestCase):
    def _guard(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "guard2", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "scripts", "collect_links_dedup_guard.py"))
        g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g); return g

    def test_calendar_titles_without_amc_links_are_not_demanded_once_cache_exists(self):
        from pathlib import Path
        guard = self._guard()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "box-office-tracker" / "data").mkdir(parents=True)
            (root / "box-office-tracker" / "data" / "release-calendar.json").write_text(json.dumps(
                {"weekend_of": "2026-10-23", "titles": [{"title": "Clayface"}, {"title": "Wildwood"}]}))
            # no cache yet -> demand everything
            self.assertEqual(["Clayface", "Wildwood"], guard._calendar_titles_to_demand(root, {}, "2026-10-23"))
            # cache for this weekend lists Clayface only -> Wildwood is not-at-AMC
            links = {"weekend_of": "2026-10-23", "theatres": {"AMC X": {"dates": {"2026-10-23": {"movies": {"Clayface": []}}}}}}
            self.assertEqual(["Clayface"], guard._calendar_titles_to_demand(root, links, "2026-10-23"))
            # cache for another weekend -> demand everything again
            stale = dict(links, weekend_of="2026-10-16")
            self.assertEqual(["Clayface", "Wildwood"], guard._calendar_titles_to_demand(root, stale, "2026-10-23"))


class GenreMapPriorityTest(unittest.TestCase):
    def test_priority_rules(self):
        import fill_movie_metadata as F
        self.assertEqual("broad_family", F.map_genre(["Adventure", "·", "Animation", "Horror"])[1])
        self.assertEqual("adult_drama", F.map_genre(["Sci-Fi"])[1])
        self.assertEqual("fan_driven", F.map_genre(["Sci-Fi", "Action"])[1])
        self.assertEqual("female_skewing", F.map_genre(["Drama", "Romance"])[1])
        self.assertEqual("horror_fan", F.map_genre(["Horror", "Sci-Fi", "Thriller"])[1])
