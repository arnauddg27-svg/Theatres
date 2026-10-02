import csv
import gzip
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import rotate_lane_csv as R  # noqa: E402
import union_csv_rows as U  # noqa: E402

FIELDS = ["weekend_of", "show_date", "theatre_name", "reserved_seats"]


def write(path, rows, fields=FIELDS):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


class LaneRotationTest(unittest.TestCase):
    def test_keeps_newest_weekends_whole_and_archives_the_rest(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cinemark-pre-reservation-snapshots.csv")
            adir = os.path.join(d, "cinemark-archive")
            rows = [{"weekend_of": w, "show_date": w, "theatre_name": "T", "reserved_seats": "1"}
                    for w in ("2026-09-11", "2026-09-18", "2026-09-25", "2026-09-25")]
            write(p, rows)
            self.assertEqual(1, R.rotate(p, adir, keep=2))
            live = list(csv.DictReader(open(p)))
            self.assertEqual({"2026-09-18", "2026-09-25"}, {r["weekend_of"] for r in live})
            arch = os.path.join(adir, "cinemark-pre-reservation-snapshots-2026-09-11.csv.gz")
            self.assertEqual(1, len(list(csv.DictReader(gzip.open(arch, "rt")))))
            self.assertEqual(0, R.rotate(p, adir, keep=2))              # idempotent
            # a stale runner's union cannot re-import the archived weekend
            ours = os.path.join(d, "ours.csv")
            write(ours, rows + [{"weekend_of": "2026-09-25", "show_date": "2026-09-27",
                                 "theatre_name": "T2", "reserved_seats": "5"}])
            added = U.union_rows(ours, p, key=["weekend_of", "show_date", "theatre_name"],
                                 archived=U.archived_weekends(adir))
            self.assertEqual(1, added)                                   # only the new live row
            self.assertNotIn("2026-09-11", {r["weekend_of"] for r in csv.DictReader(open(p))})

    def test_never_cuts_mid_weekend(self):
        rows = [{"weekend_of": "2026-09-25", "show_date": s} for s in ("2026-09-24", "2026-09-27")]
        self.assertEqual(([], {"2026-09-25"}), R.plan(rows, keep=2))


class CrossChainArchiveTest(unittest.TestCase):
    def test_cross_chain_reads_rotated_weekend(self):
        import predict as P
        with tempfile.TemporaryDirectory() as d:
            old = (P.DATA_DIR, P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV)
            try:
                P.DATA_DIR = d
                P.FANDANGO_SNAPSHOTS_CSV = os.path.join(d, "fandango-pre-reservation-snapshots.csv")
                P.CINEMARK_SNAPSHOTS_CSV = os.path.join(d, "cinemark-pre-reservation-snapshots.csv")
                os.makedirs(os.path.join(d, "cinemark-archive"))
                with gzip.open(os.path.join(d, "cinemark-archive",
                                            "cinemark-pre-reservation-snapshots-2026-09-11.csv.gz"), "wt") as f:
                    f.write("weekend_of,movie_title\n2026-09-11,Film\n")
                opened = []
                real_gzip_open = P.gzip.open

                def spy(path, *a, **k):
                    opened.append(os.path.basename(path)); return real_gzip_open(path, *a, **k)
                P.gzip.open = spy
                P._CROSS_CHAIN_CACHE.clear()
                try:
                    P.load_cross_chain_occupancy(weekend_of="2026-09-11")
                except Exception:
                    pass   # the AMC side is absent here; we only assert the archive was read
                finally:
                    P.gzip.open = real_gzip_open
                self.assertIn("cinemark-pre-reservation-snapshots-2026-09-11.csv.gz", opened)
            finally:
                P.DATA_DIR, P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV = old
                P._CROSS_CHAIN_CACHE.clear()


if __name__ == "__main__":
    unittest.main()


class CommitLaneScriptTest(unittest.TestCase):
    """2026-10-02: lane commits share scripts/commit_lane.sh; loop jobs call it per pass."""

    def test_script_and_workflow_wiring(self):
        import subprocess
        root = ROOT.parent
        script = root / "box-office-tracker" / "scripts" / "commit_lane.sh"
        self.assertEqual(0, subprocess.run(["bash", "-n", str(script)]).returncode)
        yml = (root / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        for lane in ("alamo", "harkins", "webedia"):
            self.assertIn(f"commit_lane.sh {lane} box-office-tracker/data/{lane}-pre-reservation-snapshots.csv", yml)
        self.assertIn("ALAMO_LOOP_COMMIT: ${{ contains(github.event.inputs.schedule_slot, 'loop') && '1' || '0' }}", yml)
        import alamo_collect as A
        self.assertFalse(A.ALAMO_LOOP_COMMIT)      # off outside loop jobs
