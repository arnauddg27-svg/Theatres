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

    def test_leading_article_moves_to_end(self):
        # the-numbers convention, verified against stored history sources:
        # Dog-Stars-The-(2026), Odyssey-The-(2026), Devil-Wears-Prada-2-The-(2026)
        cands = T.slug_candidates("The Social Reckoning", 2026)
        self.assertTrue(cands[0].endswith("/Social-Reckoning-The-(2026)"))
        self.assertIn("https://www.the-numbers.com/movie/The-Social-Reckoning-(2026)", cands)
        self.assertTrue(T.slug_candidates("The Amazing Digital Circus: The Last Act", 2026)[0]
                        .endswith("/Amazing-Digital-Circus-The-The-Last-Act-(2026)"))
        self.assertTrue(T.slug_candidates("A Quiet Place", 2026)[0].endswith("/Quiet-Place-A-(2026)"))
        self.assertTrue(T.slug_candidates("Other Mommy", 2026)[0].endswith("/Other-Mommy-(2026)"))


class ChartResolvedSlugTests(unittest.TestCase):
    def test_country_suffixed_page_found_via_friday_chart(self):
        # 2026-10-28 audit: Fjord lives at Fjord-(2026-Norway); every guessed
        # slug 404s, so live daily actuals were never fetched for it.
        from unittest import mock
        good = "https://www.the-numbers.com/movie/Fjord-(2026-Norway)"
        page = ("<h2>Daily Box Office Performance</h2><table>"
                "<tr><td>Oct 30, 2026</td><td>9</td><td>$1,234,567</td></tr></table>")
        seen = []

        def fake_get(url):
            seen.append(url)
            if url != good:
                raise OSError("404")
            return page

        with mock.patch.object(T.C, "numbers_chart_movie_urls", return_value=[good]) as chart, \
                mock.patch.object(T, "_get", side_effect=fake_get):
            out = T.fetch_daily_table("Fjord", 2026, weekend_of="2026-10-30")
        chart.assert_called_once_with("Fjord", "2026-10-30")
        self.assertEqual(seen, [good])
        self.assertAlmostEqual(out[date(2026, 10, 30)][1], 1.234567)

    def test_without_weekend_only_guessed_slugs(self):
        from unittest import mock
        with mock.patch.object(T.C, "numbers_chart_movie_urls") as chart, \
                mock.patch.object(T, "_get", side_effect=OSError("404")):
            self.assertIsNone(T.fetch_daily_table("Fjord", 2026))
        chart.assert_not_called()


if __name__ == "__main__":
    unittest.main()
