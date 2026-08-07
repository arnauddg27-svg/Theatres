import sys
import unittest
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
            # retries are exact clones: same inputs, same cron days
            self.assertEqual(s.inputs, base.inputs)
            self.assertEqual(s.cron_days, base.cron_days)


if __name__ == "__main__":
    unittest.main()
