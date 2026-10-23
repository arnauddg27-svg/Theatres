"""Small-film collection gate (2026-10-23)."""
import csv
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import small_film_gate as G  # noqa: E402
import scraper  # noqa: E402

FIELDS = ["logged_at", "weekend_of", "movie", "headline_mid_m", "forecast_stage"]


def write_log(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(dict(zip(FIELDS, r)))


class SmallFilmGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "prediction-log.csv")
        write_log(self.log, [
            ("2026-10-22T02:00:00Z", "2026-10-23", "Klara and the Sun", "1.43", "presales"),
            ("2026-10-23T08:59:00Z", "2026-10-23", "Klara and the Sun", "0.92", "after-previews"),
            ("2026-10-23T02:00:00Z", "2026-10-23", "A Talent for Murder", "0.54", "presales"),  # one call only
            ("2026-10-22T02:00:00Z", "2026-10-23", "Wicker", "1.20", "presales"),
            ("2026-10-23T08:59:00Z", "2026-10-23", "Wicker", "9.11", "after-previews"),     # recovered
            ("2026-10-23T08:59:00Z", "2026-10-23", "Ali G: Who Iz I?", "0", "presales"),    # no forecast
            ("2026-10-15T08:59:00Z", "2026-10-16", "Whalefall", "0.80", "presales"),
            ("2026-10-16T08:59:00Z", "2026-10-16", "Whalefall", "0.90", "presales"),
        ])
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        for k in ("SMALL_FILM_GATE", "SMALL_FILM_MIN_M", "SMALL_FILM_CONSECUTIVE"):
            os.environ.pop(k, None)
        G._REPORTED.clear()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_drops_only_after_consecutive_small_calls(self):
        self.assertEqual(G.dropped_titles("2026-10-23", path=self.log), {"klara and the sun": 0.92})

    def test_other_weekend_rows_do_not_leak(self):
        self.assertEqual(set(G.dropped_titles("2026-10-16", path=self.log)), {"whalefall"})
        self.assertEqual(G.dropped_titles("2026-10-30", path=self.log), {})

    def test_filter_keeps_order_and_unforecast_titles(self):
        titles = ["Clayface", "The Klara and the Sun", "Wicker", "Ali G: Who Iz I?"]
        self.assertEqual(G.filter_titles(titles, "2026-10-23", path=self.log),
                         ["Clayface", "Wicker", "Ali G: Who Iz I?"])

    def test_env_switches(self):
        os.environ["SMALL_FILM_GATE"] = "0"
        self.assertEqual(G.dropped_titles("2026-10-23", path=self.log), {})
        os.environ["SMALL_FILM_GATE"] = "1"
        os.environ["SMALL_FILM_CONSECUTIVE"] = "1"
        self.assertIn("talent for murder", G.dropped_titles("2026-10-23", path=self.log))
        os.environ["SMALL_FILM_MIN_M"] = "0.5"
        self.assertEqual(set(G.dropped_titles("2026-10-23", path=self.log)), set())

    def test_missing_log_keeps_everything(self):
        self.assertEqual(G.filter_titles(["A"], "2026-10-23", path=self.log + ".nope"), ["A"])

    def test_scraper_slate_is_filtered(self):
        with mock.patch.object(G, "PREDICTION_LOG", self.log), \
             mock.patch.object(scraper, "_select_collection_markets_base",
                               return_value=[{"movie_title": "Clayface"}, {"movie_title": "Klara and the Sun"}]), \
             mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=["Klara and the Sun", "Wildwood"]):
            markets = scraper.select_collection_markets([], None, "Phase 2", weekend_override="2026-10-23")
        self.assertEqual([m["movie_title"] for m in markets], ["Clayface", "Wildwood"])


if __name__ == "__main__":
    unittest.main()
