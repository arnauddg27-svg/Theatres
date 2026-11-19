"""The finalize guard regenerates a forecast that has gone 6+ hours without one
(2026-11-19: blocked AMC legs merged nothing and the forecast step was skipped)."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import forecast_age_hours as fah  # noqa: E402

NOW = datetime(2026, 11, 19, 22, 0, tzinfo=timezone.utc)
WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "box-office-pipeline.yml"


def log(*stamps):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
    handle.write("logged_at,weekend_of,movie\n")
    for stamp in stamps:
        handle.write(f"{stamp},2026-11-20,Film\n")
    handle.close()
    return handle.name


class ForecastAgeTest(unittest.TestCase):
    def test_age_is_measured_from_the_newest_row(self):
        path = log("2026-11-19T07:22:10Z", "2026-11-19T08:14:23Z", "2026-11-18T16:33:40Z")
        self.assertEqual(13, fah.age_hours(path, now=NOW))

    def test_unreadable_or_empty_log_is_minus_one(self):
        self.assertEqual(-1, fah.age_hours("/nonexistent/prediction-log.csv", now=NOW))
        self.assertEqual(-1, fah.age_hours(log(), now=NOW))
        self.assertEqual(-1, fah.age_hours(log("not-a-date", ""), now=NOW))

    def test_a_future_stamp_is_zero_not_negative(self):
        self.assertEqual(0, fah.age_hours(log("2026-11-19T23:00:00Z"), now=NOW))

    def test_refresh_window(self):
        self.assertFalse(fah.refresh_due(-1))
        self.assertFalse(fah.refresh_due(5))
        self.assertTrue(fah.refresh_due(6))
        self.assertTrue(fah.refresh_due(72))
        self.assertFalse(fah.refresh_due(73))       # nothing is being forecast

    def test_the_guard_asks_before_it_skips(self):
        body = WORKFLOW.read_text()
        guard = body[body.index("- name: Finalize guard"):]
        guard = guard[:guard.index("echo \"needs_finalize=false\"")]
        self.assertIn("scripts/forecast_age_hours.py --due", guard)
        self.assertIn('if [ "$forecast_due" = "1" ]; then', guard)


if __name__ == "__main__":
    unittest.main()
