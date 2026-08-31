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

    def test_absent_rc_files_is_empty(self):
        orig = (P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV)
        try:
            P.FANDANGO_SNAPSHOTS_CSV = "/nonexistent/fan.csv"
            P.CINEMARK_SNAPSHOTS_CSV = "/nonexistent/cnmk.csv"
            P._CROSS_CHAIN_CACHE.clear()
            self.assertEqual(P.load_cross_chain_occupancy(weekend_of="2026-05-01"), {})
        finally:
            P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV = orig
            P._CROSS_CHAIN_CACHE.clear()

    def test_cinemark_direct_csv_blends_into_rc_side(self):
        # 2026-08-31 regime: Fandango carries REGL only, the Cinemark direct
        # lane carries CNMK. The RC side must be the blend of both files —
        # Regal-only rc_occ runs far below the level CROSS_CHAIN_WALKUP_K was
        # calibrated on.
        import tempfile
        from pathlib import Path as _P
        with tempfile.TemporaryDirectory() as td:
            seat = _P(td) / "seat.csv"
            fan = _P(td) / "fan.csv"
            cnmk = _P(td) / "cnmk.csv"
            self._write(seat, ["weekend_of", "date", "movie_title", "occupancy_pct"], [
                {"weekend_of": "2026-09-04", "date": "2026-09-04",
                 "movie_title": "F", "occupancy_pct": "20"},
            ])
            self._write(fan, ["weekend_of", "snapshot_time", "movie_title",
                              "occupancy_pct", "chain"], [
                {"weekend_of": "2026-09-04", "snapshot_time": "2026-09-03T03:00:00Z",
                 "movie_title": "F", "occupancy_pct": "6", "chain": "REGL"},
            ])
            self._write(cnmk, ["weekend_of", "snapshot_time", "movie_title",
                               "occupancy_pct", "chain"], [
                {"weekend_of": "2026-09-04", "snapshot_time": "2026-09-03T04:00:00Z",
                 "movie_title": "F", "occupancy_pct": "30", "chain": "CNMK"},
            ])
            orig = (P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV)
            try:
                P.SEAT_CSV = str(seat)
                P.FANDANGO_SNAPSHOTS_CSV = str(fan)
                P.CINEMARK_SNAPSHOTS_CSV = str(cnmk)
                P._CROSS_CHAIN_CACHE.clear()
                cc = P.load_cross_chain_occupancy(weekend_of="2026-09-04")
                self.assertAlmostEqual(cc["F"]["rc_occ"], 18.0)   # (6+30)/2
                self.assertEqual(cc["F"]["rc_rows"], 2)
            finally:
                (P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV,
                 P.CINEMARK_SNAPSHOTS_CSV) = orig
                P._CROSS_CHAIN_CACHE.clear()


if __name__ == "__main__":
    unittest.main()


class VolumeShareTests(unittest.TestCase):
    def _cc(self, q, days=2, amc_rows=100, rc_rows=100, amc_occ=25.0, rc_occ=15.0):
        return {"F": {"amc_occ": amc_occ, "rc_occ": rc_occ, "amc_rows": amc_rows,
                      "rc_rows": rc_rows, "volume_ratio": q, "volume_days": days}}

    def test_reduces_to_occupancy_formula_at_showings_parity(self):
        # same showings per theatre on both chains -> q = occA/occRC -> identical share
        occ_a, occ_rc = 25.0, 13.5
        occ_share = P.cross_chain_share(
            "F", {"F": {"amc_occ": occ_a, "rc_occ": occ_rc,
                        "amc_rows": 100, "rc_rows": 100}}, CAL)
        vol_share = P.cross_chain_volume_share(
            "F", self._cc(occ_a / occ_rc, amc_occ=occ_a, rc_occ=occ_rc), CAL)
        self.assertAlmostEqual(occ_share, vol_share, places=6)

    def test_no_saturation_gate_in_volume_mode(self):
        # occupancy mode gates at 42% AMC occ; volume mode measures instead
        s = P.cross_chain_volume_share("F", self._cc(1.5, amc_occ=42.0), CAL)
        self.assertIsNotNone(s)
        self.assertIsNone(P.cross_chain_share(
            "F", {"F": {"amc_occ": 42.0, "rc_occ": 20.0,
                        "amc_rows": 100, "rc_rows": 100}}, CAL))

    def test_needs_volume_days_and_rows(self):
        self.assertIsNone(P.cross_chain_volume_share("F", self._cc(None), CAL))
        self.assertIsNone(P.cross_chain_volume_share("F", self._cc(1.2, days=0), CAL))
        self.assertIsNone(P.cross_chain_volume_share("F", self._cc(1.2, rc_rows=5), CAL))

    def test_volume_mode_applied_after_odyssey_validation(self):
        # validate-then-apply satisfied: The Odyssey (2026-07-17, $124.5M) —
        # frozen volume hypothesis +6.0% beat gated-fleet -8.5% and capacity
        # -25%, and the flip improved the Thursday backtest 18.5% -> 18.0%.
        self.assertTrue(P.CROSS_CHAIN_VOLUME_APPLY)


