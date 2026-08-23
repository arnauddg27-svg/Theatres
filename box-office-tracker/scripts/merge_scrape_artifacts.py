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
    seat_metadata_updated: int = 0
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
            "seat_metadata_updated": self.seat_metadata_updated,
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


def _artifact_dir_for_source(artifact_root: Path, source: Path) -> Path:
    try:
        rel = source.resolve().relative_to(artifact_root.resolve())
    except ValueError:
        return source.parent
    if len(rel.parts) <= 1:
        return artifact_root
    return artifact_root / rel.parts[0]


def _read_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(errors="ignore").splitlines():
        if "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _artifact_manifest(artifact_root: Path, source: Path) -> dict[str, str]:
    artifact_dir = _artifact_dir_for_source(artifact_root, source)
    candidates = sorted(artifact_dir.rglob("scrape-manifest/*.env"))
    if not candidates:
        return {}
    return _read_manifest(candidates[0])


def _filter_pre_reservation_sources(artifact_root: Path, sources: list[Path]) -> list[Path]:
    filtered: list[Path] = []
    for source in sources:
        manifest = _artifact_manifest(artifact_root, source)
        snapshots_only = manifest.get("snapshots_only", "").lower() == "true"
        writes_snapshots = snapshots_only or manifest.get("pre_reservation_snapshots", "").lower() == "true"
        successful = manifest.get("workflow_job_status", "").lower() == "success"
        # Snapshot-only runs are designed to be useful even when partial. The
        # scraper writes rows incrementally and coverage is model-weighted later,
        # so keep any rows it managed to capture. Regular scrape artifacts can
        # include optional snapshot CSVs too; if those failed, keep protecting
        # the model-driving scrape and ignore their partial snapshot sidecar.
        if writes_snapshots and not successful and not snapshots_only:
            continue
        # A snapshot-only leg that tripped the FATAL coverage floor writes a
        # marker next to its manifest. Honour the refusal: without this, the
        # snapshots_only exemption above merged the "refused" sparse rows into
        # canonical anyway, defeating the floor (verified 2026-08-23).
        artifact_dir = _artifact_dir_for_source(artifact_root, source)
        tz = manifest.get("timezone", "")
        fatal_markers = (list(artifact_dir.rglob(
            f"scrape-manifest/{tz}-snapshot-fatal.marker")) if tz else [])
        if fatal_markers:
            print(f"  dropping {source} — leg {tz} tripped the snapshot "
                  f"fatal-coverage floor and refused its own rows")
            continue
        filtered.append(source)
    return filtered


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
            if fields == SEAT_FIELDS:
                normalized = _normalize_seat_count_fields(normalized)
            rows.append(normalized)
    return rows


def _is_repeated_header(row: dict[str, str], fields: list[str]) -> bool:
    return all(row.get(field, "") == field for field in fields if field in row)


def _parse_seat_count(value: str) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _format_seat_number(value: float) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}".rstrip("0").rstrip(".")


def _normalize_seat_count_fields(row: dict[str, str]) -> dict[str, str]:
    total = _parse_seat_count(row.get("total_seats", ""))
    sold = _parse_seat_count(row.get("seats_sold", ""))
    available = _parse_seat_count(row.get("seats_available", ""))
    if total is None or total < 0:
        return row

    if sold is None and available is not None:
        sold = max(total - available, 0)
    if available is None and sold is not None:
        available = max(total - sold, 0)

    if sold is not None:
        row["seats_sold"] = str(sold)
    if available is not None:
        row["seats_available"] = str(available)
    if sold is not None and total > 0:
        row["occupancy_pct"] = _format_seat_number(round(sold / total * 100, 1))
    elif total == 0:
        row["occupancy_pct"] = "0"

    return row


def _tuple_key(fields: Iterable[str]) -> Callable[[dict[str, str]], tuple[str, ...]]:
    key_fields = tuple(fields)

    def key(row: dict[str, str]) -> tuple[str, ...]:
        return tuple(str(row.get(field, "") or "") for field in key_fields)

    return key


def _merge_seat_row_metadata(existing: dict[str, str], incoming: dict[str, str]) -> bool:
    """Carry forward metadata from duplicate seat rows without duplicating facts."""
    existing_note = str(existing.get("notes", "") or "")
    incoming_note = str(incoming.get("notes", "") or "")
    changed = False

    for part in (piece.strip() for piece in incoming_note.split(";")):
        if not part.startswith("showtime_window="):
            continue
        if part and part not in existing_note:
            existing["notes"] = f"{existing_note}; {part}" if existing_note else part
            existing_note = existing["notes"]
            changed = True

    return changed


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
    merge_duplicate: Callable[[dict[str, str], dict[str, str]], bool] | None = None,
    row_filter: Callable[[dict[str, str]], bool] | None = None,
) -> tuple[int, int, int, list[dict[str, str]], list[dict[str, str]]]:
    existing = _read_rows(target, fields)
    rows_by_key = {key_fn(row): row for row in existing}
    seen = set(rows_by_key)
    merged = list(existing)
    added_rows: list[dict[str, str]] = []
    updated_rows: list[dict[str, str]] = []
    duplicates = 0
    metadata_updated = 0

    for source in sources:
        if source.resolve() == target.resolve():
            continue
        for row in _read_rows(source, fields):
            if row_filter and not row_filter(row):
                continue
            key = key_fn(row)
            if key in seen:
                duplicates += 1
                existing_row = rows_by_key.get(key)
                if merge_duplicate and existing_row and merge_duplicate(existing_row, row):
                    metadata_updated += 1
                    updated_rows.append(existing_row)
                continue
            merged.append(row)
            added_rows.append(row)
            seen.add(key)
            rows_by_key[key] = row

    if added_rows or metadata_updated or (sources and not target.exists()):
        _write_rows(target, fields, merged)

    return len(added_rows), duplicates, metadata_updated, added_rows, updated_rows


