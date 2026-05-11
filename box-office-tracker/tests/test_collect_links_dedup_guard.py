import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.collect_links_dedup_guard import should_skip  # noqa: E402


def run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=True,
    )


class CollectLinksDedupGuardTest(unittest.TestCase):
    def test_marker_only_commit_does_not_skip_but_link_data_commit_does(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            data_dir = repo / "box-office-tracker" / "data"
            data_dir.mkdir(parents=True)
            (repo / "README.md").write_text("init\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            (repo / "marker-only.txt").write_text("marker\n")
            run(["git", "add", "marker-only.txt"], repo)
            run(["git", "commit", "-m", "data: box office ET collect-links"], repo)

            self.assertFalse(should_skip(repo, "ET", False, "2000-01-01"))

            (data_dir / "showtime-links.json").write_text('{"theatres": {}}\n')
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office ET collect-links"], repo)

            self.assertTrue(should_skip(repo, "ET", False, "2000-01-01"))

    def test_force_bypasses_collect_links_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            self.assertFalse(should_skip(repo, "ET", True, "2000-01-01"))


if __name__ == "__main__":
    unittest.main()
