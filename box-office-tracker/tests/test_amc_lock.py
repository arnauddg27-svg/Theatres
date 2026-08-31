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


def _load_amc_lock_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("amc_lock_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LockStaleTest(unittest.TestCase):
    """The lock must never be broken while the holder might still be running."""

    def setUp(self):
        self.mod = _load_amc_lock_module()
        self.ttl = 600  # seconds
        # A lock created well past TTL but within the hard ceiling (3x TTL).
        self.over_ttl = {"created_at_epoch": __import__("time").time() - (self.ttl + 60),
                         "run_id": "999"}
        # A lock created past the hard ceiling.
        self.over_hard = {"created_at_epoch": __import__("time").time() - (self.ttl * 4),
                          "run_id": "999"}

    def _patch_probe(self, value):
        self.mod._github_run_is_active = lambda run_id: value

    def test_unreadable_payload_is_never_stale(self):
        # The lock commit lives on a branch actions/checkout never fetches, so
        # a failed `git show` is the NORMAL CI state, not an orphan. The old
        # code surfaced it as an empty payload, which read as an over-TTL
        # orphan — every lane instantly broke every other lane's LIVE lock.
        self._patch_probe(False)  # even a "dead holder" probe must not matter
        self.assertFalse(self.mod._lock_is_stale({"payload_unreadable": True}, self.ttl))

    def test_metadata_read_fetches_lock_object_from_remote(self):
        # Reproduce the CI shape end-to-end: the lock commit is pushed from a
        # throwaway temp repo, so it exists ONLY on the remote — never in the
        # reader's object store. _read_lock_metadata must fetch it and return
        # the real payload, not (sha, {}).
        import tempfile as _tf
        from pathlib import Path as _P
        with _tf.TemporaryDirectory() as tmp:
            root = _P(tmp)
            bare = root / "origin.git"
            repo = root / "repo"
            run(["git", "init", "--bare", str(bare)])
            run(["git", "clone", str(bare), str(repo)])
            run(["git", "config", "user.name", "Test"], cwd=repo)
            run(["git", "config", "user.email", "test@example.com"], cwd=repo)
            (repo / "README.md").write_text("test\n")
            run(["git", "add", "README.md"], cwd=repo)
            run(["git", "commit", "-m", "init"], cwd=repo)
            run(["git", "push", "origin", "HEAD:main"], cwd=repo)

            ok, sha = self.mod._create_lock_commit(
                repo, self.mod.LOCK_BRANCH,
                {"created_at_epoch": __import__("time").time(), "run_id": "42"},
            )
            self.assertTrue(ok, sha)
            # The reader's local store must not already contain the object.
            probe = run(["git", "cat-file", "-e", sha], cwd=repo, check=False)
            self.assertNotEqual(0, probe.returncode, "lock object unexpectedly local")

            got = self.mod._read_lock_metadata(repo, self.mod.LOCK_BRANCH)
            self.assertIsNotNone(got)
            got_sha, metadata = got
            self.assertEqual(sha, got_sha)
            self.assertEqual("42", metadata.get("run_id"))
            self.assertNotIn("payload_unreadable", metadata)
            # And a fresh, readable lock is held, not stale.
            self.assertFalse(self.mod._lock_is_stale(metadata, self.ttl))

    def test_api_failure_over_ttl_does_not_break_active_lock(self):
        # UNKNOWN (API unreachable) + age over TTL but under hard ceiling -> KEEP lock.
        self._patch_probe(self.mod.RUN_STATE_UNKNOWN)
        self.assertFalse(self.mod._lock_is_stale(self.over_ttl, self.ttl))

    def test_api_failure_over_hard_ceiling_breaks_lock(self):
        # UNKNOWN but age beyond the hard ceiling -> break as last-resort deadlock guard.
        self._patch_probe(self.mod.RUN_STATE_UNKNOWN)
        self.assertTrue(self.mod._lock_is_stale(self.over_hard, self.ttl))

    def test_confirmed_inactive_breaks_lock(self):
        # Run confirmed NOT active -> safe to break even just past TTL.
        self._patch_probe(False)
        self.assertTrue(self.mod._lock_is_stale(self.over_ttl, self.ttl))

    def test_confirmed_active_keeps_lock(self):
        # Run confirmed active -> never break, even past TTL.
        self._patch_probe(True)
        self.assertFalse(self.mod._lock_is_stale(self.over_ttl, self.ttl))

    def test_missing_run_id_breaks_orphan_at_ttl(self):
        # No run id recorded -> genuinely orphaned -> break once past TTL.
        self._patch_probe(None)
        orphan = {"created_at_epoch": __import__("time").time() - (self.ttl + 60),
                  "run_id": ""}
        self.assertTrue(self.mod._lock_is_stale(orphan, self.ttl))

    def test_self_leaked_lock_is_breakable_by_sibling_leg(self):
        """A lock held by MY OWN workflow run was leaked by an earlier leg.

        run_id is the WORKFLOW run id, shared by all three matrix legs. The
        liveness probe therefore reports "active" (that's me), so a leaked lock
        could never go stale: the remaining legs burned their full wait budget
        and failed, and it only became breakable once the whole run ended. The
        matrix is max-parallel: 1, so no sibling can hold it while I execute.
        """
        self._patch_probe(True)   # probe says active — it is seeing MY run
        self.assertTrue(
            self.mod._lock_is_stale(self.over_ttl, self.ttl, current_run_id="999"))

    def test_another_runs_active_lock_is_still_protected(self):
        # a DIFFERENT run that is genuinely active must never be broken
        self._patch_probe(True)
        self.assertFalse(
            self.mod._lock_is_stale(self.over_ttl, self.ttl, current_run_id="12345"))

    def test_self_leaked_lock_still_respects_ttl(self):
        # inside TTL the holder may legitimately still be working
        self._patch_probe(True)
        fresh = {"created_at_epoch": __import__("time").time() - 5, "run_id": "999"}
        self.assertFalse(
            self.mod._lock_is_stale(fresh, self.ttl, current_run_id="999"))

    def test_under_ttl_never_stale(self):
        self._patch_probe(self.mod.RUN_STATE_UNKNOWN)
        fresh = {"created_at_epoch": __import__("time").time() - 10, "run_id": "999"}
        self.assertFalse(self.mod._lock_is_stale(fresh, self.ttl))

    def test_probe_returns_unknown_on_api_failure(self):
        # When `gh` exits nonzero every attempt, the probe returns UNKNOWN (not None).
        calls = {"n": 0}

        def fake_run(cmd, capture=False, **kw):
            calls["n"] += 1
            return __import__("types").SimpleNamespace(returncode=1, stdout="", stderr="boom")

        self.mod._run = fake_run
        self.mod.AMC_LOCK_PROBE_ATTEMPTS = 2
        self.mod.AMC_LOCK_PROBE_BACKOFF_SEC = 0.0  # no real sleeping in tests
        self.assertEqual(self.mod.RUN_STATE_UNKNOWN, self.mod._github_run_is_active("999"))
        self.assertEqual(2, calls["n"])  # retried

    def test_probe_returns_none_for_missing_run_id(self):
        self.assertIsNone(self.mod._github_run_is_active(""))


if __name__ == "__main__":
    unittest.main()
