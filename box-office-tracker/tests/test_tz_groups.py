import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tz_groups  # noqa: E402


class MountainLegTest(unittest.TestCase):
    def test_arizona_follows_its_clock(self):
        az = {"name": "AMC Arrowhead 14", "state": "AZ"}
        summer = datetime(2026, 7, 1, 18, tzinfo=timezone.utc)
        winter = datetime(2026, 12, 1, 18, tzinfo=timezone.utc)
        self.assertEqual("PT", tz_groups.effective_group(az, "MT", now=summer))   # UTC-7 = PDT
        self.assertEqual("MT", tz_groups.effective_group(az, "MT", now=winter))   # UTC-7 = MST
        co = {"name": "AMC Castle Rock 12", "state": "CO"}
        self.assertEqual("MT", tz_groups.effective_group(co, "MT", now=summer))
        self.assertEqual("ET", tz_groups.effective_group({"state": "AZ"}, "ET", now=summer))

    def test_mountain_theatres_are_collected_but_not_modelled(self):
        import scraper
        import predict
        legs = scraper.load_theatres()
        names = {t["name"]: g for g, ts in legs.items() for t in ts}
        self.assertIn("AMC Albuquerque 12", names)
        self.assertEqual("mountain", next(t for t in legs[names["AMC Albuquerque 12"]]
                                          if t["name"] == "AMC Albuquerque 12")["cohort"])
        self.assertFalse(predict.model_allows_theatre("AMC Albuquerque 12"))
        self.assertTrue(predict.model_allows_theatre("AMC Empire 25"))

    def test_scheduler_has_mountain_link_slots(self):
        import importlib.util
        path = Path(__file__).resolve().parents[1] / "scripts" / "schedule_box_office_pipeline.py"
        spec = importlib.util.spec_from_file_location("sched_mt", path)
        mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
        mt = [s for s in mod.SLOTS if s.inputs.get("tz_group") == "MT"]
        self.assertEqual({"collect-links MT 16Z", "collect-links MT 22Z"}, {s.name for s in mt})