def _is_future_pre_reservation_row(row: dict[str, str]) -> bool:
    """Only ingest snapshot rows that are still future reservations."""
    raw_minutes = str(row.get("minutes_until_showtime", "") or "").strip()
    try:
        minutes_until_showtime = float(raw_minutes)
    except ValueError:
        return False
    return minutes_until_showtime >= 0


# weekend -> rows refused because that weekend is already archived. Reported at
# the end of a merge: the drop is correct, but silently dropping EVERY row made
# a recovery rerun look like a clean no-op. Artifacts are retained 14 days while
# rotation archives a weekend ~10 days after it ends, so a rerun inside that gap
# merges nothing and the finalize guard reports "no net canonical data changes"
# — a green run with no data and no explanation.
ARCHIVED_WEEKEND_DROPS: dict[str, int] = {}


def _archived_weekend_filter(data_dir: Path, subdir: str, prefix: str):
    """Refuse rows whose weekend has been rotated into an archive."""
    archive_dir = data_dir / subdir

    def _filter(row: dict[str, str]) -> bool:
        weekend = str(row.get("weekend_of", "") or "").strip()
        if weekend and (archive_dir / f"{prefix}-{weekend}.csv.gz").exists():
            key = f"{prefix}:{weekend}"
            ARCHIVED_WEEKEND_DROPS[key] = ARCHIVED_WEEKEND_DROPS.get(key, 0) + 1
            return False
        return True

    return _filter


def report_archived_weekend_drops() -> None:
    """Print what the archived-weekend guard refused, so it is never silent."""
    if not ARCHIVED_WEEKEND_DROPS:
        return
    total = sum(ARCHIVED_WEEKEND_DROPS.values())
    print(f"\n\u26a0\ufe0f  archived-weekend guard refused {total} artifact row(s) "
          f"(already rotated into per-weekend archives):")
    for key in sorted(ARCHIVED_WEEKEND_DROPS):
        prefix, _, weekend = key.partition(":")
        print(f"    {weekend} [{prefix}]: {ARCHIVED_WEEKEND_DROPS[key]} row(s)")
    print("    If this was a recovery rerun, its rows are settled and already "
          "archived — re-merging them is what breached the 100MB push limit "
          "on 2026-07-12. Nothing was lost.")


def _seat_row_filter(data_dir: Path):
    """Refuse seat rows for archived weekends (same stale-artifact trap as
    pre-reservation: legs upload their full local CSV, so pre-rotation
    artifacts would re-import every settled weekend)."""
    return _archived_weekend_filter(data_dir, "seat-archive", "seat-counts")


def _pre_reservation_row_filter(data_dir: Path):
    """Future-rows filter that ALSO refuses rows for archived weekends.

    Scrape legs upload their FULL local pre-reservation CSV as the artifact, so
    an artifact built before a rotation contains every settled weekend. Merging
    it into the rotated (weekends-trimmed) live CSV would re-import ~200K
    archived rows and re-breach GitHub's 100MB push limit — exactly how the
    2026-07-12 recovery rerun pushed a 100.38MB file. An archived weekend is
    settled: artifacts can only ever add rows for live weekends.
    """
    archived = _archived_weekend_filter(
        data_dir, "pre-reservation-archive", "pre-reservation-snapshots")

    def _filter(row: dict[str, str]) -> bool:
        return _is_future_pre_reservation_row(row) and archived(row)

    return _filter


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
    seat_added, seat_dupes, seat_metadata_updated, added_seats, updated_seats = _merge_csv(
        data_dir / SEAT_CSV,
        _csv_sources(artifact_root, SEAT_CSV),
        SEAT_FIELDS,
        _tuple_key(SEAT_DEDUPE_FIELDS),
        merge_duplicate=_merge_seat_row_metadata,
        row_filter=_seat_row_filter(data_dir),
    )
    summary.seat_added = seat_added
    summary.seat_duplicates = seat_dupes
    summary.seat_metadata_updated = seat_metadata_updated
    summary.markers.update(
        str(row.get("timezone", "") or "").strip()
        for row in [*added_seats, *updated_seats]
        if str(row.get("timezone", "") or "").strip()
    )

    poly_added, poly_dupes, _, _, _ = _merge_csv(
        data_dir / POLY_CSV,
        _csv_sources(artifact_root, POLY_CSV),
        POLY_FIELDS,
        _polymarket_key,
    )
    summary.polymarket_added = poly_added
    summary.polymarket_duplicates = poly_dupes

    pre_sources = _filter_pre_reservation_sources(
        artifact_root,
        _csv_sources(artifact_root, PRE_RESERVATION_CSV),
    )
    pre_added, pre_dupes, _, added_pre, _ = _merge_csv(
        data_dir / PRE_RESERVATION_CSV,
        pre_sources,
        PRE_RESERVATION_FIELDS,
        _tuple_key(PRE_RESERVATION_DEDUPE_FIELDS),
        row_filter=_pre_reservation_row_filter(data_dir),
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
    report_archived_weekend_drops()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
