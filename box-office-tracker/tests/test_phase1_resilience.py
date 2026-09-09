"""Phase 1 (showtime-link collection) resilience — 2026-09-09.

Before: every empty listing printed "0 showtime(s)" whatever the cause, ALL
zero theatres were re-visited, and a snapshot run's link repair ran three
full Phase 1 passes. Result: the AMC lock was held 2h+ by link jobs (runs
34396443091, 34387368815) while the seat lane queued behind them.
"""
import asyncio
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402


class FakePage:
    def __init__(self, title="AMC Empire 25 | AMC Theatres", body="Showtimes", sections=None,
                 goto_raises=None, url="https://www.amctheatres.com/showtimes/all/2026-09-11/amc-empire-25/all"):
        self._title, self._body, self._sections, self._goto_raises = title, body, sections, goto_raises
        self.url = url

    async def goto(self, *a, **k):
        if self._goto_raises:
            raise self._goto_raises

    async def wait_for_selector(self, *a, **k):
        if self._sections:
            return True
        raise TimeoutError("no sections")

    async def title(self):
        return self._title

    async def evaluate(self, js):
        if "innerText" in js:
            return self._body
        return list(self._sections or [])


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


class ListingClassificationTest(unittest.TestCase):
    def _fetch(self, page):
        with redirect_stdout(io.StringIO()):
            return _run(scraper.fetch_amc_showtimes_pw(page, {"name": "AMC Test 9", "slug": "amc-test-9"}, "2026-09-11"))

    def test_showtimes_present_is_ok(self):
        out = self._fetch(FakePage(sections=[{"movie": "Runner", "showtime": "7:00pm", "showtime_id": "1"}]))
        self.assertEqual(1, len(out))
        self.assertEqual("ok", out.reason)

    def test_rendered_page_with_nothing_listed_is_authoritative_empty(self):
        out = self._fetch(FakePage(sections=None))
        self.assertEqual([], list(out))
        self.assertEqual("empty", out.reason)

    def test_cloudflare_block_and_challenge_are_classified_not_empty(self):
        blocked = self._fetch(FakePage(title="Attention Required! | Cloudflare",
                                       body="Sorry, you have been blocked"))
        self.assertEqual("blocked", blocked.reason)
        challenged = self._fetch(FakePage(title="Just a moment...", body="Verify you are human"))
        self.assertEqual("challenge", challenged.reason)

    def test_navigation_error_and_queue(self):
        nav = self._fetch(FakePage(goto_raises=RuntimeError("net::ERR_CONNECTION_RESET")))
        self.assertEqual("nav_error", nav.reason)
        queued = self._fetch(FakePage(url="https://queue.amctheatres.com/?c=amc"))
        self.assertEqual("queue", queued.reason)


class RetryPolicyTest(unittest.TestCase):
    def _outcomes(self, reasons):
        theatres = [{"name": f"T{i}", "_tz": "ET", "_date": "2026-09-11"} for i in range(len(reasons))]
        key = lambda t: (t["name"], t["_tz"], t["_date"])
        by_key = {}
        for t, r in zip(theatres, reasons):
            collected = scraper.phase1_result({"Runner": [{"showtime_id": "1"}]} if r == "ok" else None, r)
            by_key[key(t)] = (t["name"], "ET", "2026-09-11", collected)
        return theatres, by_key, key

    def test_transient_always_empties_only_when_rare_walls_never(self):
        theatres, by_key, key = self._outcomes(
            ["ok"] * 8 + ["empty", "timeout", "nav_error", "blocked", "challenge", "queue"])
        names = {t["name"] for t in scraper.phase1_retry_candidates(theatres, by_key, key)}
        # 1 empty of 14 = 7% -> retried; blocked/challenge/queue never
        self.assertEqual({"T8", "T9", "T10"}, names)

    def test_mass_empty_pass_is_not_re_walked(self):
        # the 2026-09-09 shape: ~150 of 218 theatres listed nothing for the
        # forward date — a market fact; re-visiting them doubled the pass
        theatres, by_key, key = self._outcomes(["empty"] * 150 + ["ok"] * 68 + ["timeout"])
        names = {t["name"] for t in scraper.phase1_retry_candidates(theatres, by_key, key)}
        self.assertEqual({"T218"}, names)   # only the timeout

    def test_aborted_pass_retries_nothing(self):
        theatres, by_key, key = self._outcomes(["blocked"] * 12 + ["aborted"] * 5)
        self.assertEqual([], scraper.phase1_retry_candidates(theatres, by_key, key, aborted=True))

    def test_legacy_plain_dict_outcomes_still_work(self):
        theatres = [{"name": "T0", "_tz": "ET", "_date": "d"}, {"name": "T1", "_tz": "ET", "_date": "d"}]
        key = lambda t: (t["name"], t["_tz"], t["_date"])
        by_key = {key(theatres[0]): ("T0", "ET", "d", {}), key(theatres[1]): ("T1", "ET", "d", {"F": [1]})}
        # a bare {} reads as 'empty' -> 1 of 2 = 50% > 30% cap -> not retried
        self.assertEqual([], scraper.phase1_retry_candidates(theatres, by_key, key))
        self.assertEqual(["T0"], [t["name"] for t in scraper.phase1_retry_candidates(
            theatres, by_key, key, empty_retry_max_share=0.5)])


