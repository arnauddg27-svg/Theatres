#!/usr/bin/env python3
"""Write each opener's real opening-weekend theatre count into movie-metadata.csv.

    python3 scripts/sync_opening_theatre_counts.py [--write]

Why (audit 2026-11-03): metadata's national_theatre_count is filled before
release from Box Office Mojo's "Widest Release" field, which pre-release is a
placeholder more often than not — Sense and Sensibility 705 (opened in
2,545), The Only Living Pickpocket 6 (1,112), Queen at Sea 1. The footprint
factor turns 705 into a 0.55x haircut on a film that deserved ~0.92x, and
calibrate.py replays the weekend with the same wrong number for ever.

The weekend chart count in data/theatre-counts.json (scraper.
fetch_bom_theatre_counts, strict title match since 1e590653) IS the opening
count once the chart includes Friday, i.e. once the file's _updated stamp is
Saturday of that weekend or later. For every film whose metadata weekend_of
equals the counts file's weekend and whose stored count is blank or more
than SYNC_TOLERANCE off, the chart count replaces it with a dated note. Runs
in finalize after fill_movie_metadata; a dry run prints what would change.
"""
import csv
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

METADATA_CSV = ROOT / "data" / "movie-metadata.csv"
THEATRE_COUNTS_JSON = ROOT / "data" / "theatre-counts.json"
SYNC_TOLERANCE = 0.15


def _weekend_of(updated_iso):
    """Friday anchor of the collection window that stamped the counts file."""
    from scraper import opening_weekend_friday
    dt = datetime.fromisoformat(updated_iso.replace("Z", "+00:00")).replace(tzinfo=None)
    return opening_weekend_friday(dt), dt.date()


def chart_counts(counts_path=THEATRE_COUNTS_JSON):
    """(weekend_of, {movie: count}) when the chart already includes that
    weekend's Friday; (None, {}) otherwise."""
    try:
        data = json.loads(Path(counts_path).read_text())
    except (OSError, ValueError):
        return None, {}
    updated = str(data.get("_updated") or "")
    if not updated:
        return None, {}
    try:
        weekend, stamped = _weekend_of(updated)
    except (ValueError, ImportError):
        return None, {}
    friday = date.fromisoformat(weekend)
    if stamped < friday + timedelta(days=1):
        return weekend, {}            # Thursday-preview chart: not the opening count yet
    return weekend, {k: int(v) for k, v in data.items()
                     if not k.startswith("_") and isinstance(v, (int, float)) and v > 0}


def sync(rows, weekend, counts, today=None):
    """Mutate metadata rows; return [(movie, old, new)]."""
    changes = []
    if not weekend or not counts:
        return changes
    by_key = {m.strip().lower(): c for m, c in counts.items()}
    stamp = today or time.strftime("%Y-%m-%d")
    for row in rows:
        if (row.get("weekend_of") or "").strip() != weekend:
            continue
        new = by_key.get((row.get("movie") or "").strip().lower())
        if not new:
            continue
        old_raw = (row.get("national_theatre_count") or "").strip()
        try:
            old = int(float(old_raw)) if old_raw else None
        except ValueError:
            old = None
        if old and abs(new - old) / new <= SYNC_TOLERANCE:
            continue
        row["national_theatre_count"] = str(new)
        tag = f"opening-weekend chart count {old_raw or '-'}->{new} (synced {stamp})"
        notes = (row.get("notes") or "").strip()
        row["notes"] = f"{notes}; {tag}" if notes else tag
        changes.append((row["movie"], old_raw or "-", new))
    return changes


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    write = "--write" in argv
    weekend, counts = chart_counts()
    if not counts:
        print(f"sync_opening_theatre_counts: no post-Friday chart counts in {THEATRE_COUNTS_JSON.name}"
              f"{f' (weekend {weekend})' if weekend else ''}; nothing to do")
        return 0
    with open(METADATA_CSV, newline="") as f:
        reader = csv.DictReader(f)
        rows, fields = list(reader), list(reader.fieldnames or [])
    changes = sync(rows, weekend, counts)
    for movie, old, new in changes:
        print(f"  {movie}: national_theatre_count {old} -> {new}")
    if not changes:
        print(f"sync_opening_theatre_counts: metadata already matches the {weekend} chart")
        return 0
    if write:
        tmp = METADATA_CSV.with_suffix(".csv.tmp")
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, METADATA_CSV)
        print(f"sync_opening_theatre_counts: wrote {len(changes)} count(s) to {METADATA_CSV.name}")
    else:
        print(f"sync_opening_theatre_counts: {len(changes)} change(s) (dry run; pass --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
