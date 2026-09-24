"""Size-capped rotation of the live snapshot CSV (2026-09-24: four finalize
pushes were rejected at GitHub's 100MB limit with two weekends kept)."""
import csv
import gzip
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import predict as P  # noqa: E402
import rotate_pre_reservation_snapshots as R  # noqa: E402

FIELDS = ["weekend_of", "run_id", "snapshot_time", "snapshot_bucket", "show_date", "day_of_week",
          "theatre_name", "theatre_city", "timezone", "movie_title", "showtime", "showtime_id",
          "minutes_until_showtime", "auditorium_name", "auditorium_type", "total_seats",
          "reserved_seats", "available_seats", "occupancy_pct", "delta_reserved_since_previous",
          "amc_seat_map_url", "notes"]


def row(weekend, show_date, snap, theatre="AMC Test 1", sid="1", pad=200):
    return {"weekend_of": weekend, "run_id": "r", "snapshot_time": snap, "snapshot_bucket": "b",
            "show_date": show_date, "day_of_week": "x", "theatre_name": theatre, "theatre_city": "c",
            "timezone": "America/New_York", "movie_title": "Film", "showtime": "7:00pm",
            "showtime_id": sid, "minutes_until_showtime": "100", "auditorium_name": "a",
            "auditorium_type": "t", "total_seats": "100", "reserved_seats": "10",
            "available_seats": "90", "occupancy_pct": "10", "delta_reserved_since_previous": "",
            "amc_seat_map_url": "u", "notes": "x" * pad}


class RotationPlanTest(unittest.TestCase):
    NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)   # Saturday noon UTC

    def rows(self):
        out = []
        for i in range(10):
            out.append(row("2026-09-18", "2026-09-19", f"2026-09-18T1{i}", sid=f"a{i}"))
        for d in ("2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27"):
            for i in range(10):
                out.append(row("2026-09-25", d, f"2026-09-2{i % 4}T12", sid=f"{d}-{i}"))
        return out

    def test_keep_two_under_cap_archives_nothing_kept(self):
        rows = self.rows()
        archive, keep, notes = R.plan(rows, size_before=50 * 1000, keep=2, max_bytes=10 ** 9, now_utc=self.NOW)
        self.assertEqual({"2026-09-18", "2026-09-25"}, keep)
        self.assertEqual({}, {w: v for w, v in archive.items() if v})

    def test_over_cap_drops_older_kept_weekend_first(self):
        rows = self.rows()                      # 50 rows at 1000 B/row = 50 KB
        archive, keep, notes = R.plan(rows, size_before=50_000, keep=2, max_bytes=45_000, now_utc=self.NOW)
        self.assertEqual({"2026-09-25"}, keep)
        self.assertEqual(10, len(archive["2026-09-18"]))
        self.assertNotIn("2026-09-25", archive)   # 40 rows = 40 KB fits; no played rows touched

    def test_single_weekend_over_cap_archives_only_played_dates(self):
        rows = self.rows()
        archive, keep, notes = R.plan(rows, size_before=50_000, keep=2, max_bytes=25_000, now_utc=self.NOW)
        self.assertEqual({"2026-09-25"}, keep)
        played = archive["2026-09-25"]
        # Saturday 12Z minus 10h = Saturday 02Z -> cutoff 2026-09-26: Thu + Fri played, Sat/Sun stay
        self.assertEqual(20, len(played))
        self.assertTrue(all(rows[i]["show_date"] < "2026-09-26" for i in played))
        self.assertTrue(any("played rows" in n for n in notes))

    def test_played_cutoff_never_includes_a_date_still_showing(self):
        # 05Z Thursday is 01:00 ET / 22:00 PT Wednesday: Wednesday must NOT count as played
        self.assertEqual("2026-09-23", R.played_cutoff(datetime(2026, 9, 24, 5, 0, tzinfo=timezone.utc)))
        # 10Z Thursday: every Wednesday show is over
        self.assertEqual("2026-09-24", R.played_cutoff(datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)))


class RotationRoundTripTest(unittest.TestCase):
    def test_rotate_then_load_returns_every_row_once(self):
        with tempfile.TemporaryDirectory() as td:
            live = os.path.join(td, "live.csv"); adir = os.path.join(td, "arch")
            rows = RotationPlanTest().rows()
            with open(live, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
            path_fn = lambda wk: os.path.join(adir, f"pre-reservation-snapshots-{wk}.csv.gz")
            saved = (P.PRE_RESERVATION_CSV, P.PRE_RESERVATION_ARCHIVE_DIR, P._pre_reservation_archive_path)
            P.PRE_RESERVATION_CSV, P.PRE_RESERVATION_ARCHIVE_DIR, P._pre_reservation_archive_path = live, adir, path_fn
            try:
                cap = int(os.path.getsize(live) * 0.5)   # forces: drop 09-18, then Thu+Fri of 09-25
                R.rotate(keep=2, path=live, archive_dir=adir, archive_path_fn=path_fn,
                         max_bytes=cap, now_utc=RotationPlanTest.NOW)
                with open(live) as f:
                    kept = list(csv.DictReader(f))
                self.assertEqual(20, len(kept))                       # Sat + Sun of 09-25 only
                with gzip.open(path_fn("2026-09-25"), "rt") as f:
                    arch = list(csv.DictReader(f))
                self.assertEqual(20, len(arch))                       # Thu + Fri of 09-25
                # the loader stitches live + archive back together, once each
                orig_allows = P.model_allows_theatre
                P.model_allows_theatre = lambda *a, **k: True
                try:
                    data = P.load_pre_reservation_data(weekend_of="2026-09-25")
                finally:
                    P.model_allows_theatre = orig_allows
                n = sum(len(v) for v in data["Film"].values())
                self.assertEqual(40, n)
                self.assertEqual({"2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27"}, set(data["Film"]))
                # a re-appended archived row (late artifact merge) is not double counted
                with open(live, "a", newline="") as f:
                    csv.DictWriter(f, fieldnames=FIELDS).writerow(arch[0])
                P.model_allows_theatre = lambda *a, **k: True
                try:
                    data = P.load_pre_reservation_data(weekend_of="2026-09-25")
                finally:
                    P.model_allows_theatre = orig_allows
                self.assertEqual(40, sum(len(v) for v in data["Film"].values()))
                # idempotent: a second rotation is a no-op
                R.rotate(keep=2, path=live, archive_dir=adir, archive_path_fn=path_fn,
                         max_bytes=cap, now_utc=RotationPlanTest.NOW)
                with open(live) as f:
                    self.assertEqual(21, len(list(csv.DictReader(f))))   # 20 + the appended dup, all unplayed or dup
            finally:
                P.PRE_RESERVATION_CSV, P.PRE_RESERVATION_ARCHIVE_DIR, P._pre_reservation_archive_path = saved


if __name__ == "__main__":
    unittest.main()
