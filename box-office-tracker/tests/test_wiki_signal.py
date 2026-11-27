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


def _fact(title, film=True, years=(), us=True, imdb=()):
    return {"item": "Q1", "title": title, "film": film, "us": us,
            "years": list(years), "imdb": list(imdb)}


class ArticleResolveTests(unittest.TestCase):
    """2026-11-27: the first search hit containing the title won, so 9 of 217
    comps read another page ('theaccountant2' sits inside
    'theaccountant2016film'). The choosing itself is tested in
    test_wiki_film_article.py; here, how the importer uses it."""

    def test_imdb_id_decides_without_a_search(self):
        from unittest import mock
        facts = {"tt0000001": [_fact("The Accountant 2", years=[2025], imdb=["tt0000001"])]}
        with mock.patch.object(W, "search_hits", side_effect=AssertionError("no search needed")):
            self.assertEqual("The Accountant 2", W.resolve_article(
                "The Accountant 2", 2025, "https://www.imdb.com/title/tt0000001/", facts))

    def test_without_an_id_only_a_verified_hit_is_taken(self):
        from unittest import mock
        hits = ["The Accountant (2016 film)", "The Accountant 2", "Ben Affleck"]
        known = {"The Accountant (2016 film)": _fact("The Accountant (2016 film)", years=[2016]),
                 "The Accountant 2": _fact("The Accountant 2", years=[2025]),
                 "Ben Affleck": _fact("Ben Affleck", film=False)}
        with mock.patch.object(W, "search_hits", return_value=hits), \
                mock.patch.object(W.WA, "facts_for_titles", return_value=known):
            self.assertEqual("The Accountant 2", W.resolve_article("The Accountant 2", 2025))

    def test_no_verified_hit_is_no_article(self):
        from unittest import mock
        known = {"The Sea Beast (2022 film)": _fact("The Sea Beast (2022 film)", years=[2022])}
        with mock.patch.object(W, "search_hits", return_value=["The Sea Beast (2022 film)"]), \
                mock.patch.object(W.WA, "facts_for_titles", return_value=known):
            self.assertIsNone(W.resolve_article("Beast", 2022))
        with mock.patch.object(W, "search_hits", return_value=[]):
            self.assertIsNone(W.resolve_article("Unlisted", 2025))

    def test_an_id_for_another_film_falls_back_to_the_search(self):
        from unittest import mock
        facts = {"tt0000009": [_fact("Villeneuve: The Rise of a Legend", years=[2026], imdb=["tt0000009"])]}
        known = {"Ramayana: Rise of A Legend": _fact("Ramayana: Rise of A Legend", years=[2026])}
        with mock.patch.object(W, "search_hits", return_value=["Ramayana: Rise of A Legend"]), \
                mock.patch.object(W.WA, "facts_for_titles", return_value=known):
            self.assertEqual("Ramayana: Rise of A Legend", W.resolve_article(
                "Ramayana: Rise of A Legend", 2026, "tt0000009", facts))

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

    @staticmethod
    def _daily(n, date, gross):
        return (f'<tr><td><a class="a-link-normal" href="/date/{date}/?ref_=bo_rl_table_{n}">x</a></td>'
                f'<td>1</td><td class="mojo-field-type-money">${gross:,}</td></tr>')

    def test_the_weekend_with_the_rows_grosses_decides(self):
        # A limited opening on Sep 12, the wide weekend two weeks later: the
        # stated release date and a chart of the limited run are both wrong.
        page = (self.PAGE + self._daily(1, "2025-09-12", 90_000) + self._daily(2, "2025-09-13", 120_000)
                + self._daily(3, "2025-09-14", 80_000) + self._daily(15, "2025-09-26", 8_800_000)
                + self._daily(16, "2025-09-27", 7_600_000) + self._daily(17, "2025-09-28", 5_600_000))
        row = {"source_url": "https://www.the-numbers.com/box-office-chart/daily/2025/09/11",
               "daily_source_url": self.BOM,
               "friday_m": "8.8", "saturday_m": "7.6", "sunday_m": "5.6"}
        self.assertEqual(("2025-09-26", "bom-daily"), W.comp_opening_friday(row, fetch_text=lambda u: page))

    def test_dated_chart_when_no_weekend_matches(self):
        row = {"source_url": "https://www.the-numbers.com/box-office-chart/daily/2025/09/25",
               "daily_source_url": self.BOM,
               "friday_m": "8.8", "saturday_m": "7.6", "sunday_m": "5.6"}
        self.assertEqual(("2025-09-26", "numbers-chart"),
                         W.comp_opening_friday(row, fetch_text=lambda u: self.PAGE))

        def boom(url):
            raise OSError("blocked")
        self.assertEqual(("2025-09-26", "numbers-chart"), W.comp_opening_friday(row, fetch_text=boom))

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

    def test_only_rows_whose_page_or_views_are_wrong_are_read_again(self):
        import csv
        import json
        import tempfile
        from unittest import mock
        cols = ["movie", "release_year", "imdb_url", "wiki_release_week_views",
                "wiki_article", "wiki_opening_friday"]
        comps = [["Elvis", "2022", "https://www.imdb.com/title/tt0000001/", "169847", "Elvis (2022 film)", "2022-06-24"],
                 ["The Menu", "2022", "https://www.imdb.com/title/tt0000002/", "241738", "The Menu (2022 film)", "2022-11-18"],
                 ["Tarot", "2024", "https://www.imdb.com/title/tt0000003/", "", "Tarot (2024 American film)", "2024-05-03"]]
        cache = {f"v2|{m}|{y}": {"article": a, "friday": f, "views": int(v or 0), "peak": 0, "basis": "x"}
                 for m, y, _, v, a, f in comps}
        facts = {"tt0000001": [_fact("Elvis (2022 film)", years=[2022], imdb=["tt0000001"])],
                 "tt0000002": [_fact("The Menu", years=[2022], imdb=["tt0000002"])],       # the page was renamed
                 "tt0000003": [_fact("Tarot (2024 American film)", years=[2024], imdb=["tt0000003"])]}
        read = []

        def fake_resolve(r, title, year, throttle, art, titles=None, touched=None):
            read.append((title, art))
            return {"article": art, "friday": r["wiki_opening_friday"], "views": 5000, "peak": 0, "basis": "x"}

        with tempfile.TemporaryDirectory() as tmp:
            comps_csv, cache_path = os.path.join(tmp, "comps.csv"), os.path.join(tmp, "cache.json")
            with open(comps_csv, "w", newline="") as f:
                csv.writer(f).writerows([cols] + comps)
            json.dump(cache, open(cache_path, "w"))
            with mock.patch.object(W, "COMPS_CSV", comps_csv), mock.patch.object(W, "CACHE_PATH", cache_path), \
                    mock.patch.object(W.WA, "facts_for_imdb_ids", return_value=facts), \
                    mock.patch.object(W, "redirect_titles", lambda arts, strict=False: {a: [a] for a in arts}), \
                    mock.patch.object(W, "redirect_last_touched", lambda names: {}), \
                    mock.patch.object(W, "_resolve_comp", fake_resolve), mock.patch.object(W.time, "sleep"):
                self.assertEqual(0, W.backfill_comps())
            rows = {r["movie"]: r for r in csv.DictReader(open(comps_csv))}
        # Elvis: right page, has views -> untouched. The Menu: page renamed.
        # Tarot: views unknown -> tried again.
        self.assertEqual([("The Menu", "The Menu"), ("Tarot", "Tarot (2024 American film)")], read)
        self.assertEqual("The Menu", rows["The Menu"]["wiki_article"])
        self.assertEqual("169847", rows["Elvis"]["wiki_release_week_views"])
        self.assertEqual("5000", rows["Tarot"]["wiki_release_week_views"])

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



