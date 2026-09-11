"""Streaming HTTP seat fetch (2026-09-10): same counts as COUNT_SEATS_JS from
a fraction of the bytes, with early stop and browser fallback."""
import gzip
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import seat_fetch_http as sfh  # noqa: E402
import scraper  # noqa: E402

SEATS_HTML = """<html><head><title>Select Seats | AMC Theatres</title></head><body><main>
<form>
<input type="checkbox" aria-label="Recliner A1" disabled>
<input type="checkbox" aria-label="Recliner A2" disabled="">
<input type="checkbox" aria-label="Recliner A3">
<input type="checkbox" aria-label="Seat B1">
<input type="checkbox" aria-label="AMC Club Rocker C4" disabled="disabled">
<input type="checkbox" aria-label="Wheelchair D1">
<input type="checkbox" aria-label="Companion D2" disabled>
<input type="search" aria-label="Search movies">
<input type="checkbox" aria-label='Seat &quot;E1&quot;'>
</form></main>
<script>self.__next_f.push([1,"...huge rsc payload..."])</script>
""" + "".join("<script>self.__next_f.push([1,\"" + __import__("os").urandom(2500).hex() + "\"])</script>\n"
              for _ in range(40)) + "</body></html>"   # incompressible payload, like the real RSC data


class ParserParityTest(unittest.TestCase):
    def test_counts_match_the_dom_rules(self):
        c = sfh.parse_seat_counts(SEATS_HTML)
        # 6 seat inputs (A1 A2 A3 B1 C4 "E1"), wheelchair+companion skipped, search skipped
        self.assertEqual({"total_seats": 6, "seats_sold": 3, "seats_available": 3, "occupancy_pct": 50.0}, c)

    def test_disabled_detection_forms(self):
        for tag, want in [('<input aria-label="Seat A1" disabled>', True),
                          ('<input aria-label="Seat A1" disabled="">', True),
                          ('<input aria-label="Seat A1" disabled="disabled"/>', True),
                          ('<input disabled aria-label="Seat A1">', True),
                          ('<input aria-label="Seat A1" data-disabledx="1">', False),
                          ('<input aria-label="Seat A1" class="disabled-look">', False)]:
            with self.subTest(tag=tag):
                self.assertEqual(want, sfh.parse_seat_counts(tag)["seats_sold"] == 1)

    def test_no_seats_is_none_and_classification(self):
        self.assertIsNone(sfh.parse_seat_counts("<html><input aria-label='Search'></html>"))
        self.assertEqual("seats", sfh.classify_page(SEATS_HTML))
        self.assertEqual("blocked", sfh.classify_page("<title>Attention Required! | Cloudflare</title>Sorry, you have been blocked"))
        self.assertEqual("challenge", sfh.classify_page("<title>Just a moment...</title>"))
        self.assertEqual("other", sfh.classify_page("<title>Select Seats</title><p>We use cookies</p>"))

    def test_early_stop_rule_only_counts_markers_after_the_last_seat_input(self):
        # no seat input yet -> never stop, even on a marker
        self.assertFalse(sfh.should_stop(b"<script>self.__next_f.push(1)</script>", -1))
        buf = b"<script>self.__next_f.push(1)</script><input aria-label='Seat A1'><input aria-label='Seat A2'>"
        pos = sfh.last_seat_input_pos(buf)
        self.assertGreater(pos, 0)
        # marker BEFORE the seats must not stop the read (Next.js interleaves flight scripts)
        self.assertFalse(sfh.should_stop(buf, pos))
        # marker AFTER the last seat input ends the read
        self.assertTrue(sfh.should_stop(buf + b" disabled></form></main>", pos))
        self.assertTrue(sfh.should_stop(buf + b"<script>self.__next_f.push(", pos))
        # incremental rescan finds an input that straddles a chunk boundary
        whole = b"x" * 1000 + b"<input aria-label='Seat B1'>"
        self.assertEqual(sfh.last_seat_input_pos(whole), sfh.last_seat_input_pos(whole, search_from=990))
        self.assertEqual(-1, sfh.last_seat_input_pos(whole, search_from=1010))


class FakeResp:
    def __init__(self, body, encoding="gzip", chunk=4096):
        self.body = gzip.compress(body) if encoding == "gzip" else body
        self.headers = {"content-encoding": encoding} if encoding else {}
        self.status_code = 200
        self.chunk = chunk
        self.served = 0
        self.closed = False

    def iter_content(self, chunk_size=None):
        for i in range(0, len(self.body), self.chunk):
            self.served += len(self.body[i:i + self.chunk])
            yield self.body[i:i + self.chunk]

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, resp):
        self.resp = resp
        self.calls = []

    def get(self, url, **kw):
        self.calls.append((url, kw))
        return self.resp


