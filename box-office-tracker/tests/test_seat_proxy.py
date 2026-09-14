import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402


class SeatProxyTest(unittest.TestCase):
    def test_proxy_url_parsing(self):
        self.assertIsNone(scraper.proxy_settings_from_url(""))
        self.assertIsNone(scraper.proxy_settings_from_url(None))
        s = scraper.proxy_settings_from_url("http://user-abc:p%40ss@gate.example.com:7000")
        self.assertEqual({"server": "http://gate.example.com:7000",
                          "username": "user-abc", "password": "p@ss"}, s)
        self.assertEqual({"server": "http://gate.example.com:7000"},
                         scraper.proxy_settings_from_url("gate.example.com:7000"))

    def test_trim_blocks_decoration_never_the_document(self):
        b = scraper._should_block_request
        for rt in ("script", "stylesheet", "font", "image", "media"):
            self.assertTrue(b(rt, "https://amc/x.js", trim=True), rt)
            self.assertFalse(b(rt, "https://amc/x.js", trim=False), rt)
        self.assertFalse(b("document", "https://www.amctheatres.com/showtimes/1/seats", trim=True))
        self.assertFalse(b("xhr", "https://amc/api", trim=True))
        # RSC is blocked regardless (403s from cloud IPs, breaks hydration)
        self.assertTrue(b("fetch", "https://amc/page?_rsc=abc", trim=False))

    def test_malformed_secret_never_crashes_import(self):
        # A '/' in an unencoded password makes urlsplit misread the port; the
        # loader must log and fall back to direct, never raise at import
        # (a raise here would take down Phase 1 too).
        self.assertRaises(ValueError, scraper.proxy_settings_from_url,
                          "http://user:pa/ss@us.decodo.com:10000")
        import os
        old = os.environ.get("AMC_SEAT_PROXY_URL")
        try:
            scraper.AMC_SEAT_PROXY_URL = "http://user:pa/ss@us.decodo.com:10000"
            self.assertIsNone(scraper._load_seat_proxy())
        finally:
            scraper.AMC_SEAT_PROXY_URL = old or ""

    def test_parsing_is_strict_never_silently_wrong(self):
        # audit-10: a NUMERIC prefix before an unencoded '/' used to parse
        # silently into server='http://user:12' with no credentials — every
        # navigation then failed as a "proxy refusal" and blamed the provider.
        bad = ["http://user:12/34@host:7000",          # numeric-prefix password
               "http://user:pa?ss@host:7000",          # '?' -> query
               "http://user:pa#ss@host:7000",          # '#' -> fragment
               "http://user:pass@host:7000/",          # trailing path
               "socks5://user:pass@host:1080",         # Chromium rejects socks5 auth at launch()
               "http://host:notaport",
               "http://"]
        for url in bad:
            with self.subTest(url=url):
                self.assertRaises(ValueError, scraper.proxy_settings_from_url, url)
        # Legit shapes still parse, IPv6 keeps its brackets, no-auth is fine.
        self.assertEqual({"server": "http://[::1]:8080", "username": "u", "password": "p"},
                         scraper.proxy_settings_from_url("http://u:p@[::1]:8080"))
        self.assertEqual({"server": "https://gate.example.com:7000"},
                         scraper.proxy_settings_from_url("https://gate.example.com:7000"))
        # Percent-encoding is the documented escape hatch and round-trips.
        self.assertEqual("12/34?#", scraper.proxy_settings_from_url(
            "http://u:12%2F34%3F%23@host:1")["password"])

    def test_loader_error_line_never_quotes_the_secret(self):
        # audit-10: urlsplit's own ValueError text quotes the password prefix
        # ("Port could not be cast to integer value as 'Abc123'") and GitHub
        # masks only the exact full secret. The ::error:: line must carry
        # our own shape message or a bare exception class name, never str(exc)
        # of a stdlib error.
        import contextlib, io
        cases = ["http://user:Abc123/xyz@us.decodo.com:10000",   # stdlib port error
                 "http://user:Zq9pass?x@us.decodo.com:10000",    # our shape error
                 "http://user:12/34@host:7000"]
        for url in cases:
            with self.subTest(url=url):
                buf = io.StringIO()
                old = scraper.AMC_SEAT_PROXY_URL
                try:
                    scraper.AMC_SEAT_PROXY_URL = url
                    with contextlib.redirect_stdout(buf):
                        self.assertIsNone(scraper._load_seat_proxy())
                finally:
                    scraper.AMC_SEAT_PROXY_URL = old
                out = buf.getvalue()
                self.assertIn("::error::", out)
                for fragment in ("Abc123", "Zq9pass", "12/34", "user:", "decodo"):
                    self.assertNotIn(fragment, out, out)
        # Strict parsing rejects those shapes before the stdlib can complain,
        # so ALSO pin the loader itself: a stdlib-style ValueError that quotes
        # a password fragment must be reduced to its class name.
        import contextlib, io
        real = scraper.proxy_settings_from_url
        try:
            def leaky(_url):
                raise ValueError("Port could not be cast to integer value as 'Abc123'")
            scraper.proxy_settings_from_url = leaky
            scraper.AMC_SEAT_PROXY_URL = "http://user:Abc123/xyz@us.decodo.com:10000"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertIsNone(scraper._load_seat_proxy())
            self.assertIn("ValueError", buf.getvalue())
            self.assertNotIn("Abc123", buf.getvalue(), buf.getvalue())
        finally:
            scraper.proxy_settings_from_url = real
            scraper.AMC_SEAT_PROXY_URL = ""

    def test_trim_follows_the_parsed_proxy_not_the_raw_secret(self):
        # A malformed secret runs DIRECT, so the banner/trim must say off too
        # (it printed proxy=off trim=ON during exactly the incident an
        # operator would be reading logs for).
        import importlib, os, contextlib, io
        old = os.environ.get("AMC_SEAT_PROXY_URL")
        try:
            os.environ["AMC_SEAT_PROXY_URL"] = "http://user:pa/ss@us.decodo.com:10000"
            os.environ.pop("AMC_SEAT_TRIM", None)
            with contextlib.redirect_stdout(io.StringIO()):
                fresh = importlib.reload(scraper)
            self.assertIsNone(fresh._SEAT_PROXY)
            self.assertFalse(fresh.AMC_SEAT_TRIM)
            os.environ["AMC_SEAT_PROXY_URL"] = "http://user:pass@us.decodo.com:10000"
            fresh = importlib.reload(scraper)
            self.assertIsNotNone(fresh._SEAT_PROXY)
            self.assertTrue(fresh.AMC_SEAT_TRIM)
        finally:
            if old is None:
                os.environ.pop("AMC_SEAT_PROXY_URL", None)
            else:
                os.environ["AMC_SEAT_PROXY_URL"] = old
            with contextlib.redirect_stdout(io.StringIO()):
                importlib.reload(scraper)

    def test_proxy_error_classifier(self):
        self.assertTrue(scraper._is_proxy_error("Page.goto: net::ERR_TUNNEL_CONNECTION_FAILED at https://x"))
        self.assertTrue(scraper._is_proxy_error("net::ERR_PROXY_AUTH_UNSUPPORTED"))
        self.assertFalse(scraper._is_proxy_error("Timeout 30000ms exceeded"))
        self.assertIsNot(scraper.PROXY_BLOCK_SENTINEL, scraper.CF_BLOCK_SENTINEL)

    def test_defaults_without_secret_are_direct_and_untrimmed(self):
        # Nothing changes until the AMC_SEAT_PROXY_URL secret exists.
        import os
        if not os.environ.get("AMC_SEAT_PROXY_URL"):
            self.assertIsNone(scraper._SEAT_PROXY)
            self.assertFalse(scraper.AMC_SEAT_TRIM)


