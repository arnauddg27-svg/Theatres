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

    def test_workflow_gives_both_lanes_the_secret_and_a_ceiling(self):
        yml = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        fan = yml.split("- name: Fandango snapshot", 1)[1].split("run: |", 1)[0]
        cin = yml.split("- name: Cinemark collect", 1)[1].split("run: |", 1)[0]
        for block, ceiling in ((fan, "FANDANGO_MAX_MB: '60'"), (cin, "CINEMARK_MAX_MB: '150'")):
            self.assertIn("AMC_SEAT_PROXY_URL: ${{ secrets.AMC_SEAT_PROXY_URL }}", block)
            self.assertIn(ceiling, block)
        self.assertIn("CINEMARK_PROXY_PER_THEATRE_CAP: '3'", cin)
        self.assertIn("FANDANGO_PROXY_RENDER_BUDGET: '55'", fan)


if __name__ == "__main__":
    unittest.main()
