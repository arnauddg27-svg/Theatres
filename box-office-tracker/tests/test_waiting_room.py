"""AMC's waiting room (Queue-It) and spaced AMC retries (2026-11-19).

On 2026-11-16 ~14:00-20:00Z the waiting room redirected hundreds of requests
per run. The seat lane's data-endpoint path returned without logging, the
listing pass kept asking, and the scheduler re-dispatched as fast as runs
failed."""
import datetime as dt
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import scraper  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "schedule_for_waiting_room", os.path.join(ROOT, "scripts", "schedule_box_office_pipeline.py"))
schedule = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = schedule
_spec.loader.exec_module(schedule)


class SeatLaneWaitingRoomTest(unittest.TestCase):
    def test_queue_redirect_is_a_named_issue(self):
        issue = scraper._sentinel_issue(scraper.QUEUE_SENTINEL, "AMC Test 12")
        self.assertIn(scraper.QUEUE_ISSUE, issue)

    def test_queue_redirects_advance_the_leg_streak_and_name_the_cause(self):
        issue = scraper._sentinel_issue(scraper.QUEUE_SENTINEL, "T")
        self.assertEqual((1, None), scraper._next_block_streak(0, [], [], [issue]))
        streak, why = scraper._next_block_streak(scraper.CF_BLOCK_ABORT_AFTER - 1, [], [], [issue])
        self.assertEqual(scraper.CF_BLOCK_ABORT_AFTER, streak)
        self.assertIn("waiting room", why)

    def test_real_rows_still_reset_the_streak(self):
        issue = scraper._sentinel_issue(scraper.QUEUE_SENTINEL, "T")
        self.assertEqual((0, None), scraper._next_block_streak(7, [{"x": 1}], [], [issue]))

    def test_counter_exists_and_shows_in_the_summary_only_when_nonzero(self):
        saved = scraper._HTTP_STATE["queue"]
        try:
            scraper._HTTP_STATE["queue"] = 0
            self.assertNotIn("queue_redirects", scraper._http_fetch_summary())
            scraper._HTTP_STATE["queue"] = 72
            self.assertIn("queue_redirects=72", scraper._http_fetch_summary())
        finally:
            scraper._HTTP_STATE["queue"] = saved


class ListingWaitingRoomTest(unittest.TestCase):
    def test_queue_advances_the_pass_streak(self):
        self.assertEqual(3, scraper.phase1_next_block_streak(2, "queue", False))
        self.assertEqual(0, scraper.phase1_next_block_streak(9, "empty", False))

    def test_queue_is_never_redrawn_on_a_fresh_exit(self):
        self.assertNotIn("queue", scraper.PHASE1_BLOCK_REASONS)


class SpacedRetryTest(unittest.TestCase):
    NOW = dt.datetime(2026, 11, 16, 15, 0, tzinfo=dt.timezone.utc)

    def _failed(self, ended):
        return [{"created_at": "2026-11-16T14:33:00Z", "updated_at": ended, "conclusion": "failure"}]

    def test_only_amc_slots_wait(self):
        for title in ("box office scheduled snapshot 14:30Z", "box office scheduled snapshot 02:30Z",
                      "box office scheduled regular scrape 07Z", "box office scheduled collect-links ET 13Z"):
            self.assertEqual(45, schedule.retry_gap_minutes(title), title)
        for title in ("box office scheduled snapshot fandango core 14Z", "box office scheduled cinemark pre 14:20Z s0",
                      "box office scheduled regal inventory 12:10Z", "box office scheduled alamo pre 12:40Z"):
            self.assertEqual(0, schedule.retry_gap_minutes(title), title)

    def test_a_just_failed_amc_slot_is_held(self):
        ready = schedule.failed_run_cooling(self._failed("2026-11-16T14:40:00Z"),
                                            "box office scheduled snapshot 14:30Z", self.NOW)
        self.assertEqual(dt.datetime(2026, 11, 16, 15, 25, tzinfo=dt.timezone.utc), ready)

    def test_after_the_gap_it_is_due_again(self):
        self.assertIsNone(schedule.failed_run_cooling(self._failed("2026-11-16T14:10:00Z"),
                                                      "box office scheduled snapshot 14:30Z", self.NOW))

    def test_other_lanes_and_clean_slots_never_wait(self):
        self.assertIsNone(schedule.failed_run_cooling(self._failed("2026-11-16T14:59:00Z"),
                                                      "box office scheduled cinemark pre 14:20Z s0", self.NOW))
        self.assertIsNone(schedule.failed_run_cooling([], "box office scheduled snapshot 14:30Z", self.NOW))

    def test_three_attempts_still_fit_the_shortest_amc_window(self):
        # 240-minute watchdog lookback; a fail-fast leg ends ~5 min after it starts
        attempts = [0]
        while len(attempts) < schedule.MAX_SLOT_RETRIES:
            attempts.append(attempts[-1] + 5 + schedule.AMC_RETRY_GAP_MINUTES + 5)   # run + gap + next 5-min tick
        self.assertLess(attempts[-1], 240)


class AlamoLoopDaysTest(unittest.TestCase):
    def test_daytime_post_loop_runs_thursday_to_sunday(self):
        slot = next(s for s in schedule.SLOTS if s.name == "alamo post loop 15:10Z")
        evening = next(s for s in schedule.SLOTS if s.name == "alamo post loop 20:50Z")
        days = next(v for v in vars(slot).values() if isinstance(v, frozenset))
        self.assertEqual(next(v for v in vars(evening).values() if isinstance(v, frozenset)), days)
        self.assertEqual(4, len(days))


if __name__ == "__main__":
    unittest.main()
