import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timezone

from scripts.scrape_dedup_guard import should_skip, slot_since


def run(cmd, cwd, check=True):
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)


class ScrapeDedupGuardTest(unittest.TestCase):
    def test_marker_only_commit_does_not_skip_but_data_commit_does(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            data_dir = repo / "box-office-tracker" / "data"
            data_dir.mkdir(parents=True)
            (data_dir / "seat-counts.csv").write_text("timezone,seats_sold\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            (repo / "marker-only.txt").write_text("marker\n")
            run(["git", "add", "marker-only.txt"], repo)
            run(["git", "commit", "-m", "data: box office ET scrape"], repo)

            self.assertFalse(
                should_skip(repo, "ET", force=False, snapshots_only=False, since="2000-01-01")
            )

            (data_dir / "seat-counts.csv").write_text("timezone,seats_sold\nET,10\n")
            run(["git", "add", "box-office-tracker/data/seat-counts.csv"], repo)
            run(["git", "commit", "-m", "data: box office ET scrape"], repo)

            self.assertTrue(
                should_skip(repo, "ET", force=False, snapshots_only=False, since="2000-01-01")
            )

    def test_slot_since_looks_back_to_the_slots_last_occurrence(self):
        now = datetime(2026, 9, 16, 1, 10, tzinfo=timezone.utc)      # 22:30Z retry, next day
        self.assertEqual("2026-09-15T22:30:00Z", slot_since("snapshot 22:30Z", now))
        self.assertEqual("2026-09-16T00:30:00Z", slot_since("snapshot 00:30Z", now))
        now = datetime(2026, 9, 16, 6, 10, tzinfo=timezone.utc)      # 02:30Z third retry
        self.assertEqual("2026-09-16T02:30:00Z", slot_since("snapshot 02:30Z", now))
        for other in ("", "amc bridge 17Z", "regal meter", "snapshot fandango 03Z", "scrape regular"):
            self.assertIsNone(slot_since(other, now), other)

    def test_snapshot_retry_skips_legs_that_already_committed_this_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            data_dir = repo / "box-office-tracker" / "data"
            data_dir.mkdir(parents=True)
            (data_dir / "pre-reservation-snapshots.csv").write_text("timezone\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)
            # ad-hoc snapshot run (no slot): never skipped, as before
            self.assertFalse(should_skip(repo, "ET", False, True, "2000-01-01", schedule_slot=""))
            # slot retry with nothing committed yet: runs
            self.assertFalse(should_skip(repo, "ET", False, True, "2000-01-01",
                                         schedule_slot="snapshot 22:30Z"))
            (data_dir / "pre-reservation-snapshots.csv").write_text("timezone\nET\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "data: box office scrape merge + predictions\n\n"
                 "data: box office ET pre-reservation snapshot"], repo)
            # ET landed: ET skips, CT (still missing) runs — the point of the change
            self.assertTrue(should_skip(repo, "ET", False, True, "2000-01-01",
                                        schedule_slot="snapshot 22:30Z"))
            self.assertFalse(should_skip(repo, "CT", False, True, "2000-01-01",
                                         schedule_slot="snapshot 22:30Z"))
            # a marker without the snapshot file does not count
            (repo / "note.txt").write_text("x")
            run(["git", "add", "note.txt"], repo)
            run(["git", "commit", "-m", "data: box office CT pre-reservation snapshot"], repo)
            self.assertFalse(should_skip(repo, "CT", False, True, "2000-01-01",
                                         schedule_slot="snapshot 22:30Z"))


if __name__ == "__main__":
    unittest.main()
