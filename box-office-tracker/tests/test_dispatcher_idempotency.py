import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "box-office-tracker" / "scripts" / "dispatch_box_office_pipeline.sh"


class DispatcherIdempotencyTest(unittest.TestCase):
    def test_duplicate_scrape_dispatch_in_same_window_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            state_dir = tmp_path / "state"
            calls_log = tmp_path / "gh-calls.log"
            bin_dir.mkdir()
            fake_gh = bin_dir / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                "if [ \"$1\" = \"api\" ]; then echo main; exit 0; fi\n"
                "echo \"$@\" >> \"$CALLS_LOG\"\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)

            env = os.environ.copy()
            env.update({
                "PATH": f"{bin_dir}:{env.get('PATH', '')}",
                "CALLS_LOG": str(calls_log),
                "DISPATCH_STATE_DIR": str(state_dir),
                "DISPATCH_DEDUP_WINDOW_SEC": "900",
                "GH_REPO": "owner/repo",
                "GH_TOKEN": "fake-token",
            })

            first = subprocess.run(
                ["bash", str(DISPATCHER), "scrape"],
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )
            second = subprocess.run(
                ["bash", str(DISPATCHER), "scrape"],
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )

            calls = calls_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(calls))
            self.assertIn("workflow run box-office-pipeline.yml --ref main", calls[0])
            self.assertIn("phase=scrape", calls[0])
            self.assertIn("snapshots_only=false", calls[0])
            self.assertIn("dispatch:", first.stdout)
            self.assertIn("recent dispatch already sent", second.stdout)

    def test_bad_github_token_fails_before_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            state_dir = tmp_path / "state"
            calls_log = tmp_path / "gh-calls.log"
            bin_dir.mkdir()
            fake_gh = bin_dir / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                "echo \"$@\" >> \"$CALLS_LOG\"\n"
                "if [ \"$1\" = \"api\" ]; then echo 'Bad credentials' >&2; exit 1; fi\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)

            env = os.environ.copy()
            env.update({
                "PATH": f"{bin_dir}:{env.get('PATH', '')}",
                "CALLS_LOG": str(calls_log),
                "DISPATCH_STATE_DIR": str(state_dir),
                "GH_REPO": "owner/repo",
                "GH_TOKEN": "bad-token",
            })

            result = subprocess.run(
                ["bash", str(DISPATCHER), "snapshot"],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("GitHub auth failed", result.stderr)
            self.assertIn("Actions: read/write", result.stderr)
            calls = calls_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(calls))
            self.assertIn("api repos/owner/repo", calls[0])
            self.assertFalse(any(state_dir.glob("*.stamp")))

    def test_env_file_token_is_exported_to_gh_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            state_dir = tmp_path / "state"
            calls_log = tmp_path / "gh-calls.log"
            token_file = tmp_path / ".env"
            bin_dir.mkdir()
            token_file.write_text("GH_TOKEN=fake-token-from-file\n", encoding="utf-8")
            fake_gh = bin_dir / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                "if [ -z \"$GH_TOKEN\" ]; then echo 'missing exported GH_TOKEN' >&2; exit 7; fi\n"
                "if [ \"$1\" = \"api\" ]; then echo main; exit 0; fi\n"
                "echo \"$@ token=$GH_TOKEN\" >> \"$CALLS_LOG\"\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)

            env = os.environ.copy()
            env.pop("GH_TOKEN", None)
            env.update({
                "PATH": f"{bin_dir}:{env.get('PATH', '')}",
                "CALLS_LOG": str(calls_log),
                "DISPATCH_STATE_DIR": str(state_dir),
                "GH_REPO": "owner/repo",
                "GH_TOKEN_FILE": str(token_file),
            })

            result = subprocess.run(
                ["bash", str(DISPATCHER), "snapshot"],
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )

            self.assertIn("dispatch:", result.stdout)
            calls = calls_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(calls))
            self.assertIn("workflow run box-office-pipeline.yml --ref main", calls[0])
            self.assertIn("token=fake-token-from-file", calls[0])


if __name__ == "__main__":
    unittest.main()
