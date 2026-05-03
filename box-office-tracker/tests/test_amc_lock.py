import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "box-office-tracker" / "scripts" / "amc_lock.py"


def run(cmd, cwd=None, check=True):
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


class AmcLockTest(unittest.TestCase):
    def test_acquire_and_release_lock_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bare = root / "origin.git"
            repo = root / "repo"
            output = root / "github-output.txt"

            run(["git", "init", "--bare", str(bare)])
            run(["git", "clone", str(bare), str(repo)])
            run(["git", "config", "user.name", "Test"], cwd=repo)
            run(["git", "config", "user.email", "test@example.com"], cwd=repo)
            (repo / "README.md").write_text("test\n")
            run(["git", "add", "README.md"], cwd=repo)
            run(["git", "commit", "-m", "init"], cwd=repo)
            run(["git", "push", "origin", "HEAD:main"], cwd=repo)

            run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "acquire",
                    "--repo-root",
                    str(repo),
                    "--mode",
                    "test",
                    "--run-id",
                    "123",
                    "--wait-seconds",
                    "1",
                    "--poll-seconds",
                    "1",
                    "--github-output",
                    str(output),
                ]
            )
            values = dict(
                line.split("=", 1)
                for line in output.read_text().splitlines()
                if "=" in line
            )
            self.assertEqual("true", values["acquired"])
            lock_sha = values["lock_sha"]
            refs = run(["git", "ls-remote", "--heads", "origin", "refs/heads/box-office-amc-lock"], cwd=repo)
            self.assertIn("refs/heads/box-office-amc-lock", refs.stdout)

            run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "release",
                    "--repo-root",
                    str(repo),
                    "--lock-sha",
                    lock_sha,
                ]
            )
            refs = run(["git", "ls-remote", "--heads", "origin", "refs/heads/box-office-amc-lock"], cwd=repo)
            self.assertEqual("", refs.stdout.strip())


if __name__ == "__main__":
    unittest.main()
