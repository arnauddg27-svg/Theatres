import datetime as dt
import sys
import unittest
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


class DataOutageDetectionTests(unittest.TestCase):
    # Spider-Man 2026-07-31 profile: AMC Queue-It wall left 81/425 theatres,
    # 1% weighted coverage, 8% quality, snapshot weight 5%.
    OUTAGE = {"seat_weighted_coverage_ratio": 0.01, "seat_data_quality": 0.08,
              "snapshot_effective_model_weight": 0.05}

    def test_queue_wall_profile_flags(self):
        self.assertTrue(P.detect_data_outage(dict(self.OUTAGE)))

    def test_healthy_weekend_does_not_flag(self):
        # Odyssey full-weekend profile
        self.assertFalse(P.detect_data_outage({
            "seat_weighted_coverage_ratio": 0.89, "seat_data_quality": 0.92,
            "snapshot_effective_model_weight": 0.4}))

    def test_snapshot_layer_can_rescue(self):
        # Seat panel starved but a strong snapshot layer still measures demand
        pred = dict(self.OUTAGE, snapshot_effective_model_weight=0.5)
        self.assertFalse(P.detect_data_outage(pred))

    def test_thursday_stage_thin_seat_is_not_an_outage(self):
        # Ordinary early-week read: quality above the floor -> never flagged,
        # so the flag cannot fire on normal Thursday-stage forecasts.
        self.assertFalse(P.detect_data_outage({
            "seat_weighted_coverage_ratio": 0.04, "seat_data_quality": 0.30,
            "snapshot_effective_model_weight": 0.05}))

    def test_uses_the_weight_field_the_snapshot_layer_actually_writes(self):
        # snapshot_{original,effective}_model_weight are written only by the
        # disagreement profiler, which is not wired into production. Reading
        # them alone left this clause permanently true. A healthy snapshot
        # layer reports snapshot_model_weight, and that must veto the flag.
        healthy_snapshot = {"seat_weighted_coverage_ratio": 0.01,
                            "seat_data_quality": 0.08,
                            "snapshot_model_weight": 0.45}
        self.assertFalse(P.detect_data_outage(healthy_snapshot))
        starved = dict(healthy_snapshot, snapshot_model_weight=0.05)
        self.assertTrue(P.detect_data_outage(starved))

    def test_missing_fields_default_safe(self):
        # No coverage fields at all (e.g. very old preds) -> defaults healthy
        self.assertFalse(P.detect_data_outage({}))


class SchedulerRetrySlotTests(unittest.TestCase):
    def _slots(self):
        import importlib.util
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "sched_mod_outage_test",
            root / "scripts" / "schedule_box_office_pipeline.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod.SLOTS

    def test_late_listed_market_still_gets_links_thursday(self):
        # One Night Only (2026-08-07) was listed after Wednesday's Phase 1
        # cleanly skipped, so links stayed on the prior weekend and every
        # Friday snapshot lane hard-failed. One Thursday pass per group closes
        # that window; the late pair stays Tue/Wed to bound cost.
        slots = [s for s in self._slots() if s.inputs.get("phase") == "collect-links"]
        early = [s for s in slots if s.name.endswith(("13Z", "15Z", "17Z"))]
        late = [s for s in slots if s.name.endswith(("19Z", "21Z", "23Z"))]
        self.assertEqual(3, len(early))
        for s in early:
            self.assertIn(4, s.cron_days)   # Thursday
        for s in late:
            self.assertNotIn(4, s.cron_days)

    def test_amc_snapshot_has_wall_retry_slots(self):
        slots = self._slots()
        amc_snap = [s for s in slots if s.title == "box office scrape snapshot"]
        names = {s.name for s in amc_snap}
        self.assertIn("snapshot 14:30Z", names)
        self.assertIn("snapshot 22:30Z", names)
        base = next(s for s in amc_snap if s.name == "snapshot 02:30Z")
        for s in amc_snap:
            # the retries must carry the same PHASE INPUTS as the original...
            self.assertEqual(s.inputs, base.inputs)
        # ...but pinning cron_days to the 02:30Z set would block a future
        # correction, so assert the invariants that actually hold instead.
        # Since the Mon-Wed early-lead expansion the daytime 14:30Z/22:30Z
        # slots run every UTC day (Mon-Wed local daytime probes the UPCOMING
        # weekend). The night 02:30Z slot still must exclude UTC Monday: at
        # 22:30 local that is Sunday NIGHT, after the weekend has closed —
        # Sunday is collected by the Monday 07:00Z regular scrape instead.
        night = next(s for s in amc_snap if s.name == "snapshot 02:30Z")
        with self.subTest(slot=night.name):
            self.assertNotIn(1, night.cron_days, "02:30Z includes UTC Monday (Sunday night local)")
        for s in amc_snap:
            if s.name == "snapshot 02:30Z":
                continue
            with self.subTest(slot=s.name):
                self.assertEqual(7, len(s.cron_days), f"{s.name}: {sorted(s.cron_days)}")


