import csv
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.merge_scrape_artifacts import (  # noqa: E402
    POLY_FIELDS,
    PRE_RESERVATION_FIELDS,
    SEAT_FIELDS,
    merge_artifacts,
    write_markers,
)


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def seat_row(tz, theatre, seats_sold):
    row = {field: "" for field in SEAT_FIELDS}
    row.update(
        {
            "weekend_of": "2026-05-01",
            "run_id": f"run-{tz}",
            "date": "2026-05-01",
            "day_of_week": "Friday",
            "theatre_name": theatre,
            "theatre_city": "Test City",
            "timezone": tz,
            "movie_title": "The Devil Wears Prada 2",
            "polymarket_market": "https://polymarket.com/event/test",
            "showtime": "7:00pm",
            "check_time": "2026-05-02T03:00:00+00:00",
            "auditorium_type": "IMAX with Laser at AMC",
            "total_seats": "200",
            "seats_sold": str(seats_sold),
            "seats_available": str(200 - seats_sold),
            "occupancy_pct": str(round(seats_sold / 2, 1)),
            "amc_seat_map_url": f"https://example.test/{theatre}/{seats_sold}",
        }
    )
    return row


def poly_row(market_id, question):
    row = {field: "" for field in POLY_FIELDS}
    row.update(
        {
            "date": "2026-05-01",
            "movie_title": "The Devil Wears Prada 2",
            "market_url": "https://polymarket.com/event/test",
            "market_question": question,
            "outcome_prices": '["0.5", "0.5"]',
            "volume": "1000",
            "market_id": market_id,
        }
    )
    return row


def pre_reservation_row(reserved):
    row = {field: "" for field in PRE_RESERVATION_FIELDS}
    row.update(
        {
            "weekend_of": "2026-05-01",
            "run_id": "snapshot-run",
            "snapshot_time": "2026-05-01T18:00:00+00:00",
            "snapshot_bucket": "2026-05-01T18:00Z",
            "show_date": "2026-05-02",
            "day_of_week": "Saturday",
            "theatre_name": "AMC Snapshot",
            "theatre_city": "Test City",
            "timezone": "ET",
            "movie_title": "The Devil Wears Prada 2",
            "showtime": "7:00pm",
            "showtime_id": "123",
            "minutes_until_showtime": "180",
            "auditorium_type": "Standard",
            "reserved_seats": str(reserved),
            "available_seats": str(200 - reserved),
            "amc_seat_map_url": "https://example.test/showtimes/123/seats",
        }
    )
    return row


