import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "box-office-tracker" / "scripts" / "clean_canonical_data.py"


def run_cleaner(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), *args],
        text=True,
        capture_output=True,
    )


def run_cleaner_from(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


class CleanCanonicalDataTest(unittest.TestCase):
    def test_cleans_excluded_movies_classic_theatres_duplicate_urls_and_calibration(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            data = repo / "box-office-tracker" / "data"
            seat_fields = [
                "weekend_of",
                "run_id",
                "date",
                "theatre_name",
                "timezone",
                "movie_title",
                "showtime",
                "auditorium_type",
                "amc_seat_map_url",
                "notes",
            ]
            snapshot_fields = [
                "weekend_of",
                "run_id",
                "snapshot_time",
                "snapshot_bucket",
                "show_date",
                "theatre_name",
                "timezone",
                "movie_title",
                "showtime",
                "auditorium_type",
                "amc_seat_map_url",
                "notes",
            ]
            write_csv(
                data / "seat-counts.csv",
                seat_fields,
                [
                    {
                        "weekend_of": "2026-05-22",
                        "run_id": "run",
                        "date": "2026-05-24",
                        "theatre_name": "AMC Factoria 8",
                        "timezone": "PT",
                        "movie_title": "The Mandalorian and Grogu",
                        "showtime": "10:40pm",
                        "auditorium_type": "IMAX",
                        "amc_seat_map_url": "https://www.amctheatres.com/showtimes/143248343/seats",
                        "notes": "",
                    },
                    {
                        "weekend_of": "2026-05-22",
                        "run_id": "run",
                        "date": "2026-05-24",
                        "theatre_name": "AMC Factoria 8",
                        "timezone": "PT",
                        "movie_title": "Passenger",
                        "showtime": "10:40pm",
                        "auditorium_type": "IMAX",
                        "amc_seat_map_url": "https://www.amctheatres.com/showtimes/143248343/seats",
                        "notes": "",
                    },
                    {
                        "weekend_of": "2026-05-01",
                        "run_id": "run",
                        "date": "2026-05-02",
                        "theatre_name": "AMC Good Theatre 12",
                        "timezone": "ET",
                        "movie_title": "Animal Farm",
                        "showtime": "7:00pm",
                        "auditorium_type": "Standard",
                        "amc_seat_map_url": "animal-url",
                        "notes": "",
                    },
                    {
                        "weekend_of": "2026-05-30",
                        "run_id": "run",
                        "date": "2026-05-31",
                        "theatre_name": "AMC CLASSIC Example 10",
                        "timezone": "CT",
                        "movie_title": "Backrooms",
                        "showtime": "8:00pm",
                        "auditorium_type": "Standard",
                        "amc_seat_map_url": "classic-url",
                        "notes": "",
                    },
                    {
                        "weekend_of": "2026-05-29",
                        "run_id": "run",
                        "date": "2026-05-31",
                        "theatre_name": "AMC Bayou 15",
                        "timezone": "ET",
                        "movie_title": "The Breadwinner",
                        "showtime": "10:45pm",
                        "auditorium_type": "undefined",
                        "amc_seat_map_url": "breadwinner-url",
                        "notes": "undefined @ AMC Bayou 15",
                    },
                ],
            )
            write_csv(
                data / "pre-reservation-snapshots.csv",
                snapshot_fields,
                [
                    {
                        "weekend_of": "2026-05-01",
                        "run_id": "run",
                        "snapshot_time": "2026-05-01T12:00:00",
                        "snapshot_bucket": "morning",
                        "show_date": "2026-05-02",
                        "theatre_name": "AMC Good Theatre 12",
                        "timezone": "ET",
                        "movie_title": "Hokum",
                        "showtime": "9:00pm",
                        "auditorium_type": "Standard",
                        "amc_seat_map_url": "hokum-url",
                        "notes": "",
                    },
                    {
                        "weekend_of": "2026-05-30",
                        "run_id": "run",
                        "snapshot_time": "2026-05-30T12:00:00",
                        "snapshot_bucket": "morning",
                        "show_date": "2026-05-31",
                        "theatre_name": "AMC CLASSIC Example 10",
                        "timezone": "CT",
                        "movie_title": "Backrooms",
                        "showtime": "8:00pm",
                        "auditorium_type": "Standard",
                        "amc_seat_map_url": "classic-snapshot-url",
                        "notes": "",
                    },
                ],
            )
            calibration = {
                "history": [
                    {"movie": "Animal Farm", "actual_m": 12.0},
                    {"movie": "Backrooms", "actual_m": 82.0},
                ],
                "calibration_factors": {
                    "historical_accuracy": [
                        {"movie": "Hokum", "error_pct": 20},
                        {"movie": "Backrooms", "error_pct": 5},
                    ]
                },
            }
            (data / "calibration.json").write_text(json.dumps(calibration))
            freeze_dir = data / "calibration-freezes"
            freeze_dir.mkdir(parents=True)
            (freeze_dir / "2026-05-01.json").write_text(json.dumps(calibration))

            result = run_cleaner(repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            cleaned_seats = read_csv(data / "seat-counts.csv")
            self.assertEqual(
                ["The Mandalorian and Grogu", "The Breadwinner"],
                [row["movie_title"] for row in cleaned_seats],
            )
            self.assertEqual("", cleaned_seats[1]["auditorium_type"])
            self.assertTrue(cleaned_seats[1]["notes"].startswith("Unknown format @"))
            self.assertEqual([], read_csv(data / "pre-reservation-snapshots.csv"))

            cleaned_calibration = json.loads((data / "calibration.json").read_text())
            self.assertEqual(["Backrooms"], [row["movie"] for row in cleaned_calibration["history"]])
            self.assertEqual(
                ["Backrooms"],
                [
                    row["movie"]
                    for row in cleaned_calibration["calibration_factors"]["historical_accuracy"]
                ],
            )
            cleaned_freeze = json.loads((freeze_dir / "2026-05-01.json").read_text())
            self.assertEqual(["Backrooms"], [row["movie"] for row in cleaned_freeze["history"]])

            check_result = run_cleaner(repo, "--check")
            self.assertEqual(check_result.returncode, 0, check_result.stderr)

    def test_cleans_when_launched_from_tracker_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            tracker = repo / "box-office-tracker"
            data = tracker / "data"
            seat_fields = [
                "weekend_of",
                "run_id",
                "date",
                "theatre_name",
                "timezone",
                "movie_title",
                "showtime",
                "auditorium_type",
                "amc_seat_map_url",
                "notes",
            ]
            write_csv(
                data / "seat-counts.csv",
                seat_fields,
                [
                    {
                        "weekend_of": "2026-06-05",
                        "run_id": "run",
                        "date": "2026-06-04",
                        "theatre_name": "AMC River Park Square 20",
                        "timezone": "PT",
                        "movie_title": "Scary Movie",
                        "showtime": "7:30pm",
                        "auditorium_type": "undefined",
                        "amc_seat_map_url": "seat-url",
                        "notes": "undefined @ 7:30pm",
                    },
                ],
            )

            result = run_cleaner_from(tracker)

            self.assertEqual(result.returncode, 0, result.stderr)
            cleaned = read_csv(data / "seat-counts.csv")
            self.assertEqual("", cleaned[0]["auditorium_type"])
            self.assertTrue(cleaned[0]["notes"].startswith("Unknown format @"))


if __name__ == "__main__":
    unittest.main()
