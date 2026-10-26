"""Paper-trading tracker (2026-10-26)."""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import paper_trade as T  # noqa: E402

W = "2026-10-23"
RATIOS = {"after-friday": [("2026-09-%02d" % d, "m%d" % d, v) for d, v in
                           enumerate([0.1, -0.1, 0.05, -0.05, 0.0, 0.08, -0.08, 0.02], start=1)]}


def odds(at, prices, slug="clayface-obo", movie="Clayface", bid_ask=True):
    rows = []
    for i, (b, p) in enumerate(prices):
        rows.append({"logged_at": at, "weekend_of": W, "movie": movie, "event_slug": slug, "bracket": b,
                     "yes_price": p, "best_bid": (p - 0.01) if bid_ask else "",
                     "best_ask": (p + 0.01) if bid_ask else "", "last_trade": p, "volume": 100, "market_id": i})
    return rows


class PaperTradeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.pred = os.path.join(d, "pred.csv")
        self.odds = os.path.join(d, "odds.csv")
        with open(self.pred, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["logged_at", "weekend_of", "movie", "headline_mid_m",
                                              "forecast_stage", "poly_logged_at", "poly_event"])
            w.writeheader()
            # Market 90% on <22m; we say 23.5 with sigma ~0.15 -> we disagree.
            w.writerow({"logged_at": "2026-10-24T08:36:08Z", "weekend_of": W, "movie": "Clayface",
                        "headline_mid_m": "23.5", "forecast_stage": "after-friday",
                        "poly_logged_at": "2026-10-24T08:36:08Z", "poly_event": "clayface-obo"})
            # Same stage later: same bets must not be placed twice.
            w.writerow({"logged_at": "2026-10-24T12:00:00Z", "weekend_of": W, "movie": "Clayface",
                        "headline_mid_m": "23.4", "forecast_stage": "after-friday",
                        "poly_logged_at": "2026-10-24T12:00:00Z", "poly_event": "clayface-obo"})
            # No market: skipped.
            w.writerow({"logged_at": "2026-10-24T08:36:09Z", "weekend_of": W, "movie": "Wicker",
                        "headline_mid_m": "5.7", "forecast_stage": "after-friday", "poly_logged_at": "", "poly_event": ""})
        prices = [("<22m", 0.90), ("22m-25m", 0.08), ("25m-28m", 0.01), ("28m+", 0.01)]
        with open(self.odds, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(odds("x", prices)[0].keys()))
            w.writeheader()
            w.writerows(odds("2026-10-24T08:36:08Z", prices) + odds("2026-10-24T12:00:00Z", prices))

    def tearDown(self):
        self.tmp.cleanup()

    def test_places_edge_bets_once_per_stage_and_settles(self):
        trades, new, probs = T.place_bets(self.pred, self.odds, trades={}, ratios=RATIOS)
        ids = sorted(t["bet_id"].split("|")[3:5] for t in new)
        self.assertEqual(ids, [["22m-25m", "YES"], ["<22m", "NO"]])
        yes = next(t for t in new if t["side"] == "YES")
        self.assertEqual((yes["cost"], yes["entry_basis"]), ("0.0900", "ask"))     # ask = price + 0.01
        self.assertGreater(float(yes["our_prob"]) - 0.09, T.EDGE)
        self.assertEqual(len(trades), 2)                                           # 12:00 row added nothing
        self.assertEqual(len(probs), 8)                                            # 2 priced forecasts x 4 brackets
        self.assertAlmostEqual(sum(float(p["our_prob"]) for p in probs[:4]), 1.0, places=3)

        snaps = T.load_snapshots(self.odds)
        changed = T.settle(trades, snaps=snaps, finals={(W, "clayface"): 23.1}, provisionals={}, now="2026-10-28T12:00:00Z")
        self.assertEqual(changed, 2)
        self.assertTrue(all(t["status"] == "settled" and t["outcome_bracket"] == "22m-25m" for t in trades.values()))
        self.assertAlmostEqual(float(yes["pnl"]), 1 / 0.09 - 1, places=3)
        no = next(t for t in trades.values() if t["side"] == "NO")
        self.assertAlmostEqual(float(no["pnl"]), 1 / float(no["cost"]) - 1, places=3)
        self.assertEqual(T.settle(trades, snaps=snaps, finals={(W, "clayface"): 23.1}, provisionals={}), 0)

    def test_provisional_then_final(self):
        trades, _, _ = T.place_bets(self.pred, self.odds, trades={}, ratios=RATIOS)
        snaps = T.load_snapshots(self.odds)
        T.settle(trades, snaps=snaps, finals={}, provisionals={(W, "clayface"): 21.0})
        self.assertTrue(all(t["status"] == "provisional" and t["settled_at"] == "" for t in trades.values()))
        yes = next(t for t in trades.values() if t["side"] == "YES")
        self.assertEqual(float(yes["pnl"]), -1.0)
        T.settle(trades, snaps=snaps, finals={(W, "clayface"): 23.1}, provisionals={}, now="x")
        self.assertTrue(all(t["status"] == "settled" for t in trades.values()))
        self.assertGreater(float(yes["pnl"]), 0)

    def test_unfitted_stage_places_nothing(self):
        trades, new, probs = T.place_bets(self.pred, self.odds, trades={}, ratios={})
        self.assertEqual((trades, new, probs), ({}, [], []))

    def test_outcome_and_provisional_helpers(self):
        self.assertEqual(T.outcome_bracket(22.0, ["<22m", "22m-25m", "25m+"]), "22m-25m")
        self.assertEqual(T.outcome_bracket(1.3, ["<2M", "2-3M"]), "<2M")
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
            w = csv.writer(f)
            w.writerow(["weekend_of", "movie_title", "day_of_week", "gross_m", "source", "status", "as_of_date", "notes"])
            w.writerow([W, "Clayface", "Thursday", "3.5", "s", "reported", "2026-10-23", ""])
            w.writerow([W, "Clayface", "Friday", "6.9", "s", "reported", "2026-10-24", ""])
            w.writerow([W, "Clayface", "Friday", "7.1", "s", "reported", "2026-10-25", ""])   # revision wins
            w.writerow([W, "Clayface", "Saturday", "7.8", "s", "reported", "2026-10-25", ""])
            w.writerow([W, "Wildwood", "Friday", "3.0", "s", "reported", "2026-10-24", ""])      # incomplete
            path = f.name
        try:
            self.assertEqual(T.provisional_actuals(path), {})
            with open(path, "a", newline="") as f:
                csv.writer(f).writerow([W, "Clayface", "Sunday", "5.0", "s", "reported", "2026-10-26", ""])
            self.assertAlmostEqual(T.provisional_actuals(path)[(W, "clayface")], 23.4)
        finally:
            os.unlink(path)

    def test_report_mentions_sections(self):
        trades, new, _ = T.place_bets(self.pred, self.odds, trades={}, ratios=RATIOS)
        text = T.report(trades, new)
        self.assertIn("2 new bet(s)", text)
        self.assertIn("open (no actuals yet): 2", text)


if __name__ == "__main__":
    unittest.main()
