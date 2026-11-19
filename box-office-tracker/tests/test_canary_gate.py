"""After a pause the seat lane is checked with one theatre, not restarted.

2026-11-19 15:20-16:08Z, Mountain snapshot re-read: refused from the first
seat request, three 15-minute pauses, and after each one all 8 tabs went
straight back into the block (136, 118 and 213 refused requests; 4 of 1,274
showings read).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402

BLOCK = f"AMC Test 12: {scraper.CF_BLOCK_ISSUE}"
PAUSE = 900


def run_leg(theatres, lane_opens_at, tabs=8, pauses=3, visit_sec=10, empty=(),
            slow=(), can_pause=True):
    """Replay a leg against a lane that refuses everything before
    `lane_opens_at`. Returns (visits, pauses_used, gate, skipped) where a
    visit is (start_time, theatre, role)."""
    gate = scraper.CanaryGate()
    queue = list(theatres)
    now = 0
    pause_until = 0
    pauses_left = pauses
    in_flight = []
    visits = []
    skipped = 0
    while queue or in_flight:
        while queue and len(in_flight) < tabs:
            role = gate.claim(now, pause_until)
            if role == "dead":
                skipped += len(queue)
                queue = []
                break
            if role == "wait":
                break
            name = queue.pop(0)
            visits.append((now, name, role))
            took = 270 if name in slow else visit_sec
            in_flight.append((now + took, name, role == "canary"))
        if not in_flight:
            if not queue:
                break
            now = max(now + 1, pause_until)
            continue
        in_flight.sort()
        if queue and len(in_flight) < tabs and in_flight[0][0] > now + 2:
            now += 2                 # parked tabs ask the gate again every 2 s
            continue
        now, name, is_canary = in_flight.pop(0)
        if name in empty:
            outcome = ([], [], [], [])
        elif now >= lane_opens_at:
            outcome = ([{"movie": "x"}], [], [], [])
        else:
            outcome = ([], [], [], [BLOCK])
        if is_canary:
            action = gate.settle(scraper.canary_verdict(*outcome), pauses_left, can_pause)
            if action == "pause":
                pauses_left -= 1
                pause_until = now + PAUSE
    return visits, pauses - pauses_left, gate, skipped


class CanaryVerdictTest(unittest.TestCase):
    def test_any_row_means_the_lane_answers(self):
        self.assertEqual("read", scraper.canary_verdict([{"m": 1}], [], [], [BLOCK]))
        self.assertEqual("read", scraper.canary_verdict([], [{"s": 1}], [], [BLOCK]))
        self.assertEqual("read", scraper.canary_verdict([], [], [["row"]], [BLOCK]))

    def test_nothing_read_and_a_refusal_is_blocked(self):
        for marker in (scraper.CF_BLOCK_ISSUE, scraper.PROXY_BLOCK_ISSUE, scraper.QUEUE_ISSUE):
            self.assertEqual("blocked", scraper.canary_verdict([], [], [], [f"AMC X: {marker}"]))

    def test_nothing_read_and_no_refusal_cannot_tell(self):
        self.assertEqual("unknown", scraper.canary_verdict([], [], [], []))
        self.assertEqual("unknown", scraper.canary_verdict([], [], [], ["AMC X: timeout after 270s"]))
        self.assertEqual("unknown", scraper.canary_verdict([], [], [], None))


class CanaryStepTest(unittest.TestCase):
    def test_one_or_two_refusals_are_not_enough(self):
        # quiet legs still refuse 1-6% of seat requests
        self.assertEqual(3, scraper.CF_CANARY_CONFIRM)
        self.assertEqual(("again", 1, 0), scraper.canary_step("blocked", 0, 0, 3, True))
        self.assertEqual(("again", 2, 0), scraper.canary_step("blocked", 1, 0, 3, True))

    def test_confirmed_refusal_pauses_while_a_pause_is_left(self):
        self.assertEqual(("pause", 0, 0), scraper.canary_step("blocked", 2, 0, 1, True))

    def test_confirmed_refusal_stops_without_a_pause(self):
        self.assertEqual(("stop", 0, 0), scraper.canary_step("blocked", 2, 0, 0, True))
        self.assertEqual(("stop", 0, 0), scraper.canary_step("blocked", 2, 0, 2, False))

    def test_a_read_opens_and_clears_the_counts(self):
        self.assertEqual(("open", 0, 0), scraper.canary_step("read", 2, 2, 0, False))

    def test_canaries_that_cannot_tell_do_not_hold_the_leg_for_ever(self):
        self.assertEqual(("again", 1, 1), scraper.canary_step("unknown", 1, 0, 3, True, unknown_max=3))
        self.assertEqual(("open", 0, 0), scraper.canary_step("unknown", 1, 2, 3, True, unknown_max=3))

    def test_a_refusal_restarts_the_cannot_tell_count(self):
        # unknown, unknown, blocked, unknown must not open the gate
        self.assertEqual(("again", 1, 0), scraper.canary_step("blocked", 0, 2, 3, True))
        self.assertEqual(("again", 1, 1), scraper.canary_step("unknown", 1, 0, 3, True))

    def test_cannot_tell_keeps_the_refusals_counted(self):
        # blocked, blocked, unknown, blocked is three refusals and no read
        self.assertEqual(("again", 2, 1), scraper.canary_step("unknown", 2, 0, 3, True))
        self.assertEqual(("pause", 0, 0), scraper.canary_step("blocked", 2, 1, 3, True))


class LegReplayTest(unittest.TestCase):
    THEATRES = [f"AMC {i}" for i in range(72)]

    def test_a_block_that_never_lifts_costs_twelve_visits_not_hundreds(self):
        visits, used, gate, skipped = run_leg(self.THEATRES, lane_opens_at=10 ** 9)
        self.assertEqual(3, used)
        self.assertTrue(gate.dead)
        # three canaries before each of three pauses, three more after the last
        self.assertEqual(12, len(visits))
        self.assertEqual({"canary"}, {role for _, _, role in visits})
        self.assertEqual(60, skipped)

    def test_canaries_never_overlap(self):
        visits, _, _, _ = run_leg(self.THEATRES, lane_opens_at=10 ** 9)
        starts = [t for t, _, _ in visits]
        self.assertTrue(all(b - a >= 10 for a, b in zip(starts, starts[1:])))

    def test_nothing_is_sent_during_a_pause(self):
        visits, _, _, _ = run_leg(self.THEATRES, lane_opens_at=10 ** 9)
        # canaries at 0, 10 and 20 -> pause from 30 to 930
        self.assertFalse([v for v in visits if 30 <= v[0] < 930])

    def test_the_leg_resumes_on_every_tab_once_a_canary_reads(self):
        visits, used, gate, skipped = run_leg(self.THEATRES, lane_opens_at=1000)
        self.assertEqual(2, used)             # shut at 0 and still shut at 930
        self.assertFalse(gate.dead)
        self.assertFalse(gate.closed)
        self.assertEqual(0, skipped)
        self.assertEqual(72, len(visits))
        self.assertEqual(7, sum(1 for _, _, role in visits if role == "canary"))
        after = [v for v in visits if v[2] == "go"]
        self.assertEqual(8, sum(1 for v in after if v[0] == after[0][0]))   # full width

    def test_no_room_for_a_pause_before_the_deadline_stops_the_leg(self):
        visits, used, gate, skipped = run_leg(self.THEATRES, lane_opens_at=10 ** 9,
                                              can_pause=False)
        self.assertEqual(0, used)
        self.assertTrue(gate.dead)
        self.assertEqual(3, len(visits))
        self.assertEqual(69, skipped)

    def test_a_healthy_leg_pays_one_theatre(self):
        visits, used, gate, _ = run_leg(self.THEATRES, lane_opens_at=0)
        self.assertEqual(0, used)
        self.assertEqual(["canary"] + ["go"] * 71, [role for _, _, role in visits])
        self.assertEqual(10, visits[1][0])

    def test_a_slow_canary_does_not_hold_the_other_tabs(self):
        # a hanging proxy: the first theatre takes its whole 270 s timeout
        visits, used, gate, _ = run_leg(self.THEATRES, lane_opens_at=0, slow={"AMC 0"})
        self.assertEqual(0, used)
        self.assertEqual(1, sum(1 for _, _, role in visits if role == "canary"))
        self.assertLessEqual(visits[1][0], scraper.CF_CANARY_SLOW_SEC + 2)
        self.assertEqual(72, len(visits))

    def test_empty_theatres_cannot_keep_the_gate_shut(self):
        visits, used, gate, _ = run_leg(self.THEATRES, lane_opens_at=0,
                                        empty=set(self.THEATRES[:5]))
        self.assertEqual(0, used)
        self.assertEqual(3, sum(1 for _, _, role in visits if role == "canary"))
        self.assertEqual(72, len(visits))

    def test_shutting_the_gate_sends_a_canary_next(self):
        gate = scraper.CanaryGate()
        self.assertEqual("canary", gate.claim(0, 0))
        self.assertEqual("open", gate.settle("read", 3, True))
        self.assertEqual("go", gate.claim(5, 0))
        gate.shut()                                   # a pause was called at t=5
        self.assertEqual("wait", gate.claim(100, 905))
        self.assertEqual("canary", gate.claim(905, 905))
        self.assertEqual("wait", gate.claim(906, 905))
        gate.release()                                # that canary crashed
        self.assertEqual("canary", gate.claim(907, 905))

    def test_a_canary_that_never_reports_frees_the_leg(self):
        gate = scraper.CanaryGate(slow_sec=90)
        self.assertEqual("canary", gate.claim(0, 0))
        self.assertEqual("wait", gate.claim(89, 0))
        self.assertEqual("go", gate.claim(90, 0))
        self.assertFalse(gate.closed)
        # its late verdict cannot shut or kill a gate that already opened
        self.assertEqual("open", gate.settle("blocked", 0, False))
        self.assertFalse(gate.dead)

    def test_a_top_up_leg_can_start_open(self):
        gate = scraper.CanaryGate(closed=False)
        self.assertEqual("go", gate.claim(0, 0))
        gate.shut()
        self.assertEqual("canary", gate.claim(900, 900))

    def test_a_lane_still_shut_in_the_retry_pass_stops_it(self):
        gate = scraper.CanaryGate()
        gate.shut()
        for _ in range(2):
            self.assertEqual("canary", gate.claim(900, 900))
            self.assertEqual("again", gate.settle("blocked", 0, True))   # retry pass: no pauses
        self.assertEqual("canary", gate.claim(900, 900))
        self.assertEqual("stop", gate.settle("blocked", 0, True))
        self.assertEqual("dead", gate.claim(901, 900))


class WiringTest(unittest.TestCase):
    BODY = Path(scraper.__file__).read_text()

    def test_the_gate_is_asked_before_a_theatre_is_read(self):
        claim = self.BODY.index("role = cf_gate.claim(gate_now, cf_pause_until)")
        read = self.BODY.index("sink = _new_theatre_sink()", claim)
        self.assertLess(read - claim, 1200)

    def test_a_pause_shuts_the_gate(self):
        block = self.BODY[self.BODY.index("if ((cf_block_streak >= CF_BLOCK_PAUSE_AFTER or wave)"):][:500]
        self.assertIn("cf_gate.shut()", block)

    def test_the_canary_decides_alone(self):
        block = self.BODY[self.BODY.index("if ((cf_block_streak >= CF_BLOCK_PAUSE_AFTER or wave)") - 120:][:120]
        self.assertIn("if is_canary:", block)

    def test_the_retry_pass_cannot_pause_and_is_skipped_when_the_lane_stayed_shut(self):
        self.assertIn("0 if cf_retry_pass else cf_pauses_left,", self.BODY)
        self.assertIn("and not cf_gate.dead):", self.BODY)

    def test_a_cancelled_canary_hands_over(self):
        block = self.BODY[self.BODY.index("except BaseException:"):][:160]
        self.assertIn("cf_gate.release()", block)

    def test_the_abort_is_checked_again_after_the_wait(self):
        after = self.BODY[self.BODY.index("role = cf_gate.claim(gate_now, cf_pause_until)"):][:1300]
        self.assertIn("if cf_block_streak >= CF_BLOCK_ABORT_AFTER or _egress_dead():", after)

    def test_a_crashed_canary_hands_over(self):
        block = self.BODY[self.BODY.index('print(f"  ❌ {name}: {e}")'):][:200]
        self.assertIn("cf_gate.release()", block)


if __name__ == "__main__":
    unittest.main()
