"""Opening-weekend chart counts replace pre-release placeholders (2026-11-03)."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("sync_counts", ROOT / "scripts" / "sync_opening_theatre_counts.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def counts_file(td, updated, **counts):
    p = Path(td) / "theatre-counts.json"
    p.write_text(json.dumps({**counts, "_requested_movies": list(counts), "_updated": updated}))
    return p


class ChartCountsTest(unittest.TestCase):
    def test_thursday_preview_chart_is_not_an_opening_count(self):
        with tempfile.TemporaryDirectory() as td:
            weekend, counts = S.chart_counts(counts_file(td, "2026-11-06T03:40:00", **{"Godzilla Minus Zero": 2900}))
            self.assertEqual(weekend, "2026-11-06")
            self.assertEqual(counts, {})

    def test_saturday_and_sunday_charts_count(self):
        with tempfile.TemporaryDirectory() as td:
            for stamp in ("2026-11-07T07:10:00", "2026-11-08T15:08:00"):
                weekend, counts = S.chart_counts(counts_file(td, stamp, **{"Godzilla Minus Zero": 3412, "Jimmy": 2100}))
                self.assertEqual(weekend, "2026-11-06", stamp)
                self.assertEqual(counts, {"Godzilla Minus Zero": 3412, "Jimmy": 2100}, stamp)

    def test_unreadable_or_unstamped_file(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(S.chart_counts(Path(td) / "missing.json"), (None, {}))
            p = Path(td) / "t.json"
            p.write_text(json.dumps({"Jimmy": 2100}))
            self.assertEqual(S.chart_counts(p), (None, {}))


class SyncTest(unittest.TestCase):
    def rows(self):
        return [
            {"movie": "Sense and Sensibility", "weekend_of": "2026-10-16", "national_theatre_count": "705", "notes": "BOM auto-fill"},
            {"movie": "Street Fighter", "weekend_of": "2026-10-16", "national_theatre_count": "3575", "notes": ""},
            {"movie": "Whalefall", "weekend_of": "2026-10-16", "national_theatre_count": "", "notes": ""},
            {"movie": "Clayface", "weekend_of": "2026-10-23", "national_theatre_count": "", "notes": ""},
        ]

    def test_placeholder_and_blank_are_replaced_small_drift_kept(self):
        rows = self.rows()
        changes = S.sync(rows, "2026-10-16", {"Sense and Sensibility": 2545, "Street Fighter": 3540,
                                               "Whalefall": 3065, "Clayface": 3478}, today="2026-10-19")
        self.assertEqual(changes, [("Sense and Sensibility", "705", 2545), ("Whalefall", "-", 3065)])
        self.assertEqual(rows[0]["national_theatre_count"], "2545")
        self.assertIn("opening-weekend chart count 705->2545 (synced 2026-10-19)", rows[0]["notes"])
        self.assertEqual(rows[1]["national_theatre_count"], "3575")      # within 15%: untouched
        self.assertEqual(rows[3]["national_theatre_count"], "")          # other weekend: untouched

    def test_no_counts_is_a_no_op(self):
        rows = self.rows()
        self.assertEqual(S.sync(rows, "2026-10-16", {}), [])
        self.assertEqual(S.sync(rows, None, {"Whalefall": 3065}), [])
        self.assertEqual(rows[2]["national_theatre_count"], "")


class WorkflowWiringTest(unittest.TestCase):
    def test_finalize_runs_the_sync_after_the_filler(self):
        text = (ROOT.parent / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        fill = text.index("fill_movie_metadata.py --tracked --write")
        sync = text.index("sync_opening_theatre_counts.py --write")
        predict = text.index("name: Generate predictions")
        self.assertTrue(fill < sync < predict)


if __name__ == "__main__":
    unittest.main()
