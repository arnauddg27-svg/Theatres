"""The live headline is now logged (data/prediction-log.csv) and the history
table says when a stored grade is a degraded replay rather than the live
forecast (2026-09-18 audit: Practical Magic 2 showed $32.4M, replay recorded
$23.0M, actual $30.0M)."""
import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


def _pred():
    return {
        "movie": "Test Film", "weekend_of": "2026-09-18",
        "regression_mid_m": 47.0, "regression_low_m": 34.8, "regression_high_m": 54.0,
        "regression_source": "snapshot-daily-evidence",
        "seat_mid_m": 91.0, "snapshot_mid_m": 46.2, "coverage_ratio": 0.99,
        "daily_details": {"Thursday": {"amc_market_share_used": 0.288}},
        "poly_result": {"ev": 66.6},
    }


class PredictionLogTest(unittest.TestCase):
    def test_row_captures_what_the_run_showed(self):
        row = P.prediction_log_row(_pred(), logged_at=datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc), weekend_of="2026-09-18")
        self.assertEqual("2026-09-18T12:00:00Z", row["logged_at"])
        self.assertEqual("2026-09-18", row["weekend_of"])
        self.assertEqual((47.0, 34.8, 54.0), (row["headline_mid_m"], row["headline_low_m"], row["headline_high_m"]))
        self.assertEqual("snapshot-daily-evidence", row["source"])
        self.assertEqual((91.0, 46.2, 0.288, 66.6), (row["seat_only_m"], row["snapshot_mid_m"], row["amc_share_used"], row["poly_ev_m"]))
        self.assertEqual("Thursday", row["seat_days"])
        self.assertEqual(list(row), P.PREDICTION_LOG_FIELDS)

    def test_append_creates_header_once_and_never_raises(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "log.csv")
            self.assertTrue(P.append_prediction_log(_pred(), path=path))
            self.assertTrue(P.append_prediction_log(_pred(), path=path))
            rows = list(csv.DictReader(open(path)))
            self.assertEqual(2, len(rows))
            self.assertEqual("Test Film", rows[1]["movie"])
            # a broken pred is reported, not raised
            self.assertFalse(P.append_prediction_log({"daily_details": None, "regression_mid_m": "x"}, path=os.path.join(td, "nope", "x.csv")))

    def test_history_flag_names_degraded_replays(self):
        self.assertEqual("", P.history_entry_flag({"coverage_ratio": 0.99}))
        self.assertEqual("data outage", P.history_entry_flag({"data_outage": True, "coverage_ratio": 0.1}))
        self.assertEqual("replay excluded Sat/Sun",
                         P.history_entry_flag({"coverage_ratio": 0.58, "calibration_excluded_days": ["Saturday", "Sunday"]}))
        self.assertEqual("coverage 18%", P.history_entry_flag({"coverage_ratio": 0.175}))

    def test_resident_evil_has_metadata(self):
        meta = P.load_movie_metadata()
        mm = P.metadata_for_movie("Resident Evil", meta)
        self.assertIsNotNone(mm)
        self.assertEqual(("horror", "horror_fan", "R", 3500),
                         (mm.genre, mm.audience_type, mm.rating, mm.national_theatre_count))

    def test_prediction_log_is_committed_by_finalize(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        import stage_finalize_outputs as sfo
        self.assertIn("box-office-tracker/data/prediction-log.csv", sfo.OUTPUT_FILES)


class LiveHeadlineGradeTest(unittest.TestCase):
    ROWS = [
        {"weekend_of": "2026-09-18", "movie": "Resident Evil", "logged_at": "2026-09-18T07:00:00Z", "headline_mid_m": "47.0", "headline_low_m": "34.8", "headline_high_m": "54.0", "seat_days": "Thursday", "source": "snapshot-daily-evidence"},
        {"weekend_of": "2026-09-18", "movie": "Resident Evil", "logged_at": "2026-09-19T07:00:00Z", "headline_mid_m": "58.0", "headline_low_m": "50", "headline_high_m": "66", "seat_days": "Thursday+Friday", "source": "regression"},
        {"weekend_of": "2026-09-18", "movie": "Resident Evil", "logged_at": "2026-09-20T23:10:00Z", "headline_mid_m": "63.0", "headline_low_m": "58", "headline_high_m": "68", "seat_days": "Thursday+Friday+Saturday", "source": "regression"},
        {"weekend_of": "2026-09-18", "movie": "Resident Evil", "logged_at": "2026-09-21T12:30:00Z", "headline_mid_m": "99.0", "headline_low_m": "1", "headline_high_m": "2", "seat_days": "Thursday+Friday+Saturday+Sunday", "source": "post-weekend"},
        {"weekend_of": "2026-09-11", "movie": "Resident Evil", "logged_at": "2026-09-13T12:30:00Z", "headline_mid_m": "5.0", "headline_low_m": "1", "headline_high_m": "2", "seat_days": "Thursday", "source": "x"},
    ]

    def test_final_is_last_before_monday_noon_and_thursday_stage_is_kept(self):
        out = P.select_live_headline(self.ROWS, "2026-09-18")
        self.assertEqual(63.0, out["mid_m"])                       # Monday 12:30Z row excluded
        self.assertEqual("2026-09-20T23:10:00Z", out["logged_at"])
        self.assertEqual(47.0, out["thursday_mid_m"])
        self.assertEqual(3, out["rows"])
        self.assertIsNone(P.select_live_headline(self.ROWS, "2026-10-02"))
        self.assertIsNone(P.select_live_headline([], "2026-09-18"))

    def test_lookup_reads_the_log_by_movie(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "log.csv")
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(self.ROWS[0])); w.writeheader(); w.writerows(self.ROWS)
            self.assertEqual(63.0, P.live_headline_for("resident evil", "2026-09-18", path=path)["mid_m"])
            self.assertIsNone(P.live_headline_for("Other Film", "2026-09-18", path=path))
            self.assertIsNone(P.live_headline_for("Resident Evil", "2026-09-18", path=os.path.join(td, "missing.csv")))

    def test_record_result_stores_live_grade_beside_the_replay(self):
        import calibrate as C
        import json
        cal = json.load(open(Path(__file__).resolve().parents[1] / "data" / "calibration.json"))
        cal["history"] = []                                          # real shape, empty history
        saved = C.CALIBRATION_JSON
        with tempfile.TemporaryDirectory() as td:
            C.CALIBRATION_JSON = os.path.join(td, "calibration.json")   # record_result saves to disk
            try:
                entry = C.record_result(cal, "Resident Evil", "2026-09-18", predicted_mid=23.0, predicted_low=12.0,
                                        predicted_high=52.0, daily_actuals={"Friday": 25.0, "Saturday": 25.0, "Sunday": 15.0},
                                        daily_predictions={"Friday": 8.0, "Saturday": 8.0, "Sunday": 7.0}, n_theatres=421, n_days=3,
                                        live_headline={"mid_m": 63.0, "logged_at": "2026-09-20T23:10:00Z"})
                self.assertEqual(23.0, entry["predicted_mid"])             # replay untouched: it is the fit input
                self.assertEqual(63.0, entry["live_headline"]["mid_m"])
                self.assertAlmostEqual(-3.1, entry["live_error_pct"], places=1)
                e2 = C.record_result(cal, "X", "2026-09-18", predicted_mid=1, predicted_low=1, predicted_high=1,
                                     daily_actuals={"Friday": 1.0}, daily_predictions={"Friday": 1.0}, n_theatres=1, n_days=1)
                self.assertNotIn("live_headline", e2)
                self.assertTrue(os.path.exists(C.CALIBRATION_JSON))
            finally:
                C.CALIBRATION_JSON = saved