class StreamingFetchTest(unittest.TestCase):
    def test_stops_early_and_counts_raw_bytes(self):
        resp = FakeResp(SEATS_HTML.encode(), encoding="gzip", chunk=2048)
        sess = FakeSession(resp)
        res = sfh.fetch_seat_page("https://www.amctheatres.com/showtimes/1/seats",
                                  "http://u:p@gw:823", session=sess)
        self.assertEqual("seats", res["kind"])
        self.assertTrue(res["stopped_early"])
        self.assertEqual(6, sfh.parse_seat_counts(res["html"])["total_seats"])
        self.assertLess(res["raw_bytes"], len(resp.body))       # did not read the whole payload
        self.assertEqual(res["raw_bytes"], resp.served)         # raw == wire bytes served
        self.assertTrue(resp.closed)
        self.assertEqual({"http": "http://u:p@gw:823", "https": "http://u:p@gw:823"}, sess.calls[0][1]["proxies"])

    def test_identity_encoding_and_block_page(self):
        resp = FakeResp(b"<title>Attention Required! | Cloudflare</title><p>Sorry, you have been blocked</p>", encoding=None)
        res = sfh.fetch_seat_page("https://x/seats", None, session=FakeSession(resp))
        self.assertEqual("blocked", res["kind"])
        self.assertFalse(res["stopped_early"])


class ParityToleranceTest(unittest.TestCase):
    def test_browser_may_show_a_couple_more_sold_never_fewer(self):
        h = {"total_seats": 100, "seats_sold": 10}
        self.assertTrue(scraper._seat_counts_match(h, {"total_seats": 100, "seats_sold": 10}))
        self.assertTrue(scraper._seat_counts_match(h, {"total_seats": 100, "seats_sold": 12}))
        self.assertFalse(scraper._seat_counts_match(h, {"total_seats": 100, "seats_sold": 13}))
        self.assertFalse(scraper._seat_counts_match(h, {"total_seats": 100, "seats_sold": 9}))
        self.assertFalse(scraper._seat_counts_match(h, {"total_seats": 101, "seats_sold": 10}))
        self.assertFalse(scraper._seat_counts_match(None, h))