class PastNameViewsTests(unittest.TestCase):
    """Tarot (2024): its release-week name now leads elsewhere, so the film's
    page and redirects show 37 views; the page's move history has the name."""
    MOVES = [
        {"timestamp": "2023-12-18T09:00:00Z",
         "comment": "X moved page [[Draft:Horrorscope (film)]] to [[Horrorscope (film)]]"},
        {"timestamp": "2024-01-30T12:00:00Z",
         "comment": "X moved page [[Horrorscope (film)]] to [[Tarot (2024 film)]]"},
        {"timestamp": "2024-07-23T18:00:00Z",
         "comment": "X moved page [[Tarot (2024 film)]] to [[Tarot (2024 American film)]]"},
    ]

    def test_views_under_the_names_the_page_had_that_week(self):
        from unittest import mock
        views = {"Horrorscope (film)": 9, "Tarot (2024 film)": 17000, "Tarot (2024 American film)": 0}
        asked = []

        def fake_views(name, start, end):
            asked.append(name)
            return [{"timestamp": f"202404{d}00", "views": views[name]} for d in ("29", "30")] + \
                   [{"timestamp": f"202405{d}00", "views": views[name]} for d in ("01", "02")]

        with mock.patch.object(W, "daily_pageviews", fake_views), mock.patch.object(W.time, "sleep"):
            total, names = W.anticipation_under_past_names(
                "Tarot (2024 American film)", "2024-05-03", fetch_revisions=lambda a: self.MOVES)
        self.assertEqual(4 * 17000 + 4 * 9, total)
        self.assertEqual(["Horrorscope (film)", "Tarot (2024 film)"], sorted(asked))

    def test_a_name_counts_only_from_the_day_the_page_took_it(self):
        mon = datetime(2025, 3, 10)
        items = [{"timestamp": f"202503{d}00", "views": 100} for d in ("10", "11", "12", "13")]
        self.assertEqual(400, W.views_from(items, mon))
        self.assertEqual(200, W.views_from(items, mon, since="2025-03-12"))

    def test_an_unreadable_history_stays_unknown(self):
        def boom(article):
            raise OSError("blocked")
        self.assertEqual((0, {}), W.anticipation_under_past_names("Tarot", "2024-05-03", fetch_revisions=boom))


class LiveArticleTests(unittest.TestCase):
    def test_imdb_ids_come_from_the_review_rows(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("weekend_of,as_of_date,movie_title,notes\n"
                    "2026-09-11,2026-09-10,Runner,https://www.imdb.com/title/tt31349844/\n"
                    "2026-09-11,2026-09-10,Hope,https://www.rottentomatoes.com/m/hope_2026\n")
        try:
            self.assertEqual({"Runner": "tt31349844"}, W.review_imdb_ids(f.name))
        finally:
            os.unlink(f.name)
        self.assertEqual({}, W.review_imdb_ids("/nonexistent/reviews.csv"))

    def test_a_film_without_a_verified_page_is_skipped_not_guessed(self):
        from unittest import mock
        written = []
        with mock.patch.object(W, "review_imdb_ids", return_value={"Runner": "tt31349844"}), \
                mock.patch.object(W, "resolve_article", side_effect=[None, OSError("wikidata down")]) as res, \
                mock.patch.object(W, "_append_social", written.append):
            W.fetch_current("2026-09-11", ["Runner", "Hope"])
        self.assertEqual(("Runner", 2026, "tt31349844"), res.call_args_list[0].args)
        self.assertEqual([[]], written)
