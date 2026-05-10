import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "box-office-tracker" / "scripts" / "stage_finalize_outputs.py"


def run(cmd, cwd=None, check=True):
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


class StageFinalizeOutputsTest(unittest.TestCase):
    def _repo(self, root):
        repo = root / "repo"
        repo.mkdir()
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.name", "Test"], cwd=repo)
        run(["git", "config", "user.email", "test@example.com"], cwd=repo)
        data = repo / "box-office-tracker" / "data"
        data.mkdir(parents=True)
        (data / "seat-counts.csv").write_text("timezone,seats_sold\n")
        (data / "polymarket-markets.csv").write_text("date,market_id\n")
        run(["git", "add", "."], cwd=repo)
        run(["git", "commit", "-m", "init"], cwd=repo)
        return repo

    def test_stages_existing_files_one_by_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            summary = root / "summary.json"
            marker = root / "markers.txt"
            summary.write_text(json.dumps({"seat_added": 1, "pre_reservation_added": 0, "polymarket_added": 0}))
            marker.write_text("data: box office ET scrape\n")
            (repo / "box-office-tracker" / "data" / "seat-counts.csv").write_text(
                "timezone,seats_sold\nET,10\n"
            )

            run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--summary-file",
                    str(summary),
                    "--marker-file",
                    str(marker),
                ]
            )
            staged = run(["git", "diff", "--cached", "--name-only"], cwd=repo).stdout
            self.assertIn("box-office-tracker/data/seat-counts.csv", staged)

    def test_stages_seat_metadata_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            summary = root / "summary.json"
            marker = root / "markers.txt"
            summary.write_text(json.dumps({
                "seat_added": 0,
                "seat_metadata_updated": 1,
                "pre_reservation_added": 0,
                "polymarket_added": 0,
            }))
            marker.write_text("data: box office ET scrape\n")
            (repo / "box-office-tracker" / "data" / "seat-counts.csv").write_text(
                "timezone,seats_sold,notes\nET,10,showtime_window=sat-sun-10-23-v1\n"
            )

            run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--summary-file",
                    str(summary),
                    "--marker-file",
                    str(marker),
                ]
            )

            staged = run(["git", "diff", "--cached", "--name-only"], cwd=repo).stdout
            self.assertIn("box-office-tracker/data/seat-counts.csv", staged)

    def test_refuses_marker_only_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            summary = root / "summary.json"
            marker = root / "markers.txt"
            summary.write_text(json.dumps({"seat_added": 1, "pre_reservation_added": 0, "polymarket_added": 0}))
            marker.write_text("data: box office ET scrape\n")

            result = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--summary-file",
                    str(summary),
                    "--marker-file",
                    str(marker),
                ],
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("seat_added=1", result.stderr)


if __name__ == "__main__":
    unittest.main()
