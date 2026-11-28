"""A lane that has read nothing for a day stops a refused leg without pausing.

2026-11-27 22:30Z snapshot: AMC had refused every leg since 11-19. Each of
the four zones still waited three 15-minute pauses (22:39-23:33, 23:33-00:29,
00:29-01:24, 01:24-02:18Z) and the slot's forecast landed at 02:25Z.
"""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402

HEADER = "weekend_of,run_id,snapshot_time,snapshot_bucket,show_date,theatre_name\n"
NOW = datetime(2026, 11, 28, 1, 0, tzinfo=timezone.utc)


def row(stamp, theatre="AMC Test 12"):
    return f"2026-11-20,run,{stamp},2026-11-20T18:00Z,2026-11-21,{theatre}\n"


class NewestSnapshotTimeTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.csv = self.dir / "pre-reservation-snapshots.csv"
        self.archive = self.dir / "archive"
        self.archive.mkdir()

    def newest(self, **kw):
        return scraper.newest_snapshot_time(self.csv, self.archive, **kw)

    def test_reads_the_newest_row_from_the_tail(self):
        self.csv.write_text(HEADER + row("2026-11-19T10:00:00+00:00")
                            + row("2026-11-20T18:11:00.121761+00:00"))
        self.assertEqual(self.newest(),
                         datetime(2026, 11, 20, 18, 11, 0, 121761, tzinfo=timezone.utc))

    def test_a_tail_cut_mid_line_is_skipped_not_fatal(self):
        self.csv.write_text(HEADER + "".join(
            row(f"2026-11-20T18:{m:02d}:00+00:00", "AMC \"Quoted, Name\" 9") for m in range(60)))
        self.assertEqual(self.newest(tail_bytes=300),
                         datetime(2026, 11, 20, 18, 59, tzinfo=timezone.utc))

    def test_missing_file_is_unknown(self):
        self.assertIsNone(self.newest())

    def test_header_only_file_falls_back_to_the_newest_archive(self):
        self.csv.write_text(HEADER)
        (self.archive / "pre-reservation-snapshots-2026-11-06.csv.gz").write_bytes(b"")
        (self.archive / "pre-reservation-snapshots-2026-11-13.csv.gz").write_bytes(b"")
        self.assertEqual(self.newest(), datetime(2026, 11, 17, tzinfo=timezone.utc))

    def test_header_only_file_with_no_archive_is_unknown(self):
        self.csv.write_text(HEADER)
        self.assertIsNone(self.newest())

    def test_unparseable_rows_are_unknown_not_dark(self):
        self.csv.write_text(HEADER + "a,b,not-a-time,d,e,f\n" * 5)
        self.assertIsNone(self.newest())

    def test_a_file_without_the_column_is_unknown(self):
        self.csv.write_text("a,b,c\n1,2,3\n")
        self.assertIsNone(self.newest())


class LaneDarkTest(unittest.TestCase):
    def test_a_week_old_row_is_dark(self):
        self.assertTrue(scraper.lane_dark(NOW - timedelta(days=7), now=NOW))

    def test_a_row_from_this_morning_is_not(self):
        self.assertFalse(scraper.lane_dark(NOW - timedelta(hours=10), now=NOW))

    def test_unknown_is_never_dark(self):
        self.assertFalse(scraper.lane_dark(None, now=NOW))

    def test_zero_hours_turns_it_off(self):
        self.assertFalse(scraper.lane_dark(NOW - timedelta(days=7), now=NOW, after_hours=0))

    def test_default_threshold_outlasts_the_gap_between_slots(self):
        # Slots run 02:30 / 14:30 / 22:30Z: one failed slot must not make
        # the lane dark, or a single wave night would cost the next slot
        # its pauses.
        self.assertGreaterEqual(scraper.CF_DARK_AFTER_HOURS, 24)


class DarkLegTest(unittest.TestCase):
    def test_a_dark_leg_stops_on_the_first_confirmed_refusal(self):
        blocked = 0
        for n in range(scraper.CF_CANARY_CONFIRM):
            action, blocked, _ = scraper.canary_step("blocked", blocked, 0, 0, True)
        self.assertEqual(action, "stop")
        self.assertEqual(n + 1, scraper.CF_CANARY_CONFIRM)

    def test_a_dark_leg_that_reads_opens(self):
        self.assertEqual(scraper.canary_step("read", 2, 0, 0, True)[0], "open")

    def test_the_leg_wires_the_budget_and_restores_it(self):
        body = Path(scraper.__file__).read_text()
        start = body.index("cf_dark = lane_dark(cf_newest_row)")
        self.assertIn("cf_pauses_left = 0 if cf_dark else CF_BLOCK_PAUSES",
                      body[start:start + 200])
        self.assertIn("except Exception", body[start - 200:start])
        restore = body.index("cf_pauses_left = CF_BLOCK_PAUSES", start + 200)
        guard = body[restore - 500:restore]
        # Restored on rows read, never on the gate merely opening: a slow
        # check opens the gate too (CF_CANARY_SLOW_SEC) while still blocked.
        self.assertIn("if cf_dark and (csv_rows or snapshot_rows):", guard)
        opened = body.index('if action == "open":', start)
        self.assertNotIn("cf_pauses_left = CF_BLOCK_PAUSES", body[opened:opened + 400])

if __name__ == "__main__":
    unittest.main()
