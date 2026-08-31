import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "fetch_daily_actuals", ROOT / "scripts" / "fetch_daily_actuals.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def _utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


class CompletedDaysTest(unittest.TestCase):
    """Day D becomes fetchable at D+1 13:00 UTC (The Numbers' next morning)."""

    def test_saturday_morning_has_thursday_and_friday(self):
        # Sat 2026-08-29 14:00Z: Thu (publishable Fri 13Z) and Fri (Sat 13Z).
        days = mod.completed_days("2026-08-28", _utc(2026, 8, 29, 14))
        self.assertEqual({"Thursday", "Friday"}, set(days))

    def test_saturday_before_publication_lacks_friday(self):
        days = mod.completed_days("2026-08-28", _utc(2026, 8, 29, 3, 10))
        self.assertEqual(["Thursday"], days)

    def test_monday_has_all_four(self):
        days = mod.completed_days("2026-08-28", _utc(2026, 8, 31, 14))
        self.assertEqual(4, len(days))

    def test_thursday_stage_has_none(self):
        self.assertEqual([], mod.completed_days("2026-08-28", _utc(2026, 8, 28, 3)))

    def test_bad_weekend_is_empty(self):
        self.assertEqual([], mod.completed_days("", _utc(2026, 8, 31, 14)))


class MergeOverrideRowsTest(unittest.TestCase):
    def test_appends_new_days_and_skips_unchanged(self):
        existing = [{"weekend_of": "2026-08-28", "movie_title": "The Dog Stars",
                     "day_of_week": "Friday", "gross_m": "3.0"}]
        rows = mod.merge_override_rows(
            existing, "2026-08-28", "The Dog Stars",
            {"Friday": 3.02, "Saturday": 2.8}, "2026-08-29")
        # Friday within 2% tolerance -> skipped; Saturday appended.
        self.assertEqual(1, len(rows))
        self.assertEqual("Saturday", rows[0]["day_of_week"])
        self.assertEqual(2.8, rows[0]["gross_m"])
        self.assertEqual("reported", rows[0]["status"])

    def test_revision_beyond_tolerance_reappends(self):
        existing = [{"weekend_of": "2026-08-28", "movie_title": "The Dog Stars",
                     "day_of_week": "Friday", "gross_m": "3.0"}]
        rows = mod.merge_override_rows(
            existing, "2026-08-28", "The Dog Stars", {"Friday": 3.3}, "2026-08-30")
        self.assertEqual(1, len(rows))
        self.assertEqual(3.3, rows[0]["gross_m"])

    def test_bogus_values_dropped(self):
        rows = mod.merge_override_rows(
            [], "2026-08-28", "X", {"Friday": 0.001, "Saturday": 900.0}, "2026-08-29")
        self.assertEqual([], rows)

    def test_other_weekend_rows_do_not_suppress(self):
        existing = [{"weekend_of": "2026-08-21", "movie_title": "The Dog Stars",
                     "day_of_week": "Friday", "gross_m": "3.0"}]
        rows = mod.merge_override_rows(
            existing, "2026-08-28", "The Dog Stars", {"Friday": 3.0}, "2026-08-29")
        self.assertEqual(1, len(rows))


if __name__ == "__main__":
    unittest.main()


class SafeAnchorDaysTest(unittest.TestCase):
    def test_only_saturday_sunday_are_anchor_safe(self):
        # Friday anchors tested HARMFUL on 2026-08-28 (previews folded into
        # Friday's reported gross + Friday share is the weekend's low outlier):
        # Coyote +46%->+88%, Dog Stars +75%->+97%. Saturday anchors improved
        # both films. Do not widen this without re-running that comparison.
        self.assertEqual(("Saturday", "Sunday"), mod.SAFE_ANCHOR_DAYS)
