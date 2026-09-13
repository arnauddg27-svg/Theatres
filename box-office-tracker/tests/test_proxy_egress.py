"""Residential-proxy egress shared by the Regal and Cinemark lanes (2026-09-12).
Both were limited by PER-NETWORK throttles; rotating addresses lift those, at
the price of metered bytes — so the byte ceiling is the safety property."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import proxy_egress as pe  # noqa: E402


class ByteBudgetTest(unittest.TestCase):
    def test_metered_budget_stops_the_lane_once(self):
        b = pe.ByteBudget(1, "lane")
        self.assertTrue(b.metered)
        self.assertFalse(b.exhausted())
        b.add(512 * 1024, is_document=True)
        self.assertFalse(b.exhausted())
        b.add(600 * 1024, is_document=True)
        self.assertTrue(b.exhausted())
        self.assertTrue(b.exhausted())          # idempotent
        self.assertIn("2 page loads", b.summary())
        self.assertIn("/1 MB", b.summary())

    def test_zero_limit_is_unmetered_and_never_stops(self):
        b = pe.ByteBudget(0, "direct")
        self.assertFalse(b.metered)
        b.add(50 * 1024 * 1024)
        self.assertFalse(b.exhausted())
        self.assertIn("unmetered", b.summary())

    def test_summary_never_divides_by_zero(self):
        self.assertIn("0.0 MB", pe.ByteBudget(10, "x").summary())

    def test_counts_are_thread_safe(self):
        import threading
        b = pe.ByteBudget(0, "x")
        def hammer():
            for _ in range(500):
                b.add(10, is_document=True)
        ts = [threading.Thread(target=hammer) for _ in range(8)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(8 * 500 * 10, b.bytes)
        self.assertEqual(8 * 500, b.documents)


class LaunchWiringTest(unittest.TestCase):
    def test_launch_kwargs_adds_the_proxy_only_when_configured(self):
        import scraper
        orig = scraper._SEAT_PROXY
        try:
            scraper._SEAT_PROXY = None
            self.assertEqual({"headless": True}, pe.launch_kwargs({"headless": True}))
            scraper._SEAT_PROXY = {"server": "http://gw:823", "username": "u", "password": "p"}
            kw = pe.launch_kwargs({"headless": True, "args": ["--x"]})
            self.assertEqual(scraper._SEAT_PROXY, kw["proxy"])
            self.assertEqual(["--x"], kw["args"])          # caller's kwargs preserved
        finally:
            scraper._SEAT_PROXY = orig

    def test_attach_meter_is_a_no_op_when_unmetered_and_never_raises(self):
        class Boom:
            def new_cdp_session(self, page):
                raise RuntimeError("no cdp here")
        pe.attach_meter(Boom(), object(), pe.ByteBudget(0, "x"))     # skipped
        pe.attach_meter(Boom(), object(), pe.ByteBudget(5, "x"))     # swallowed

    def test_both_lanes_read_the_budget_from_env(self):
        import importlib, os
        for mod, var, val in (("fandango_collect", "FANDANGO_MAX_MB", "60"),
                              ("cinemark_collect", "CINEMARK_MAX_MB", "150")):
            old = os.environ.get(var)
            try:
                os.environ[var] = val
                m = importlib.reload(importlib.import_module(mod))
                self.assertEqual(int(val), getattr(m, var))
            finally:
                if old is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = old
                importlib.reload(importlib.import_module(mod))

    def test_cinemark_stays_direct_and_regal_is_metered(self):
        # Measured 2026-09-12: through the proxy a browser render costs
        # 6.3 MB/theatre (Cinemark, run 34729565675) and 7.4 MB/theatre (Regal,
        # run 34730147947) — 1.9-2.8 GB for ONE full-pool pass against a
        # 1.6 GB/day budget, and trimming to cut it made Cinemark block us.
        # The capability stays wired (proxy_egress) but neither lane assigns
        # the secret; only a lightweight read would change that.
        yml = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        fan = yml.split("- name: Fandango snapshot", 1)[1].split("run: |", 1)[0]
        cin = yml.split("- name: Cinemark collect", 1)[1].split("run: |", 1)[0]
        self.assertNotIn("AMC_SEAT_PROXY_URL: ${{", cin)   # cinemark direct
        self.assertNotIn("CINEMARK_MAX_MB: '", cin)
        self.assertNotIn("CINEMARK_PROXY_PER_THEATRE_CAP: '", cin)

    def test_lanes_run_unmetered_and_unproxied_without_the_env(self):
        # the safety property: no secret -> no meter, no ceiling, no behaviour
        # change from the code that is now wired in
        import importlib
        for mod, var in (("fandango_collect", "FANDANGO_MAX_MB"), ("cinemark_collect", "CINEMARK_MAX_MB")):
            m = importlib.reload(importlib.import_module(mod))
            self.assertEqual(0, getattr(m, var))
            self.assertFalse(pe.ByteBudget(getattr(m, var), "x").metered)


if __name__ == "__main__":
    unittest.main()


class TrimTest(unittest.TestCase):
    def test_media_and_tracker_hosts_are_dropped(self):
        # measured: images.fandango.com is 3.0 MB of a 5.37 MB theatre page
        self.assertTrue(pe.should_block("image", "https://images.fandango.com/x.jpg"))
        # ...but that same host also serves the app's JS; blocking it wholesale
        # left the page with no showtimes at all
        self.assertFalse(pe.should_block("script", "https://images.fandango.com/app.js"))
        self.assertFalse(pe.should_block("xhr", "https://images.fandango.com/data"))
        for h in ("https://securepubads.g.doubleclick.net/gampad/ads",
                  "https://assets.adobedtm.com/x.js", "https://cdn.cookielaw.org/x.js",
                  "https://g2.gumgum.com/hbid/imp", "https://connect.facebook.net/en_US/fbevents.js"):
            self.assertTrue(pe.should_block("script", h), h)

    def test_the_sites_own_requests_always_pass(self):
        for h in ("https://www.fandango.com/x", "https://tickets.fandango.com/seatpicker",
                  "https://www.cinemark.com/TicketSeatMap/", "https://www.regmovies.com/x"):
            for rt in ("document", "script", "stylesheet", "xhr", "fetch", "image"):
                self.assertFalse(pe.should_block(rt, h), f"{rt} {h}")

    def test_recaptcha_hosts_stay_allowed_but_map_widgets_do_not(self):
        self.assertTrue(pe.should_block("script", "https://maps.googleapis.com/maps/api/js"))
        # the checkout flow can require reCAPTCHA from these
        self.assertFalse(pe.should_block("script", "https://www.gstatic.com/recaptcha/api.js"))
        self.assertFalse(pe.should_block("script", "https://www.google.com/recaptcha/api.js"))

    def test_the_cloudflare_challenge_is_never_blocked(self):
        # 1.13 MB of a Cinemark page, but blocking it would fail the check
        self.assertFalse(pe.should_block("script", "https://challenges.cloudflare.com/turnstile/v0/api.js"))

    def test_a_lookalike_host_is_not_matched_by_suffix(self):
        self.assertFalse(pe.should_block("script", "https://notdoubleclick.net.example.com/x.js"))

    def test_trim_is_skipped_when_unmetered_and_never_raises(self):
        class Page:
            routed = False
            def route(self, pattern, handler):
                Page.routed = True
        pe.trim_page(Page(), pe.ByteBudget(0, "direct"))
        self.assertFalse(Page.routed)                 # direct runs unchanged
        pe.trim_page(Page(), pe.ByteBudget(50, "metered"))
        self.assertTrue(Page.routed)
        class Boom:
            def route(self, *a, **k):
                raise RuntimeError("nope")
        pe.trim_page(Boom(), pe.ByteBudget(50, "x"))  # swallowed
