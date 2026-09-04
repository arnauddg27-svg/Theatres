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