class BlockStreakTest(unittest.TestCase):
    def test_streak_rule(self):
        nxt = scraper.phase1_next_block_streak
        self.assertEqual(1, nxt(0, "blocked", False))
        self.assertEqual(2, nxt(1, "challenge", False))
        self.assertEqual(2, nxt(2, "timeout", False))     # transient leaves it
        self.assertEqual(2, nxt(2, "nav_error", False))
        self.assertEqual(0, nxt(5, "empty", False))       # a rendered AMC page resets
        self.assertEqual(0, nxt(5, "ok", True))
        self.assertGreaterEqual(scraper.CF_BLOCK_ABORT_AFTER, 3)


class RepairBudgetTest(unittest.TestCase):
    def test_one_total_budget_across_repair_passes(self):
        calls = []
        clock = {"t": 1000.0}

        async def fake_run(group, target_date=None, full_weekend=None, deadline_sec=None):
            calls.append((group, target_date, deadline_sec))
            clock["t"] += 150     # each pass "takes" 150s

        skipped_items = [
            {"timezone": "ET", "show_date": "2026-09-11", "missing_movies": ["Runner"]},
            {"timezone": "CT", "show_date": "2026-09-11", "missing_movies": ["Runner"]},
            {"timezone": "PT", "show_date": "2026-09-11", "missing_movies": ["Runner"]},
        ]
        state = {"n": 0}

        def fake_usable(*a, **k):
            state["n"] += 1
            return ({}, skipped_items if state["n"] == 1 else [])

        orig = (scraper.snapshot_usable_date_sets, scraper.LINKS_JSON)
        try:
            scraper.snapshot_usable_date_sets = fake_usable
            scraper.LINKS_JSON = Path(tempfile.gettempdir()) / "no-such-links-for-test.json"
            with redirect_stdout(io.StringIO()) as buf:
                _run(scraper.repair_snapshot_phase1_links_async(
                    [], {}, ["ET", "CT", "PT"], {}, budget_sec=300,
                    _clock=lambda: clock["t"], _run_collect=fake_run))
        finally:
            scraper.snapshot_usable_date_sets, scraper.LINKS_JSON = orig
        # pass 1 gets the whole 300s, pass 2 the remaining 150s, pass 3 is
        # skipped (< 120s left) — total wall time bounded by ONE budget.
        # repairs run in sorted (group, date) order: CT, ET, PT
        self.assertEqual([("CT", "2026-09-11", 300), ("ET", "2026-09-11", 150)], calls)
        self.assertIn("repair budget exhausted", buf.getvalue())

    def test_default_budget_is_a_fraction_of_a_phase1_deadline(self):
        self.assertLessEqual(scraper.PHASE1_REPAIR_BUDGET_SEC, 1800)
        self.assertGreaterEqual(scraper.PHASE1_REPAIR_BUDGET_SEC, 300)


if __name__ == "__main__":
    unittest.main()


class FakeContext:
    def __init__(self, browser):
        self.browser = browser
        self.closed = False

    async def add_init_script(self, *_):
        pass

    async def new_page(self):
        pg = FakePage(**self.browser.next_page_kwargs())
        pg.routes = []
        async def route(pattern, handler):
            pg.routes.append(pattern)
        pg.route = route
        return pg

    async def close(self):
        self.closed = True


class FakeBrowser:
    """Serves a scripted sequence of page behaviours, one per new context."""
    def __init__(self, sequence):
        self.sequence = list(sequence)
        self.contexts = []

    def next_page_kwargs(self):
        return self.sequence.pop(0) if self.sequence else {"sections": None}

    async def new_context(self, **_):
        ctx = FakeContext(self)
        self.contexts.append(ctx)
        return ctx


