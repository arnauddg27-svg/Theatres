import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402

CAL = {"calibration_factors": {"amc_market_share": 0.244}}


class CrossChainShareTests(unittest.TestCase):
    def _cc(self, amc_occ, rc_occ, amc_rows=100, rc_rows=100):
        return {"F": {"amc_occ": amc_occ, "rc_occ": rc_occ,
                      "amc_rows": amc_rows, "rc_rows": rc_rows}}

    def test_amc_skewed_film_gets_higher_share(self):
        # Jackass profile: fills AMC, empty at Regal -> share up -> forecast down
        s = P.cross_chain_share("F", self._cc(25.0, 13.5), CAL)
        self.assertGreater(s, 0.244)

    def test_broad_film_gets_lower_share(self):
        s = P.cross_chain_share("F", self._cc(15.0, 25.0), CAL)
        self.assertLess(s, 0.244)

    def test_formula_uses_fixed_capacity_share(self):
        # v2: wA is the pinned capacity constant, so the formula's output is
        # identical whatever the calibrated fleet prior has drifted to.
        cc = self._cc(25.0, 13.5)
        drifted = {"calibration_factors": {"amc_market_share": 0.196}}
        wa = P.CROSS_CHAIN_CAPACITY_SHARE
        a, b = wa * 25.0, (1 - wa) * P.CROSS_CHAIN_WALKUP_K * 13.5
        formula = a / (a + b)
        for cal in (CAL, drifted):
            base = cal["calibration_factors"]["amc_market_share"]
            expected = base + P.CROSS_CHAIN_SHARE_WEIGHT * (formula - base)
            expected = max(P.CROSS_CHAIN_SHARE_CLAMP_ABS[0],
                           min(P.CROSS_CHAIN_SHARE_CLAMP_ABS[1], expected))
            self.assertAlmostEqual(P.cross_chain_share("F", cc, cal), expected, places=6)

    def test_saturation_gate_blocks_supply_constrained(self):
        # Young Washington signature: AMC occupancy saturated at 42% because
        # scarce showings ran full -> occupancy stopped measuring preference.
        self.assertIsNone(P.cross_chain_share("F", self._cc(42.1, 21.0), CAL))
        self.assertIsNotNone(P.cross_chain_share("F", self._cc(29.9, 16.4), CAL))

    def test_clamped_at_extremes(self):
        # absurd skew cannot move the share beyond the absolute clamp
        s = P.cross_chain_share("F", self._cc(34.0, 2.0), CAL)
        self.assertLessEqual(s, P.CROSS_CHAIN_SHARE_CLAMP_ABS[1] + 1e-9)

    def test_no_data_and_thin_rows_are_neutral(self):
        self.assertIsNone(P.cross_chain_share("Other", self._cc(25, 13.5), CAL))
        self.assertIsNone(P.cross_chain_share("F", self._cc(25, 13.5, amc_rows=10), CAL))
        self.assertIsNone(P.cross_chain_share("F", self._cc(25, 13.5, rc_rows=5), CAL))
        self.assertIsNone(P.cross_chain_share("F", {}, CAL))
        self.assertIsNone(P.cross_chain_share("F", None, CAL))


class LoadCrossChainOccupancyTests(unittest.TestCase):
    def _write(self, path, fields, rows):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    def test_loader_pairs_and_leak_filters(self):
        with tempfile.TemporaryDirectory() as d:
            seat = Path(d) / "seat.csv"
            fan = Path(d) / "fan.csv"
            self._write(seat, ["weekend_of", "date", "movie_title", "occupancy_pct"], [
                {"weekend_of": "2026-06-26", "date": "2026-06-25", "movie_title": "F", "occupancy_pct": "20"},
                {"weekend_of": "2026-06-26", "date": "2026-06-27", "movie_title": "F", "occupancy_pct": "40"},
            ])
            self._write(fan, ["weekend_of", "snapshot_time", "movie_title", "occupancy_pct", "chain"], [
                {"weekend_of": "2026-06-26", "snapshot_time": "2026-06-25T03:00:00Z",
                 "movie_title": "F", "occupancy_pct": "10", "chain": "REGL"},
                {"weekend_of": "2026-06-26", "snapshot_time": "2026-06-28T03:00:00Z",
                 "movie_title": "F", "occupancy_pct": "30", "chain": "CNMK"},
            ])
            orig = (P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV)
            try:
                P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV = str(seat), str(fan)
                P._CROSS_CHAIN_CACHE.clear()
                full = P.load_cross_chain_occupancy(weekend_of="2026-06-26")
                self.assertAlmostEqual(full["F"]["amc_occ"], 30.0)   # (20+40)/2
                self.assertAlmostEqual(full["F"]["rc_occ"], 20.0)    # (10+30)/2
                # leak filter: as-of Thursday only the early rows survive
                thu = P.load_cross_chain_occupancy(weekend_of="2026-06-26",
                                                   through_date="2026-06-25")
                self.assertAlmostEqual(thu["F"]["amc_occ"], 20.0)
                self.assertAlmostEqual(thu["F"]["rc_occ"], 10.0)
            finally:
                P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV = orig
                P._CROSS_CHAIN_CACHE.clear()

    def test_absent_fandango_file_is_empty(self):
        orig = P.FANDANGO_SNAPSHOTS_CSV
        try:
            P.FANDANGO_SNAPSHOTS_CSV = "/nonexistent/fan.csv"
            P._CROSS_CHAIN_CACHE.clear()
            self.assertEqual(P.load_cross_chain_occupancy(weekend_of="2026-05-01"), {})
        finally:
            P.FANDANGO_SNAPSHOTS_CSV = orig
            P._CROSS_CHAIN_CACHE.clear()


if __name__ == "__main__":
    unittest.main()
