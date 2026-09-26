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
    def test_every_opening_day_is_recorded(self):
        # 2026-09-26: Thu/Fri were manual-only and never entered. The old
        # "Friday anchor hurts" result used Friday grosses with previews folded
        # in; with previews split out, Thu+Fri at the Friday-seats stage cut
        # recent-film MAE 15.9% -> 11.8%. Usage timing lives in the model
        # (predict.stage_gated_overrides), not in this list.
        self.assertEqual(("Thursday", "Friday", "Saturday", "Sunday"), mod.SAFE_ANCHOR_DAYS)

    def test_previews_are_split_out_of_friday(self):
        from datetime import date
        table = {date(2026, 9, 24): ("P", 2.0), date(2026, 9, 25): ("1", 7.45)}
        days = mod.fetch_split_opening_days("Heart of the Beast", "2026-09-25", fetch_table=lambda t, y: table)
        self.assertEqual({"Thursday": 2.0, "Friday": 5.45}, days)

    def test_friday_without_its_thursday_row_is_not_recorded(self):
        from datetime import date
        table = {date(2026, 9, 25): ("1", 7.45)}      # previews possibly still folded in
        self.assertEqual({}, mod.fetch_split_opening_days("X", "2026-09-25", fetch_table=lambda t, y: table))


class StageGatedOverridesTest(unittest.TestCase):
    def test_thursday_friday_wait_for_friday_seats(self):
        import predict as P
        ov = {"Heart of the Beast": {"Thursday": {"gross_m": 2.0}, "Friday": {"gross_m": 5.45}, "Saturday": {"gross_m": 7.0}},
              "Primetime": {"Thursday": {"gross_m": 2.7}}}
        early = P.stage_gated_overrides("Heart of the Beast", ov, {"Thursday"})
        self.assertEqual({"Saturday"}, set(early["Heart of the Beast"]))
        self.assertEqual({"Thursday"}, set(early["Primetime"]))          # other films untouched
        self.assertEqual({"Thursday", "Friday", "Saturday"}, set(ov["Heart of the Beast"]))   # input not mutated
        later = P.stage_gated_overrides("Heart of the Beast", ov, {"Thursday", "Friday"})
        self.assertIs(ov, later)
        self.assertEqual({}, P.stage_gated_overrides("X", {}, {"Thursday"}))


if __name__ == "__main__":
    unittest.main()
