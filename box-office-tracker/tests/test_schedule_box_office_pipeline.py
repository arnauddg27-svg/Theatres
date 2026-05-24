import datetime as dt
import importlib.util
import sys
import unittest
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

    def test_recent_pipeline_run_blocks_duplicate_watchdog_dispatch(self):
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
            title="box office scrape snapshot",
            scheduled_at=schedule.parse_utc("2026-05-24T02:30:00Z"),
            now=schedule.parse_utc("2026-05-24T04:00:00Z"),
        )

        self.assertTrue(exists)

    def test_cron_dow_matches_cron_sunday_zero(self):
        self.assertEqual(0, schedule.cron_dow(dt.datetime(2026, 5, 24, tzinfo=dt.timezone.utc)))
        self.assertEqual(3, schedule.cron_dow(dt.datetime(2026, 5, 27, tzinfo=dt.timezone.utc)))


if __name__ == "__main__":
    unittest.main()
