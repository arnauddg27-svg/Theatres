import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import ModuleType
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", ModuleType("requests"))
playwright_mod = ModuleType("playwright")
playwright_async = ModuleType("playwright.async_api")
playwright_async.async_playwright = lambda: None
sys.modules.setdefault("playwright", playwright_mod)
sys.modules.setdefault("playwright.async_api", playwright_async)
import dashboard


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class DashboardTest(unittest.TestCase):
    def test_dashboard_reports_current_snapshot_when_regular_scrape_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            write_csv(
                data_dir / "pre-reservation-snapshots.csv",
                dashboard.PRE_RESERVATION_FIELDS,
                [
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "run-et",
                        "snapshot_time": "2026-05-07T03:00:00+00:00",
                        "show_date": "2026-05-07",
                        "theatre_name": "AMC A",
                        "timezone": "ET",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "10",
                        "total_seats": "100",
                    },
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "run-ct",
                        "snapshot_time": "2026-05-07T04:00:00+00:00",
                        "show_date": "2026-05-07",
                        "theatre_name": "AMC B",
                        "timezone": "CT",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "20",
                        "total_seats": "100",
                    },
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "run-pt",
                        "snapshot_time": "2026-05-07T05:00:00+00:00",
                        "show_date": "2026-05-07",
                        "theatre_name": "AMC C",
                        "timezone": "PT",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "30",
                        "total_seats": "100",
                    },
                ],
            )
            write_csv(
                data_dir / "seat-counts.csv",
                dashboard.SEAT_FIELDS,
                [
                    {
                        "weekend_of": "2026-05-01",
                        "run_id": "old-seat",
                        "date": "2026-05-03",
                        "day_of_week": "Sunday",
                        "theatre_name": "AMC Old",
                        "timezone": "ET",
                        "movie_title": "Old Movie",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-04T07:00:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "40",
                    }
                ],
            )
            write_csv(
                data_dir / "polymarket-markets.csv",
                dashboard.POLY_FIELDS,
                [
                    {
                        "date": "2026-05-07",
                        "movie_title": "Mortal Kombat II",
                        "market_url": "https://example.test",
                        "market_question": "Question",
                        "outcome_prices": "[\"0.5\", \"0.5\"]",
                        "volume": "100",
                        "market_id": "1",
                        "notes": "",
                    }
                ],
            )
            (data_dir / "showtime-links.json").write_text(json.dumps({
                "weekend_of": "2026-05-08",
                "collected_at": "2026-05-07T01:33:00",
                "_requested_movies": ["Mortal Kombat II"],
                "theatres": {},
            }))

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 8, 12, 0),
            )

        self.assertEqual("2026-05-08", data["current_weekend"])
        self.assertEqual("partial", data["runs"]["snapshot"]["status"])
        self.assertEqual(
            ["2026-05-08"],
            data["runs"]["snapshot"]["missing_show_dates"],
        )
        self.assertEqual("pending", data["runs"]["regular"]["status"])
        movie = data["movies"][0]
        self.assertEqual("Mortal Kombat II", movie["movie"])
        self.assertEqual(3, movie["snapshot"]["rows"])
        self.assertEqual({"ET": 1, "CT": 1, "PT": 1}, movie["snapshot"]["timezone_rows"])
        self.assertIsNone(movie["prediction"])

    def test_dashboard_marks_regular_scrape_ok_when_current_weekend_has_seat_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            write_csv(data_dir / "pre-reservation-snapshots.csv", dashboard.PRE_RESERVATION_FIELDS, [])
            write_csv(
                data_dir / "seat-counts.csv",
                dashboard.SEAT_FIELDS,
                [
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "seat-et",
                        "date": "2026-05-07",
                        "day_of_week": "Thursday",
                        "theatre_name": "AMC A",
                        "timezone": "ET",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-08T07:00:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "50",
                    },
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "seat-ct",
                        "date": "2026-05-07",
                        "day_of_week": "Thursday",
                        "theatre_name": "AMC B",
                        "timezone": "CT",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-08T07:10:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "40",
                    },
                    {
                        "weekend_of": "2026-05-08",
                        "run_id": "seat-pt",
                        "date": "2026-05-07",
                        "day_of_week": "Thursday",
                        "theatre_name": "AMC C",
                        "timezone": "PT",
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-08T07:20:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "30",
                    },
                ],
            )
            write_csv(data_dir / "polymarket-markets.csv", dashboard.POLY_FIELDS, [])
            (data_dir / "showtime-links.json").write_text("{}")

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 8, 12, 0),
            )

        self.assertEqual("2026-05-08", data["current_weekend"])
        self.assertEqual("ok", data["runs"]["regular"]["status"])
        self.assertEqual("Mortal Kombat II", data["movies"][0]["movie"])
        self.assertEqual(3, data["movies"][0]["seat_data"]["rows"])

    def test_dashboard_includes_model_audit_summary_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            write_csv(data_dir / "pre-reservation-snapshots.csv", dashboard.PRE_RESERVATION_FIELDS, [])
            write_csv(
                data_dir / "seat-counts.csv",
                dashboard.SEAT_FIELDS,
                [
                    {
                        "weekend_of": "2026-05-15",
                        "run_id": "seat-et",
                        "date": "2026-05-15",
                        "day_of_week": "Friday",
                        "theatre_name": "AMC A",
                        "timezone": "ET",
                        "movie_title": "Obsession",
                        "showtime": "7:00pm",
                        "check_time": "2026-05-16T07:00:00+00:00",
                        "total_seats": "100",
                        "seats_sold": "50",
                    },
                ],
            )
            write_csv(data_dir / "polymarket-markets.csv", dashboard.POLY_FIELDS, [])
            (data_dir / "showtime-links.json").write_text("{}")
            audit_dir = data_dir / "model-audits"
            audit_dir.mkdir()
            (audit_dir / "as-of-grid-summary.json").write_text(json.dumps({
                "overall": {"n": 7, "mape": 0.18, "bias_m": 1.2},
                "by_forecast_cut": {
                    "saturday_morning": {"n": 4, "mape": 0.12, "bias_m": -0.4}
                },
            }))

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 16, 12, 0),
            )

        self.assertEqual(7, data["model_audit"]["overall"]["n"])
        self.assertIn("saturday_morning", data["model_audit"]["by_forecast_cut"])

    def test_dashboard_model_precision_panel_uses_clean_headline_metric(self):
        self.assertIn("audit.headline_clean", dashboard.HTML_PAGE)
        self.assertIn("clean replays", dashboard.HTML_PAGE)

    def test_dashboard_snapshot_status_requires_each_date_timezone_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            rows = []
            for tz in ("ET", "CT", "PT"):
                rows.append({
                    "weekend_of": "2026-05-08",
                    "run_id": f"run-thu-{tz.lower()}",
                    "snapshot_time": "2026-05-07T03:00:00+00:00",
                    "show_date": "2026-05-07",
                    "theatre_name": f"AMC Thu {tz}",
                    "timezone": tz,
                    "movie_title": "Mortal Kombat II",
                    "showtime": "7:00pm",
                    "reserved_seats": "10",
                    "total_seats": "100",
                })
            rows.append({
                "weekend_of": "2026-05-08",
                "run_id": "run-fri-et",
                "snapshot_time": "2026-05-07T03:10:00+00:00",
                "show_date": "2026-05-08",
                "theatre_name": "AMC Fri ET",
                "timezone": "ET",
                "movie_title": "Mortal Kombat II",
                "showtime": "7:00pm",
                "reserved_seats": "10",
                "total_seats": "100",
            })
            for date in ("2026-05-09", "2026-05-10"):
                for tz in ("ET", "CT", "PT"):
                    rows.append({
                        "weekend_of": "2026-05-08",
                        "run_id": f"run-{date}-{tz.lower()}",
                        "snapshot_time": "2026-05-07T03:20:00+00:00",
                        "show_date": date,
                        "theatre_name": f"AMC {date} {tz}",
                        "timezone": tz,
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "10",
                        "total_seats": "100",
                    })
            write_csv(data_dir / "pre-reservation-snapshots.csv", dashboard.PRE_RESERVATION_FIELDS, rows)
            write_csv(data_dir / "seat-counts.csv", dashboard.SEAT_FIELDS, [])
            write_csv(data_dir / "polymarket-markets.csv", dashboard.POLY_FIELDS, [])
            (data_dir / "showtime-links.json").write_text("{}")

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 8, 12, 0),
            )

        snapshot = data["runs"]["snapshot"]
        self.assertEqual("partial", snapshot["status"])
        self.assertEqual([], snapshot["missing_show_dates"])
        self.assertEqual({"2026-05-08": ["CT", "PT"]}, snapshot["missing_date_timezones"])

    def test_dashboard_snapshot_status_checks_theatre_coverage_by_date_timezone(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            rows = []
            theatres = {}
            for date in ("2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"):
                for tz in ("ET", "CT", "PT"):
                    for idx in range(4):
                        name = f"AMC {tz} {idx}"
                        theatres.setdefault(name, {
                            "tz": tz,
                            "dates": {},
                        })
                        theatres[name]["dates"][date] = {
                            "movies": {
                                "Mortal Kombat II": [
                                    {"showtime": "7:00pm", "showtime_id": f"{date}-{tz}-{idx}"}
                                ]
                            }
                        }
                    rows.append({
                        "weekend_of": "2026-05-08",
                        "run_id": f"snapshot-{date}-{tz}",
                        "snapshot_time": "2026-05-07T03:00:00+00:00",
                        "show_date": date,
                        "theatre_name": f"AMC {tz} 0",
                        "timezone": tz,
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "10",
                        "total_seats": "100",
                    })

            write_csv(data_dir / "pre-reservation-snapshots.csv", dashboard.PRE_RESERVATION_FIELDS, rows)
            write_csv(data_dir / "seat-counts.csv", dashboard.SEAT_FIELDS, [])
            write_csv(data_dir / "polymarket-markets.csv", dashboard.POLY_FIELDS, [])
            (data_dir / "showtime-links.json").write_text(json.dumps({
                "weekend_of": "2026-05-08",
                "collected_at": "2026-05-07T01:33:00",
                "theatres": theatres,
            }))

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 8, 12, 0),
            )

        snapshot = data["runs"]["snapshot"]
        self.assertEqual("partial", snapshot["status"])
        self.assertEqual([], snapshot["missing_show_dates"])
        self.assertEqual({}, snapshot["missing_date_timezones"])
        self.assertTrue(snapshot["low_coverage_slices"])
        self.assertEqual(
            {"observed": 1, "expected": 4, "ratio": 0.25},
            snapshot["theatre_coverage"]["2026-05-08:ET"],
        )

    def test_dashboard_snapshot_health_uses_latest_snapshot_run_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            rows = []
            for date in ("2026-05-07", "2026-05-08"):
                for tz, snapshot_time in (
                    ("ET", "2026-05-08T03:30:00+00:00"),
                    ("CT", "2026-05-08T04:30:00+00:00"),
                    ("PT", "2026-05-08T06:30:00+00:00"),
                ):
                    rows.append({
                        "weekend_of": "2026-05-08",
                        "run_id": f"snapshot-{date}-{tz}",
                        "snapshot_time": snapshot_time,
                        "show_date": date,
                        "theatre_name": f"AMC {date} {tz}",
                        "timezone": tz,
                        "movie_title": "Mortal Kombat II",
                        "showtime": "7:00pm",
                        "reserved_seats": "10",
                        "total_seats": "100",
                    })

            write_csv(data_dir / "pre-reservation-snapshots.csv", dashboard.PRE_RESERVATION_FIELDS, rows)
            write_csv(data_dir / "seat-counts.csv", dashboard.SEAT_FIELDS, [])
            write_csv(data_dir / "polymarket-markets.csv", dashboard.POLY_FIELDS, [])
            (data_dir / "showtime-links.json").write_text("{}")

            data = dashboard.build_dashboard_data(
                data_dir=data_dir,
                auto_pull=False,
                include_predictions=False,
                now=datetime(2026, 5, 8, 12, 0),
            )

        snapshot = data["runs"]["snapshot"]
        self.assertEqual("ok", snapshot["status"])
        self.assertEqual(["2026-05-07", "2026-05-08"], snapshot["show_dates"])
        self.assertEqual([], snapshot["missing_show_dates"])

    def test_dashboard_snapshot_health_ignores_stale_timezone_slice(self):
        rows = [
            {
                "weekend_of": "2026-05-08",
                "run_id": "current-et",
                "snapshot_time": "2026-05-09T04:00:00+00:00",
                "show_date": "2026-05-08",
                "theatre_name": "AMC ET",
                "timezone": "ET",
                "movie_title": "Mortal Kombat II",
            },
            {
                "weekend_of": "2026-05-08",
                "run_id": "current-ct",
                "snapshot_time": "2026-05-09T05:00:00+00:00",
                "show_date": "2026-05-08",
                "theatre_name": "AMC CT",
                "timezone": "CT",
                "movie_title": "Mortal Kombat II",
            },
            {
                "weekend_of": "2026-05-08",
                "run_id": "stale-pt",
                "snapshot_time": "2026-05-08T05:00:00+00:00",
                "show_date": "2026-05-08",
                "theatre_name": "AMC PT",
                "timezone": "PT",
                "movie_title": "Mortal Kombat II",
            },
        ]

        fresh = dashboard.latest_snapshot_window_rows(rows)

        self.assertEqual(["CT", "ET"], sorted({row["timezone"] for row in fresh}))
        self.assertNotIn("stale-pt", {row["run_id"] for row in fresh})

    def test_phase1_status_surfaces_movie_timezone_link_holes(self):
        theatres = {}
        for tz in ("ET", "CT", "PT"):
            name = f"AMC {tz}"
            theatres[name] = {
                "tz": tz,
                "dates": {
                    "2026-05-07": {
                        "movies": {
                            "Mortal Kombat II": [
                                {"showtime": "7:00pm", "showtime_id": f"mk-{tz}"}
                            ],
                            **({} if tz == "PT" else {
                                "The Sheep Detectives": [
                                    {"showtime": "7:00pm", "showtime_id": f"sheep-{tz}"}
                                ]
                            }),
                        }
                    }
                },
            }
        showtime_links = {
            "weekend_of": "2026-05-08",
            "collected_at": "2026-05-07T01:33:00",
            "theatres": theatres,
        }

        status = dashboard.phase1_status(showtime_links, "2026-05-08")

        self.assertEqual("partial", status["status"])
        self.assertTrue(
            any("The Sheep Detectives 2026-05-07:PT 0/1" in item for item in status["low_coverage"])
        )


if __name__ == "__main__":
    unittest.main()
