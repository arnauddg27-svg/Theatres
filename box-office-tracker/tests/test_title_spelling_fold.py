"""One film, two punctuation spellings = one film (2026-11-26 audit).

Polymarket "Focker-In-Law" vs calendar "Focker In-Law": rows were stored under
both and the forecast read only the first spelling's 14 rows (73 dropped)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import predict  # noqa: E402
import scraper  # noqa: E402

HYPHEN = "Focker-In-Law"
SPACE = "Focker In-Law"


class PredictFoldTest(unittest.TestCase):
    def test_same_key_titles_merge_onto_larger_spelling(self):
        data = {
            HYPHEN: {"2026-11-26": [{"r": 1}]},
            SPACE: {"2026-11-26": [{"r": 2}, {"r": 3}], "2026-11-27": [{"r": 4}]},
            "Hexed": {"2026-11-26": [{"r": 5}]},
        }
        out = predict.fold_title_spellings(data)
        self.assertEqual(sorted(out), ["Focker In-Law", "Hexed"])
        self.assertEqual(len(out[SPACE]["2026-11-26"]), 3)
        self.assertEqual(len(out[SPACE]["2026-11-27"]), 1)
        self.assertNotIn(HYPHEN, predict.prediction_movie_names({}, out))

    def test_no_duplicates_returns_input_unchanged(self):
        data = {"Hexed": {"d": [1]}, "Hershey": {"d": [2]}}
        self.assertIs(predict.fold_title_spellings(data), data)


class MarketSameKeyTest(unittest.TestCase):
    def test_market_takes_calendar_spelling(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "title-aliases.json"
            with mock.patch.object(scraper, "TITLE_ALIASES_JSON", p), \
                 mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[SPACE, "Hexed"]), \
                 mock.patch.object(scraper, "market_matches_collection_weekend", return_value=True):
                out = scraper.canonicalise_market_titles(
                    [{"movie_title": HYPHEN}, {"movie_title": "Hexed"}], "2026-11-27", "Phase 2")
        self.assertEqual([m["movie_title"] for m in out], [SPACE, "Hexed"])
        self.assertEqual(out[0]["market_title"], HYPHEN)


if __name__ == "__main__":
    unittest.main()
