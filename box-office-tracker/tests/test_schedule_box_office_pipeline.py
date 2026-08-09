import datetime as dt
import importlib.util
import io
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEDULER = ROOT / "box-office-tracker" / "scripts" / "schedule_box_office_pipeline.py"


spec = importlib.util.spec_from_file_location("schedule_box_office_pipeline", SCHEDULER)
schedule = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = schedule
spec.loader.exec_module(schedule)


class ScheduleBoxOfficePipelineTest(unittest.TestCase):
    def test_primary_catches_delayed_snapshot_tick_inside_lookback(self):
        due = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-24T03:30:00Z"),
            lookback_minutes=75,
            mode="primary",
            fallback_grace_minutes=90,
        )

        # Both late-night snapshot slots fall inside this lookback window: the
        # AMC snapshot at 02:30Z and the Fandango lane at 03:00Z (sorted by
        # scheduled_at).
        self.assertEqual(
            ["snapshot 02:30Z", "snapshot fandango 03Z"],
            [slot.name for _, slot in due],
        )

    def test_fandango_slot_dispatches_isolated_phase(self):
        slot = next(s for s in schedule.SLOTS if s.name == "snapshot fandango 03Z")
        self.assertEqual(slot.inputs["phase"], "scrape-fandango")
        self.assertEqual(slot.cron_days, frozenset({0, 4, 5, 6}))
        self.assertEqual((slot.hour, slot.minute), (3, 0))
        # It runs the same nights as the AMC snapshot.
        amc = next(s for s in schedule.SLOTS if s.name == "snapshot 02:30Z")
        self.assertEqual(slot.cron_days, amc.cron_days)

    def test_fandango_full_pool_plus_core_second_pass(self):
        fslots = [s for s in schedule.SLOTS if s.inputs.get("phase") == "scrape-fandango"]
        self.assertEqual(len(fslots), 12)
        self.assertTrue(all(s.inputs["fandango_num_shards"] == "6" for s in fslots))
        self.assertTrue(all(s.cron_days == frozenset({0, 4, 5, 6}) for s in fslots))
        by_hour = {s.hour: int(s.inputs["fandango_shard"]) for s in fslots}
        # 03-08Z cover all 6 shards once → the full ~320 pool per night
        self.assertEqual({h: by_hour[h] for h in range(3, 9)},
                         {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5})
        # 09-11Z re-run shards 0-2 → the core ~160 get a 2nd reading (velocity)
        self.assertEqual({h: by_hour[h] for h in range(9, 12)},
                         {9: 0, 10: 1, 11: 2})
        # 16-20Z afternoon near-showtime pass over the core, nearest-show-first
        # (like-for-like occupancy for the cross-chain share; family-gate data)
        self.assertEqual({h: by_hour[h] for h in (16, 18, 20)},
                         {16: 0, 18: 1, 20: 2})
        near = [s for s in fslots if s.hour in (16, 18, 20)]
        self.assertTrue(all(s.inputs.get("fandango_order") == "nearest" for s in near))
        others = [s for s in fslots if s.hour not in (16, 18, 20)]
        self.assertTrue(all("fandango_order" not in s.inputs for s in others))

    def test_snapshot_does_not_run_sunday_night_local_time(self):
        due = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-25T03:30:00Z"),
            lookback_minutes=75,
            mode="primary",
            fallback_grace_minutes=90,
        )

        self.assertNotIn("snapshot 02:30Z", [slot.name for _, slot in due])

    def test_watchdog_uses_short_grace_to_protect_snapshot_date_boundary(self):
        too_early = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-24T02:59:00Z"),
            lookback_minutes=240,
            mode="watchdog",
            fallback_grace_minutes=30,
        )
        ready = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-24T03:00:00Z"),
            lookback_minutes=240,
            mode="watchdog",
            fallback_grace_minutes=30,
        )

        self.assertEqual([], too_early)
        self.assertEqual(["snapshot 02:30Z"], [slot.name for _, slot in ready])

    def test_weekly_phase1_schedule_has_all_tuesday_and_wednesday_slots(self):
        due = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-27T23:30:00Z"),
            lookback_minutes=720,
            mode="primary",
            fallback_grace_minutes=90,
        )

        names = [slot.name for _, slot in due]
        self.assertIn("collect-links ET 13Z", names)
        self.assertIn("collect-links CT 15Z", names)
        self.assertIn("collect-links PT 17Z", names)
        self.assertIn("collect-links ET 19Z", names)
        self.assertIn("collect-links CT 21Z", names)
        self.assertIn("collect-links PT 23Z", names)

    def test_recent_pipeline_run_blocks_duplicate_watchdog_dispatch_for_legacy_title(self):
        parent = self

        class FakeClient:
            repo = "owner/repo"

            def request_json(self, method, path, body=None):
                parent.assertEqual("GET", method)
                parent.assertIn("box-office-pipeline.yml", path)
                return {
                    "workflow_runs": [
                        {
                            "display_title": "box office scrape snapshot",
                            "created_at": "2026-05-24T03:40:00Z",
                            "html_url": "https://example.test/run",
                        }
                    ]
                }

        exists = schedule.recent_pipeline_run_exists(
            client=FakeClient(),
            workflow="box-office-pipeline.yml",
            titles=("box office scheduled snapshot 02:30Z", "box office scrape snapshot"),
            scheduled_at=schedule.parse_utc("2026-05-24T02:30:00Z"),
            now=schedule.parse_utc("2026-05-24T04:00:00Z"),
        )

        self.assertTrue(exists)

    def _run_exists_with(self, run):
        class FakeClient:
            repo = "owner/repo"

            def request_json(self, method, path, body=None):
                return {"workflow_runs": [run]}

        return schedule.recent_pipeline_run_exists(
            client=FakeClient(),
            workflow="box-office-pipeline.yml",
            titles=("box office scheduled snapshot 02:30Z", "box office scrape snapshot"),
            scheduled_at=schedule.parse_utc("2026-05-24T02:30:00Z"),
            now=schedule.parse_utc("2026-05-24T04:00:00Z"),
        )

    def test_failed_run_does_not_consume_its_slot(self):
        # A leg that died in 30s (queue wall, lock timeout, stale links) used to
        # count as "slot serviced", so neither scheduler ever retried it and the
        # weekend's capture was lost. A failure must leave the slot due.
        base = {"display_title": "box office scrape snapshot",
                "created_at": "2026-05-24T02:35:00Z",
                "html_url": "https://example.test/run",
                "status": "completed"}
        for bad in ("failure", "cancelled", "timed_out", "startup_failure"):
            with self.subTest(conclusion=bad):
                self.assertFalse(self._run_exists_with(dict(base, conclusion=bad)))
        for ok in ("success", "skipped"):
            with self.subTest(conclusion=ok):
                self.assertTrue(self._run_exists_with(dict(base, conclusion=ok)))

    def _run_exists_with_many(self, runs):
        class FakeClient:
            repo = "owner/repo"

            def request_json(self, method, path, body=None):
                return {"workflow_runs": runs}

        return schedule.recent_pipeline_run_exists(
            client=FakeClient(),
            workflow="box-office-pipeline.yml",
            titles=("box office scheduled snapshot 02:30Z", "box office scrape snapshot"),
            scheduled_at=schedule.parse_utc("2026-05-24T02:30:00Z"),
            now=schedule.parse_utc("2026-05-24T04:00:00Z"),
        )

    def test_persistent_failure_stops_retrying(self):
        """Circuit breaker: retrying is right for a transient fault, wrong for a
        permanent one. An unresolvable seat-map collision failed the 22:30Z and
        02:30Z slots 8 times in one night, each run re-collecting ~2,000 rows
        and discarding them. After MAX_SLOT_RETRIES the slot must stop."""
        def failed(n):
            return [{"display_title": "box office scrape snapshot",
                     "created_at": "2026-05-24T02:35:00Z",
                     "html_url": f"https://example.test/run{i}",
                     "status": "completed", "conclusion": "failure"}
                    for i in range(n)]

        # under the limit -> still due, keep retrying
        self.assertFalse(self._run_exists_with_many(failed(schedule.MAX_SLOT_RETRIES - 1)))
        # at the limit -> stop re-dispatching
        self.assertTrue(self._run_exists_with_many(failed(schedule.MAX_SLOT_RETRIES)))

    def test_a_success_among_failures_still_holds_the_slot(self):
        runs = [{"display_title": "box office scrape snapshot",
                 "created_at": "2026-05-24T02:35:00Z",
                 "html_url": "https://example.test/ok",
                 "status": "completed", "conclusion": "success"}]
        runs += [{"display_title": "box office scrape snapshot",
                  "created_at": "2026-05-24T02:35:00Z",
                  "html_url": f"https://example.test/bad{i}",
                  "status": "completed", "conclusion": "failure"} for i in range(5)]
        self.assertTrue(self._run_exists_with_many(runs))

    def test_in_progress_run_still_holds_its_slot(self):
        # a run that is still going must NOT be duplicated
        self.assertTrue(self._run_exists_with({
            "display_title": "box office scrape snapshot",
            "created_at": "2026-05-24T02:35:00Z",
            "html_url": "https://example.test/run",
            "status": "in_progress", "conclusion": None}))

    def test_scheduled_dispatch_sends_slot_metadata(self):
        class FakeClient:
            repo = "owner/repo"

            def __init__(self):
                self.requests = []

            def request_json(self, method, path, body=None):
                self.requests.append((method, path, body))
                return {}

        client = FakeClient()
        slot = next(slot for slot in schedule.SLOTS if slot.name == "regular scrape 07Z")

        schedule.dispatch_slot(
            client=client,
            workflow="box-office-pipeline.yml",
            ref="main",
            slot=slot,
            mode="watchdog",
            dry_run=False,
        )

        self.assertEqual(1, len(client.requests))
        method, path, body = client.requests[0]
        self.assertEqual("POST", method)
        self.assertIn("/dispatches", path)
        self.assertEqual("main", body["ref"])
        self.assertEqual("regular scrape 07Z", body["inputs"]["schedule_slot"])
        self.assertEqual("watchdog", body["inputs"]["schedule_mode"])
        self.assertEqual("scrape", body["inputs"]["phase"])
        self.assertEqual("false", body["inputs"]["snapshots_only"])

    def test_cron_dow_matches_cron_sunday_zero(self):
        self.assertEqual(0, schedule.cron_dow(dt.datetime(2026, 5, 24, tzinfo=dt.timezone.utc)))
        self.assertEqual(3, schedule.cron_dow(dt.datetime(2026, 5, 27, tzinfo=dt.timezone.utc)))

    def test_main_returns_clean_failure_for_github_auth_error(self):
        original_client = schedule.GitHubClient
        original_token = os.environ.get("GITHUB_TOKEN")

        class FakeClient:
            def __init__(self, *, repo, token, api_url=schedule.API):
                self.repo = repo

            def request_json(self, method, path, body=None):
                raise urllib.error.HTTPError(
                    url="https://api.github.test",
                    code=401,
                    msg="Unauthorized",
                    hdrs={},
                    fp=io.BytesIO(b""),
                )

        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "dispatch-token-error.marker"
            try:
                os.environ["GITHUB_TOKEN"] = "fake-token"
                schedule.GitHubClient = FakeClient
                result = schedule.main([
                    "--mode",
                    "watchdog",
                    "--repo",
                    "owner/repo",
                    "--now",
                    "2026-05-24T04:00:00Z",
                    "--lookback-minutes",
                    "240",
                    "--fallback-grace-minutes",
                    "30",
                    "--token-error-marker",
                    str(marker),
                ])
            finally:
                schedule.GitHubClient = original_client
                if original_token is None:
                    os.environ.pop("GITHUB_TOKEN", None)
                else:
                    os.environ["GITHUB_TOKEN"] = original_token

            self.assertEqual(1, result)
            # A 401 must now leave a visible marker (was previously silent).
            self.assertTrue(marker.exists())
            self.assertIn("401", marker.read_text())

    def test_successful_dispatch_clears_stale_token_error_marker(self):
        original_client = schedule.GitHubClient
        original_token = os.environ.get("GITHUB_TOKEN")

        class FakeClient:
            def __init__(self, *, repo, token, api_url=schedule.API):
                self.repo = repo

            def request_json(self, method, path, body=None):
                # No prior runs -> not a duplicate; dispatch "succeeds".
                return {"workflow_runs": []}

        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "dispatch-token-error.marker"
            marker.write_text("stale token error from a previous run\n")
            try:
                os.environ["GITHUB_TOKEN"] = "fake-token"
                schedule.GitHubClient = FakeClient
                result = schedule.main([
                    "--mode", "watchdog", "--repo", "owner/repo",
                    "--now", "2026-05-24T04:00:00Z",
                    "--lookback-minutes", "240", "--fallback-grace-minutes", "30",
                    "--dry-run",
                    "--token-error-marker", str(marker),
                ])
            finally:
                schedule.GitHubClient = original_client
                if original_token is None:
                    os.environ.pop("GITHUB_TOKEN", None)
                else:
                    os.environ["GITHUB_TOKEN"] = original_token

            self.assertEqual(0, result)
            self.assertFalse(marker.exists())  # cleared on a working token


if __name__ == "__main__":
    unittest.main()