class EgressSentinelPolicyTest(unittest.TestCase):
    """The abort path had NO tests (audit-10): deleting a sentinel branch or
    the PROXY clause of the streak check left the suite green while the leg
    walked every theatre again. These pin the two pure rules."""

    def test_every_sentinel_yields_an_issue_and_is_truthy(self):
        # Sentinels are non-empty dicts — a forgotten branch falls through to
        # seat_data["occupancy_pct"] and a KeyError that moves no streak.
        for sentinel, marker in ((scraper.QUEUE_SENTINEL, "queue redirect"),
                                 (scraper.CF_BLOCK_SENTINEL, scraper.CF_BLOCK_ISSUE),
                                 (scraper.PROXY_BLOCK_SENTINEL, scraper.PROXY_BLOCK_ISSUE)):
            with self.subTest(marker=marker):
                self.assertTrue(sentinel)
                issue = scraper._sentinel_issue(sentinel, "AMC Test 12")
                self.assertIsNotNone(issue)
                self.assertIn("AMC Test 12", issue)
                self.assertIn(marker, issue)
        self.assertIsNone(scraper._sentinel_issue(None, "x"))
        self.assertIsNone(scraper._sentinel_issue({"occupancy_pct": 1.0}, "x"))
        self.assertIsNone(scraper._sentinel_issue({}, "x"))

    def test_streak_rule(self):
        nxt = scraper._next_block_streak
        n = scraper.CF_BLOCK_ABORT_AFTER
        proxy_issue = scraper._sentinel_issue(scraper.PROXY_BLOCK_SENTINEL, "T")
        cf_issue = scraper._sentinel_issue(scraper.CF_BLOCK_SENTINEL, "T")
        # advances on proxy refusal AND on Cloudflare block
        self.assertEqual((1, None), nxt(0, [], [], [proxy_issue]))
        self.assertEqual((1, None), nxt(0, [], [], [cf_issue]))
        # unchanged on anything else (timeouts, KeyError text, no seat map)
        self.assertEqual((5, None), nxt(5, [], [], ["T: timeout after 180s — skipped"]))
        self.assertEqual((5, None), nxt(5, [], [], ["T: 'occupancy_pct'"]))
        self.assertEqual((5, None), nxt(5, [], [], []))
        # any real data resets — results OR snapshot rows
        self.assertEqual((0, None), nxt(11, [{"x": 1}], [], [cf_issue]))
        self.assertEqual((0, None), nxt(11, [], [{"x": 1}], [proxy_issue]))
        # the abort banner fires exactly once, at n, naming the cause
        s, why = nxt(n - 1, [], [], [proxy_issue])
        self.assertEqual(n, s)
        self.assertIn("proxy", why)
        s, why = nxt(n - 1, [], [], [cf_issue])
        self.assertEqual(n, s)
        self.assertIn("Cloudflare", why)
        self.assertEqual((n + 1, None), nxt(n, [], [], [cf_issue]))

    def test_cloudflare_challenge_classifier(self):
        c = scraper._is_cloudflare_challenge
        self.assertTrue(c("Just a moment..."))
        self.assertTrue(c("", "Verify you are human by completing the action below."))
        self.assertFalse(c("Select Seats | AMC Theatres", "Row A"))
        self.assertFalse(c("", ""))
        # the hard block stays the hard block's job
        self.assertFalse(c("Attention Required! | Cloudflare"))

    def test_snapshot_cap_agrees_between_scraper_and_predict(self):
        # predict.py's fallback denominator for capped snapshot probes must
        # equal the scraper's cap, or finalize's coverage ratio is inflated
        # (it said 100 while the scraper ran 200, then 120).
        import predict
        self.assertEqual(scraper.SNAPSHOT_TOP_THEATRE_CAP, predict.SNAPSHOT_STRATEGIC_THEATRE_CAP)
        self.assertEqual(120, predict.SNAPSHOT_STRATEGIC_THEATRE_CAP)


