"""Recorded actuals must mean one thing: Thursday = previews, Friday = Friday."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import seat_regression  # noqa: E402
import model_calibration  # noqa: E402
import split_thursday_previews as sp  # noqa: E402


class SplitTest(unittest.TestCase):
    def test_split_moves_previews_out_of_friday_and_keeps_the_total(self):
        e = {"movie": "X", "daily_actuals": {"Friday": 50.98, "Saturday": 41.7, "Sunday": 30.8}, "actual_total": 123.5,
             "previews_folded_into_friday": True}
        self.assertTrue(sp.split_entry(e, 17.6, "Variety"))
        da = e["daily_actuals"]
        self.assertAlmostEqual(17.6, da["Thursday"]); self.assertAlmostEqual(33.38, da["Friday"], places=2)
        self.assertAlmostEqual(123.5, sum(da.values()), places=1)
        self.assertNotIn("previews_folded_into_friday", e)
        self.assertFalse(sp.split_entry(e, 17.6, "Variety"), "idempotent")

    def test_split_refuses_when_previews_exceed_friday(self):
        e = {"daily_actuals": {"Friday": 1.0}}
        self.assertFalse(sp.split_entry(e, 1.7, "x")); self.assertNotIn("Thursday", e["daily_actuals"])

    def test_flag_only_when_thursday_missing(self):
        self.assertTrue(sp.flag_entry({"daily_actuals": {"Friday": 2.0}}))
        self.assertFalse(sp.flag_entry({"daily_actuals": {"Thursday": 0.5, "Friday": 2.0}}))

    def test_fits_skip_thursday_and_friday_of_a_folded_entry(self):
        folded = {"movie": "F", "previews_folded_into_friday": True,
                  "raw_daily_predictions": {"Thursday": 1, "Friday": 3, "Saturday": 4, "Sunday": 3},
                  "daily_actuals": {"Friday": 3.5, "Saturday": 4, "Sunday": 3},
                  "daily_coverage_ratios": {"Thursday": 0.9, "Friday": 0.9, "Saturday": 0.9, "Sunday": 0.9},
                  "snapshot_daily_predictions": {"Friday": 3, "Saturday": 4, "Sunday": 3},
                  "snapshot_daily_lead_buckets": {"Friday": "1d", "Saturday": "2d", "Sunday": "3d"}}
        self.assertEqual({"Saturday", "Sunday"}, {r["day"] for r in seat_regression.build_seat_rows([folded])})
        self.assertEqual({"Saturday", "Sunday"}, {r["day"] for r in seat_regression.build_snapshot_rows([folded])})
        self.assertEqual({"Thursday", "Friday"}, model_calibration.excluded_calibration_days(folded))
        clean = dict(folded); clean.pop("previews_folded_into_friday")
        self.assertIn("Friday", {r["day"] for r in seat_regression.build_seat_rows([clean])})
        self.assertEqual(set(), model_calibration.excluded_calibration_days(clean))

    def test_preview_table_is_plausible(self):
        for movie, (m, src) in sp.PREVIEWS.items():
            self.assertTrue(0.1 <= m <= 30, movie); self.assertTrue(src, movie)
