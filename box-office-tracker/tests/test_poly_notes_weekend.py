"""polymarket-markets.csv notes read "weekend_of=YYYY-MM-DD; settlement_rules=..."
since 2026-09-23. Three readers split on the first "=" and matched no weekend
(found 2026-11-05): predict.load_polymarket_data, scraper.load_movies_from_csv
and the capture_completeness side-data count."""
import csv
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import predict  # noqa: E402
import scraper  # noqa: E402

FIELDS = ["date", "movie_title", "market_url", "market_question", "market_id",
          "bracket_low", "bracket_high", "yes_price", "volume", "notes"]


def write_markets(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


ROWS = [
    {"date": "2026-11-05", "movie_title": "Ramayana: Rise of A Legend", "market_url": "u1",
     "market_question": "q1", "market_id": "m1", "yes_price": "0.4", "volume": "100",
     "notes": "weekend_of=2026-11-06; settlement_rules=Box Office Mojo domestic opening"},
    {"date": "2026-11-05", "movie_title": "Godzilla Minus Zero", "market_url": "u2",
     "market_question": "q2", "market_id": "m2", "yes_price": "0.3", "volume": "100",
     "notes": "weekend_of=2026-11-06"},                      # pre-09-23 format
    {"date": "2026-10-28", "movie_title": "Wildwood", "market_url": "u3",
     "market_question": "q3", "market_id": "m3", "yes_price": "0.5", "volume": "100",
     "notes": "weekend_of=2026-10-30; settlement_rules=x"},   # other weekend
]


class NotesWeekendTest(unittest.TestCase):
    def test_helper_reads_the_date_only(self):
        self.assertEqual(predict.weekend_from_notes("weekend_of=2026-11-06; settlement_rules=a=b"), "2026-11-06")
        self.assertEqual(predict.weekend_from_notes("weekend_of=2026-11-06"), "2026-11-06")
        self.assertEqual(predict.weekend_from_notes("settlement_rules=a"), "")
        self.assertEqual(predict.weekend_from_notes(None), "")

    def test_predict_loader_sees_rows_with_settlement_rules(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "polymarket-markets.csv")
            write_markets(p, ROWS)
            with mock.patch.object(predict, "POLY_CSV", p):
                data = predict.load_polymarket_data("2026-11-06")
        self.assertEqual(sorted(data), ["Godzilla Minus Zero", "Ramayana: Rise of A Legend"])

    def test_scraper_fallback_sees_rows_with_settlement_rules(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "polymarket-markets.csv"
            write_markets(p, ROWS)
            with mock.patch.object(scraper, "POLY_CSV", p):
                movies = scraper.load_movies_from_csv("2026-11-06")
        self.assertEqual(sorted(m["movie_title"] for m in movies),
                         ["Godzilla Minus Zero", "Ramayana: Rise of A Legend"])

    def test_completeness_side_data_counts_the_weekend(self):
        spec = importlib.util.spec_from_file_location("cc", ROOT / "scripts" / "capture_completeness.py")
        src = (ROOT / "scripts" / "capture_completeness.py").read_text()
        self.assertIn("P.weekend_from_notes(r.get(\"notes\"))", src)
        self.assertNotIn('notes.split("=", 1)', src)
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()