if __name__ == "__main__":
    unittest.main()


class FullUniverseSafetyTest(unittest.TestCase):
    def test_fatal_floor_is_about_few_rows_not_a_small_fraction_of_a_big_universe(self):
        # 24% of 950 slices is ~230 slices — never "too sparse to record"
        big = {"expected_total": 950, "observed_total": 230, "ratio": 230 / 950}
        self.assertFalse(scraper.snapshot_coverage_failure_is_fatal(big, 2000))
        # but 24% of 120 (29 slices) still is
        small = {"expected_total": 120, "observed_total": 29, "ratio": 29 / 120}
        self.assertTrue(scraper.snapshot_coverage_failure_is_fatal(small, 200))
        self.assertTrue(scraper.snapshot_coverage_failure_is_fatal({"expected_total": 950, "observed_total": 0, "ratio": 0}, 0))

    def test_timed_out_theatre_keeps_its_rows(self):
        sink = scraper._new_theatre_sink()
        sink["csv_rows"].append({"a": 1}); sink["pre_reservation_rows"].extend([{"b": 1}, {"b": 2}])
        sink["issues"].append("AMC T: earlier issue")
        results, issues, csv_rows, snap = scraper._harvest_sink(sink, "AMC T", 270)
        self.assertEqual(1, len(csv_rows)); self.assertEqual(2, len(snap))
        self.assertEqual(2, len(issues)); self.assertIn("partial (3 rows kept)", issues[-1])

    def test_http_overhead_constant_is_sane(self):
        self.assertGreaterEqual(scraper.HTTP_FETCH_OVERHEAD_BYTES, 4096)
        self.assertLessEqual(scraper.HTTP_FETCH_OVERHEAD_BYTES, 16384)
        self.assertGreaterEqual(scraper.AMC_BROWSER_FALLBACK_CAP, 100)