class Phase1ProxyRedrawTest(unittest.TestCase):
    def _collect(self, browser, proxy_on):
        orig = (scraper._SEAT_PROXY, scraper.AMC_PHASE1_PROXY)
        try:
            scraper._SEAT_PROXY = {"server": "http://x"} if proxy_on else None
            scraper.AMC_PHASE1_PROXY = True
            with redirect_stdout(io.StringIO()):
                return _run(scraper._collect_links_theatre(
                    browser, {"name": "AMC Test 9", "slug": "amc-test-9"}, "2026-09-11", ["Runner"]))
        finally:
            scraper._SEAT_PROXY, scraper.AMC_PHASE1_PROXY = orig

    def test_proxy_mode_redraws_a_blocked_listing_on_a_fresh_context(self):
        blocked = {"title": "Attention Required! | Cloudflare", "body": "Sorry, you have been blocked"}
        ok = {"sections": [{"movie": "Runner", "showtime": "7:00pm", "showtime_id": "1"}]}
        b = FakeBrowser([blocked, blocked, ok])
        out = self._collect(b, proxy_on=True)
        self.assertEqual(["Runner"], list(out))           # third draw succeeded
        self.assertEqual(3, len(b.contexts))              # one fresh context per draw
        self.assertTrue(all(c.closed for c in b.contexts))
        self.assertTrue(all(c.browser is b for c in b.contexts))

    def test_proxy_mode_gives_up_after_the_retry_budget(self):
        blocked = {"title": "Attention Required! | Cloudflare", "body": "blocked"}
        b = FakeBrowser([blocked] * 6)
        out = self._collect(b, proxy_on=True)
        self.assertEqual({}, dict(out))
        self.assertEqual("blocked", out.reason)
        self.assertEqual(1 + scraper.AMC_PROXY_SHOWTIME_RETRIES, len(b.contexts))

    def test_direct_mode_never_redraws_and_never_trims(self):
        blocked = {"title": "Attention Required! | Cloudflare", "body": "blocked"}
        b = FakeBrowser([blocked, {"sections": [{"movie": "Runner", "showtime": "7:00pm", "showtime_id": "1"}]}])
        out = self._collect(b, proxy_on=False)
        self.assertEqual("blocked", out.reason)
        self.assertEqual(1, len(b.contexts))

    def test_trim_and_threshold_follow_proxy_mode(self):
        self.assertTrue(scraper._phase1_should_block_request("image", trim=True))
        self.assertTrue(scraper._phase1_should_block_request("font", trim=True))
        self.assertFalse(scraper._phase1_should_block_request("script", trim=True))   # listings hydrate
        self.assertFalse(scraper._phase1_should_block_request("document", trim=True))
        self.assertFalse(scraper._phase1_should_block_request("image", trim=False))
        self.assertEqual(scraper.CF_BLOCK_ABORT_AFTER, scraper.phase1_abort_threshold(proxy_on=False))
        self.assertEqual(4 * scraper.CF_BLOCK_ABORT_AFTER, scraper.phase1_abort_threshold(proxy_on=True))

    def test_workflow_gives_phase1_the_proxy_secret(self):
        yml = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        step = yml.split("- name: Phase 1 — collect showtime links", 1)[1].split("- name:", 1)[0]
        self.assertIn("AMC_SEAT_PROXY_URL: ${{ secrets.AMC_SEAT_PROXY_URL }}", step)


class EarlyBlockClassificationTest(unittest.TestCase):
    def test_hard_block_is_classified_before_the_section_wait(self):
        # audit-11: through the proxy three walled draws waited 3 x 25s and
        # overran the 90s theatre timeout, filing the wall as "timeout".
        class NoWaitPage(FakePage):
            waited = False
            async def wait_for_selector(self, *a, **k):
                NoWaitPage.waited = True
                raise TimeoutError()
        page = NoWaitPage(title="Attention Required! | Cloudflare", body="Sorry, you have been blocked")
        with redirect_stdout(io.StringIO()):
            out = _run(scraper.fetch_amc_showtimes_pw(page, {"name": "AMC T", "slug": "amc-t"}, "2026-09-11"))
        self.assertEqual("blocked", out.reason)
        self.assertFalse(NoWaitPage.waited)

    def test_repair_budget_floor_is_one_pass(self):
        self.assertGreaterEqual(scraper.PHASE1_REPAIR_BUDGET_SEC, scraper.PHASE1_REPAIR_MIN_PASS_SEC)