class CrossChainArchiveTests(unittest.TestCase):
    """A rotated weekend must keep its AMC side (predict.py read SEAT_CSV raw)."""

    def _write(self, path, fields, rows):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    def test_archived_weekend_still_yields_amc_side(self):
        import gzip
        seat_fields = ["weekend_of", "date", "movie_title", "occupancy_pct",
                       "theatre_name", "showtime"]
        seat_rows = [{"weekend_of": "2026-07-10", "date": "2026-07-09",
                      "movie_title": "F", "occupancy_pct": "20",
                      "theatre_name": f"AMC {i}", "showtime": "19:00"}
                     for i in range(60)]
        with tempfile.TemporaryDirectory() as d:
            live = Path(d) / "seat.csv"
            arch_dir = Path(d) / "seat-archive"
            arch_dir.mkdir()
            fan = Path(d) / "fan.csv"
            # weekend fully rotated: live holds a DIFFERENT weekend only
            self._write(live, seat_fields, [dict(seat_rows[0], weekend_of="2026-07-17")])
            with gzip.open(arch_dir / "seat-counts-2026-07-10.csv.gz", "wt", newline="") as f:
                w = csv.DictWriter(f, fieldnames=seat_fields)
                w.writeheader()
                w.writerows(seat_rows)
            self._write(fan, ["weekend_of", "snapshot_time", "movie_title",
                              "occupancy_pct", "chain", "show_date"],
                        [{"weekend_of": "2026-07-10",
                          "snapshot_time": "2026-07-09T03:00:00Z",
                          "movie_title": "F", "occupancy_pct": "10",
                          "chain": "REGL", "show_date": "2026-07-09"}
                         for _ in range(50)])
            orig = (P.SEAT_CSV, P.SEAT_ARCHIVE_DIR, P.FANDANGO_SNAPSHOTS_CSV)
            try:
                P.SEAT_CSV, P.SEAT_ARCHIVE_DIR = str(live), str(arch_dir)
                P.FANDANGO_SNAPSHOTS_CSV = str(fan)
                P._CROSS_CHAIN_CACHE.clear()
                cc = P.load_cross_chain_occupancy(weekend_of="2026-07-10")
                self.assertIn("F", cc)
                self.assertAlmostEqual(cc["F"]["amc_occ"], 20.0)
                self.assertEqual(cc["F"]["amc_rows"], 60)
            finally:
                P.SEAT_CSV, P.SEAT_ARCHIVE_DIR, P.FANDANGO_SNAPSHOTS_CSV = orig
                P._CROSS_CHAIN_CACHE.clear()