class DispatcherTest(unittest.TestCase):
    def setUp(self):
        self.orig = dict(scraper._HTTP_STATE), scraper._SEAT_PROXY, scraper.AMC_SEAT_FETCH
        scraper._HTTP_STATE.update(checked=0, mismatch=0, disabled=False, disabled_reason="",
                                   http_ok=0, http_fallback=0, http_blocked=0, http_bytes=0)

    def tearDown(self):
        st, proxy, mode = self.orig
        scraper._HTTP_STATE.update(st); scraper._SEAT_PROXY = proxy; scraper.AMC_SEAT_FETCH = mode

    def _run(self, coro):
        import asyncio
        return asyncio.run(coro)

    def test_auto_mode_is_off_without_proxy_and_on_with_it(self):
        scraper.AMC_SEAT_FETCH = "auto"
        scraper._SEAT_PROXY = None
        self.assertFalse(scraper._http_seat_fetch_enabled())
        scraper._SEAT_PROXY = {"server": "http://gw:823", "username": "u", "password": "p@ss/x"}
        self.assertTrue(scraper._http_seat_fetch_enabled())
        self.assertEqual("http://u:p%40ss%2Fx@gw:823", scraper._http_proxy_url())

    def test_parity_mismatch_disables_http_and_uses_browser(self):
        scraper.AMC_SEAT_FETCH = "http"
        http_result = {"total_seats": 100, "seats_sold": 10, "seats_available": 90, "occupancy_pct": 10.0}
        # a DIFFERENT auditorium size is a real disagreement (a couple more sold
        # seats in the later browser read is not — see ParityToleranceTest)
        browser_result = {"total_seats": 98, "seats_sold": 10, "seats_available": 88, "occupancy_pct": 10.2}
        async def fake_http(sid): return dict(http_result)
        async def fake_pw(page, sid): return dict(browser_result)
        orig = (scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw)
        try:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw = fake_http, fake_pw
            with redirect_stdout(io.StringIO()) as buf:
                out = self._run(scraper.fetch_amc_seat_map(None, "1"))
            self.assertEqual(browser_result, out)                 # browser wins on disagreement
            # ONE strike is not enough (a hot auditorium can sell seats between reads)
            self.assertFalse(scraper._HTTP_STATE["disabled"])
            self.assertIn("strike 1/2", buf.getvalue())
            with redirect_stdout(io.StringIO()):
                self._run(scraper.fetch_amc_seat_map(None, "2"))
            self.assertTrue(scraper._HTTP_STATE["disabled"])
            self.assertEqual("parity", scraper._HTTP_STATE["disabled_reason"])
            # disabled -> straight to the browser afterwards
            out2 = self._run(scraper.fetch_amc_seat_map(None, "3"))
            self.assertEqual(browser_result, out2)
        finally:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw = orig

    def test_breaker_disables_http_after_only_fallbacks(self):
        scraper.AMC_SEAT_FETCH = "http"
        async def fake_http(sid): return None
        async def fake_pw(page, sid): return {"total_seats": 5, "seats_sold": 1}
        orig = (scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw, scraper.AMC_HTTP_FALLBACK_BREAKER)
        try:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw = fake_http, fake_pw
            scraper.AMC_HTTP_FALLBACK_BREAKER = 5
            with redirect_stdout(io.StringIO()) as buf:
                for i in range(6):
                    self._run(scraper.fetch_amc_seat_map(None, str(i)))
            self.assertTrue(scraper._HTTP_STATE["disabled"])
            self.assertEqual("breaker", scraper._HTTP_STATE["disabled_reason"])
            self.assertIn("DISABLED for this leg", buf.getvalue())
            self.assertEqual(5, scraper._HTTP_STATE["http_fallback"])   # 6th call went straight to the browser
        finally:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw, scraper.AMC_HTTP_FALLBACK_BREAKER = orig

    def test_http_none_falls_back_and_sentinels_pass_through(self):
        scraper.AMC_SEAT_FETCH = "http"
        calls = []
        async def fake_http(sid): return None if sid == "1" else scraper.CF_BLOCK_SENTINEL
        async def fake_pw(page, sid): calls.append(sid); return {"total_seats": 5, "seats_sold": 1}
        orig = (scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw)
        try:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw = fake_http, fake_pw
            with redirect_stdout(io.StringIO()):
                self.assertEqual({"total_seats": 5, "seats_sold": 1}, self._run(scraper.fetch_amc_seat_map(None, "1")))
                self.assertIs(scraper.CF_BLOCK_SENTINEL, self._run(scraper.fetch_amc_seat_map(None, "2")))
            self.assertEqual(["1"], calls)
            self.assertEqual(1, scraper._HTTP_STATE["http_fallback"])
        finally:
            scraper.fetch_amc_seat_map_http, scraper.fetch_amc_seat_map_pw = orig


if __name__ == "__main__":
    unittest.main()


class CurlProxyMarkerTest(unittest.TestCase):
    def test_only_true_refusals_are_proxy_errors(self):
        self.assertTrue(scraper._is_proxy_error("Failed to perform, curl: (56) Received HTTP code 407 from proxy after CONNECT"))
        self.assertTrue(scraper._is_proxy_error("CONNECT tunnel failed, response 403"))
        # one exit misbehaving is not a provider refusal — falls through to the browser
        self.assertFalse(scraper._is_proxy_error("Failed to perform, curl: (7) Failed to connect to gw port 823"))
        self.assertFalse(scraper._is_proxy_error("curl: (56) Received HTTP code 502 from proxy after CONNECT"))


class RealClientApiPinTest(unittest.TestCase):
    def test_make_session_accepts_our_options_and_fetch_raises_a_curl_error_not_typeerror(self):
        # audit-12: the FakeSession accepts any kwargs, which let a per-request
        # curl_options TypeError reach production. Pin the real API against a
        # closed port: the failure must be curl_cffi's, never a TypeError.
        from curl_cffi.requests.exceptions import RequestException
        sess = sfh.make_session()
        with self.assertRaises(RequestException):
            sfh.fetch_seat_page("http://127.0.0.1:9/seats", None, session=sess, timeout=2)

    def test_seat_input_anchor_ignores_non_seat_inputs(self):
        buf = b"<input aria-label='Search movies'><script>self.__next_f.push(1)</script>"
        self.assertEqual(-1, sfh.last_seat_input_pos(buf))          # header search is not an anchor
        buf2 = buf + b"<input aria-label='Seat A1'>"
        self.assertGreater(sfh.last_seat_input_pos(buf2), 0)
        self.assertFalse(sfh.should_stop(bytearray(buf2), sfh.last_seat_input_pos(buf2)))  # marker was BEFORE

    def test_result_carries_final_url_for_queue_detection(self):
        resp = FakeResp(b"<title>x</title>", encoding=None)
        resp.url = "https://queue.amctheatres.com/?c=amc"
        res = sfh.fetch_seat_page("https://www.amctheatres.com/showtimes/1/seats", None, session=FakeSession(resp))
        self.assertEqual("https://queue.amctheatres.com/?c=amc", res["url"])