class RotatingProxyRetryPolicyTest(unittest.TestCase):
    """2026-09-09 first DataImpulse run: per-load outcomes were a MIX of clean
    maps, Cloudflare blocks, a challenge and slow renders — bad IP draws, not a
    dead egress. Direct mode keeps 'one block = theatre dead'."""

    def test_retry_only_walls_and_empties_in_proxy_mode(self):
        w = scraper._proxy_retry_worthwhile
        cf, none, data = scraper.CF_BLOCK_SENTINEL, None, {"occupancy_pct": 1}
        self.assertTrue(w(cf, 1, proxy_on=True, max_retries=2))
        # audit-11: an empty render is NOT redrawn (goto + 25s wait per draw
        # would overrun the per-theatre timeout and drop captured rows)
        self.assertFalse(w(none, 1, proxy_on=True, max_retries=2))
        self.assertFalse(w(cf, 3, proxy_on=True, max_retries=2))            # retries spent
        self.assertFalse(w(data, 1, proxy_on=True, max_retries=2))          # real data
        self.assertFalse(w(scraper.PROXY_BLOCK_SENTINEL, 1, proxy_on=True, max_retries=2))  # provider refusal
        self.assertFalse(w(scraper.QUEUE_SENTINEL, 1, proxy_on=True, max_retries=2))
        self.assertFalse(w(cf, 1, proxy_on=False, max_retries=2))           # direct: never

    def test_block_outcome_skips_showtimes_then_gives_up_on_theatre(self):
        o = scraper._proxy_block_outcome
        cf = scraper.CF_BLOCK_SENTINEL
        self.assertEqual(("skip_showtime", 1), o(cf, 0, proxy_on=True, giveup=4))
        self.assertEqual(("skip_showtime", 3), o(cf, 2, proxy_on=True, giveup=4))
        self.assertEqual(("break_theatre", 4), o(cf, 3, proxy_on=True, giveup=4))
        # non-Cloudflare sentinels and direct mode: theatre-level break as before
        self.assertEqual("break_theatre", o(scraper.PROXY_BLOCK_SENTINEL, 0, proxy_on=True, giveup=4)[0])
        self.assertEqual("break_theatre", o(scraper.QUEUE_SENTINEL, 0, proxy_on=True, giveup=4)[0])
        self.assertEqual("break_theatre", o(cf, 0, proxy_on=False, giveup=4)[0])

    def test_skipped_showtime_issue_still_feeds_the_streak_only_when_theatre_is_empty(self):
        # A theatre with some clean maps resets the leg streak even if other
        # showtimes were blocked; a fully blocked theatre advances it.
        issue = f"AMC T: {scraper.CF_BLOCK_ISSUE} {scraper.PROXY_IP_BLOCK_NOTE} (3 IPs tried) 7:00pm"
        self.assertEqual((0, None), scraper._next_block_streak(5, [{"x": 1}], [], [issue]))
        self.assertEqual((6, None), scraper._next_block_streak(5, [], [], [issue]))


class EgressTimeoutBreakerTest(unittest.TestCase):
    """2026-09-14: every AMC fetch through the proxy HUNG for hours. Timeouts
    are not blocks, so the block breaker never fired and the legs ran their
    whole deadline holding the AMC lock. A timeout streak ends such a leg."""

    def test_timeout_errors_are_recognised(self):
        class Timeout(Exception):
            pass
        is_t = scraper._is_timeout_error
        self.assertTrue(is_t(Timeout("curl: (28)")))                     # curl_cffi class name
        self.assertTrue(is_t(Exception("Page.goto: Timeout 30000ms exceeded.")))
        self.assertTrue(is_t(Exception("net::ERR_TIMED_OUT at https://x")))
        self.assertTrue(is_t(Exception("operation timed out")))
        self.assertFalse(is_t(Exception("net::ERR_ABORTED; maybe frame was detached?")))
        self.assertFalse(is_t(KeyError("occupancy_pct")))
        self.assertFalse(is_t(None))

    def test_streak_rule(self):
        nxt = scraper._next_egress_timeout_streak
        self.assertEqual((1, False), nxt(0, "timeout", limit=3))
        self.assertEqual((3, True), nxt(2, "timeout", limit=3))       # trips at the limit
        self.assertEqual((4, False), nxt(3, "timeout", limit=3))      # ...exactly once
        self.assertEqual((0, False), nxt(7, "response", limit=3))     # anything back resets
        self.assertEqual((2, False), nxt(2, "other", limit=3))        # proves nothing

    def test_note_egress_trips_the_leg_and_a_leg_reset_clears_it(self):
        scraper._egress_reset()
        saved = scraper._SEAT_PROXY
        scraper._SEAT_PROXY = None              # direct leg: nothing to fall back from
        try:
            for _ in range(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER - 1):
                scraper._note_egress("timeout")
            self.assertFalse(scraper._egress_dead())
            scraper._note_egress("response")                           # one real answer
            for _ in range(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER - 1):
                scraper._note_egress("timeout")
            self.assertFalse(scraper._egress_dead())                   # streak restarted
            scraper._note_egress("timeout")
            self.assertTrue(scraper._egress_dead())
            scraper._note_egress("response")
            self.assertTrue(scraper._egress_dead(), "a trip is sticky for the leg")
            scraper._egress_reset()
            self.assertFalse(scraper._egress_dead())
        finally:
            scraper._SEAT_PROXY = saved
            scraper._egress_reset()

    def test_healthy_leg_pattern_never_trips(self):
        # Monday's healthy ET leg: 47 HTTP fallbacks spread over 1,833 fetches.
        scraper._egress_reset()
        try:
            for i in range(1833):
                scraper._note_egress("timeout" if i % 39 == 0 else "response")
            self.assertFalse(scraper._egress_dead())
        finally:
            scraper._egress_reset()


