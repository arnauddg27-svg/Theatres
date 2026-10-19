"""latest_snapshot_window_rows must keep already-started showtimes that the
freshest same-day run no longer lists (2026-10-10: Saturday lost 48% of its
showtimes — the matinees — once the evening read became the freshest run)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict  # noqa: E402


def _row(run_id, snapshot_time, showtime_id, lead_min, reserved=10):
    return {
        "show_date": "2026-10-10", "timezone": "ET", "theatre_name": "AMC Test 1",
        "run_id": run_id, "snapshot_time": snapshot_time, "snapshot_bucket": snapshot_time[:13] + ":00Z",
        "showtime_id": showtime_id, "showtime": "x", "minutes_until_showtime": str(lead_min),
        "reserved_seats": str(reserved), "total_seats": "100",
    }


class SnapshotSliceCarryForwardTest(unittest.TestCase):
    def test_started_showtimes_carried_forward_from_earlier_run(self):
        night = "2026-10-10T03:00:00+00:00"   # Friday-night read, all of Saturday ahead
        evening = "2026-10-10T22:30:00+00:00"  # same-day evening read
        rows = [
            _row("run-night", night, "matinee", 10 * 60),      # 13:00Z show: played before 22:30Z
            _row("run-night", night, "evening", 20 * 60),      # 23:00Z show
            _row("run-night", night, "late", 22 * 60),         # 01:00Z show
            _row("run-night", night, "delisted", 21 * 60),     # 00:00Z show, missing from evening run
            _row("run-eve", evening, "evening", 30, reserved=40),
            _row("run-eve", evening, "late", 150, reserved=25),
        ]
        kept = predict.latest_snapshot_window_rows(rows, max_slice_age_hours=48)
        by_id = {(r["showtime_id"], r["run_id"]) for r in kept}
        self.assertIn(("matinee", "run-night"), by_id)        # carried forward (already started)
        self.assertIn(("evening", "run-eve"), by_id)
        self.assertIn(("late", "run-eve"), by_id)
        self.assertNotIn(("evening", "run-night"), by_id)     # superseded by the fresh read
        self.assertNotIn(("delisted", "run-night"), by_id)    # still future at 22:30Z -> not resurrected
        self.assertEqual(3, len(kept))

    def test_freshest_of_several_earlier_reads_is_carried(self):
        rows = [
            _row("run-a", "2026-10-09T03:00:00+00:00", "matinee", 34 * 60, reserved=3),
            _row("run-b", "2026-10-10T03:00:00+00:00", "matinee", 10 * 60, reserved=9),
            _row("run-eve", "2026-10-10T22:30:00+00:00", "evening", 30, reserved=40),
        ]
        kept = predict.latest_snapshot_window_rows(rows, max_slice_age_hours=48)
        carried = [r for r in kept if r["showtime_id"] == "matinee"]
        self.assertEqual(1, len(carried))
        self.assertEqual("run-b", carried[0]["run_id"])

    def test_no_change_when_latest_run_lists_everything(self):
        rows = [
            _row("run-a", "2026-10-10T03:00:00+00:00", "s1", 600),
            _row("run-a", "2026-10-10T03:00:00+00:00", "s2", 1200),
            _row("run-b", "2026-10-10T14:30:00+00:00", "s1", 60),
            _row("run-b", "2026-10-10T14:30:00+00:00", "s2", 500),
        ]
        kept = predict.latest_snapshot_window_rows(rows, max_slice_age_hours=48)
        self.assertEqual({"run-b"}, {r["run_id"] for r in kept})
        self.assertEqual(2, len(kept))


if __name__ == "__main__":
    unittest.main()


class PerDateFreshnessTest(unittest.TestCase):
    def test_slice_age_is_judged_against_its_own_show_date(self):
        # Saturday slice read at 03Z, Friday slice re-read at 15Z (daytime slot
        # covering only the nearest dates): Saturday must survive.
        sat = dict(_row("run-night", "2026-10-16T03:00:00+00:00", "s1", 20 * 60), show_date="2026-10-17")
        fri = dict(_row("run-day", "2026-10-16T15:00:00+00:00", "f1", 180), show_date="2026-10-16")
        kept = predict.latest_snapshot_window_rows([sat, fri], max_slice_age_hours=8)
        self.assertEqual({"2026-10-16", "2026-10-17"}, {r["show_date"] for r in kept})