class RscSeatParserTest(unittest.TestCase):
    PAYLOAD = (b'...,{"node":{"code":"descriptivevideo"}}]},"seatingLayout":{"columns":3,"rows":2,"seats":['
               b'{"available":false,"column":1,"row":1,"name":"","type":"NotASeat","seatTier":"Regular","shouldDisplay":false},'
               b'{"available":true,"column":2,"row":1,"name":"A2","type":"LoveSeatLeft","seatTier":"Regular","shouldDisplay":true},'
               b'{"available":false,"column":3,"row":1,"name":"A1","type":"LoveSeatRight","seatTier":"Regular","shouldDisplay":true},'
               b'{"available":true,"column":1,"row":2,"name":"B3","type":"Wheelchair","seatTier":"Regular","shouldDisplay":true},'
               b'{"available":true,"column":2,"row":2,"name":"B2","type":"Companion","seatTier":"Regular","shouldDisplay":true},'
               b'{"available":false,"column":3,"row":2,"name":"B1","type":"Recliner","seatTier":"Premium","shouldDisplay":true}]}}...')

    def test_counts_with_markup_exclusions(self):
        self.assertEqual({"total_seats": 3, "seats_sold": 2, "seats_available": 1, "occupancy_pct": 66.7},
                         sfh.parse_rsc_seats(self.PAYLOAD))

    def test_no_layout_is_none(self):
        self.assertIsNone(sfh.parse_rsc_seats(b'{"foo":1}'))
        self.assertIsNone(sfh.parse_rsc_seats(b'"seatingLayout":{"seats":[]}'))


