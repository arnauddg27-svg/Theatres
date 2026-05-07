import csv
import json
import tempfile
import unittest
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
            )

        self.assertEqual("2026-05-08", data["current_weekend"])
        self.assertEqual("partial", data["runs"]["snapshot"]["status"])
        self.assertEqual(
            ["2026-05-08", "2026-05-09", "2026-05-10"],
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
            )

        self.assertEqual("2026-05-08", data["current_weekend"])
        self.assertEqual("ok", data["runs"]["regular"]["status"])
        self.assertEqual("Mortal Kombat II", data["movies"][0]["movie"])
        self.assertEqual(3, data["movies"][0]["seat_data"]["rows"])

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
            )

        snapshot = data["runs"]["snapshot"]
        self.assertEqual("partial", snapshot["status"])
        self.assertEqual([], snapshot["missing_show_dates"])
        self.assertEqual({"2026-05-08": ["CT", "PT"]}, snapshot["missing_date_timezones"])


if __name__ == "__main__":
    unittest.main()
