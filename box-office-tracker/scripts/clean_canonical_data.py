#!/usr/bin/env python3
"""Clean canonical box-office training data.

This is intentionally deterministic and conservative. It removes rows that are
known to be out of scope for the production model, fixes harmless missing-format
sentinels, and refuses to guess when it finds an unexpected cross-movie
seat-map collision.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


EXCLUDED_MOVIES = {"Animal Farm", "Hokum"}
EXCLUDED_THEATRE_PREFIXES = ("AMC CLASSIC ",)
MISSING_FORMAT_VALUES = {"", "undefined", "none", "null", "nan"}

KNOWN_BAD_SEAT_ROWS = [
    {
        "weekend_of": "2026-05-22",
        "date": "2026-05-24",
        "timezone": "PT",
        "theatre_name": "AMC Factoria 8",
        "movie_title": "Passenger",
        "showtime": "10:40pm",
        "amc_seat_map_url": "https://www.amctheatres.com/showtimes/143248343/seats",
    }
]


@dataclass
class CleanStats:
    file: str
    removed_excluded_movies: int = 0
    removed_classic_theatres: int = 0
    removed_exact_duplicates: int = 0
    removed_known_bad_duplicates: int = 0
    removed_url_movie_mismatches: int = 0
    removed_ambiguous_url_rows: int = 0
    normalized_missing_formats: int = 0
    removed_calibration_entries: int = 0
    unresolved_duplicate_url_groups: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return any(
            [
                self.removed_excluded_movies,
                self.removed_classic_theatres,
                self.removed_exact_duplicates,
                self.removed_known_bad_duplicates,
                self.removed_url_movie_mismatches,
                self.removed_ambiguous_url_rows,
                self.normalized_missing_formats,
                self.removed_calibration_entries,
            ]
        )

    def summary(self) -> str:
        pieces = [
            f"excluded_movies={self.removed_excluded_movies}",
            f"classic_theatres={self.removed_classic_theatres}",
            f"exact_duplicates={self.removed_exact_duplicates}",
            f"known_bad_duplicates={self.removed_known_bad_duplicates}",
            f"url_movie_mismatches={self.removed_url_movie_mismatches}",
            f"ambiguous_url_rows={self.removed_ambiguous_url_rows}",
            f"missing_formats={self.normalized_missing_formats}",
            f"calibration_entries={self.removed_calibration_entries}",
            f"unresolved_url_groups={len(self.unresolved_duplicate_url_groups)}",
        ]
        return f"{self.file}: " + ", ".join(pieces)


class CanonicalDataError(RuntimeError):
    pass


@dataclass
class CleanCsvResult:
    stats: CleanStats
    rows: list[dict[str, str]]


def _clean_movie(value: str | None) -> str:
    return (value or "").strip()


def _is_excluded_movie(row: dict[str, str]) -> bool:
    return _clean_movie(row.get("movie_title") or row.get("movie")) in EXCLUDED_MOVIES


def _is_classic_theatre(row: dict[str, str]) -> bool:
    theatre = (row.get("theatre_name") or "").strip().upper()
    return any(theatre.startswith(prefix) for prefix in EXCLUDED_THEATRE_PREFIXES)


def _matches_subset(row: dict[str, str], expected: dict[str, str]) -> bool:
    return all((row.get(key) or "").strip() == value for key, value in expected.items())


def _is_known_bad_seat_row(row: dict[str, str]) -> bool:
    return any(_matches_subset(row, expected) for expected in KNOWN_BAD_SEAT_ROWS)


def _row_identity(row: dict[str, str], fieldnames: list[str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in fieldnames)


def _normalize_missing_format(row: dict[str, str]) -> bool:
    changed = False
    auditorium_type = (row.get("auditorium_type") or "").strip()
    if auditorium_type.lower() in MISSING_FORMAT_VALUES and auditorium_type:
        row["auditorium_type"] = ""
        changed = True

    notes = row.get("notes") or ""
    if notes.startswith("undefined @"):
        row["notes"] = "Unknown format @" + notes[len("undefined @") :]
        changed = True
    return changed


def _find_cross_movie_url_collisions(
    rows: list[dict[str, str]],
    *,
    date_col: str,
) -> list[str]:
    groups: dict[tuple[str, str, str, str], set[str]] = {}
    for row in rows:
        url = (row.get("amc_seat_map_url") or "").strip()
        if not url:
            continue
        key = (
            (row.get("weekend_of") or "").strip(),
            (row.get(date_col) or "").strip(),
            (row.get("timezone") or "").strip(),
            url,
        )
        groups.setdefault(key, set()).add(_clean_movie(row.get("movie_title")))

    collisions = []
    for key, movies in groups.items():
        clean_movies = {movie for movie in movies if movie}
        if len(clean_movies) > 1:
            weekend_of, show_date, timezone, url = key
            collisions.append(
                f"{weekend_of} {show_date} {timezone} {url} -> {sorted(clean_movies)}"
            )
    return collisions


def _collision_keys(rows: list[dict[str, str]], *, date_col: str) -> set:
    """Keys whose seat-map URL is claimed by more than one movie."""
    groups: dict = {}
    for row in rows:
        key = _url_key(row, date_col=date_col)
        if key is None:
            continue
        movie = _clean_movie(row.get("movie_title"))
        if movie:
            groups.setdefault(key, set()).add(movie)
    return {key for key, movies in groups.items() if len(movies) > 1}


def _url_key(row: dict[str, str], *, date_col: str) -> tuple[str, str, str, str] | None:
    url = (row.get("amc_seat_map_url") or "").strip()
    if not url:
        return None
    return (
        (row.get("weekend_of") or "").strip(),
        (row.get(date_col) or "").strip(),
        (row.get("timezone") or "").strip(),
        url,
    )


def _canonical_movie_by_url(
    rows: list[dict[str, str]],
    *,
    date_col: str,
) -> dict[tuple[str, str, str, str], str]:
    movies_by_key: dict[tuple[str, str, str, str], set[str]] = {}
    for row in rows:
        key = _url_key(row, date_col=date_col)
        if key is None:
            continue
        movie = _clean_movie(row.get("movie_title"))
        if movie:
            movies_by_key.setdefault(key, set()).add(movie)
    return {
        key: next(iter(movies))
        for key, movies in movies_by_key.items()
        if len(movies) == 1
    }


def clean_csv_file(
    path: Path,
    *,
    date_col: str,
    check: bool,
    canonical_movie_by_url: dict[tuple[str, str, str, str], str] | None = None,
    quarantine_unresolved: bool = False,
) -> CleanCsvResult:
    stats = CleanStats(file=str(path))
    if not path.exists():
        return CleanCsvResult(stats=stats, rows=[])

    original_bytes = path.read_bytes()
    lineterminator = "\r\n" if b"\r\n" in original_bytes[:8192] else "\n"
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        original_rows = list(reader)

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for row in original_rows:
        if _is_excluded_movie(row):
            stats.removed_excluded_movies += 1
            continue
        if _is_classic_theatre(row):
            stats.removed_classic_theatres += 1
            continue
        if date_col == "date" and _is_known_bad_seat_row(row):
            stats.removed_known_bad_duplicates += 1
            continue
        if canonical_movie_by_url:
            key = _url_key(row, date_col=date_col)
            canonical_movie = canonical_movie_by_url.get(key) if key else None
            if canonical_movie and _clean_movie(row.get("movie_title")) != canonical_movie:
                stats.removed_url_movie_mismatches += 1
                continue
        if _normalize_missing_format(row):
            stats.normalized_missing_formats += 1
        identity = _row_identity(row, fieldnames)
        if identity in seen:
            stats.removed_exact_duplicates += 1
            continue
        seen.add(identity)
        rows.append(row)

    stats.unresolved_duplicate_url_groups = _find_cross_movie_url_collisions(
        rows,
        date_col=date_col,
    )
    if stats.unresolved_duplicate_url_groups and quarantine_unresolved:
        # Pre-reservation rows are for FUTURE show dates by definition, so the
        # seat CSV — the only source of a canonical URL->movie mapping — can
        # never resolve a collision there. Raising therefore bricked finalize
        # PERMANENTLY: on 2026-08-09 one AMC showtime reported both
        # "One Night Only" and "Super Troopers 3", and every hourly retry
        # re-collected ~2,000 rows and threw them all away at this check.
        # Both attributions cannot be right and we cannot tell which is, so
        # drop just that URL group (keeping both would double-count the same
        # seats against two films) and report it loudly. Losing a handful of
        # ambiguous rows beats losing every row in the file.
        ambiguous_keys = _collision_keys(rows, date_col=date_col)
        kept = []
        for row in rows:
            key = _url_key(row, date_col=date_col)
            if key is not None and key in ambiguous_keys:
                stats.removed_ambiguous_url_rows += 1
                continue
            kept.append(row)
        rows = kept   # `changed` is derived from removed_ambiguous_url_rows
        print(
            f"\u26a0\ufe0f  {path.name}: dropped {stats.removed_ambiguous_url_rows} row(s) in "
            f"{len(stats.unresolved_duplicate_url_groups)} ambiguous seat-map group(s) "
            f"rather than failing the merge:", file=sys.stderr)
        for group in stats.unresolved_duplicate_url_groups:
            print(f"    {group}", file=sys.stderr)
    elif stats.unresolved_duplicate_url_groups:
        raise CanonicalDataError(
            f"{path} has unexpected cross-movie seat-map collisions:\n"
            + "\n".join(stats.unresolved_duplicate_url_groups)
        )

    if check:
        return CleanCsvResult(stats=stats, rows=rows)

    if stats.changed:
        with path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator=lineterminator)
            writer.writeheader()
            writer.writerows(rows)
    return CleanCsvResult(stats=stats, rows=rows)


def _filter_calibration_object(value: Any, stats: CleanStats) -> Any:
    if isinstance(value, list):
        cleaned = []
        for item in value:
            if isinstance(item, dict) and _clean_movie(item.get("movie")) in EXCLUDED_MOVIES:
                stats.removed_calibration_entries += 1
                continue
            cleaned.append(_filter_calibration_object(item, stats))
        return cleaned
    if isinstance(value, dict):
        return {key: _filter_calibration_object(item, stats) for key, item in value.items()}
    return value


def clean_calibration_json(path: Path, *, check: bool) -> CleanStats:
    stats = CleanStats(file=str(path))
    if not path.exists():
        return stats
    original = json.loads(path.read_text())
    cleaned = _filter_calibration_object(original, stats)
    if not check and stats.changed:
        path.write_text(json.dumps(cleaned, indent=2, sort_keys=False) + "\n")
    return stats


def canonical_data_dir(repo_root: Path) -> Path:
    """Return the canonical data directory for either repo or tracker cwd.

    The GitHub finalizer runs this script from ``box-office-tracker`` while
    local/manual checks often run it from the repository root. Resolve both
    layouts so the cleaner cannot silently inspect an empty nested path.
    """
    repo_layout = repo_root / "box-office-tracker" / "data"
    if repo_layout.exists():
        return repo_layout
    tracker_layout = repo_root / "data"
    if tracker_layout.exists():
        return tracker_layout
    return repo_layout


def collect_stats(repo_root: Path, *, check: bool) -> list[CleanStats]:
    data = canonical_data_dir(repo_root)
    # The seat lane needs the SAME quarantine as the snapshot lane. The
    # original reasoning — "seat rows are post-showtime so a canonical
    # URL->movie mapping can resolve them" — was wrong: _canonical_movie_by_url
    # only maps a URL claimed by exactly ONE movie, so a URL claimed by two in
    # the seat file itself is equally unresolvable and bricks finalize just as
    # permanently. It did, on 2026-08-10, discarding Sunday's seat counts.
    # --check stays strict in both lanes so audits still surface the ambiguity.
    seat_result = clean_csv_file(data / "seat-counts.csv", date_col="date",
                                 check=check, quarantine_unresolved=not check)
    canonical_url_movies = _canonical_movie_by_url(seat_result.rows, date_col="date")
    snapshot_result = clean_csv_file(
        data / "pre-reservation-snapshots.csv",
        date_col="show_date",
        check=check,
        canonical_movie_by_url=canonical_url_movies,
        # --check is the AUDIT mode: it must still raise on an unresolvable
        # collision, otherwise the ambiguity is reclassified as routine
        # "pending cleanup" and becomes invisible to the operator. Only the
        # real cleaning pass (which finalize runs) quarantines to stay alive.
        quarantine_unresolved=not check,
    )
    stats = [
        seat_result.stats,
        snapshot_result.stats,
        clean_calibration_json(data / "calibration.json", check=check),
    ]
    freeze_dir = data / "calibration-freezes"
    if freeze_dir.exists():
        for path in sorted(freeze_dir.glob("*.json")):
            stats.append(clean_calibration_json(path, check=check))
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--check",
        action="store_true",
        help="report dirty canonical data without modifying files",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    try:
        stats = collect_stats(repo_root, check=args.check)
    except CanonicalDataError as exc:
        print(f"Canonical data clean failed: {exc}", file=sys.stderr)
        return 1

    dirty = [item for item in stats if item.changed]
    for item in stats:
        print(item.summary())

    if args.check and dirty:
        print(
            "Canonical data check failed: run clean_canonical_data.py without --check.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
