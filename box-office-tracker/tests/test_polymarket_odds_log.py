"""Timestamped Polymarket odds log (2026-10-24)."""
import csv
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import log_polymarket_odds as L  # noqa: E402

NOW = datetime(2026, 10, 24, 15, 23, tzinfo=timezone.utc)


def event(title, slug, end, brackets, closed=False):
    return {"title": title, "slug": slug, "endDate": end, "closed": closed, "markets": [
        {"id": i, "groupItemTitle": b, "outcomePrices": json.dumps([str(p), str(1 - p)]),
         "bestBid": p - 0.01, "bestAsk": p + 0.01, "lastTradePrice": p, "volume": "100", "closed": False}
        for i, (b, p) in enumerate(brackets)]}


EVENTS = [
    event('"Wildwood" Opening Weekend Box Office', "wildwood-opening-weekend-box-office",
          "2026-10-25T12:00:00Z", [("10m-12m", 0.745), ("12m-14m", 0.188)]),
    event("“Clayface” Opening Weekend Box Office", "clayface-obo",
          "2026-10-26T03:59:00Z", [("22m-25m", 0.72)]),
    event('"Street Fighter" 2nd Weekend Box Office', "sf-2nd", "2026-10-25T12:00:00Z", [("x", 0.5)]),
    event('"Old" Opening Weekend Box Office', "old", "2026-10-18T12:00:00Z", [("x", 0.5)], closed=True),
]


class OddsLogTest(unittest.TestCase):
    def test_rows_only_live_opening_weekend_brackets(self):
        rows = L.odds_rows(EVENTS, NOW)
        self.assertEqual([(r["movie"], r["bracket"]) for r in rows],
                         [("Wildwood", "10m-12m"), ("Wildwood", "12m-14m"), ("Clayface", "22m-25m")])
        self.assertTrue(all(r["logged_at"] == "2026-10-24T15:23:00Z" for r in rows))
        self.assertAlmostEqual(rows[0]["yes_price"], 0.745)

    def test_weekend_from_market_end_date(self):
        self.assertEqual({r["weekend_of"] for r in L.odds_rows(EVENTS, NOW)}, {"2026-10-23"})
        self.assertEqual(L.event_weekend({"endDate": "2026-11-22T12:00:00Z"}, NOW), "2026-11-20")
        self.assertEqual(L.event_weekend({}, NOW), "2026-10-23")
        self.assertEqual(L.opening_weekend_friday(datetime(2026, 10, 21, tzinfo=timezone.utc)), "2026-10-23")

    def test_append_writes_header_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "odds.csv")
            rows = L.odds_rows(EVENTS, NOW)
            L.append(rows, path)
            L.append(rows, path)
            with open(path, newline="") as f:
                data = list(csv.DictReader(f))
            self.assertEqual(len(data), 2 * len(rows))
            self.assertEqual(data[0]["movie"], "Wildwood")


if __name__ == "__main__":
    unittest.main()