class HorrorSnapshotLiftTest(unittest.TestCase):
    def test_lift_only_for_horror_tags(self):
        from types import SimpleNamespace as NS
        self.assertEqual(P.HORROR_SNAPSHOT_LIFT, P.genre_snapshot_lift(NS(genre="horror")))
        self.assertEqual(P.HORROR_SNAPSHOT_LIFT, P.genre_snapshot_lift(NS(genre="Horror_Comedy")))
        self.assertEqual(1.0, P.genre_snapshot_lift(NS(genre="animation")))
        self.assertEqual(1.0, P.genre_snapshot_lift(NS(genre="")))
        self.assertEqual(1.0, P.genre_snapshot_lift(None))
        self.assertTrue(1.05 <= P.HORROR_SNAPSHOT_LIFT <= 1.25, "a lift outside this range needs new evidence")

    def test_apply_scales_totals_and_days_once(self):
        layer = {"snapshot_mid_m": 40.0, "snapshot_low_m": 36.0, "snapshot_high_m": 44.0,
                 "snapshot_daily_details": {"Saturday": {"domestic_mid": 10e6, "domestic_low": 9e6, "domestic_high": 11e6, "coverage_ratio": 0.9}}}
        out = P.apply_snapshot_lift(layer, 1.1)
        self.assertAlmostEqual(44.0, out["snapshot_mid_m"]); self.assertAlmostEqual(39.6, out["snapshot_low_m"])
        self.assertAlmostEqual(11e6, out["snapshot_daily_details"]["Saturday"]["domestic_mid"])
        self.assertEqual(0.9, out["snapshot_daily_details"]["Saturday"]["coverage_ratio"])
        self.assertEqual(1.1, out["snapshot_genre_lift"])
        self.assertIsNone(P.apply_snapshot_lift(None, 1.1))
        same = {"snapshot_mid_m": 5.0}
        self.assertEqual(5.0, P.apply_snapshot_lift(same, 1.0)["snapshot_mid_m"])

    def test_share_weight_is_the_shrunk_value(self):
        self.assertEqual(0.5, P.CROSS_CHAIN_SHARE_WEIGHT)