class CrossChainInactiveReasonTests(unittest.TestCase):
    """Gated-off must be distinguishable from never-wired.

    cross_chain_share returns None for five different reasons and the caller
    then silently uses the fleet prior. That made "this film has no Fandango
    coverage" identical to "we collected the data and discarded it at a gate" —
    and identical again to "the loader was pointed at the wrong weekend", which
    is exactly how the archive-blind loader and the weekend-key bug both hid.
    """

    def test_each_gate_reports_a_distinct_reason(self):
        cases = {
            "no cross-chain rows": {},
            "too few AMC rows": {"F": {"amc_occ": 25, "rc_occ": 13,
                                       "amc_rows": 10, "rc_rows": 100}},
            "too few Regal/Cinemark rows": {"F": {"amc_occ": 25, "rc_occ": 13,
                                                  "amc_rows": 100, "rc_rows": 5}},
            "saturation gate": {"F": {"amc_occ": 42.1, "rc_occ": 21,
                                      "amc_rows": 100, "rc_rows": 100}},
        }
        seen = set()
        for expected_fragment, cc in cases.items():
            with self.subTest(case=expected_fragment):
                reason = P.cross_chain_inactive_reason("F", cc)
                self.assertIsNotNone(reason)
                self.assertIn(expected_fragment, reason)
                seen.add(reason)
        self.assertEqual(len(cases), len(seen), "reasons must be distinguishable")

    def test_healthy_data_reports_no_reason(self):
        healthy = {"F": {"amc_occ": 25, "rc_occ": 13.5,
                         "amc_rows": 100, "rc_rows": 100}}
        self.assertIsNone(P.cross_chain_inactive_reason("F", healthy))
        # and the share itself is genuinely available for that input
        self.assertIsNotNone(P.cross_chain_share("F", healthy, CAL))

    def test_reason_agrees_with_the_share_gate(self):
        # every input that yields no share must yield a reason, and vice versa
        for cc in ({}, {"F": {"amc_occ": 42.1, "rc_occ": 21, "amc_rows": 100, "rc_rows": 100}},
                   {"F": {"amc_occ": 25, "rc_occ": 13.5, "amc_rows": 100, "rc_rows": 100}}):
            share = P.cross_chain_share("F", cc, CAL)
            reason = P.cross_chain_inactive_reason("F", cc)
            self.assertEqual(share is None, reason is not None, f"disagreement on {cc}")


class FamilyEarlyWindowPolicyTests(unittest.TestCase):
    """Family films: volume share on preview-day data only, then fleet prior.

    Measured (backfill experiment, 2026-08-23): the blanket family gate moved
    the Thursday backtest 17.1% -> 18.7% and collapsed PAW Patrol's Thursday
    read from +17% to -38% — the preview-day volume ratio reads family AMC
    share well. The confound is the DRIFT: across the weekend the AMC side of
    q accumulates post-showtime walk-ups while RC stays advance-online-only
    (PAW q 0.29 -> 1.10, share 10% -> 23%, nowcast -36%). Early window only:
    volume allowed at volume_days <= 1, fleet prior afterwards; occupancy mode
    stays fully gated for family (Minions read 0.26 vs true ~0.14 there).
    """

    def _cc(self, q, days):
        return {"F": {"amc_occ": 20.0, "rc_occ": 15.0, "amc_rows": 100,
                      "rc_rows": 100, "volume_ratio": q, "volume_days": days}}

    def test_volume_share_computable_for_family_inputs(self):
        # the share itself carries no family logic — gating is the caller's job
        self.assertIsNotNone(P.cross_chain_volume_share("F", self._cc(0.3, 1), CAL))
        self.assertIsNotNone(P.cross_chain_volume_share("F", self._cc(1.1, 4), CAL))

    def test_call_site_gates_family_after_day_one(self):
        # the policy lives at the predict_movie call site: volume_days <= 1
        src = open(Path(__file__).resolve().parents[1] / "predict.py").read()
        i = src.index("FAMILY + VOLUME, early window only")
        block = src[i:i + 2000]
        self.assertIn('volume_days") or 0) <= 1', block)
        self.assertIn("_is_family", src)


class VolumeDivergenceCapTest(unittest.TestCase):
    """Volume mode measures supply allocation; cap its pull vs occupancy."""

    def test_cap_binds_only_beyond_divergence(self):
        import predict as P
        # ST3 shape: volume 0.40 vs occupancy 0.288 -> capped to 0.338
        self.assertAlmostEqual(0.338, P.capped_volume_share(0.40, 0.288), places=3)
        # Downside divergence caps symmetrically
        self.assertAlmostEqual(0.235, P.capped_volume_share(0.15, 0.285), places=3)
        # Within the limit: untouched (Dog Stars shape, 0.169 vs 0.197)
        self.assertEqual(0.169, P.capped_volume_share(0.169, 0.197))
        # Missing either signal: volume passes through unchanged
        self.assertIsNone(P.capped_volume_share(None, 0.25))
        self.assertEqual(0.4, P.capped_volume_share(0.4, None))
