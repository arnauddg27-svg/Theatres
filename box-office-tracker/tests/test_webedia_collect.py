import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import webedia_collect as W  # noqa: E402

TH = {"id": "X0KAO", "name": "Landmark Glendale 12, Indianapolis",
      "timeZone": "America/Indiana/Indianapolis", "screens": 12}


def st(starts, rate, screen="6"):
    return {"id": f"m-{starts}", "startsAt": starts, "isExpired": False,
            "tags": ["Auditorium.Comfort.ReservedSeating", "Format.Projection.Digital"],
            "data": {"ticketing": [{"urls": ["https://booking.example/launch/ticketing/abc"]}]},
            "occupancy": {"rate": rate}, "screen": {"name": screen}}


class WebediaTest(unittest.TestCase):
    def test_theatres_from_static(self):
        blob = {"data": {"x": [{"__typename": "Theater", "id": "X0KAO", "name": TH["name"],
                                "timeZone": TH["timeZone"], "screens": [{"number": 1}, {"number": 2}]},
                               {"__typename": "Theater", "id": "X0NOTZ"}]}}
        got = W.theatres_from_static(blob)
        self.assertEqual([("X0KAO", 2)], [(t["id"], t["screens"]) for t in got])   # no-tz entry skipped

    def test_schedule_url_is_compact_json(self):
        # spaces in the theaters JSON made the endpoint answer HTTP 500
        u = W.schedule_url("https://x", TH, "2026-09-27", "2026-09-28")
        self.assertIn("%22id%22%3A%22X0KAO%22%2C%22timeZone%22", u)
        self.assertIn("from=2026-09-27T03%3A00%3A00", u)

    def test_showings_and_rows(self):
        sched = {"X0KAO": {"schedule": {"267335": {"2026-09-27": [st("2026-09-27T12:50:00", 3),
                                                                  st("2026-09-27T19:45:00", 2)]},
                                        "999": {"2026-09-27": [st("2026-09-27T13:00:00", None)]}}}}
        sh = W.showings(sched, "X0KAO")
        self.assertEqual(3, len(sh))
        now = datetime(2026, 9, 27, 18, 30, tzinfo=timezone.utc)      # 14:30 EDT
        rows = [W.build_row("LMRK", TH, "Film", d, s, "2026-09-25", "r", now) for _m, d, s in sh]
        self.assertIsNone(rows[2])                                    # no published rate -> skipped
        started, upcoming = rows[0], rows[1]
        self.assertEqual("post-show-census", started["row_kind"])     # 12:50 local has started
        self.assertEqual("webedia-api", upcoming["row_kind"])
        self.assertEqual(3.0, started["occupancy_pct"])
        self.assertEqual("", started["reserved_seats"])               # seats are not published
        self.assertEqual("X0KAO:2026-09-27T12:50:00:6", started["showtime_id"])
        self.assertEqual(315, upcoming["minutes_until_showtime"])      # 19:45 EDT = 23:45Z
        self.assertEqual("LMRK", started["chain"])


if __name__ == "__main__":
    unittest.main()


class DiscoveryCacheTest(unittest.TestCase):
    """2026-09-28 14:15Z: all seven sites returned no theatres for ~15 min and
    three passes failed; discovery now falls back to the last good list."""

    def test_falls_back_to_cached_list(self):
        import tempfile, os
        class Dead:
            def get(self, url, timeout=None): raise ConnectionError("cdn")
        class Resp:
            def __init__(self, j): self._j = j
            def json(self): return self._j
        class Live:
            def get(self, url, timeout=None):
                if url.endswith("index/page-data.json"): return Resp({"staticQueryHashes": ["h1"]})
                return Resp({"data": [{"__typename": "Theater", "id": "X0KAO", "name": TH["name"],
                                      "timeZone": TH["timeZone"], "screens": []}]})
        with tempfile.TemporaryDirectory() as d:
            old = W.THEATRES_CACHE; W.THEATRES_CACHE = Path(d) / "theatres-webedia.json"
            try:
                self.assertEqual([], W.discover_theatres(Dead(), "https://x", chain="LMRK"))       # nothing cached yet
                self.assertEqual(["X0KAO"], [t["id"] for t in W.discover_theatres(Live(), "https://x", chain="LMRK")])
                self.assertEqual(["X0KAO"], [t["id"] for t in W.discover_theatres(Dead(), "https://x", chain="LMRK")])  # cache
                self.assertEqual([], W.discover_theatres(Dead(), "https://x", chain="SHOW"))       # other chain: no cache
            finally:
                W.THEATRES_CACHE = old
