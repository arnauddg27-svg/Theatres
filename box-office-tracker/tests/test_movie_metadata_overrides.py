import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class MovieMetadataOverridesTest(unittest.TestCase):
    def test_godzilla_minus_zero_is_not_tagged_horror(self):
        # 2026-11-03 audit: BOM lists "Action / Drama / Horror / Sci-Fi /
        # Thriller" and the auto-fill picked horror, which would apply the
        # pure-horror pre-sales lift to a kaiju tentpole.
        import predict as P
        with open(ROOT / "data" / "movie-metadata.csv", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["movie"] == "Godzilla Minus Zero"]
        self.assertTrue(rows)
        for r in rows:
            self.assertNotIn(r["genre"].strip().lower(), P.HORROR_GENRES)
            self.assertEqual("fan_driven", r["audience_type"])


if __name__ == "__main__":
    unittest.main()
