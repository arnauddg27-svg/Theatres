#!/usr/bin/env python3
"""Rotate settled weekends out of pre-reservation-snapshots.csv into gzip archives.

The live CSV hit 99MB on 2026-07-12 — GitHub hard-blocks pushes at 100MB, which
already killed one finalize push (LFS error, run 2026-07-12T02:30Z; its snapshot
rows were lost from canonical). Every weekend adds ~15-25MB, so without rotation
the whole snapshot lane bricks.

Policy: keep the KEEP_WEEKENDS most recent weekends in the live CSV (the current
weekend is still being written; the previous one may still be calibrating);
append everything older to data/pre-reservation-archive/pre-reservation-
snapshots-<weekend>.csv.gz. predict.load_pre_reservation_data reads the archive
transparently for historical replays. Idempotent: re-running when there is
nothing to rotate is a no-op; duplicate rows are dropped on archive-merge.

Run:  python3 scripts/rotate_pre_reservation_snapshots.py [--dry-run] [--keep N]
"""
import argparse
import csv
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

KEEP_WEEKENDS = 2


def rotate(keep=KEEP_WEEKENDS, dry_run=False):
    path = P.PRE_RESERVATION_CSV
    if not os.path.exists(path):
        print("no live pre-reservation CSV; nothing to rotate")
        return 0
    size_before = os.path.getsize(path)
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    weekends = sorted({r.get("weekend_of", "") for r in rows if r.get("weekend_of")})
    keep_set = set(weekends[-keep:]) if weekends else set()
    to_archive = [w for w in weekends if w not in keep_set]
    print(f"live file: {size_before/1e6:.0f}MB, {len(rows)} rows, weekends {weekends}")
    print(f"keeping {sorted(keep_set)}; archiving {to_archive}")
    if not to_archive:
        print("nothing to rotate")
        return 0
    if dry_run:
        return 0

    os.makedirs(P.PRE_RESERVATION_ARCHIVE_DIR, exist_ok=True)
    for w in to_archive:
        w_rows = [r for r in rows if r.get("weekend_of") == w]
        apath = P._pre_reservation_archive_path(w)
        existing = []
        if os.path.exists(apath):
            with gzip.open(apath, "rt", newline="") as f:
                existing = list(csv.DictReader(f))
        seen = {tuple(sorted(r.items())) for r in existing}
        merged = existing + [r for r in w_rows
                             if tuple(sorted(r.items())) not in seen]
        tmp = apath + ".tmp"
        with gzip.open(tmp, "wt", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(merged)
        os.replace(tmp, apath)
        print(f"  archived {w}: {len(w_rows)} rows -> {os.path.basename(apath)} "
              f"({os.path.getsize(apath)/1e6:.1f}MB, {len(merged)} total)")

    kept_rows = [r for r in rows if r.get("weekend_of") in keep_set
                 or not r.get("weekend_of")]
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept_rows)
    os.replace(tmp, path)
    print(f"live file now: {os.path.getsize(path)/1e6:.0f}MB, {len(kept_rows)} rows")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep", type=int, default=KEEP_WEEKENDS)
    args = ap.parse_args()
    raise SystemExit(rotate(keep=args.keep, dry_run=args.dry_run))
