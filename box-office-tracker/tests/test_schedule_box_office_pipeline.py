import datetime as dt
import importlib.util
import io
import os
import sys
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

        self.assertEqual(["snapshot 02:30Z"], [slot.name for _, slot in due])

    def test_snapshot_does_not_run_sunday_night_local_time(self):
        due = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-25T03:30:00Z"),
            lookback_minutes=75,
            mode="primary",
            fallback_grace_minutes=90,
        )

        self.assertNotIn("snapshot 02:30Z", [slot.name for _, slot in due])

    def test_watchdog_waits_for_grace_window_before_fallback_dispatch(self):
        too_early = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-24T03:30:00Z"),
            lookback_minutes=240,
            mode="watchdog",
            fallback_grace_minutes=90,
        )
        ready = schedule.candidate_due_slots(
            now=schedule.parse_utc("2026-05-24T04:00:00Z"),
            lookback_minutes=240,
            mode="watchdog",
            fallback_grace_minutes=90,
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
                "90",
            ])
        finally:
            schedule.GitHubClient = original_client
            if original_token is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = original_token

        self.assertEqual(1, result)


if __name__ == "__main__":
    unittest.main()
