#!/usr/bin/env python3
"""Derive early-sellout fractions from pre-reservation snapshots.

A show that is effectively full (>=95% reserved) well BEFORE showtime carries
far more censored demand than one that fills at the last minute — the seat
model cannot see demand above capacity (the Backrooms-class under-prediction).
This tool computes, per (movie, weekend, day):

    early_sellout_fraction = snapshotted showtimes that hit >=95% reserved
                             more than EARLY_MINUTES before showtime
                             / all snapshotted showtimes that day

and backfills it onto calibration history entries as
`daily_early_sellout_fractions`. Data enrichment only — the prediction model
does NOT consume this field yet; adopting it as a feature must pass the
leave-one-movie-out bake-off like everything else.

Idempotent: re-running refreshes the fractions from the current snapshots CSV.

Usage:
    python3 scripts/sellout_velocity.py            # backfill calibration.json
    python3 scripts/sellout_velocity.py --dry-run  # print only
"""
from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRE_RESERVATION_CSV = ROOT / "data" / "pre-reservation-snapshots.csv"
CALIBRATION_JSON = ROOT / "data" / "calibration.json"

SELLOUT_OCCUPANCY = 0.95
EARLY_MINUTES = 60


def _snapshot_readers():
    """Live snapshot CSV plus every rotated per-weekend gzip archive.

    Settled weekends rotate out of the live CSV (100MB push cap), so reading
    it alone would silently limit this tool to the two most recent weekends.
    """
    archive_dir = ROOT / "data" / "pre-reservation-archive"
    if archive_dir.is_dir():
        for path in sorted(archive_dir.glob("*.csv.gz")):
            with gzip.open(path, "rt", newline="") as f:
                yield csv.DictReader(f)
    if PRE_RESERVATION_CSV.exists():
        with open(PRE_RESERVATION_CSV, newline="") as f:
            yield csv.DictReader(f)


def early_sellout_fractions():
    """{(movie, weekend, day): fraction of snapshotted showtimes selling out early}."""
    sold_early = {}
    seen = set()
    for reader in _snapshot_readers():
        for row in reader:
            try:
                total = float(row.get("total_seats") or 0)
                reserved = float(row.get("reserved_seats") or 0)
                minutes = int(float(row.get("minutes_until_showtime") or 0))
            except (TypeError, ValueError):
                continue
            if total <= 0:
                continue
            show_key = (
                row.get("movie_title", ""),
                row.get("weekend_of", ""),
                row.get("day_of_week", ""),
                row.get("theatre_name", ""),
                row.get("showtime_id", "") or row.get("showtime", ""),
                row.get("show_date", ""),
            )
            seen.add(show_key)
            if reserved / total >= SELLOUT_OCCUPANCY and minutes > EARLY_MINUTES:
                sold_early[show_key] = True
    counts = defaultdict(lambda: [0, 0])  # (movie, weekend, day) -> [early, total]
    for show_key in seen:
        agg_key = show_key[:3]
        counts[agg_key][1] += 1
        if sold_early.get(show_key):
            counts[agg_key][0] += 1
    return {key: early / total for key, (early, total) in counts.items() if total > 0}


def main(argv):
    dry_run = "--dry-run" in argv
    fractions = early_sellout_fractions()
    cal = json.loads(CALIBRATION_JSON.read_text())
    changed = 0
    for entry in cal.get("history", []):
        per_day = {}
        for day in ("Thursday", "Friday", "Saturday", "Sunday"):
            value = fractions.get((entry.get("movie", ""), entry.get("weekend_of", ""), day))
            if value is not None:
                per_day[day] = round(value, 4)
        if per_day:
            if entry.get("daily_early_sellout_fractions") != per_day:
                changed += 1
            entry["daily_early_sellout_fractions"] = per_day
        print(f"{entry.get('movie','')[:38]:<39} {per_day}")
    if dry_run:
        print(f"\n(dry-run) would update {changed} entr(ies)")
        return 0
    tmp = CALIBRATION_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cal, indent=2) + "\n")
    tmp.replace(CALIBRATION_JSON)
    print(f"\nupdated {changed} entr(ies) -> {CALIBRATION_JSON.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