class RscFirstDispatchTest(unittest.TestCase):
    def setUp(self):
        self.orig_state = dict(scraper._RSC_STATE)
        scraper._RSC_STATE.update(ok=0, fallback=0, checked=0, mismatch=0, disabled=False, bytes=0)
        self.orig_http = dict(scraper._HTTP_STATE)
        scraper._HTTP_STATE.update(http_blocked=0)
        self.orig_fns = (sfh.fetch_rsc_seat_page, sfh.fetch_seat_page, scraper._SEAT_PROXY, scraper.AMC_SEAT_RSC)
        scraper._SEAT_PROXY = {"server": "http://gw:1", "username": "u", "password": "p"}
        scraper.AMC_SEAT_RSC = True

    def tearDown(self):
        scraper._RSC_STATE.update(self.orig_state); scraper._HTTP_STATE.update(self.orig_http)
        sfh.fetch_rsc_seat_page, sfh.fetch_seat_page, scraper._SEAT_PROXY, scraper.AMC_SEAT_RSC = self.orig_fns

    def _run(self, coro):
        import asyncio
        return asyncio.run(coro)

    def test_rsc_result_wins_and_is_shadow_checked_against_the_page(self):
        counts = {"total_seats": 100, "seats_sold": 10, "seats_available": 90, "occupancy_pct": 10.0}
        page_html = "".join(f'<input aria-label="Seat A{i}"{" disabled" if i <= 10 else ""}>' for i in range(1, 101)) + "</main>"
        sfh.fetch_rsc_seat_page = lambda url, proxy, session=None, timeout=30: {"counts": dict(counts), "raw_bytes": 100000, "status": 200, "url": url, "kind": "seats"}
        sfh.fetch_seat_page = lambda url, proxy, session=None, timeout=30: {"html": page_html, "raw_bytes": 180000, "status": 200, "url": url, "kind": "seats", "stopped_early": True}
        scraper._HTTP_STATE["session"] = object()
        with redirect_stdout(io.StringIO()):
            out = self._run(scraper.fetch_amc_seat_map_http("1"))
        self.assertEqual(counts, out)
        self.assertEqual((1, 1, 0, False), (scraper._RSC_STATE["ok"], scraper._RSC_STATE["checked"], scraper._RSC_STATE["mismatch"], scraper._RSC_STATE["disabled"]))

    def test_rsc_disagreement_disables_rsc_and_uses_the_page(self):
        sfh.fetch_rsc_seat_page = lambda url, proxy, session=None, timeout=30: {"counts": {"total_seats": 90, "seats_sold": 5, "seats_available": 85, "occupancy_pct": 5.6}, "raw_bytes": 1, "status": 200, "url": url, "kind": "seats"}
        page_html = "".join(f'<input aria-label="Seat A{i}">' for i in range(1, 101))
        sfh.fetch_seat_page = lambda url, proxy, session=None, timeout=30: {"html": page_html, "raw_bytes": 1, "status": 200, "url": url, "kind": "seats", "stopped_early": False}
        scraper._HTTP_STATE["session"] = object()
        with redirect_stdout(io.StringIO()) as buf:
            out = self._run(scraper.fetch_amc_seat_map_http("2"))
        self.assertEqual(100, out["total_seats"])
        self.assertTrue(scraper._RSC_STATE["disabled"]); self.assertIn("RSC path DISABLED", buf.getvalue())
        # disabled -> page path only, no rsc call
        sfh.fetch_rsc_seat_page = lambda *a, **k: (_ for _ in ()).throw(AssertionError("rsc must not be called"))
        with redirect_stdout(io.StringIO()):
            out2 = self._run(scraper.fetch_amc_seat_map_http("3"))
        self.assertEqual(100, out2["total_seats"])

    def test_rsc_none_falls_back_to_page_and_block_pages_are_sentinels(self):
        sfh.fetch_rsc_seat_page = lambda url, proxy, session=None, timeout=30: {"counts": None, "raw_bytes": 1, "status": 200, "url": url, "kind": "other"}
        sfh.fetch_seat_page = lambda url, proxy, session=None, timeout=30: {"html": '<input aria-label="Seat A1" disabled>', "raw_bytes": 1, "status": 200, "url": url, "kind": "seats", "stopped_early": False}
        scraper._HTTP_STATE["session"] = object()
        with redirect_stdout(io.StringIO()):
            out = self._run(scraper.fetch_amc_seat_map_http("4"))
        self.assertEqual(1, out["total_seats"]); self.assertEqual(1, scraper._RSC_STATE["fallback"])
        sfh.fetch_rsc_seat_page = lambda url, proxy, session=None, timeout=30: {"counts": None, "raw_bytes": 1, "status": 403, "url": url, "kind": "blocked"}
        with redirect_stdout(io.StringIO()):
            self.assertIs(scraper.CF_BLOCK_SENTINEL, self._run(scraper.fetch_amc_seat_map_http("5")))


class SegmentDiffTest(unittest.TestCase):
    FLIGHT_ROW = (b'0:{"P":null,"b":"abc","p":"","c":["","showtimes","145887232","seats"],"i":false,"f":[[["",{"children":["(headless)",'
                  b'{"children":["showtimes",{"children":[["showtimeId","145887232","d",null],{"children":["seats",{"children":["__PAGE__",{}]},'
                  b'"$undefined","$undefined",4]},"$undefined","$undefined",8]},"$undefined","$undefined",12]},"$undefined","$undefined",12]},'
                  b'"$undefined","$undefined",24],["x"],null,null]],"m":"$undefined","G":["$1",[]],"s":false,"S":true}\n1:"$Sreact.fragment"\n')

    def test_sanitize_matches_what_the_browser_sends(self):
        t = sfh.sanitize_router_tree(["", {"children": ["seats", {"children": ["__PAGE__", {}]}, "$undefined", "$undefined", 4]}, "$undefined", "$undefined", 24])
        self.assertEqual(["", {"children": ["seats", {"children": ["__PAGE__", {}]}, None, None]}, None, None], t)

    def test_extract_learns_the_template_from_a_full_payload(self):
        tree = sfh.extract_router_tree(self.FLIGHT_ROW)
        self.assertIsNotNone(tree)
        s = __import__("json").dumps(tree, separators=(",", ":"))
        self.assertIn('["showtimeId","__SHOWTIME__","d",null]', s)
        self.assertNotIn("$undefined", s)
        self.assertEqual(tree, sfh.ROUTER_TREE_TEMPLATE)          # today's live shape
        self.assertIsNone(sfh.extract_router_tree(b'0:{"nope":1}\n'))

    def test_header_names_another_showtime(self):
        h = sfh.router_tree_header(sfh.ROUTER_TREE_TEMPLATE, "999")
        from urllib.parse import unquote
        self.assertIn('["showtimeId","999","d",null]', unquote(h))
        self.assertNotIn("__SHOWTIME__", unquote(h))
        self.assertNotIn(" ", h)


