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


class ArticlePickTests(unittest.TestCase):
    """2026-11-27: a substring test matched 'theaccountant2' inside
    'theaccountant2016film' and 'nobody2' inside 'nobody2025film'."""

    def test_sequel_number_does_not_match_a_year(self):
        hits = ["The Accountant (2016 film)", "The Accountant 2", "Ben Affleck"]
        self.assertEqual("The Accountant 2", W.pick_article("The Accountant 2", 2025, hits))
        self.assertEqual("Nobody 2", W.pick_article("Nobody 2", 2025, ["Nobody (2025 film)", "Nobody 2"]))

    def test_same_title_prefers_the_release_year(self):
        hits = ["Last Breath (2019 film)", "Last Breath (2025 film)", "Last Breath"]
        self.assertEqual("Last Breath (2025 film)", W.pick_article("Last Breath", 2025, hits))

    def test_punctuation_differences_still_match(self):
        hits = ["Inuyasha", "Demon Slayer: Kimetsu no Yaiba – The Movie: Infinity Castle"]
        self.assertEqual(hits[1], W.pick_article(
            "Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle", 2025, hits))

    def test_falls_back_to_the_first_hit(self):
        self.assertEqual("Something Else", W.pick_article("Unlisted", 2025, ["Something Else"]))
        self.assertIsNone(W.pick_article("Unlisted", 2025, []))

    def test_search_text_carries_no_operators(self):
        q = W.search_query("Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle", 2025)
        self.assertEqual("Demon Slayer Kimetsu no Yaiba The Movie Infinity Castle 2025 film", q)


class CompOpeningFridayTests(unittest.TestCase):
    BOM = "https://www.boxofficemojo.com/release/rl53837825"
    PAGE = '<span>Release Date</span><span><a href="/date/2025-09-12/">Sep 12, 2025</a></span>'

    def test_release_day_to_opening_friday(self):
        f = lambda s: W.opening_friday_for_date(datetime.strptime(s, "%Y-%m-%d")).strftime("%Y-%m-%d")  # noqa: E731
        self.assertEqual("2025-09-26", f("2025-09-25"))   # Thursday previews chart
        self.assertEqual("2025-09-26", f("2025-09-26"))
        self.assertEqual("2025-11-28", f("2025-11-26"))   # Wednesday opener
        self.assertEqual("2025-09-26", f("2025-09-27"))   # a Saturday date

    def test_dated_chart_decides(self):
        row = {"source_url": "https://www.the-numbers.com/box-office-chart/daily/2025/09/25",
               "daily_source_url": self.BOM}
        self.assertEqual(("2025-09-26", "numbers-chart"),
                         W.comp_opening_friday(row, fetch_text=lambda u: self.fail("not needed")))

    def test_bom_release_page_otherwise(self):
        row = {"source_url": "https://www.the-numbers.com/box-office-records/domestic/all-movies/previews/any",
               "daily_source_url": self.BOM}
        self.assertEqual(("2025-09-12", "bom-release"),
                         W.comp_opening_friday(row, fetch_text=lambda u: self.PAGE))

    def test_no_source_or_a_failed_fetch_is_unknown(self):
        def boom(url):
            raise OSError("blocked")
        self.assertEqual((None, ""), W.comp_opening_friday({"source_url": "", "daily_source_url": ""}))
        self.assertEqual((None, ""), W.comp_opening_friday(
            {"source_url": "", "daily_source_url": self.BOM}, fetch_text=boom))
        self.assertEqual((None, ""), W.comp_opening_friday(
            {"source_url": "", "daily_source_url": self.BOM}, fetch_text=lambda u: "<html></html>"))

    def test_no_contact_address_is_hard_coded(self):
        self.assertNotIn("@", W.UA if not os.environ.get("WIKIMEDIA_CONTACT") else "")


class ArticleRefinementTests(unittest.TestCase):
    def test_same_year_namesakes_prefer_the_american_film(self):
        hits = ["Beast (2022 Indian film)", "The Sea Beast (2022 film)", "Beast (2022 American film)"]
        self.assertEqual("Beast (2022 American film)", W.pick_article("Beast", 2022, hits))

    def test_apostrophes_survive_the_search_text(self):
        self.assertEqual("Don't Worry Darling 2022 film", W.search_query("Don't Worry Darling", 2022))


