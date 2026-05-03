#!/usr/bin/env python3
"""Merge Phase 2 scrape artifacts into canonical data files.

The scrape workflow runs ET/CT/PT as independent matrix legs. Those legs should
not push to main directly; this script gives the finalizer one deterministic
single-writer merge point for any rows/logs the legs collected.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SEAT_CSV = "seat-counts.csv"
PRE_RESERVATION_CSV = "pre-reservation-snapshots.csv"
POLY_CSV = "polymarket-markets.csv"
RUN_LOG_DIR = "run-logs"

SEAT_FIELDS = [
    "weekend_of",
    "run_id",
    "date",
    "day_of_week",
    "theatre_name",
    "theatre_city",
    "timezone",
    "movie_title",
    "polymarket_market",
    "showtime",
    "check_time",
    "minutes_after_showtime",
    "auditorium_name",
    "auditorium_type",
    "total_seats",
    "seats_sold",
    "seats_available",
    "occupancy_pct",
    "amc_seat_map_url",
    "notes",
]

SEAT_DEDUPE_FIELDS = (
    "weekend_of",
    "date",
    "theatre_name",
    "movie_title",
    "showtime",
    "auditorium_type",
    "amc_seat_map_url",
    "total_seats",
    "seats_sold",
    "seats_available",
)

POLY_FIELDS = [
    "date",
    "movie_title",
    "market_url",
    "market_question",
    "outcome_prices",
    "volume",
    "market_id",
    "notes",
]

PRE_RESERVATION_FIELDS = [
    "weekend_of",
    "run_id",
    "snapshot_time",
    "snapshot_bucket",
    "show_date",
    "day_of_week",
    "theatre_name",
    "theatre_city",
    "timezone",
    "movie_title",
    "showtime",
    "showtime_id",
    "minutes_until_showtime",
    "auditorium_name",
    "auditorium_type",
    "total_seats",
    "reserved_seats",
    "available_seats",
    "occupancy_pct",
    "delta_reserved_since_previous",
    "amc_seat_map_url",
    "notes",
]

PRE_RESERVATION_DEDUPE_FIELDS = (
    "weekend_of",
    "snapshot_bucket",
    "show_date",
    "theatre_name",
    "movie_title",
    "showtime_id",
    "auditorium_type",
)


@dataclass
class MergeSummary:
    seat_added: int = 0
    seat_duplicates: int = 0
    polymarket_added: int = 0
    polymarket_duplicates: int = 0
    pre_reservation_added: int = 0
    pre_reservation_duplicates: int = 0
    run_logs_copied: int = 0
    run_logs_skipped: int = 0
    markers: set[str] = field(default_factory=set)
    snapshot_markers: set[str] = field(default_factory=set)

    @property
    def scrape_markers(self) -> set[str]:
        return self.markers

    def as_dict(self) -> dict[str, object]:
        return {
            "seat_added": self.seat_added,
            "seat_duplicates": self.seat_duplicates,
            "polymarket_added": self.polymarket_added,
            "polymarket_duplicates": self.polymarket_duplicates,
            "pre_reservation_added": self.pre_reservation_added,
            "pre_reservation_duplicates": self.pre_reservation_duplicates,
            "run_logs_copied": self.run_logs_copied,
            "run_logs_skipped": self.run_logs_skipped,
            "markers": sorted(self.markers),
            "snapshot_markers": sorted(self.snapshot_markers),
        }


def _csv_sources(artifact_root: Path, filename: str) -> list[Path]:
    if not artifact_root.exists():
        return []
    return sorted(p for p in artifact_root.rglob(filename) if p.is_file())


def _read_rows(path: Path, fields: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows
        for row in reader:
            normalized = {field: str(row.get(field, "") or "") for field in fields}
            if _is_repeated_header(normalized, fields):
                continue
            rows.append(normalized)
    return rows


def _is_repeated_header(row: dict[str, str], fields: list[str]) -> bool:
    return all(row.get(field, "") == field for field in fields if field in row)


def _tuple_key(fields: Iterable[str]) -> Callable[[dict[str, str]], tuple[str, ...]]:
    key_fields = tuple(fields)

    def key(row: dict[str, str]) -> tuple[str, ...]:
        return tuple(str(row.get(field, "") or "") for field in key_fields)

    return key


def _polymarket_key(row: dict[str, str]) -> tuple[str, ...]:
    market_id = str(row.get("market_id", "") or "")
    if market_id:
        return ("id", str(row.get("date", "") or ""), market_id)
    return (
        "fallback",
        str(row.get("date", "") or ""),
        str(row.get("movie_title", "") or ""),
        str(row.get("market_url", "") or ""),
        str(row.get("market_question", "") or ""),
        str(row.get("outcome_prices", "") or ""),
    )


def _write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lineterminator = "\n"
    if path.exists() and b"\r\n" in path.read_bytes()[:8192]:
        lineterminator = "\r\n"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator=lineterminator)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def _merge_csv(
    target: Path,
    sources: list[Path],
    fields: list[str],
    key_fn: Callable[[dict[str, str]], tuple[str, ...]],
) -> tuple[int, int, list[dict[str, str]]]:
    existing = _read_rows(target, fields)
    seen = {key_fn(row) for row in existing}
    merged = list(existing)
    added_rows: list[dict[str, str]] = []
    duplicates = 0

    for source in sources:
        if source.resolve() == target.resolve():
            continue
        for row in _read_rows(source, fields):
            key = key_fn(row)
            if key in seen:
                duplicates += 1
                continue
            merged.append(row)
            added_rows.append(row)
            seen.add(key)

    if added_rows or (sources and not target.exists()):
        _write_rows(target, fields, merged)

    return len(added_rows), duplicates, added_rows


def _unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for idx in range(2, 10_000):
        candidate = parent / f"{stem}-{idx}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique destination for {path}")


def _copy_run_logs(artifact_root: Path, data_dir: Path) -> tuple[int, int]:
    if not artifact_root.exists():
        return 0, 0

    copied = 0
    skipped = 0
    dest_root = data_dir / RUN_LOG_DIR

    for source_root in sorted(p for p in artifact_root.rglob(RUN_LOG_DIR) if p.is_dir()):
        for source in sorted(p for p in source_root.rglob("*") if p.is_file()):
            rel = source.relative_to(source_root)
            dest = dest_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                if dest.read_bytes() == source.read_bytes():
                    skipped += 1
                    continue
                dest = _unique_destination(dest)
            shutil.copy2(source, dest)
            copied += 1

    return copied, skipped


def merge_artifacts(artifact_root: Path, data_dir: Path = DATA_DIR) -> MergeSummary:
    artifact_root = artifact_root.resolve()
    data_dir = data_dir.resolve()

    summary = MergeSummary()
    seat_added, seat_dupes, added_seats = _merge_csv(
        data_dir / SEAT_CSV,
        _csv_sources(artifact_root, SEAT_CSV),
        SEAT_FIELDS,
        _tuple_key(SEAT_DEDUPE_FIELDS),
    )
    summary.seat_added = seat_added
    summary.seat_duplicates = seat_dupes
    summary.markers.update(
        str(row.get("timezone", "") or "").strip()
        for row in added_seats
        if str(row.get("timezone", "") or "").strip()
    )

    poly_added, poly_dupes, _ = _merge_csv(
        data_dir / POLY_CSV,
        _csv_sources(artifact_root, POLY_CSV),
        POLY_FIELDS,
        _polymarket_key,
    )
    summary.polymarket_added = poly_added
    summary.polymarket_duplicates = poly_dupes

    pre_added, pre_dupes, added_pre = _merge_csv(
        data_dir / PRE_RESERVATION_CSV,
        _csv_sources(artifact_root, PRE_RESERVATION_CSV),
        PRE_RESERVATION_FIELDS,
        _tuple_key(PRE_RESERVATION_DEDUPE_FIELDS),
    )
    summary.pre_reservation_added = pre_added
    summary.pre_reservation_duplicates = pre_dupes
    summary.snapshot_markers.update(
        str(row.get("timezone", "") or "").strip()
        for row in added_pre
        if str(row.get("timezone", "") or "").strip()
    )

    logs_copied, logs_skipped = _copy_run_logs(artifact_root, data_dir)
    summary.run_logs_copied = logs_copied
    summary.run_logs_skipped = logs_skipped
    return summary


def write_markers(
    marker_file: Path,
    markers: Iterable[str],
    snapshot_markers: Iterable[str] | None = None,
) -> None:
    marker_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"data: box office {tz} scrape" for tz in sorted(set(markers))]
    lines.extend(
        f"data: box office {tz} pre-reservation snapshot"
        for tz in sorted(set(snapshot_markers or []))
    )
    marker_file.write_text("\n".join(lines) + ("\n" if lines else ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_root",
        nargs="?",
        default=str(DATA_DIR / "scrape-artifacts"),
        help="Directory created by actions/download-artifact.",
    )
    parser.add_argument(
        "--data-dir",
        default=str(DATA_DIR),
        help="Canonical data directory to update.",
    )
    parser.add_argument(
        "--marker-file",
        default="/tmp/box-office-scrape-markers.txt",
        help="File containing commit-message markers for TZs with newly merged rows.",
    )
    parser.add_argument(
        "--summary-file",
        default="",
        help="Optional JSON summary path for the finalize staging guard.",
    )
    args = parser.parse_args()

    summary = merge_artifacts(Path(args.artifact_root), Path(args.data_dir))
    write_markers(
        Path(args.marker_file),
        summary.scrape_markers,
        snapshot_markers=summary.snapshot_markers,
    )
    if args.summary_file:
        summary_path = Path(args.summary_file)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary.as_dict(), indent=2, sort_keys=True) + "\n")

    print(f"Seat rows added: {summary.seat_added}")
    print(f"Seat duplicates skipped: {summary.seat_duplicates}")
    print(f"Polymarket rows added: {summary.polymarket_added}")
    print(f"Polymarket duplicates skipped: {summary.polymarket_duplicates}")
    print(f"Pre-reservation snapshots added: {summary.pre_reservation_added}")
    print(f"Pre-reservation duplicates skipped: {summary.pre_reservation_duplicates}")
    print(f"Run logs copied: {summary.run_logs_copied}")
    print(f"Run logs skipped: {summary.run_logs_skipped}")
    print(f"Scrape markers: {', '.join(sorted(summary.markers)) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
