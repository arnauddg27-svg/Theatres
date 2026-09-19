"""discovered_showtimes / unavailable / row kind used to live only in free-text
notes (parsed in eight places). They are columns now; notes stays for old readers."""
import csv, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fandango_collect as fc  # noqa: E402
import predict as P  # noqa: E402


class NoteFieldsTest(unittest.TestCase):
    def test_parses_every_legacy_shape(self):
        self.assertEqual({"discovered_showtimes": "3", "unavailable_seats": "", "row_kind": "amc-bridge"},
                         fc.note_fields("amc-bridge; discovered_showtimes=3"))
        self.assertEqual({"discovered_showtimes": "5", "unavailable_seats": "24", "row_kind": "post-show-census"},
                         fc.note_fields("cinemark-direct; post-show-census; discovered_showtimes=5; unavailable=24"))
        self.assertEqual({"discovered_showtimes": "2", "unavailable_seats": "", "row_kind": ""},
                         fc.note_fields("discovered_showtimes=2"))
        self.assertEqual({"discovered_showtimes": "", "unavailable_seats": "", "row_kind": ""}, fc.note_fields(""))

    def test_schema_carries_the_columns_and_writer_fills_them(self):
        for c in ("discovered_showtimes", "unavailable_seats", "row_kind"):
            self.assertIn(c, fc.FANDANGO_PRE_RESERVATION_FIELDS)
        row = fc.build_fandango_row({"name": "Regal X", "timezone": "America/New_York"}, "F", "2026-09-18T19:00:00",
                                    "https://x/seats", {"chain": "REGL"}, {"total": 100, "reserved": 10},
                                    "2026-09-18", "r", "2026-09-17T12:00:00Z", 1860, "2026-09-18", "Friday",
                                    note="amc-bridge; discovered_showtimes=4")
        self.assertEqual(("4", "amc-bridge"), (row["discovered_showtimes"], row["row_kind"]))
        self.assertEqual(set(fc.FANDANGO_PRE_RESERVATION_FIELDS), set(row))

    def test_migrate_header_adds_columns_and_backfills_from_notes(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.csv"
            old_fields = [f for f in fc.FANDANGO_PRE_RESERVATION_FIELDS if f not in fc.STRUCTURED_NOTE_FIELDS]
            with open(p, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=old_fields); w.writeheader()
                w.writerow({k: "" for k in old_fields} | {"movie_title": "F", "notes": "cinemark-direct; discovered_showtimes=7; unavailable=9", "chain": "CNMK"})
            self.assertTrue(fc.migrate_header(p, fc.FANDANGO_PRE_RESERVATION_FIELDS))
            rows = list(csv.DictReader(open(p)))
            self.assertEqual(fc.FANDANGO_PRE_RESERVATION_FIELDS, list(rows[0].keys()))
            self.assertEqual(("7", "9", "cinemark-direct"), (rows[0]["discovered_showtimes"], rows[0]["unavailable_seats"], rows[0]["row_kind"]))
            self.assertFalse(fc.migrate_header(p, fc.FANDANGO_PRE_RESERVATION_FIELDS), "idempotent")
            self.assertFalse(fc.migrate_header(Path(td) / "missing.csv", fc.FANDANGO_PRE_RESERVATION_FIELDS))

    def test_predict_prefers_columns_and_falls_back_to_notes(self):
        self.assertEqual(3, P._bridge_discovered_showings({"row_kind": "amc-bridge", "discovered_showtimes": "3", "notes": ""}))
        self.assertEqual(3, P._bridge_discovered_showings({"notes": "amc-bridge; discovered_showtimes=3"}))
        self.assertIsNone(P._bridge_discovered_showings({"row_kind": "cinemark-direct", "discovered_showtimes": "3", "notes": ""}))