class MergeScrapeArtifactsTest(unittest.TestCase):
    def test_merge_artifacts_dedupes_rows_and_preserves_run_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-CT-1"

            old_seat = seat_row("ET", "AMC Existing", 50)
            new_seat = seat_row("CT", "AMC New", 125)
            write_csv(data_dir / "seat-counts.csv", SEAT_FIELDS, [old_seat])
            write_csv(artifact / "seat-counts.csv", SEAT_FIELDS, [old_seat, new_seat])

            old_poly = poly_row("m1", "Will Test be above 70m?")
            new_poly = poly_row("m2", "Will Test be above 80m?")
            write_csv(data_dir / "polymarket-markets.csv", POLY_FIELDS, [old_poly])
            write_csv(artifact / "polymarket-markets.csv", POLY_FIELDS, [old_poly, new_poly])

            log_path = artifact / "run-logs" / "2026-05-01" / "ct-run.md"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("# CT run\n")

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(1, summary.seat_added)
            self.assertEqual(1, summary.seat_duplicates)
            self.assertEqual({"CT"}, summary.markers)
            self.assertEqual(1, summary.polymarket_added)
            self.assertEqual(1, summary.polymarket_duplicates)
            self.assertEqual(1, summary.run_logs_copied)
            self.assertEqual(1, summary.as_dict()["seat_added"])
            self.assertEqual(["CT"], summary.as_dict()["markers"])

            with (data_dir / "seat-counts.csv").open() as f:
                merged_seats = list(csv.DictReader(f))
            self.assertEqual(2, len(merged_seats))
            self.assertEqual("AMC New", merged_seats[-1]["theatre_name"])
            self.assertTrue((data_dir / "run-logs" / "2026-05-01" / "ct-run.md").exists())

    def test_merge_artifacts_upgrades_duplicate_seat_window_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            old_seat = seat_row("ET", "AMC Existing", 50)
            old_seat["notes"] = "Standard @ 7:00 PM"
            new_seat = dict(old_seat)
            new_seat["run_id"] = "run-ET-new"
            new_seat["notes"] = "Standard @ 7:00 PM; showtime_window=sat-sun-10-23-v1"
            write_csv(data_dir / "seat-counts.csv", SEAT_FIELDS, [old_seat])
            write_csv(artifact / "seat-counts.csv", SEAT_FIELDS, [new_seat])

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(0, summary.seat_added)
            self.assertEqual(1, summary.seat_duplicates)
            self.assertEqual(1, summary.seat_metadata_updated)
            self.assertEqual({"ET"}, summary.markers)
            self.assertEqual(1, summary.as_dict()["seat_metadata_updated"])
            self.assertEqual(["ET"], summary.as_dict()["markers"])

            with (data_dir / "seat-counts.csv").open() as f:
                merged_seats = list(csv.DictReader(f))
            self.assertEqual(1, len(merged_seats))
            self.assertIn("showtime_window=sat-sun-10-23-v1", merged_seats[0]["notes"])

    def test_merge_artifacts_preserves_existing_crlf_csv_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            old_seat = seat_row("ET", "AMC Existing", 50)
            new_seat = seat_row("ET", "AMC New", 60)
            write_csv(artifact / "seat-counts.csv", SEAT_FIELDS, [old_seat, new_seat])
            target = data_dir / "seat-counts.csv"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(
                (",".join(SEAT_FIELDS) + "\r\n").encode()
                + (",".join(old_seat.get(field, "") for field in SEAT_FIELDS) + "\r\n").encode()
            )

            merge_artifacts(root / "artifacts", data_dir)

            content = target.read_bytes()
            self.assertIn(b"\r\n", content)
            self.assertNotIn(b"\r\r\n", content)

    def test_merge_artifacts_dedupes_pre_reservation_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            old_snapshot = pre_reservation_row(40)
            new_snapshot = pre_reservation_row(42)
            new_snapshot["snapshot_bucket"] = "2026-05-01T20:00Z"
            write_csv(data_dir / "pre-reservation-snapshots.csv", PRE_RESERVATION_FIELDS, [old_snapshot])
            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [old_snapshot, new_snapshot],
            )

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(1, summary.pre_reservation_added)
            self.assertEqual(1, summary.pre_reservation_duplicates)
            with (data_dir / "pre-reservation-snapshots.csv").open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(2, len(rows))
            self.assertEqual("42", rows[-1]["reserved_seats"])

    def test_failed_snapshot_only_artifact_keeps_partial_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [pre_reservation_row(31)],
            )
            manifest = artifact / "scrape-manifest" / "ET.env"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                "timezone=ET\n"
                "workflow_job_status=failure\n"
                "snapshots_only=true\n"
                "pre_reservation_snapshots=true\n"
            )

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(1, summary.pre_reservation_added)
            target = data_dir / "pre-reservation-snapshots.csv"
            with target.open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(1, len(rows))
            self.assertEqual("31", rows[0]["reserved_seats"])

    def test_merge_artifacts_rejects_non_future_pre_reservation_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            valid = pre_reservation_row(40)
            started = pre_reservation_row(41)
            started["showtime_id"] = "started"
            started["minutes_until_showtime"] = "-5"
            missing = pre_reservation_row(42)
            missing["showtime_id"] = "missing"
            missing["minutes_until_showtime"] = ""
            malformed = pre_reservation_row(43)
            malformed["showtime_id"] = "malformed"
            malformed["minutes_until_showtime"] = "soon"
            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [valid, started, missing, malformed],
            )
            manifest = artifact / "scrape-manifest" / "ET.env"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                "timezone=ET\n"
                "workflow_job_status=failure\n"
                "snapshots_only=true\n"
                "pre_reservation_snapshots=true\n"
            )

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(1, summary.pre_reservation_added)
            target = data_dir / "pre-reservation-snapshots.csv"
            with target.open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(["123"], [row["showtime_id"] for row in rows])

    def test_failed_regular_artifact_keeps_seat_rows_but_not_partial_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            write_csv(artifact / "seat-counts.csv", SEAT_FIELDS, [seat_row("ET", "AMC A", 50)])
            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [pre_reservation_row(31)],
            )
            manifest = artifact / "scrape-manifest" / "ET.env"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                "timezone=ET\n"
                "workflow_job_status=failure\n"
                "snapshots_only=false\n"
                "pre_reservation_snapshots=true\n"
            )

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(1, summary.seat_added)
            self.assertEqual(0, summary.pre_reservation_added)

    def test_cancelled_regular_artifact_ignores_partial_snapshot_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [pre_reservation_row(31)],
            )
            manifest = artifact / "scrape-manifest" / "ET.env"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                "timezone=ET\n"
                "workflow_job_status=cancelled\n"
                "snapshots_only=false\n"
                "pre_reservation_snapshots=true\n"
            )

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(0, summary.pre_reservation_added)

    def test_write_markers_uses_dedup_guard_commit_phrasing(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker_file = Path(tmp) / "markers.txt"

            write_markers(marker_file, {"PT", "ET", "PT"})

            self.assertEqual(
                "data: box office ET scrape\ndata: box office PT scrape\n",
                marker_file.read_text(),
            )

    def test_snapshot_only_markers_do_not_block_later_scrape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            snapshot = pre_reservation_row(44)
            write_csv(
                artifact / "pre-reservation-snapshots.csv",
                PRE_RESERVATION_FIELDS,
                [snapshot],
            )

            summary = merge_artifacts(root / "artifacts", data_dir)
            marker_file = root / "markers.txt"
            write_markers(
                marker_file,
                summary.scrape_markers,
                snapshot_markers=summary.snapshot_markers,
            )

            content = marker_file.read_text()
            self.assertNotIn("data: box office ET scrape", content)
            self.assertIn("data: box office ET pre-reservation snapshot", content)

    def test_merge_artifacts_ignores_legacy_run_log_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"
            artifact.mkdir(parents=True)
            (artifact / "run-log.md").write_text("# stale legacy log\n")

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(0, summary.run_logs_copied)
            self.assertFalse((data_dir / "run-logs" / "legacy").exists())


if __name__ == "__main__":
    unittest.main()
