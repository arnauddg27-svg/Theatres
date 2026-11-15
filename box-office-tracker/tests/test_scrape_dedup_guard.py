import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timezone

from scripts.scrape_dedup_guard import (
    find_run_with_leg_done,
    find_succeeded_twin,
    leg_already_done,
    should_skip,
    slot_since,
    twin_already_succeeded,
)


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


class TwinRunGuardTest(unittest.TestCase):
    """2026-11-14: watchdog + scheduler both dispatched snapshot 02:30Z 4 s
    apart; the force=true twin re-scraped for 3 h and starved the 07Z ET
    post-show leg."""

    TITLE = "box office scheduled snapshot 02:30Z"

    def _run(self, rid, created, conclusion="success", title=TITLE, status="completed"):
        return {"id": rid, "display_title": title, "created_at": created,
                "status": status, "conclusion": conclusion, "workflow_id": 7}

    def test_twin_of_successful_run_is_found(self):
        me = self._run(2, "2026-11-14T02:37:38Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T02:37:34Z")
        self.assertEqual(first, find_succeeded_twin(me, [me, first]))

    def test_failed_twin_leaves_this_run_as_retry(self):
        me = self._run(2, "2026-11-14T02:50:00Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T02:37:34Z", "failure")
        self.assertIsNone(find_succeeded_twin(me, [me, first]))

    def test_other_slots_old_runs_and_manual_runs_ignored(self):
        me = self._run(5, "2026-11-14T02:37:38Z", None, status="in_progress")
        self.assertIsNone(find_succeeded_twin(me, [
            self._run(1, "2026-11-14T02:37:34Z", title="box office scheduled snapshot 22:30Z"),
            self._run(2, "2026-11-14T01:00:00Z"),          # outside window
            self._run(9, "2026-11-14T02:37:30Z"),          # newer id
        ]))
        manual = self._run(5, "2026-11-14T02:37:38Z", None, title="box office scrape snapshot")
        self.assertIsNone(find_succeeded_twin(manual, [self._run(1, "2026-11-14T02:37:34Z",
                                                                  title="box office scrape snapshot")]))

    def test_api_lookup_and_fail_open(self):
        me = self._run(2, "2026-11-14T02:37:38Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T02:37:34Z")
        env = {"GH_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "2"}

        def fetch(url, token):
            return me if url.endswith("/runs/2") else {"workflow_runs": [me, first]}

        self.assertEqual(first, twin_already_succeeded(env, fetch))
        self.assertIsNone(twin_already_succeeded({}, fetch))

        def boom(url, token):
            raise OSError("api down")

        self.assertIsNone(twin_already_succeeded(env, boom))

    def test_twin_skips_even_forced_snapshot_run(self):
        twin = self._run(1, "2026-11-14T02:37:34Z")
        self.assertTrue(should_skip(Path("."), "ET", force=True, snapshots_only=True,
                                    since="2000-01-01", schedule_slot="snapshot 02:30Z",
                                    twin_check=lambda: twin))
        self.assertFalse(should_skip(Path("."), "ET", force=True, snapshots_only=True,
                                     since="2000-01-01", schedule_slot="snapshot 02:30Z",
                                     twin_check=lambda: None))


class RetryLegTest(unittest.TestCase):
    """2026-11-15: the retry of snapshot 22:30Z (PT leg failed) re-scraped ET,
    CT and MT for 2 h 20 min under the AMC lock before reaching PT."""

    TITLE = "box office scheduled snapshot 22:30Z"

    def _run(self, rid, created, conclusion="failure", title=TITLE, status="completed"):
        return {"id": rid, "display_title": title, "created_at": created,
                "status": status, "conclusion": conclusion, "workflow_id": 7}

    JOBS = {1: [{"name": "scrape (ET)", "conclusion": "success"}, {"name": "scrape (CT)", "conclusion": "success"},
                {"name": "scrape (MT)", "conclusion": "success"}, {"name": "scrape (PT)", "conclusion": "failure"},
                {"name": "finalize", "conclusion": "success"}]}

    def test_only_the_failed_leg_reruns(self):
        me = self._run(2, "2026-11-15T01:07:12Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T22:37:41Z")
        for tz, want in (("ET", first), ("CT", first), ("MT", first), ("PT", None)):
            self.assertEqual(want, find_run_with_leg_done(tz, me, [me, first], self.JOBS.__getitem__), tz)

    def test_leg_without_a_successful_finalize_reruns(self):
        me = self._run(2, "2026-11-15T01:07:12Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T22:37:41Z")
        jobs = [{"name": "scrape (ET)", "conclusion": "success"}, {"name": "finalize", "conclusion": "failure"}]
        self.assertIsNone(find_run_with_leg_done("ET", me, [me, first], lambda rid: jobs))

    def test_yesterdays_slot_other_slots_and_unfinished_runs_do_not_count(self):
        me = self._run(9, "2026-11-15T22:37:41Z", None, status="in_progress")
        ok = self.JOBS[1]
        self.assertIsNone(find_run_with_leg_done("ET", me, [
            self._run(1, "2026-11-14T22:37:41Z"),                                              # 24 h earlier
            self._run(2, "2026-11-15T22:30:00Z", title="box office scheduled snapshot 14:30Z"),
            self._run(3, "2026-11-15T22:37:00Z", None, status="in_progress"),
            self._run(12, "2026-11-15T22:37:00Z"),                                             # newer id
        ], lambda rid: ok))
        manual = self._run(9, "2026-11-15T22:37:41Z", None, title="box office scrape snapshot")
        self.assertIsNone(find_run_with_leg_done("ET", manual, [self._run(1, "2026-11-15T22:00:00Z",
                                                                         title="box office scrape snapshot")],
                                                 lambda rid: ok))

    def test_api_lookup_and_fail_open(self):
        me = self._run(2, "2026-11-15T01:07:12Z", None, status="in_progress")
        first = self._run(1, "2026-11-14T22:37:41Z")
        env = {"GH_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "2"}

        def fetch(url, token):
            if url.endswith("/runs/2"):
                return me
            if "/runs/1/jobs" in url:
                return {"jobs": self.JOBS[1]}
            return {"workflow_runs": [me, first]}

        self.assertEqual(first, leg_already_done("ET", env, fetch))
        self.assertIsNone(leg_already_done("PT", env, fetch))
        self.assertIsNone(leg_already_done("ET", {}, fetch))

        def boom(url, token):
            raise OSError("api down")

        self.assertIsNone(leg_already_done("ET", env, boom))

    def test_done_leg_skips_even_when_forced(self):
        first = self._run(1, "2026-11-14T22:37:41Z")
        kw = dict(force=True, snapshots_only=True, since="2000-01-01", schedule_slot="snapshot 22:30Z",
                  twin_check=lambda: None)
        self.assertTrue(should_skip(Path("."), "ET", leg_check=lambda tz: first, **kw))
        self.assertFalse(should_skip(Path("."), "PT", leg_check=lambda tz: None, **kw))




class OnlyTzTest(unittest.TestCase):
    """A top-up dispatch names its zones in tz_group; the other legs skip."""

    def test_scheduled_scrapes_run_every_leg(self):
        from scripts.scrape_dedup_guard import excluded_by_only_tz
        for value in ("ALL", "", "all", " ALL "):
            for tz in ("ET", "CT", "MT", "PT"):
                self.assertFalse(excluded_by_only_tz(tz, value))

    def test_top_up_runs_only_the_named_zones(self):
        from scripts.scrape_dedup_guard import excluded_by_only_tz
        self.assertFalse(excluded_by_only_tz("CT", "CT,MT"))
        self.assertFalse(excluded_by_only_tz("MT", "ct, mt"))
        self.assertTrue(excluded_by_only_tz("ET", "CT,MT"))
        self.assertTrue(excluded_by_only_tz("PT", "CT,MT"))


class FailedLegRetryTest(unittest.TestCase):
    """A regular leg that failed after adding rows leaves a marker; its retry
    must still run (2026-11-15)."""

    THIS = {"id": 30, "display_title": "box office scheduled regular scrape 07Z",
            "created_at": "2026-11-15T10:10:00Z"}

    def _runs(self):
        return [
            dict(self.THIS),
            {"id": 20, "display_title": self.THIS["display_title"], "status": "completed",
             "conclusion": "failure", "created_at": "2026-11-15T07:04:00Z"},
            {"id": 10, "display_title": "box office scheduled snapshot 02:30Z", "status": "completed",
             "conclusion": "failure", "created_at": "2026-11-15T02:37:00Z"},
        ]

    def _jobs(self, run_id):
        return {
            20: [{"name": "scrape (ET)", "conclusion": "success"},
                 {"name": "scrape (CT)", "conclusion": "failure"},
                 {"name": "finalize", "conclusion": "success"}],
            10: [{"name": "scrape (ET)", "conclusion": "failure"}],
        }[run_id]

    def test_finds_the_failed_leg_of_the_same_slot(self):
        from scripts.scrape_dedup_guard import find_run_with_leg_failed
        self.assertEqual(find_run_with_leg_failed("CT", self.THIS, self._runs(), self._jobs)["id"], 20)

    def test_a_leg_that_succeeded_is_not_a_retry(self):
        from scripts.scrape_dedup_guard import find_run_with_leg_failed
        self.assertIsNone(find_run_with_leg_failed("ET", self.THIS, self._runs(), self._jobs))

    def test_manual_runs_are_left_to_the_marker_check(self):
        from scripts.scrape_dedup_guard import find_run_with_leg_failed
        manual = dict(self.THIS, display_title="box office scrape regular")
        self.assertIsNone(find_run_with_leg_failed("CT", manual, self._runs(), self._jobs))

    def test_failed_leg_overrides_the_marker_skip(self):
        import scripts.scrape_dedup_guard as guard
        original = (guard._marker_commits, guard._commit_changed_path)
        guard._marker_commits = lambda *a, **k: ["abc123"]
        guard._commit_changed_path = lambda *a, **k: True
        self.addCleanup(lambda: (setattr(guard, "_marker_commits", original[0]),
                                 setattr(guard, "_commit_changed_path", original[1])))
        common = dict(twin_check=lambda: None, leg_check=lambda tz: None)
        self.assertFalse(guard.should_skip(Path("."), "CT", False, False, "2026-11-15",
                                           failed_check=lambda tz: {"id": 20}, **common))
        self.assertTrue(guard.should_skip(Path("."), "CT", False, False, "2026-11-15",
                                          failed_check=lambda tz: None, **common))


if __name__ == "__main__":
    unittest.main()
