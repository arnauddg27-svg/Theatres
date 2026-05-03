import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.scrape_dedup_guard import should_skip


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


if __name__ == "__main__":
    unittest.main()
