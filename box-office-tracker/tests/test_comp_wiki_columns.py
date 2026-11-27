"""historical-comps.csv wiki columns: reading a Box Office Mojo release page,
and the checks on the file itself that need no network."""
import csv
import os
import sys
import unittest
from collections import Counter
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bom_release_page as C  # noqa: E402

COMPS = os.path.join(ROOT, "data", "historical-comps.csv")


def daily_row(n, date, label, gross):
    return (f'<tr><td><a class="a-link-normal" href="/date/{date}/?ref_=bo_rl_table_{n}">{label}</a></td>'
            f'<td>Friday</td><td>1</td><td class="mojo-field-type-money">${gross:,}</td>'
            f'<td>-</td><td>$9,999</td></tr>')


# Elvis: a Thursday-inclusive Friday, then a second weekend.
PAGE = ('<span>Release Date</span><span><a href="/date/2022-06-24/?ref_=bo_rl_rl">Jun 24, 2022</a></span>'
        + daily_row(1, "2022-06-24", "Jun 24", 12_728_334)
        + daily_row(2, "2022-06-25", "Jun 25", 10_157_077)
        + daily_row(3, "2022-06-26", "Jun 26", 8_326_010)
        + daily_row(8, "2022-07-01", "Jul 1", 5_300_000)
        + daily_row(9, "2022-07-02", "Jul 2", 6_800_000)
        + daily_row(10, "2022-07-03", "Jul 3", 6_400_000))


class DailyTableTests(unittest.TestCase):
    def test_release_link_is_not_a_daily_row(self):
        daily = C.daily_grosses(PAGE)
        self.assertEqual(6, len(daily))
        self.assertEqual(12_728_334, daily["2022-06-24"])

    def test_the_weekend_with_the_rows_grosses_is_the_opening(self):
        row = {"friday_m": "12.728334", "saturday_m": "10.157077", "sunday_m": "8.32601"}
        self.assertEqual("2022-06-24", C.opening_friday_for_row(row, PAGE))

    def test_grosses_from_a_later_weekend_find_that_weekend(self):
        row = {"friday_m": "5.3", "saturday_m": "6.8", "sunday_m": "6.4"}
        self.assertEqual("2022-07-01", C.opening_friday_for_row(row, PAGE))

    def test_no_matching_weekend_is_unknown_not_the_nearest(self):
        row = {"friday_m": "1.0", "saturday_m": "1.0", "sunday_m": "1.0"}
        self.assertIsNone(C.opening_friday_for_row(row, PAGE))
        self.assertIsNone(C.opening_friday_for_row(row, ""))
        self.assertIsNone(C.opening_friday_for_row({"friday_m": ""}, PAGE))

    def test_release_id(self):
        self.assertEqual("rl2819065345", C.release_id("https://www.boxofficemojo.com/release/rl2819065345"))
        self.assertEqual("", C.release_id("https://www.the-numbers.com/movie/Elvis"))

    def test_stated_release_date(self):
        self.assertEqual("2022-06-24", C.release_date(PAGE).strftime("%Y-%m-%d"))
        self.assertIsNone(C.release_date("<html></html>"))


class CompFileTests(unittest.TestCase):
    """What a wrong refill looks like without asking the network. On
    2026-11-27 the file failed every one of these."""

    @classmethod
    def setUpClass(cls):
        cls.rows = list(csv.DictReader(open(COMPS)))

    def test_every_row_has_an_opening_friday_in_its_release_year(self):
        bad = []
        for r in self.rows:
            try:
                day = datetime.strptime(r["wiki_opening_friday"], "%Y-%m-%d")
            except ValueError:
                bad.append((r["movie"], r["wiki_opening_friday"] or "(blank)"))
                continue
            if day.weekday() != 4 or str(day.year) != r["release_year"]:
                bad.append((r["movie"], r["wiki_opening_friday"]))
        self.assertEqual([], bad)

    def test_no_two_comps_share_an_article(self):
        counts = Counter(r["wiki_article"] for r in self.rows if r["wiki_article"])
        self.assertEqual({}, {a: n for a, n in counts.items() if n > 1})

    def test_no_article_is_dated_to_another_year(self):
        import wiki_film_article as A
        bad = []
        for r in self.rows:
            years = A.disambiguator_years(r["wiki_article"])
            year = int(r["release_year"])
            if years and year not in years and year - 1 not in years:
                bad.append((r["movie"], r["wiki_article"]))
        self.assertEqual([], bad)

    def test_no_article_is_a_list_series_or_soundtrack_page(self):
        bad = [(r["movie"], r["wiki_article"]) for r in self.rows
               if r["wiki_article"].lower().startswith("list of")
               or any(k in r["wiki_article"].lower() for k in
                      ("(film series)", "(franchise)", "(soundtrack)", "(novel)"))]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
