"""BOM chart title matching for theatre counts (2026-11-03).

The stopword overlap gave 'The Cat in the Hat' the theatre count of a film
already on the chart; predict.py's footprint factor would have scaled a wide
family opener as a 1,100-theatre release."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper  # noqa: E402

CHART = {
    "the only living pickpocket in new york": 1112,
    "clayface": 3458,
    "godzilla minus one": 2308,
    "jimmy and me": 400,
    "ramayana: rise of a legend": 950,
    "wild horse nine": 2100,
}


class BomTitleMatchTest(unittest.TestCase):
    def test_stopwords_do_not_match(self):
        self.assertIsNone(scraper.match_bom_chart_title("The Cat in the Hat", CHART))

    def test_exact_and_punctuation_insensitive(self):
        self.assertEqual(scraper.match_bom_chart_title("Clayface", CHART), ("clayface", 3458))
        self.assertEqual(scraper.match_bom_chart_title("Ramayana: Rise of A Legend", CHART)[1], 950)
        self.assertEqual(scraper.match_bom_chart_title("Wild Horse Nine", CHART)[1], 2100)

    def test_near_titles_are_not_confused(self):
        self.assertIsNone(scraper.match_bom_chart_title("Godzilla Minus Zero", CHART))
        self.assertIsNone(scraper.match_bom_chart_title("Jimmy", CHART))
        self.assertIsNone(scraper.match_bom_chart_title("Drummer Boy", CHART))

    def test_subtitle_variants_still_match(self):
        chart = {"avengers: doomsday": 4300, "the hunger games: sunrise on the reaping": 3900}
        self.assertEqual(scraper.match_bom_chart_title("Avengers Doomsday", chart)[1], 4300)
        self.assertEqual(scraper.match_bom_chart_title("The Hunger Games: Sunrise on the Reaping", chart)[1], 3900)
        self.assertIsNone(scraper.match_bom_chart_title("", chart))


if __name__ == "__main__":
    unittest.main()
