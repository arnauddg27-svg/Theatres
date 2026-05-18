import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import model_pipeline
import model_audit


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class ModelPipelineTest(unittest.TestCase):
    def test_snapshot_training_rows_match_only_final_rows_after_snapshot(self):
        snapshot_rows = [
            {
                "weekend_of": "2026-05-15",
                "movie_title": "Obsession",
                "snapshot_time": "2026-05-15T15:00:00+00:00",
                "show_date": "2026-05-16",
                "day_of_week": "Saturday",
                "theatre_name": "AMC A",
                "timezone": "ET",
                "showtime": "7:00pm",
                "showtime_id": "abc123",
                "total_seats": "100",
                "reserved_seats": "12",
                "amc_seat_map_url": "https://www.amctheatres.com/showtimes/abc123/seats",
            },
            {
                "weekend_of": "2026-05-15",
                "movie_title": "Obsession",
                "snapshot_time": "2026-05-17T15:00:00+00:00",
                "show_date": "2026-05-16",
                "day_of_week": "Saturday",
                "theatre_name": "AMC A",
                "timezone": "ET",
                "showtime": "7:00pm",
                "showtime_id": "abc123",
                "total_seats": "100",
                "reserved_seats": "99",
                "amc_seat_map_url": "https://www.amctheatres.com/showtimes/abc123/seats",
            },
        ]
        seat_rows = [
            {
                "weekend_of": "2026-05-15",
                "movie_title": "Obsession",
                "date": "2026-05-16",
                "day_of_week": "Saturday",
                "theatre_name": "AMC A",
                "timezone": "ET",
                "showtime": "7:00pm",
                "check_time": "2026-05-17T03:00:00+00:00",
                "total_seats": "100",
                "seats_sold": "31",
                "amc_seat_map_url": "https://www.amctheatres.com/showtimes/abc123/seats",
            }
        ]

        rows = model_pipeline.build_snapshot_to_final_showtime_rows(
            snapshot_rows,
            seat_rows,
        )

        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("Obsession", row["movie_title"])
        self.assertEqual("Saturday", row["day_of_week"])
        self.assertEqual(12, row["snapshot_reserved_seats"])
        self.assertEqual(31, row["final_seats_sold"])
        self.assertEqual(19, row["pickup_seats"])
        self.assertGreater(row["minutes_to_showtime"], 0)

    def test_as_of_filter_excludes_future_rows(self):
        rows = [
            {"movie_title": "Past", "check_time": "2026-05-16T07:00:00+00:00"},
            {"movie_title": "Future", "check_time": "2026-05-16T09:00:00+00:00"},
            {"movie_title": "Blank", "check_time": ""},
        ]

        kept = model_pipeline.filter_rows_as_of(
            rows,
            "check_time",
            datetime.fromisoformat("2026-05-16T08:00:00+00:00"),
        )

        self.assertEqual(["Past"], [row["movie_title"] for row in kept])

    def test_seat_day_training_rows_include_missing_bucket_flags_and_capacity(self):
        rows = [
            {
                "weekend_of": "2026-05-15",
                "movie_title": "Obsession",
                "date": "2026-05-16",
                "day_of_week": "Saturday",
                "theatre_name": "AMC A",
                "timezone": "ET",
                "showtime": "7:00pm",
                "total_seats": "100",
                "seats_sold": "50",
            },
            {
                "weekend_of": "2026-05-15",
                "movie_title": "Obsession",
                "date": "2026-05-16",
                "day_of_week": "Saturday",
                "theatre_name": "AMC B",
                "timezone": "PT",
                "showtime": "8:00pm",
                "total_seats": "80",
                "seats_sold": "20",
            },
        ]

        table = model_pipeline.build_seat_to_amc_day_rows(
            rows,
            expected_timezone_counts={"ET": 1, "CT": 1, "PT": 1},
        )

        self.assertEqual(1, len(table))
        row = table[0]
        self.assertEqual(2, row["n_showings"])
        self.assertEqual(180, row["sample_capacity"])
        self.assertEqual(70, row["sample_seats_sold"])
        self.assertEqual(1, row["missing_timezone_CT"])
        self.assertEqual(0, row["missing_timezone_ET"])
        self.assertLess(row["timezone_coverage_ratio"], 1.0)
        self.assertEqual("medium", row["coverage_tier"])

    def test_theatre_count_feature_is_non_linear_not_direct_multiplier(self):
        limited = model_pipeline.release_footprint_features(2615)
        wide = model_pipeline.release_footprint_features(4200)
        direct_ratio = 2615 / 4000

        self.assertLess(limited["footprint_factor"], 1.0)
        self.assertGreater(limited["footprint_factor"], direct_ratio)
        self.assertAlmostEqual(1.0, wide["footprint_factor"], delta=0.10)
        self.assertGreater(limited["log_theatre_count"], 0)

    def test_model_card_intervals_widen_with_missing_data(self):
        high = model_pipeline.build_model_card(
            {
                "movie": "Sample",
                "model_forecast_mid_m": 20.0,
                "model_forecast_low_m": 18.0,
                "model_forecast_high_m": 22.0,
                "seat_weighted_coverage_ratio": 0.95,
                "missing_data_profile": {"missing_days": [], "missing_timezone_days": []},
                "snapshot_model_weight": 0.50,
                "seat_primary_w_direct": 0.70,
                "seat_primary_w_comp": 0.30,
            },
            residual_errors=[0.05, -0.04, 0.06, -0.05],
        )
        low = model_pipeline.build_model_card(
            {
                "movie": "Sample",
                "model_forecast_mid_m": 20.0,
                "model_forecast_low_m": 18.0,
                "model_forecast_high_m": 22.0,
                "seat_weighted_coverage_ratio": 0.35,
                "missing_data_profile": {
                    "missing_days": ["Sunday"],
                    "missing_timezone_days": ["Saturday"],
                    "partial_daypart_days": ["Saturday"],
                },
                "snapshot_model_weight": 0.10,
                "seat_primary_w_direct": 0.50,
                "seat_primary_w_comp": 0.50,
            },
            residual_errors=[0.05, -0.04, 0.06, -0.05],
        )

        self.assertLess(high["intervals"]["80"]["width_m"], low["intervals"]["80"]["width_m"])
        self.assertEqual("high", high["coverage_grade"])
        self.assertEqual("low", low["coverage_grade"])
        self.assertFalse(low["high_confidence"])
        self.assertEqual(0.10, low["components"]["snapshot_weight"])
        self.assertIn("missing Sunday", low["biggest_missing_data_risks"])

    def test_export_training_tables_writes_all_three_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            out_dir = data_dir / "model-audits"
            write_csv(
                data_dir / "seat-counts.csv",
                [
                    "weekend_of", "movie_title", "date", "day_of_week",
                    "theatre_name", "timezone", "showtime", "check_time",
                    "total_seats", "seats_sold", "amc_seat_map_url",
                ],
                [
                    {
                        "weekend_of": "2026-05-15",
                        "movie_title": "Obsession",
                        "date": "2026-05-16",
                        "day_of_week": "Saturday",
                        "theatre_name": "AMC A",
                        "timezone": "ET",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-17T03:00:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "31",
                        "amc_seat_map_url": "https://www.amctheatres.com/showtimes/abc123/seats",
                    }
                ],
            )
            write_csv(
                data_dir / "pre-reservation-snapshots.csv",
                [
                    "weekend_of", "movie_title", "snapshot_time", "show_date",
                    "day_of_week", "theatre_name", "timezone", "showtime",
                    "showtime_id", "total_seats", "reserved_seats",
                    "amc_seat_map_url",
                ],
                [
                    {
                        "weekend_of": "2026-05-15",
                        "movie_title": "Obsession",
                        "snapshot_time": "2026-05-15T15:00:00+00:00",
                        "show_date": "2026-05-16",
                        "day_of_week": "Saturday",
                        "theatre_name": "AMC A",
                        "timezone": "ET",
                        "showtime": "7:00pm",
                        "showtime_id": "abc123",
                        "total_seats": "100",
                        "reserved_seats": "12",
                        "amc_seat_map_url": "https://www.amctheatres.com/showtimes/abc123/seats",
                    }
                ],
            )
            (data_dir / "calibration.json").write_text(json.dumps({
                "history": [
                    {
                        "movie": "Obsession",
                        "weekend_of": "2026-05-15",
                        "predicted_mid": 17.2,
                        "actual_total": 16.1,
                        "daily_actuals": {"Thursday": 2.6},
                        "coverage_ratio": 0.8,
                    }
                ],
                "calibration_factors": {},
            }))
            write_csv(
                data_dir / "movie-metadata.csv",
                [
                    "movie", "weekend_of", "genre", "audience_type",
                    "franchise_type", "rating", "national_theatre_count",
                ],
                [
                    {
                        "movie": "Obsession",
                        "weekend_of": "2026-05-15",
                        "genre": "horror",
                        "audience_type": "horror_fan",
                        "franchise_type": "original",
                        "rating": "R",
                        "national_theatre_count": "2615",
                    }
                ],
            )

            manifest = model_pipeline.export_training_tables(data_dir, out_dir)

            self.assertEqual(1, manifest["snapshot_to_final_showtimes"]["rows"])
            self.assertEqual(1, manifest["seat_to_amc_day"]["rows"])
            self.assertEqual(1, manifest["movie_weekend_actuals"]["rows"])
            for table in manifest.values():
                self.assertTrue(Path(table["path"]).exists())

    def test_replay_rows_use_only_prior_actuals_for_interval_calibration(self):
        calibration = {
            "calibration_factors": {
                "day_weights": {
                    "Thursday": 0.12,
                    "Friday": 0.32,
                    "Saturday": 0.33,
                    "Sunday": 0.23,
                }
            },
            "history": [
                {
                    "movie": "Movie A",
                    "weekend_of": "2026-05-01",
                    "actual_total": 100.0,
                    "daily_predictions": {
                        "Thursday": 10.0,
                        "Friday": 30.0,
                        "Saturday": 30.0,
                        "Sunday": 20.0,
                    },
                    "coverage_ratio": 0.9,
                },
                {
                    "movie": "Movie B",
                    "weekend_of": "2026-05-08",
                    "actual_total": 50.0,
                    "daily_predictions": {
                        "Thursday": 5.0,
                        "Friday": 15.0,
                        "Saturday": 15.0,
                        "Sunday": 10.0,
                    },
                    "coverage_ratio": 0.9,
                },
            ],
        }

        rows = model_audit.history_replay_rows(calibration)
        final_rows = [row for row in rows if row["forecast_cut"] == "final_pre_estimate"]

        self.assertEqual(0, final_rows[0]["prior_actual_count"])
        self.assertEqual(1, final_rows[1]["prior_actual_count"])

    def test_replay_does_not_fabricate_thursday_morning_from_final_prediction(self):
        calibration = {
            "calibration_factors": {},
            "history": [
                {
                    "movie": "Movie A",
                    "weekend_of": "2026-05-01",
                    "predicted_mid": 100.0,
                    "actual_total": 80.0,
                    "daily_predictions": {
                        "Thursday": 8.0,
                    },
                }
            ],
        }

        rows = model_audit.history_replay_rows(calibration)

        self.assertNotIn(
            "thursday_morning",
            {row["forecast_cut"] for row in rows},
        )


if __name__ == "__main__":
    unittest.main()