if __name__ == "__main__":
    unittest.main()


class MetadataMissingWarningTests(unittest.TestCase):
    """A film with no metadata row must say its audience protections are off.

    PAW Patrol (2026-08-14) had no movie-metadata.csv row, so the broad_family
    cross-chain gate never engaged; the volume share drifted 10% -> 23% as
    walk-up-blind Regal/Cinemark snapshots accumulated across the weekend, and
    the film recorded -36% while every layer LOOKED correctly wired. 18 of the
    27 recorded films had no metadata row — the gate was dead by default.
    """

    def test_flag_set_when_metadata_absent(self):
        import predict as P
        import io, contextlib
        pred = {"movie": "T", "daily_details": {}, "daily_estimates": {},
                "n_theatres_total": 1, "n_days": 0, "seat_mid_m": 1.0,
                "seat_low_m": 0.5, "seat_high_m": 1.5, "regression_mid_m": 1.0,
                "regression_low_m": 0.5, "regression_high_m": 1.5,
                "snapshot_days": [], "audience_type": "",
                "metadata_missing": True}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                P.print_prediction(pred)
            except Exception:
                pass
        self.assertIn("NO AUDIENCE METADATA", buf.getvalue())

    def test_no_warning_when_metadata_present(self):
        import predict as P
        import io, contextlib
        pred = {"movie": "T", "daily_details": {}, "daily_estimates": {},
                "n_theatres_total": 1, "n_days": 0, "seat_mid_m": 1.0,
                "seat_low_m": 0.5, "seat_high_m": 1.5, "regression_mid_m": 1.0,
                "regression_low_m": 0.5, "regression_high_m": 1.5,
                "snapshot_days": [], "audience_type": "broad_family",
                "metadata_missing": False}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                P.print_prediction(pred)
            except Exception:
                pass
        self.assertNotIn("NO AUDIENCE METADATA", buf.getvalue())


class DisagreementAnnotationTests(unittest.TestCase):
    """The disagreement profile is annotation-only: recorded, never applied.

    select_regression_prediction documents that the production forecast takes
    the regression block with NO stacked adjustments; the profiler existed as
    an operator warning but nothing populated model_component_disagreement, so
    the warning block was unreachable dead code. It is now populated after the
    forecast is finalized — the backtest is byte-identical (17.2% before and
    after) and only the printout and recorded fields change.
    """

    def test_profile_populated_and_weights_reported(self):
        import predict as P
        pred = {"movie": "T", "seat_mid_m": 20.0, "snapshot_mid_m": 40.0,
                "seat_primary_mid_m": 20.0, "snapshot_model_weight": 0.30}
        profile = P.model_component_disagreement_profile(pred)
        self.assertEqual("high", profile["severity"])   # 2.0x apart
        self.assertLess(profile["snapshot_weight_multiplier"], 1.0)

    def test_wiring_is_annotation_only(self):
        # the wiring must come AFTER select_regression_prediction and must not
        # feed the multiplier back into any forecast number
        import predict as P
        import inspect
        src = inspect.getsource(P.predict_movie)
        i = src.index("select_regression_prediction(result, cal)")
        after = src[i:]
        self.assertIn("model_component_disagreement_profile(result)", after)
        self.assertIn("not applied", after)


class ZeroOutputFloorTests(unittest.TestCase):
    """Lanes with work to do must fail loudly on zero output, not exit green.

    Soft-fail audit 2026-08-23: the regular (model-driving) lane could print
    'Run complete — 0 seat counts' and exit 0; fandango's main() discarded
    collect()'s totals entirely. Green-zero is reserved for genuinely quiet
    weekends (no tracked titles anywhere)."""

    def test_regular_lane_floor_present(self):
        src = (Path(__file__).resolve().parents[1] / "scraper.py").read_text()
        i = src.index("Run complete")
        block = src[i:i + 1600]
        self.assertIn("wrote ZERO seat rows", block)
        self.assertIn("not snapshots_only and poly_markets and written_rows == 0", block)

    def test_fandango_floor_present(self):
        src = (Path(__file__).resolve().parents[1] / "fandango_collect.py").read_text()
        i = src.index("OUTPUT FLOOR")
        block = src[i:i + 1400]
        self.assertIn('totals.get("written", 0) == 0', block)
        self.assertIn("sys.exit(1)", block)

    def test_quiet_weekend_still_green_in_fandango(self):
        # collect() returns {} when no titles anywhere -> the floor must not fire
        src = (Path(__file__).resolve().parents[1] / "fandango_collect.py").read_text()
        i = src.index("OUTPUT FLOOR")
        self.assertIn("if totals and", src[i:i + 1400])