class DiffFirstChainTest(unittest.TestCase):
    def setUp(self):
        self.orig_state = dict(scraper._RSC_STATE)
        scraper._RSC_STATE.update(ok=0, fallback=0, checked=0, mismatch=0, disabled=False, bytes=0,
                                  diff_ok=0, diff_fallback=0, diff_bytes=0, tree=None, last_id="1")
        self.orig = (sfh.fetch_rsc_seat_diff, sfh.fetch_rsc_seat_page, sfh.fetch_seat_page, scraper._SEAT_PROXY,
                     scraper.AMC_SEAT_RSC, scraper.AMC_SEAT_RSC_DIFF, scraper.AMC_RSC_PARITY_CHECKS)
        scraper._SEAT_PROXY = {"server": "http://gw:1", "username": "u", "password": "p"}
        scraper.AMC_SEAT_RSC = True; scraper.AMC_SEAT_RSC_DIFF = True; scraper.AMC_RSC_PARITY_CHECKS = 0
        scraper._HTTP_STATE["session"] = object()

    def tearDown(self):
        scraper._RSC_STATE.update(self.orig_state)
        (sfh.fetch_rsc_seat_diff, sfh.fetch_rsc_seat_page, sfh.fetch_seat_page, scraper._SEAT_PROXY,
         scraper.AMC_SEAT_RSC, scraper.AMC_SEAT_RSC_DIFF, scraper.AMC_RSC_PARITY_CHECKS) = self.orig

    def _run(self, coro):
        import asyncio
        return asyncio.run(coro)

    def test_diff_wins_and_rotates_the_other_showtime(self):
        seen = []
        def fake_diff(url, proxy, header, session=None, timeout=30):
            from urllib.parse import unquote
            seen.append(unquote(header))
            return {"counts": {"total_seats": 50, "seats_sold": 5, "seats_available": 45, "occupancy_pct": 10.0},
                    "raw_bytes": 8700, "status": 200, "url": url, "kind": "seats"}
        sfh.fetch_rsc_seat_diff = fake_diff
        sfh.fetch_rsc_seat_page = lambda *a, **k: (_ for _ in ()).throw(AssertionError("full payload must not be fetched"))
        with redirect_stdout(io.StringIO()):
            out1 = self._run(scraper.fetch_amc_seat_map_http("100"))
            out2 = self._run(scraper.fetch_amc_seat_map_http("200"))
        self.assertEqual(50, out1["total_seats"]); self.assertEqual(50, out2["total_seats"])
        self.assertIn('"showtimeId","1"', seen[0])          # first: sentinel other id
        self.assertIn('"showtimeId","100"', seen[1])        # then: the previous showtime
        self.assertEqual(2, scraper._RSC_STATE["diff_ok"])
        self.assertLess(scraper._RSC_STATE["diff_bytes"], 2 * 12000)

    def test_diff_miss_falls_back_to_full_payload_and_learns_the_tree(self):
        sfh.fetch_rsc_seat_diff = lambda url, proxy, header, session=None, timeout=30: {"counts": None, "raw_bytes": 21, "status": 500, "url": url, "kind": "other"}
        sfh.fetch_rsc_seat_page = lambda url, proxy, session=None, timeout=30: {"counts": {"total_seats": 7, "seats_sold": 1, "seats_available": 6, "occupancy_pct": 14.3},
                                                                                "raw_bytes": 119000, "status": 200, "url": url, "kind": "seats", "payload": SegmentDiffTest.FLIGHT_ROW}
        with redirect_stdout(io.StringIO()):
            out = self._run(scraper.fetch_amc_seat_map_http("300"))
        self.assertEqual(7, out["total_seats"])
        self.assertEqual(1, scraper._RSC_STATE["diff_fallback"])
        self.assertEqual(sfh.ROUTER_TREE_TEMPLATE, scraper._RSC_STATE["tree"])   # learned from the payload

    def test_diff_block_page_is_a_sentinel(self):
        sfh.fetch_rsc_seat_diff = lambda url, proxy, header, session=None, timeout=30: {"counts": None, "raw_bytes": 3000, "status": 403, "url": url, "kind": "blocked"}
        with redirect_stdout(io.StringIO()):
            self.assertIs(scraper.CF_BLOCK_SENTINEL, self._run(scraper.fetch_amc_seat_map_http("400")))