class ProxyDirectFallbackTest(unittest.TestCase):
    """A hang through the proxy is the proxy's fault: switch to direct first."""

    def setUp(self):
        self.saved = (scraper._SEAT_PROXY, scraper.AMC_PROXY_DIRECT_FALLBACK,
                      dict(scraper._HTTP_STATE), dict(scraper._EGRESS_TIMEOUTS))
        scraper._egress_reset()
        scraper._EGRESS_TIMEOUTS["fell_back"] = False

    def tearDown(self):
        scraper._SEAT_PROXY, scraper.AMC_PROXY_DIRECT_FALLBACK = self.saved[0], self.saved[1]
        scraper._HTTP_STATE.clear(); scraper._HTTP_STATE.update(self.saved[2])
        scraper._EGRESS_TIMEOUTS.clear(); scraper._EGRESS_TIMEOUTS.update(self.saved[3])

    def _hang(self, n):
        for _ in range(n):
            scraper._note_egress("timeout")

    def test_first_trip_switches_to_direct_second_trip_aborts(self):
        scraper._SEAT_PROXY = {"server": "http://gw.example:823"}
        scraper.AMC_PROXY_DIRECT_FALLBACK = True
        scraper._HTTP_STATE.update(disabled=True, disabled_reason="breaker",
                                   http_ok=0, http_fallback=30, session=object())
        self._hang(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER)
        self.assertIsNone(scraper._SEAT_PROXY)
        self.assertIsNone(scraper._http_proxy_url())
        self.assertFalse(scraper._egress_dead(), "a fallback is not an abort")
        self.assertTrue(scraper._EGRESS_TIMEOUTS["relaunch"])
        self.assertTrue(scraper._EGRESS_TIMEOUTS["fell_back"])
        self.assertEqual(0, scraper._EGRESS_TIMEOUTS["streak"])
        # the proxy-caused HTTP disable is lifted and its session dropped
        self.assertFalse(scraper._HTTP_STATE["disabled"])
        self.assertIsNone(scraper._HTTP_STATE["session"])
        # direct hangs too -> now the leg aborts
        self._hang(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER)
        self.assertTrue(scraper._egress_dead())

    def test_parity_disable_is_not_lifted(self):
        scraper._SEAT_PROXY = {"server": "http://gw.example:823"}
        scraper.AMC_PROXY_DIRECT_FALLBACK = True
        scraper._HTTP_STATE.update(disabled=True, disabled_reason="parity")
        self._hang(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER)
        self.assertIsNone(scraper._SEAT_PROXY)
        self.assertTrue(scraper._HTTP_STATE["disabled"], "a data disagreement is not the proxy's fault")

    def test_fallback_can_be_switched_off(self):
        scraper._SEAT_PROXY = {"server": "http://gw.example:823"}
        scraper.AMC_PROXY_DIRECT_FALLBACK = False
        self._hang(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER)
        self.assertIsNotNone(scraper._SEAT_PROXY)
        self.assertTrue(scraper._egress_dead())

    def test_leg_reset_keeps_the_fallback_but_clears_the_relaunch(self):
        scraper._SEAT_PROXY = {"server": "http://gw.example:823"}
        scraper.AMC_PROXY_DIRECT_FALLBACK = True
        self._hang(scraper.AMC_EGRESS_TIMEOUT_ABORT_AFTER)
        scraper._egress_reset()
        self.assertIsNone(scraper._SEAT_PROXY)
        self.assertTrue(scraper._EGRESS_TIMEOUTS["fell_back"])
        self.assertFalse(scraper._EGRESS_TIMEOUTS["relaunch"])
