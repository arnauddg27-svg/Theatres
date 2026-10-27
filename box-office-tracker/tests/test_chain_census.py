"""Phase C — chain census: completeness, LOO shares, pooling, blend (2026-10-27)."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chain_census as CC  # noqa: E402

W = "2026-10-23"


def cell(seats, dollars, showings, theatres=100):
    return {"seats": seats, "dollars": dollars, "showings": showings, "theatres": theatres}


class CompletenessTest(unittest.TestCase):
    def test_regime_and_theatre_rules(self):
        by_date = {
            "2026-10-22": {"AMC": cell(1000, 13000, 200, 400), "CNMK": cell(500, 6500, 300)},
            "2026-10-23": {"AMC": cell(100, 1300, 60, 40)},                       # 10% of theatres: partial
        }
        CC.mark_complete(by_date)
        self.assertTrue(by_date["2026-10-22"]["AMC"]["complete"])
        self.assertTrue(by_date["2026-10-22"]["CNMK"]["complete"])
        self.assertFalse(by_date["2026-10-23"]["AMC"]["complete"])
        early = {"2026-10-09": {"AMC": cell(1000, 1, 200, 400), "CNMK": cell(1, 1, 100)},   # Friday before 10-15
                 "2026-09-26": {"CNMK": cell(1, 1, 100)}}                                   # before the census
        CC.mark_complete(early)
        self.assertFalse(early["2026-10-09"]["AMC"]["complete"])
        self.assertTrue(early["2026-10-09"]["CNMK"]["complete"])
        self.assertFalse(early["2026-09-26"]["CNMK"]["complete"])
        self.assertFalse(CC.present("AMC", by_date["2026-10-23"]["AMC"]))
        self.assertFalse(CC.present("CNMK", cell(10, 1, 20)))      # too few showings


class SharesTest(unittest.TestCase):
    def test_fit_is_loo_and_shrunk(self):
        samples = []
        for i in range(6):
            samples += [(f"2026-09-{10 + i:02d}", f"m{i}", "Saturday", "AMC", 0.20 + 0.01 * i),
                        (f"2026-09-{10 + i:02d}", f"m{i}", "Sunday", "AMC", 0.26),
                        (f"2026-09-{10 + i:02d}", f"m{i}", "Saturday", "CNMK", 0.15)]
        samples.append(("2026-09-20", "outlier", "Saturday", "AMC", 0.90))
        s_all = CC.fit_shares(samples)
        s_loo = CC.fit_shares(samples, exclude={("2026-09-20", "outlier")})
        self.assertLess(s_loo["AMC"]["Saturday"], s_all["AMC"]["Saturday"])
        self.assertAlmostEqual(s_loo["CNMK"]["Saturday"], 0.15, places=6)
        # Friday has no CNMK samples -> falls back to the chain's all-day prior
        self.assertAlmostEqual(s_loo["CNMK"]["Friday"], 0.15, places=6)
        self.assertGreater(s_loo["AMC"]["Sunday"], s_loo["AMC"]["Saturday"])

    def test_estimates_pool_present_chains_only(self):
        shares = {"AMC": {"Saturday": 0.25}, "CNMK": {"Saturday": 0.15}, "ALMO": {"Saturday": 0.01}}
        chains = {"AMC": cell(0, 2.5e6, 200), "CNMK": cell(0, 1.5e6, 300),
                  "ALMO": cell(0, 0.5e6, 3),                 # too few showings: reported, not pooled
                  "REGL": cell(0, 0.1e6, 100)}               # never pooled (no share)
        est = CC.estimates(chains, "Saturday", shares)
        self.assertEqual(est["pooled_chains"], ["AMC", "CNMK"])
        self.assertAlmostEqual(est["pooled_m"], (2.5 + 1.5) / 0.40, places=6)
        self.assertAlmostEqual(est["chains"]["AMC"]["national_m"], 10.0)
        self.assertAlmostEqual(est["chains"]["CNMK"]["national_m"], 10.0)
        self.assertFalse(est["chains"]["ALMO"]["present"])
        self.assertNotIn("REGL", est["chains"])
        self.assertIsNone(CC.estimates({"REGL": cell(0, 1e6, 100)}, "Saturday", shares)["pooled_m"])


class BlendTest(unittest.TestCase):
    def pred(self):
        return {"daily_details": {
            "Thursday": {"domestic_mid": 1.0e6, "actual_override": True},
            "Friday": {"domestic_mid": 4.0e6, "domestic_low": 3.0e6, "domestic_high": 5.0e6, "actual_override": False},
        }}

    def test_blend_moves_half_way_in_log_space_and_carries(self):
        p = self.pred()
        layer = {"Friday": {"pooled_m": 6.0, "pooled_share": 0.4, "pooled_chains": ["AMC", "CNMK"], "chains": {}},
                 "Thursday": {"pooled_m": 9.0, "pooled_share": 0.4, "pooled_chains": ["AMC"], "chains": {}}}
        delta, carry, info = CC.apply_to_prediction(p, layer, weight=0.5, carry=True)
        f = (6.0 / 4.0) ** 0.5
        self.assertAlmostEqual(info["Friday"]["factor"], f)
        self.assertAlmostEqual(info["Friday"]["blended_m"], 4.0 * f)
        self.assertEqual(p["daily_details"]["Friday"]["domestic_mid"], 4.0e6)   # never mutated
        self.assertAlmostEqual(delta, 4.0 * (f - 1))
        # idempotent: a second assembly pass derives the same overlay
        delta2, carry2, _ = CC.apply_to_prediction(p, layer, weight=0.5, carry=True)
        self.assertAlmostEqual((delta2, carry2), (delta, carry))
        self.assertAlmostEqual(carry, f)
        self.assertNotIn("Thursday", info)                     # reported day untouched
        self.assertEqual(p["daily_details"]["Thursday"]["domestic_mid"], 1.0e6)

    def test_weight_one_and_clamp_and_no_carry(self):
        p = self.pred()
        layer = {"Friday": {"pooled_m": 40.0, "pooled_share": 0.4, "pooled_chains": ["AMC"], "chains": {}}}
        delta, carry, info = CC.apply_to_prediction(p, layer, weight=1.0, carry=False)
        self.assertAlmostEqual(info["Friday"]["factor"], CC.FACTOR_CLAMP[1])
        self.assertEqual(carry, 1.0)

    def test_kill_switch(self):
        import predict as P
        with mock.patch.object(P, "CHAIN_CENSUS_MODE", "off"):
            self.assertEqual(P.CHAIN_CENSUS_MODE, "off")


if __name__ == "__main__":
    unittest.main()


class RegalEstimatorTest(unittest.TestCase):
    """Regal = near-showtime sample x full showing inventory, by daypart."""

    def rows(self):
        inv, reads = [], []
        # theatre A has 12 showings (tier 0), B 6 (tier 1), C 3 (tier 2); half matinee
        sizes = {"A": 12, "B": 6, "C": 3}
        for th, n in sizes.items():
            for i in range(n):
                inv.append({"show_date": "2026-10-24", "movie_title": "Clayface", "theatre_name": th,
                            "showtime_id": f"{th}{i}", "showtime": "13:00" if i % 2 == 0 else "19:30",
                            "chain": "REGL", "row_kind": "regal-inventory"})
        seats = {("A", "13:00"): 20, ("A", "19:30"): 60, ("B", "13:00"): 10, ("B", "19:30"): 30,
                 ("C", "13:00"): 4, ("C", "19:30"): 12}
        for (th, t), v in seats.items():
            for i in range(3):
                reads.append({"show_date": "2026-10-24", "movie_title": "Clayface", "theatre_name": th,
                              "showtime_id": f"r{th}{t}{i}", "showtime": t, "chain": "REGL",
                              "reserved_seats": str(v), "minutes_until_showtime": "20",
                              "notes": "sample=census", "snapshot_time": "t"})
        # three full (after-start) counts in A-evening replace the pre-start reads there
        for i in range(3):
            reads.append({"show_date": "2026-10-24", "movie_title": "Clayface", "theatre_name": "A",
                          "showtime_id": f"post{i}", "showtime": "19:30", "chain": "REGL", "reserved_seats": "90",
                          "minutes_until_showtime": "0", "notes": "sample=census; started_min=6",
                          "snapshot_time": "t"})
        # ignored: a priority read and a long-lead random read
        reads.append(dict(reads[0], showtime_id="p", reserved_seats="500", notes="sample=priority"))
        reads.append(dict(reads[0], showtime_id="far", reserved_seats="500", minutes_until_showtime="600",
                          notes="sample=random"))
        return inv, reads

    def test_dayparts_scale_to_inventory(self):
        inv, reads = self.rows()
        def lane(chain, w):
            return iter(inv if chain == "RINV" else reads)
        with mock.patch.object(CC, "_lane_rows", side_effect=lane), \
             mock.patch.object(CC, "_price", return_value=10.0):
            est = CC.regal_day_dollars(W, CC.weekend_dates(W))
        cell = est[("Clayface", "2026-10-24")]
        self.assertEqual((cell["showings"], cell["theatres"], cell["sampled"]), (21, 3, 18))
        # A: 6 matinee x 20 + 6 evening x 90 (full count wins); B: 3x10 + 3x30; C: 2x4 + 1x12
        expected = 6 * 20 + 6 * 90 + 3 * 10 + 3 * 30 + 2 * 4 + 1 * 12
        self.assertAlmostEqual(cell["seats"], expected)
        self.assertAlmostEqual(cell["dollars"], expected * 10.0)

    def test_presence_needs_reads_and_inventory(self):
        self.assertFalse(CC.present("REGL", {"showings": 300, "sampled": 5, "dollars": 1}))
        self.assertFalse(CC.present("REGL", {"showings": 300, "sampled": 99, "lower_bound": True}))
        self.assertTrue(CC.present("REGL", {"showings": 300, "sampled": 40, "dollars": 1}))

    def test_regal_pooled_only_when_gate_passes(self):
        shares = {"AMC": {"Saturday": 0.25}, "REGL": {"Saturday": 0.15}}
        chains = {"AMC": cell(0, 2.5e6, 200), "REGL": {"seats": 0, "dollars": 1.8e6, "showings": 400,
                                                         "theatres": 300, "sampled": 60}}
        no = CC.estimates(chains, "Saturday", shares)
        yes = CC.estimates(chains, "Saturday", shares, pooled=CC.POOLED_CHAINS + ("REGL",))
        self.assertEqual(no["pooled_chains"], ["AMC"])
        self.assertEqual(yes["pooled_chains"], ["AMC", "REGL"])
        self.assertAlmostEqual(yes["pooled_m"], 4.3 / 0.40)
