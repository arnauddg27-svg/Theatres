"""AMC bridge (2026-09-08): AMC seat maps read through Fandango (chainCode=AMC)
while AMC's own seat route is Cloudflare-blocked for datacenter egress.

Pins the four seams the bridge depends on: discovery maps amc-* slugs to the
AMC lane's canonical names; the collector's chain gate follows FANDANGO_CHAINS
(the probe's static set hard-excluded AMC); predict fills the AMC snapshot
layer from bridge rows ONLY where the native lane has none; and the
cross-chain (RC) side never counts a bridge row as Regal/Cinemark."""
import csv
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fandango_collect as fc  # noqa: E402
import predict as P  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _load_discover():
    spec = importlib.util.spec_from_file_location(
        "fandango_discover_bridge_test",
        Path(__file__).resolve().parents[1] / "scripts" / "fandango_discover.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class DiscoveryMapsAmcTest(unittest.TestCase):
    def test_amc_slugs_are_detected_and_canonicalised(self):
        d = _load_discover()
        self.assertEqual("AMC", d.chain_for_slug("amc-empire-25-aaore"))
        self.assertEqual("REGL", d.chain_for_slug("regal-atlas-park-aatzo"))
        canonical = {d._name_key("AMC Empire 25"): "AMC Empire 25",
                     d._name_key("AMC DINE-IN Essex Green 9"): "AMC DINE-IN Essex Green 9",
                     d._name_key("AMC 19th St. East 6"): "AMC 19th St. East 6"}
        # Fandango's slug-derived names differ in case/punctuation only.
        self.assertEqual("AMC Empire 25",
                         d.canonical_amc_name(d.name_from_slug("amc-empire-25-aaore"), canonical))
        self.assertEqual("AMC DINE-IN Essex Green 9",
                         d.canonical_amc_name(d.name_from_slug("amc-dine-in-essex-green-9-aafmu"), canonical))
        self.assertEqual("AMC 19th St. East 6",
                         d.canonical_amc_name(d.name_from_slug("amc-19th-st-east-6-aabqg"), canonical))
        # A Fandango AMC theatre the AMC lane does not track -> None (bridge skips it)
        self.assertIsNone(d.canonical_amc_name(d.name_from_slug("amc-garden-state-16-aaujg"), canonical))

    def test_real_amc_configs_load_and_match_a_known_theatre(self):
        d = _load_discover()
        names = d.load_amc_canonical_names()
        self.assertGreater(len(names), 300)
        self.assertEqual("AMC Empire 25", d.canonical_amc_name("Amc Empire 25", names))


class CollectorChainGateTest(unittest.TestCase):
    def test_chain_gate_follows_configured_chains(self):
        orig = fc.FANDANGO_CHAINS
        try:
            fc.FANDANGO_CHAINS = frozenset({"REGL"})
            self.assertTrue(fc.is_wanted_chain("REGL"))
            self.assertFalse(fc.is_wanted_chain("AMC"))   # default lane never reads AMC
            fc.FANDANGO_CHAINS = frozenset({"AMC"})
            self.assertTrue(fc.is_wanted_chain("AMC"))
            self.assertTrue(fc.is_wanted_chain("amc"))
            self.assertFalse(fc.is_wanted_chain("REGL"))
            self.assertFalse(fc.is_wanted_chain(""))
        finally:
            fc.FANDANGO_CHAINS = orig

    def test_pool_loader_skips_unmatched_amc_theatres(self):
        pool = {"theatres": [
            {"name": "AMC Empire 25", "slug": "amc-empire-25-aaore", "chain": "AMC", "amc_match": True, "zip": "10001"},
            {"name": "Amc Garden State 16", "slug": "amc-garden-state-16-aaujg", "chain": "AMC", "amc_match": False, "zip": "07652"},
            {"name": "Regal Atlas Park", "slug": "regal-atlas-park-aatzo", "chain": "REGL", "zip": "10001"},
        ]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pool.json"
            import json
            path.write_text(json.dumps(pool))
            orig = (fc.THEATRES_JSON, fc.FANDANGO_CHAINS)
            try:
                fc.THEATRES_JSON = path
                fc.FANDANGO_CHAINS = frozenset({"AMC"})
                self.assertEqual(["AMC Empire 25"], [t["name"] for t in fc.load_fandango_theatres()])
                fc.FANDANGO_CHAINS = frozenset({"REGL"})
                self.assertEqual(["Regal Atlas Park"], [t["name"] for t in fc.load_fandango_theatres()])
            finally:
                fc.THEATRES_JSON, fc.FANDANGO_CHAINS = orig


def _snap(movie, date, theatre, chain, occ, snap="2026-09-10T15:00:00+00:00"):
    return {"weekend_of": "2026-09-11", "snapshot_time": snap, "show_date": date,
            "movie_title": movie, "theatre_name": theatre, "chain": chain,
            "occupancy_pct": str(occ), "reserved_seats": "10", "total_seats": "100",
            "notes": "amc-bridge; discovered_showtimes=3" if chain == "AMC" else "discovered_showtimes=3"}


class PredictBridgeFillInTest(unittest.TestCase):
    def test_fill_in_rule_native_wins(self):
        rows = [_snap("F", "2026-09-11", "AMC Empire 25", "AMC", 20),
                _snap("F", "2026-09-11", "AMC Kips Bay 15", "AMC", 25),
                _snap("F", "2026-09-12", "AMC Empire 25", "AMC", 30),
                _snap("F", "2026-09-11", "Regal Atlas Park", "REGL", 40)]   # never AMC data
        native = {("F", "2026-09-11", "AMC Empire 25")}
        kept = P.select_amc_bridge_rows(rows, native)
        self.assertEqual([("AMC Kips Bay 15", "2026-09-11"), ("AMC Empire 25", "2026-09-12")],
                         [(r["theatre_name"], r["show_date"]) for r in kept])
        # No native data at all (the 2026-09 outage) -> every AMC bridge row fills in
        self.assertEqual(3, len(P.select_amc_bridge_rows(rows, set())))

    def test_loader_merges_bridge_rows_for_missing_theatre_dates(self):
        with tempfile.TemporaryDirectory() as td:
            fan = Path(td) / "fan.csv"
            native = Path(td) / "native.csv"
            fields = ["weekend_of", "snapshot_time", "show_date", "movie_title", "theatre_name",
                      "chain", "occupancy_pct", "reserved_seats", "total_seats", "notes"]
            with open(fan, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                w.writerows([_snap("F", "2026-09-11", "AMC Empire 25", "AMC", 20),
                             _snap("F", "2026-09-11", "AMC Kips Bay 15", "AMC", 25),
                             _snap("F", "2026-09-11", "Regal Atlas Park", "REGL", 40)])
            with open(native, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                w.writerows([_snap("F", "2026-09-11", "AMC Empire 25", "", 22)])
            orig = (P.FANDANGO_SNAPSHOTS_CSV, P.PRE_RESERVATION_CSV)
            try:
                P.FANDANGO_SNAPSHOTS_CSV = str(fan)
                P.PRE_RESERVATION_CSV = str(native)
                data = P.load_pre_reservation_data(weekend_of="2026-09-11")
                rows = data["F"]["2026-09-11"]
                by_theatre = {r["theatre_name"]: r["occupancy_pct"] for r in rows}
                # native Empire reading kept (22), bridge Empire (20) dropped,
                # bridge Kips Bay filled in, Regal never enters the AMC layer
                self.assertEqual({"AMC Empire 25": "22", "AMC Kips Bay 15": "25"}, by_theatre)
                # through_date honours bridge rows too
                data = P.load_pre_reservation_data(weekend_of="2026-09-11", through_date="2026-09-09")
                self.assertEqual({}, data)
            finally:
                P.FANDANGO_SNAPSHOTS_CSV, P.PRE_RESERVATION_CSV = orig

    def test_cross_chain_never_counts_bridge_rows_as_rc(self):
        with tempfile.TemporaryDirectory() as td:
            seat = Path(td) / "seat.csv"
            fan = Path(td) / "fan.csv"
            with open(seat, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["weekend_of", "date", "movie_title", "occupancy_pct"]); w.writeheader()
                w.writerow({"weekend_of": "2026-09-11", "date": "2026-09-11", "movie_title": "F", "occupancy_pct": "20"})
            with open(fan, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["weekend_of", "snapshot_time", "show_date", "movie_title",
                                                  "theatre_name", "occupancy_pct", "chain", "notes"]); w.writeheader()
                w.writerow({"weekend_of": "2026-09-11", "snapshot_time": "2026-09-10T03:00:00Z", "show_date": "2026-09-11",
                            "movie_title": "F", "theatre_name": "Regal X", "occupancy_pct": "10", "chain": "REGL", "notes": ""})
                w.writerow({"weekend_of": "2026-09-11", "snapshot_time": "2026-09-10T03:00:00Z", "show_date": "2026-09-11",
                            "movie_title": "F", "theatre_name": "AMC Empire 25", "occupancy_pct": "90", "chain": "AMC",
                            "notes": "amc-bridge; discovered_showtimes=3"})
            orig = (P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV)
            try:
                P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV = str(seat), str(fan)
                P.CINEMARK_SNAPSHOTS_CSV = "/nonexistent/cnmk.csv"
                P._CROSS_CHAIN_CACHE.clear()
                out = P.load_cross_chain_occupancy(weekend_of="2026-09-11")
                self.assertAlmostEqual(10.0, out["F"]["rc_occ"])   # the 90% AMC row must not leak in
            finally:
                P.SEAT_CSV, P.FANDANGO_SNAPSHOTS_CSV, P.CINEMARK_SNAPSHOTS_CSV = orig
                P._CROSS_CHAIN_CACHE.clear()


class BridgeSchedulingTest(unittest.TestCase):
    def _sched(self):
        spec = importlib.util.spec_from_file_location(
            "sched_bridge_test",
            Path(__file__).resolve().parents[1] / "scripts" / "schedule_box_office_pipeline.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_bridge_slots_use_only_the_hours_regal_leaves_free(self):
        m = self._sched()
        fan = [s for s in m.SLOTS if s.inputs.get("phase") == "scrape-fandango"]
        bridge = [s for s in fan if s.name.startswith(m.AMC_BRIDGE_SLOT_PREFIX)]
        regal = [s for s in fan if not s.name.startswith(m.AMC_BRIDGE_SLOT_PREFIX)]
        self.assertEqual(6, len(bridge))
        self.assertEqual(18, len(regal))
        # Same Azure-range seat budget (~30 renders/hour): the bridge must not
        # share an hour with a Regal slot, and all fandango hours stay unique.
        self.assertFalse({s.hour for s in bridge} & {s.hour for s in regal})
        hours = [s.hour for s in fan]
        self.assertEqual(len(hours), len(set(hours)))
        self.assertEqual({0, 1, 2, 15, 17, 19}, {s.hour for s in bridge})
        # every shard once a day; shard inputs are the same 6-way split
        self.assertEqual({"0", "1", "2", "3", "4", "5"}, {s.inputs["fandango_shard"] for s in bridge})
        self.assertTrue(all(s.inputs["fandango_num_shards"] == "6" for s in bridge))
        for s in bridge:
            if s.hour in (0, 1, 2):
                self.assertEqual(frozenset({0, 2, 3, 4, 5, 6}), s.cron_days, s.name)  # = AMC 02:30Z
                self.assertNotIn("fandango_order", s.inputs)
            else:
                self.assertEqual(frozenset(range(7)), s.cron_days, s.name)          # = AMC 14:30Z/22:30Z
                self.assertEqual("nearest", s.inputs["fandango_order"])

    def test_workflow_keys_the_chain_off_the_slot_name(self):
        yml = (ROOT / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
        self.assertIn("FANDANGO_CHAINS: ${{ contains(github.event.inputs.schedule_slot, 'amc bridge') && 'AMC' || 'REGL' }}", yml)
        m = self._sched()
        # the slot titles the dispatch will carry contain the trigger substring
        for s in m.SLOTS:
            if s.name.startswith(m.AMC_BRIDGE_SLOT_PREFIX):
                self.assertIn("amc bridge", s.name)


if __name__ == "__main__":
    unittest.main()


class WatchdogLaneAttributionTest(unittest.TestCase):
    def test_bridge_rows_count_as_amc_snapshot_not_fandango(self):
        spec = importlib.util.spec_from_file_location(
            "capture_completeness_bridge_test",
            Path(__file__).resolve().parents[1] / "scripts" / "capture_completeness.py")
        cc = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cc
        spec.loader.exec_module(cc)
        with tempfile.TemporaryDirectory() as td:
            fan = Path(td) / "fan.csv"
            fields = ["weekend_of", "snapshot_time", "show_date", "movie_title", "theatre_name",
                      "chain", "occupancy_pct", "reserved_seats", "total_seats", "notes"]
            with open(fan, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                w.writerows([_snap("F", "2026-09-11", "AMC Empire 25", "AMC", 20, snap="2026-09-11T15:00:00+00:00"),
                             _snap("F", "2026-09-11", "Regal Atlas Park", "REGL", 40, snap="2026-09-11T15:00:00+00:00")])
            orig = (P.FANDANGO_SNAPSHOTS_CSV, P.PRE_RESERVATION_CSV, P.SEAT_CSV,
                    cc.FANDANGO_CSV, cc.CINEMARK_CSV)
            try:
                P.FANDANGO_SNAPSHOTS_CSV = str(fan)
                P.PRE_RESERVATION_CSV = str(Path(td) / "none-native.csv")
                P.SEAT_CSV = str(Path(td) / "none-seat.csv")
                cc.FANDANGO_CSV = str(fan)
                cc.CINEMARK_CSV = str(Path(td) / "none-cnmk.csv")
                counts, films = cc.lane_counts("2026-09-11")
                self.assertEqual({"F"}, films)
                self.assertEqual(1, sum(counts["fandango"].values()))       # Regal row only
                self.assertEqual(1, sum(counts["amc_snapshot"].values()))   # the bridge row, via predict
            finally:
                (P.FANDANGO_SNAPSHOTS_CSV, P.PRE_RESERVATION_CSV, P.SEAT_CSV,
                 cc.FANDANGO_CSV, cc.CINEMARK_CSV) = orig


class BridgeTopTheatreRegimeTest(unittest.TestCase):
    def test_restrict_keeps_only_native_top_amc_theatres(self):
        pool = [{"name": "AMC Empire 25", "chain": "AMC"},
                {"name": "AMC Nowhere 4", "chain": "AMC"},
                {"name": "Regal Atlas Park", "chain": "REGL"}]
        kept = fc.restrict_to_amc_top(pool, {"AMC Empire 25"})
        self.assertEqual(["AMC Empire 25", "Regal Atlas Park"], [t["name"] for t in kept])
        # empty top set (selection unavailable) -> whole pool, never zero
        self.assertEqual(3, len(fc.restrict_to_amc_top(pool, set())))

    def test_native_top_set_is_the_snapshot_cap_and_is_amc_names(self):
        import scraper
        top = fc.amc_top_theatre_names()
        self.assertEqual(scraper.SNAPSHOT_TOP_THEATRE_CAP, len(top))
        self.assertTrue(all(n.startswith("AMC") or "Cinema" in n for n in top), sorted(top)[:5])
