"""An ambiguous seat-map URL must not brick finalize forever.

Live failure 2026-08-09: one AMC showtime reported both "One Night Only" and
"Super Troopers 3". `clean_canonical_data` raised CanonicalDataError, the
finalize step has no continue-on-error and runs before the finalize guard, so
the whole job aborted and every merged row was discarded. The retry logic then
re-collected ~2,000 rows every hour and threw them all away again.

Pre-reservation rows are for FUTURE show dates, so the seat CSV — the only
source of a canonical URL->movie mapping — can never resolve a collision there.
The failure was therefore permanent, not transient.
"""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import clean_canonical_data as C  # noqa: E402

FIELDS = ["weekend_of", "show_date", "timezone", "movie_title",
          "amc_seat_map_url", "reserved_seats"]
COLLIDING_URL = "https://www.amctheatres.com/showtimes/144572999/seats"
CLEAN_URL = "https://www.amctheatres.com/showtimes/999/seats"


def _row(movie, url, seats="5"):
    return {"weekend_of": "2026-08-07", "show_date": "2026-08-09",
            "timezone": "ET", "movie_title": movie,
            "amc_seat_map_url": url, "reserved_seats": seats}


class QuarantineAmbiguousUrlTests(unittest.TestCase):
    def _write(self, tmpdir, rows):
        path = Path(tmpdir) / "pre-reservation-snapshots.csv"
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        return path

    def test_only_the_ambiguous_group_is_dropped(self):
        rows = [_row("One Night Only", COLLIDING_URL, "5"),
                _row("Super Troopers 3", COLLIDING_URL, "7"),
                _row("One Night Only", CLEAN_URL, "9")]
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, rows)
            res = C.clean_csv_file(path, date_col="show_date", check=False,
                                   quarantine_unresolved=True)
            self.assertEqual(2, res.stats.removed_ambiguous_url_rows)
            self.assertEqual(1, len(res.rows), "the unambiguous row must survive")
            self.assertEqual(CLEAN_URL, res.rows[0]["amc_seat_map_url"])

    def test_quarantine_does_not_raise(self):
        rows = [_row("One Night Only", COLLIDING_URL),
                _row("Super Troopers 3", COLLIDING_URL)]
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, rows)
            # must not raise — that is the whole point
            C.clean_csv_file(path, date_col="show_date", check=False,
                             quarantine_unresolved=True)

    def test_strict_mode_still_raises_for_audits(self):
        rows = [_row("One Night Only", COLLIDING_URL),
                _row("Super Troopers 3", COLLIDING_URL)]
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, rows)   # fresh file, never rewritten
            with self.assertRaises(C.CanonicalDataError):
                C.clean_csv_file(path, date_col="show_date", check=True,
                                 quarantine_unresolved=False)

    def test_clean_data_is_untouched(self):
        rows = [_row("One Night Only", CLEAN_URL, "9"),
                _row("One Night Only", COLLIDING_URL, "4")]
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, rows)
            res = C.clean_csv_file(path, date_col="show_date", check=False,
                                   quarantine_unresolved=True)
            self.assertEqual(0, res.stats.removed_ambiguous_url_rows)
            self.assertEqual(2, len(res.rows))

    def _data_dir(self, tmpdir, snapshot_rows, seat_rows=None):
        data = Path(tmpdir) / "data"
        data.mkdir()
        with (data / "pre-reservation-snapshots.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(snapshot_rows)
        seat_fields = ["weekend_of", "date", "timezone", "movie_title",
                       "amc_seat_map_url"]
        with (data / "seat-counts.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=seat_fields)
            w.writeheader()
            for r in (seat_rows or []):
                w.writerow(r)
        return Path(tmpdir)

    def test_real_cleaning_pass_survives_a_collision(self):
        """Behavioural: the configuration finalize actually runs must not raise."""
        rows = [_row("One Night Only", COLLIDING_URL),
                _row("Super Troopers 3", COLLIDING_URL)]
        with tempfile.TemporaryDirectory() as d:
            root = self._data_dir(d, rows)
            C.collect_stats(root, check=False)   # must not raise

    def test_audit_mode_still_raises_on_the_same_data(self):
        """--check is the audit path: an unresolvable collision must surface,
        not be reclassified as routine pending cleanup."""
        rows = [_row("One Night Only", COLLIDING_URL),
                _row("Super Troopers 3", COLLIDING_URL)]
        with tempfile.TemporaryDirectory() as d:
            root = self._data_dir(d, rows)
            with self.assertRaises(C.CanonicalDataError):
                C.collect_stats(root, check=True)

    def test_seat_lane_keeps_the_strict_raise(self):
        """Only the snapshot lane quarantines; seat collisions still hard-fail,
        because seat rows are post-showtime and can be resolved properly."""
        seat_rows = [{"weekend_of": "2026-08-07", "date": "2026-08-09",
                      "timezone": "ET", "movie_title": m,
                      "amc_seat_map_url": COLLIDING_URL}
                     for m in ("One Night Only", "Super Troopers 3")]
        with tempfile.TemporaryDirectory() as d:
            root = self._data_dir(d, [], seat_rows=seat_rows)
            with self.assertRaises(C.CanonicalDataError):
                C.collect_stats(root, check=False)


if __name__ == "__main__":
    unittest.main()
