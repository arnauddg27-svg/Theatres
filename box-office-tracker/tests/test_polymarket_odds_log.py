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


class PredictionAnnotationTest(unittest.TestCase):
    def test_bracket_labels(self):
        self.assertEqual(L.bracket_range("<22m"), (None, 22.0))
        self.assertEqual(L.bracket_range("22m-25m"), (22.0, 25.0))
        self.assertEqual(L.bracket_range("2-3M"), (2.0, 3.0))
        self.assertEqual(L.bracket_range("37m+"), (37.0, None))
        self.assertIsNone(L.bracket_range("Yes"))

    def test_market_summary(self):
        out = L.market_summary([("<8m", .001), ("8m-10m", .015), ("10m-12m", .745),
                                ("12m-14m", .188), ("14m-16m", .003), ("18m+", .002)], 13.34)
        self.assertEqual((out["poly_bracket"], out["poly_bracket_prob"]), ("12m-14m", 0.188))
        self.assertEqual((out["poly_favorite"], out["poly_favorite_prob"]), ("10m-12m", 0.745))
        self.assertAlmostEqual(out["poly_implied_mid_m"], 11.24, places=2)
        low = L.market_summary([("<2M", .99), ("2-3M", .01)], 1.08)
        self.assertEqual(low["poly_bracket"], "<2M")
        self.assertGreaterEqual(low["poly_implied_mid_m"], 0)

    def test_annotates_nearest_snapshot_of_main_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            pred = os.path.join(tmp, "pred.csv")
            odds = os.path.join(tmp, "odds.csv")
            with open(pred, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["logged_at", "weekend_of", "movie", "headline_mid_m", "user_col"])
                w.writerow(["2026-10-24T08:36:08Z", "2026-10-23", "Clayface", "22.48", "keep"])
                w.writerow(["2026-10-24T08:36:09Z", "2026-10-23", "Wicker", "5.72", ""])
                w.writerow(["2026-10-20T08:36:09Z", "2026-10-23", "Clayface", "25.0", ""])  # no snapshot near
            snap = lambda at, slug, b, p, v: {  # noqa: E731
                "logged_at": at, "weekend_of": "2026-10-23", "movie": "Clayface", "event_slug": slug,
                "bracket": b, "yes_price": p, "best_bid": "", "best_ask": "", "last_trade": "",
                "volume": v, "market_id": "1"}
            L.append([snap("2026-10-24T08:40:00Z", "clayface-obo", "<22m", .3, 100),
                      snap("2026-10-24T08:40:00Z", "clayface-obo", "22m-25m", .7, 100),
                      snap("2026-10-24T08:40:00Z", "clayface-tighter", "22-23m", .9, 5),
                      snap("2026-10-24T03:00:00Z", "clayface-obo", "22m-25m", .1, 100)], odds)
            self.assertEqual(L.annotate_prediction_log(pred, odds), 1)
            with open(pred, newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["poly_event"], "clayface-obo")
            self.assertEqual(rows[0]["poly_logged_at"], "2026-10-24T08:40:00Z")
            self.assertEqual((rows[0]["poly_bracket"], rows[0]["poly_bracket_prob"]), ("22m-25m", "0.7"))
            self.assertEqual(rows[0]["user_col"], "keep")
            self.assertEqual(rows[1]["poly_bracket"], "")      # Wicker: no market
            self.assertEqual(rows[2]["poly_logged_at"], "")    # too far from any snapshot
            self.assertEqual(L.annotate_prediction_log(pred, odds), 0)  # idempotent
