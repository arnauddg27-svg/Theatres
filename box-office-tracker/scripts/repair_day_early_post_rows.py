#!/usr/bin/env python3
"""Relabel Alamo/Harkins "post-show-census" rows that were read BEFORE the show.

Until 2026-11-19 both collectors moved any start more than 12 h ahead back a
day, so tomorrow's showing looked like it had begun minutes ago and its seat
count was written as a post-show read 24 h early (39% of Alamo's post rows,
43% of Harkins'). Each such row is a real reading at the time it was taken —
just not a final one — so it is relabelled as the lane's ordinary pre-show
row; when an ordinary row with the same dedupe key already exists, the
mislabelled copy is dropped instead (it says nothing new).

Idempotent. Live CSVs and their gzip archives; --dry-run prints the counts.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fandango_collect import fandango_row_key  # noqa: E402

LANES = {
    "alamo": {"pre_kind": "alamo-api", "tz": "America/Chicago"},
    "harkins": {"pre_kind": "harkins-api", "tz": "America/Phoenix"},
}
POST = "post-show-census"
ROLLOVER_HOUR = 5
# A genuine post read happens at or after the start; the mislabelled ones sit
# about 24 h before it. An hour of slack keeps clock skew out of it.
EARLY_SEC = 3600


def show_start_utc(row, default_tz):
    try:
        local = datetime.strptime(f"{row['show_date']} {row['showtime']}", "%Y-%m-%d %H:%M")
    except (KeyError, ValueError):
        return None
    start = local.replace(tzinfo=ZoneInfo(row.get("timezone") or default_tz)).astimezone(timezone.utc)
    if local.hour < ROLLOVER_HOUR:
        start += timedelta(days=1)
    return start


def read_before_start(row, default_tz):
    if row.get("row_kind") != POST:
        return False
    start = show_start_utc(row, default_tz)
    try:
        snap = datetime.fromisoformat(str(row.get("snapshot_time", "")).replace("Z", "+00:00"))
    except ValueError:
        return False
    if start is None:
        return False
    if snap.tzinfo is None:
        snap = snap.replace(tzinfo=timezone.utc)
    return (start - snap).total_seconds() > EARLY_SEC


def repair_rows(rows, lane):
    """-> (rows, relabelled, dropped). Pure."""
    cfg = LANES[lane]
    keys = {fandango_row_key(r) for r in rows if r.get("row_kind") != POST}
    out, relabelled, dropped = [], 0, 0
    for row in rows:
        if not read_before_start(row, cfg["tz"]):
            out.append(row)
            continue
        fixed = dict(row)
        fixed["row_kind"] = cfg["pre_kind"]
        fixed["notes"] = (row.get("notes") or "").replace(f"{POST}; ", "")
        key = fandango_row_key(fixed)
        if key in keys:
            dropped += 1
            continue
        keys.add(key)
        out.append(fixed)
        relabelled += 1
    return out, relabelled, dropped


def _open(path, mode):
    if path.suffix == ".gz":
        return io.TextIOWrapper(gzip.open(path, mode + "b"), encoding="utf-8", newline="")
    return open(path, mode, newline="", encoding="utf-8")


def repair_file(path, lane, dry_run=False):
    with _open(path, "r") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        rows = list(reader)
    out, relabelled, dropped = repair_rows(rows, lane)
    if (relabelled or dropped) and not dry_run:
        with _open(path, "w") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(out)
    return len(rows), relabelled, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    data = ROOT / "data"
    for lane in LANES:
        paths = [data / f"{lane}-pre-reservation-snapshots.csv"] + sorted((data / f"{lane}-archive").glob("*.csv.gz"))
        for path in paths:
            if not path.exists():
                continue
            total, relabelled, dropped = repair_file(path, lane, args.dry_run)
            print(f"{path.relative_to(ROOT)}: {total} rows, {relabelled} relabelled, {dropped} dropped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