class RedirectViewsTests(unittest.TestCase):
    """Views sit under the title the page had that week ('Black Bag (film)')."""

    def test_views_are_summed_over_the_article_and_its_redirects(self):
        from unittest import mock
        redirects = {"query": {"pages": {"1": {"title": "Black Bag", "redirects": [
            {"title": "Black Bag (film)"}, {"title": "Black bag"}]}}}}
        views = {"Black_Bag": 16000, "Black_Bag_(film)": 100000, "Black_bag": 1500}

        def fake_get(url, tries=4):
            if "prop=redirects" in url:
                return redirects
            name = url.split("/all-agents/")[1].split("/daily/")[0]
            from urllib.parse import unquote
            return {"items": [{"timestamp": "2025031000", "views": views[unquote(name)]}]}

        with mock.patch.object(W, "_get", fake_get), mock.patch.object(W.time, "sleep"):
            self.assertEqual(["Black Bag", "Black Bag (film)", "Black bag"], W.article_titles("Black Bag"))
            self.assertEqual((117500, "2025-03-14"), W.anticipation_for_weekend("Black Bag", "2025-03-14"))

    def test_only_former_page_titles_are_read(self):
        self.assertTrue(W.former_title("Tarot (2024 American film)", "Horrorscope (film)"))
        self.assertTrue(W.former_title("Longlegs (film)", "Longlegs"))
        self.assertFalse(W.former_title("Top Gun: Maverick", "TGM"))
        self.assertFalse(W.former_title("Sonic the Hedgehog 2 (film)", "Sonic 2 Movie"))
        self.assertFalse(W.former_title("M3GAN", "M3GAN (soundtrack)"))

    def test_a_failed_redirect_lookup_keeps_the_article(self):
        from unittest import mock

        def boom(url, tries=4):
            raise OSError("down")

        with mock.patch.object(W, "_get", boom):
            self.assertEqual(["Black Bag"], W.article_titles("Black Bag"))


class BackfillLoadTests(unittest.TestCase):
    """2026-11-27: one search + one redirect request per film was throttled."""

    def test_a_plainly_correct_stored_article_is_reused(self):
        self.assertTrue(W.reusable_article("Black Bag", 2025, "Black Bag"))
        self.assertTrue(W.reusable_article("Last Breath", 2025, "Last Breath (2025 film)"))
        self.assertTrue(W.reusable_article("The Monkey", 2025, "The Monkey (film)"))

    def test_a_doubtful_one_is_searched_again(self):
        for title, year, article in (
                ("No Time to Die", 2021, "No Time to Die (1958 film)"),
                ("M3GAN", 2023, "M3GAN (film series)"),
                ("Nobody 2", 2025, "Nobody (2025 film)"),
                ("The Accountant 2", 2025, "The Accountant (2016 film)"),
                ("Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle", 2025, "Inuyasha"),
                ("Weapons", 2025, "")):
            self.assertFalse(W.reusable_article(title, year, article), article)

    def test_redirects_are_read_in_batches(self):
        from unittest import mock
        calls = []

        def fake_get(url, tries=4):
            calls.append(url)
            return {"query": {
                "normalized": [{"from": "black bag", "to": "Black bag"}],
                "pages": {"1": {"title": "Weapons (2025 film)", "redirects": [{"title": "Weapons (film)"}]},
                          "2": {"title": "Black bag"}}}}

        with mock.patch.object(W, "_get", fake_get), mock.patch.object(W.time, "sleep"):
            out = W.redirect_titles(["Weapons (2025 film)", "black bag"])
        self.assertEqual(1, len(calls))
        self.assertEqual({"Weapons (2025 film)": ["Weapons (2025 film)", "Weapons (film)"],
                          "black bag": ["black bag"]}, out)


class RedirectDateTests(unittest.TestCase):
    """A redirect last written before release week was not the page that week."""

    def test_settled_redirects_are_not_asked_for_views(self):
        from unittest import mock
        asked = []

        def fake_views(name, start, end):
            asked.append(name)
            return [{"timestamp": "2025031000", "views": 1000}]

        touched = {"Black Bag (film)": "2025-04-02", "Black bag": "2019-06-01"}
        with mock.patch.object(W, "daily_pageviews", fake_views), mock.patch.object(W.time, "sleep"):
            total, _ = W.anticipation_for_weekend(
                "Black Bag", "2025-03-14", titles=["Black Bag", "Black Bag (film)", "Black bag", "Undated"],
                touched=touched)
        self.assertEqual(["Black Bag", "Black Bag (film)", "Undated"], asked)
        self.assertEqual(3000, total)

    def test_last_touched_is_read_in_one_request(self):
        from unittest import mock
        calls = []

        def fake_get(url, tries=4):
            calls.append(url)
            return {"query": {"pages": {
                "1": {"title": "Black Bag (film)", "revisions": [{"timestamp": "2025-04-02T10:00:00Z"}]},
                "2": {"title": "Gone", "missing": ""}}}}

        with mock.patch.object(W, "_get", fake_get), mock.patch.object(W.time, "sleep"):
            self.assertEqual({"Black Bag (film)": "2025-04-02"},
                             W.redirect_last_touched(["Black Bag (film)", "Gone"]))
        self.assertEqual(1, len(calls))
