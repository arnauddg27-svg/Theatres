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


if __name__ == "__main__":
    unittest.main()
