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
