import csv
import sys
import tempfile
import contextlib
import io
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import merge_scrape_artifacts as M  # noqa: E402
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

    def test_merge_artifacts_fills_inferable_blank_seat_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            artifact = root / "artifacts" / "scrape-ET-1"

            zero_sold = seat_row("ET", "AMC Empty", 0)
            zero_sold["seats_sold"] = ""
            zero_sold["occupancy_pct"] = ""
            sold_out = seat_row("ET", "AMC Full", 200)
            sold_out["seats_available"] = ""
            sold_out["occupancy_pct"] = ""
            write_csv(artifact / "seat-counts.csv", SEAT_FIELDS, [zero_sold, sold_out])

            summary = merge_artifacts(root / "artifacts", data_dir)

            self.assertEqual(2, summary.seat_added)
            with (data_dir / "seat-counts.csv").open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual("0", rows[0]["seats_sold"])
            self.assertEqual("200", rows[0]["seats_available"])
            self.assertEqual("0", rows[0]["occupancy_pct"])
            self.assertEqual("200", rows[1]["seats_sold"])
            self.assertEqual("0", rows[1]["seats_available"])
            self.assertEqual("100", rows[1]["occupancy_pct"])

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


class ArchivedWeekendGuardTest(unittest.TestCase):
    def test_archived_weekend_rows_are_refused(self):
        # Artifacts built before a rotation carry every settled weekend; merging
        # them must not re-import archived rows (2026-07-12: re-import pushed the
        # live CSV to 100.38MB and re-breached GitHub's push limit).
        from scripts import merge_scrape_artifacts as M
        with tempfile.TemporaryDirectory() as d:
            data_dir = Path(d)
            (data_dir / "pre-reservation-archive").mkdir()
            (data_dir / "pre-reservation-archive"
             / "pre-reservation-snapshots-2026-06-19.csv.gz").write_bytes(b"")
            f = M._pre_reservation_row_filter(data_dir)
            archived = {"weekend_of": "2026-06-19", "minutes_until_showtime": "60"}
            live = {"weekend_of": "2026-07-10", "minutes_until_showtime": "60"}
            past = {"weekend_of": "2026-07-10", "minutes_until_showtime": "-5"}
            self.assertFalse(f(archived))   # settled weekend -> refused
            self.assertTrue(f(live))        # live weekend -> accepted
            self.assertFalse(f(past))       # past-showtime still refused


class ArchivedWeekendDropReportingTests(unittest.TestCase):
    """The guard is correct, but it must not be silent.

    Artifacts live 14 days; rotation archives a weekend ~10 days after it ends.
    A recovery rerun inside that gap merges ZERO rows, and the finalize guard
    then reports "no net canonical data changes" — a green run with no data and
    no explanation of why.
    """

    def setUp(self):
        M.ARCHIVED_WEEKEND_DROPS.clear()

    def tearDown(self):
        M.ARCHIVED_WEEKEND_DROPS.clear()

    def test_refused_rows_are_counted_per_weekend(self):
        with tempfile.TemporaryDirectory() as d:
            data_dir = Path(d)
            (data_dir / "seat-archive").mkdir()
            (data_dir / "seat-archive" / "seat-counts-2026-05-01.csv.gz").write_bytes(b"")
            f = M._seat_row_filter(data_dir)
            for _ in range(3):
                self.assertFalse(f({"weekend_of": "2026-05-01"}))
            self.assertTrue(f({"weekend_of": "2026-07-31"}))
            self.assertEqual({"seat-counts:2026-05-01": 3}, dict(M.ARCHIVED_WEEKEND_DROPS))

    def test_report_names_the_weekend_and_count(self):
        M.ARCHIVED_WEEKEND_DROPS["seat-counts:2026-05-01"] = 12345
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.report_archived_weekend_drops()
        out = buf.getvalue()
        self.assertIn("2026-05-01", out)
        self.assertIn("12345", out)

    def test_report_is_silent_when_nothing_was_dropped(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.report_archived_weekend_drops()
        self.assertEqual("", buf.getvalue())
