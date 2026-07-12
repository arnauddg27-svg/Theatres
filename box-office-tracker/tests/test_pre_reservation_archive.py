import csv
import gzip
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402

FIELDS = ["weekend_of", "movie_title", "show_date", "snapshot_time",
          "theatre_name", "reserved_seats"]


def _rows(weekend, movie, n):
    return [{"weekend_of": weekend, "movie_title": movie,
             "show_date": weekend, "snapshot_time": f"{weekend}T03:00:00Z",
             "theatre_name": "AMC Test 1", "reserved_seats": str(i)}
            for i in range(n)]


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _write_gz(path, rows):
    with gzip.open(path, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


class ArchiveLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.orig = (P.PRE_RESERVATION_CSV, P.PRE_RESERVATION_ARCHIVE_DIR)
        P.PRE_RESERVATION_CSV = os.path.join(self.tmp.name, "live.csv")
        P.PRE_RESERVATION_ARCHIVE_DIR = os.path.join(self.tmp.name, "archive")
        os.makedirs(P.PRE_RESERVATION_ARCHIVE_DIR)
        # allow the test theatre through the cohort gate
        self.orig_allow = P.model_allows_theatre
        P.model_allows_theatre = lambda *a, **k: True

    def tearDown(self):
        P.PRE_RESERVATION_CSV, P.PRE_RESERVATION_ARCHIVE_DIR = self.orig
        P.model_allows_theatre = self.orig_allow
        self.tmp.cleanup()

    def test_archived_weekend_is_read_transparently(self):
        _write_csv(P.PRE_RESERVATION_CSV, _rows("2026-07-10", "New Film", 3))
        _write_gz(P._pre_reservation_archive_path("2026-06-19"),
                  _rows("2026-06-19", "Old Film", 5))
        old = P.load_pre_reservation_data(weekend_of="2026-06-19")
        self.assertEqual(len(old["Old Film"]["2026-06-19"]), 5)
        new = P.load_pre_reservation_data(weekend_of="2026-07-10")
        self.assertEqual(len(new["New Film"]["2026-07-10"]), 3)

    def test_live_and_archive_rows_merge_for_same_weekend(self):
        # mid-rotation state: some of a weekend archived, remainder still live
        _write_csv(P.PRE_RESERVATION_CSV, _rows("2026-06-19", "Old Film", 2))
        _write_gz(P._pre_reservation_archive_path("2026-06-19"),
                  _rows("2026-06-19", "Old Film", 5))
        data = P.load_pre_reservation_data(weekend_of="2026-06-19")
        self.assertEqual(len(data["Old Film"]["2026-06-19"]), 7)

    def test_through_date_filter_applies_to_archive(self):
        rows = _rows("2026-06-19", "Old Film", 4)
        rows[0]["snapshot_time"] = "2026-06-20T03:00:00Z"   # after through
        _write_gz(P._pre_reservation_archive_path("2026-06-19"), rows)
        _write_csv(P.PRE_RESERVATION_CSV, [])
        data = P.load_pre_reservation_data(weekend_of="2026-06-19",
                                           through_date="2026-06-19")
        self.assertEqual(len(data["Old Film"]["2026-06-19"]), 3)

    def test_missing_everything_is_empty(self):
        os.remove_ = None
        P.PRE_RESERVATION_CSV = os.path.join(self.tmp.name, "absent.csv")
        self.assertEqual(P.load_pre_reservation_data(weekend_of="2026-01-02"), {})


class MoanaSlugTests(unittest.TestCase):
    def test_trailing_year_stripped(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import fandango_collect as fc
        # live miss 2026-07-10: 'Moana (2026)' slugged to 'moana-2026' but
        # Fandango's core slug is 'moana' -> zero rows all weekend
        self.assertEqual(fc.slugify_title("Moana (2026)"), "moana")
        self.assertEqual(
            fc.match_target_title("/moana-2026-245678/movie-overview",
                                  {fc.slugify_title("Moana (2026)"): "Moana (2026)"}),
            "Moana (2026)")
        # a year mid-title is NOT stripped
        self.assertEqual(fc.slugify_title("Blade Runner 2049"), "blade-runner-2049")


if __name__ == "__main__":
    unittest.main()
