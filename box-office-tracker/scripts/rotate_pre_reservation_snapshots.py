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

Size cap (2026-09-24): keeping two weekends was itself 98.5 MiB once a
one-film weekend reached 219k rows, and four finalize pushes were rejected
(rows recovered from artifacts). With --max-mb the script also (1) drops older
kept weekends while the projected live size is over the cap and (2) if a single
weekend is still over it, archives that weekend's PLAYED show dates (local day
fully over, judged as UTC now minus PLAYED_MARGIN_HOURS) into the same per-
weekend archive. Rows for a played show date are never appended again, and the
loader reads live + archive for one weekend, so nothing is lost.

Run:  python3 scripts/rotate_pre_reservation_snapshots.py [--dry-run] [--keep N] [--max-mb M]
"""
import argparse
import csv
import gzip
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

KEEP_WEEKENDS = 2
# A show on the last US date ends by ~09Z the next day (23:45 PT + runtime);
# 10h after that is still Wednesday for the 09-24T05Z finalize and Thursday for
# the 10Z one, so "played" never includes a date with showtimes still ahead.
PLAYED_MARGIN_HOURS = 10


def played_cutoff(now_utc=None):
    """ISO date: show dates strictly before it have fully played everywhere."""
    now_utc = now_utc or datetime.now(timezone.utc)
    return (now_utc - timedelta(hours=PLAYED_MARGIN_HOURS)).date().isoformat()


def plan(rows, size_before, keep=KEEP_WEEKENDS, max_bytes=None, now_utc=None):
    """Pure: -> (archive_index_by_weekend {w: [row idx]}, keep_set, note).

    1. weekends beyond the newest `keep` are archived whole;
    2. with max_bytes, older KEPT weekends go too while the projected live size
       (bytes/row * rows) is over the cap, always keeping the newest weekend;
    3. still over: the played show dates of the remaining weekend(s) go.
    """
    weekends = sorted({r.get("weekend_of", "") for r in rows if r.get("weekend_of")})
    keep_set = set(weekends[-keep:]) if weekends else set()
    by_w = {}
    for i, r in enumerate(rows):
        by_w.setdefault(r.get("weekend_of", ""), []).append(i)
    archive = {w: list(by_w[w]) for w in weekends if w not in keep_set}
    notes = []
    if max_bytes and rows:
        per_row = size_before / len(rows)
        def projected():
            archived = sum(len(v) for v in archive.values())
            return (len(rows) - archived) * per_row
        for w in sorted(keep_set):
            if projected() <= max_bytes or len(keep_set) <= 1:
                break
            keep_set.discard(w); archive[w] = list(by_w[w])
            notes.append(f"over cap: also archiving weekend {w}")
        if projected() > max_bytes:
            cutoff = played_cutoff(now_utc)
            for w in sorted(keep_set):
                idx = [i for i in by_w[w] if (rows[i].get("show_date") or "9999") < cutoff]
                if idx:
                    archive.setdefault(w, []).extend(idx)
                    notes.append(f"over cap: archiving {len(idx)} played rows (show_date < {cutoff}) of weekend {w}")
        if projected() > max_bytes:
            notes.append(f"still ~{projected()/1e6:.0f}MB after rotation — only unplayed rows remain")
    return archive, keep_set, notes


def rotate(keep=KEEP_WEEKENDS, dry_run=False,
           path=None, archive_dir=None, archive_path_fn=None, label="pre-reservation",
           max_bytes=None, now_utc=None):
    path = path or P.PRE_RESERVATION_CSV
    archive_dir = archive_dir or P.PRE_RESERVATION_ARCHIVE_DIR
    archive_path_fn = archive_path_fn or P._pre_reservation_archive_path
    if not os.path.exists(path):
        print(f"no live {label} CSV; nothing to rotate")
        return 0
    size_before = os.path.getsize(path)
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    weekends = sorted({r.get("weekend_of", "") for r in rows if r.get("weekend_of")})
    archive, keep_set, notes = plan(rows, size_before, keep=keep, max_bytes=max_bytes, now_utc=now_utc)
    print(f"live file: {size_before/1e6:.0f}MB, {len(rows)} rows, weekends {weekends}")
    print(f"keeping {sorted(keep_set)}; archiving {sorted(archive)}")
    for n in notes:
        print(f"  {n}")
    archive = {w: idx for w, idx in archive.items() if idx}
    if not archive:
        print("nothing to rotate")
        return 0
    if dry_run:
        return 0

    os.makedirs(archive_dir, exist_ok=True)
    archived_idx = set()
    for w, idx in sorted(archive.items()):
        w_rows = [rows[i] for i in idx]
        archived_idx.update(idx)
        apath = archive_path_fn(w)
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

    kept_rows = [r for i, r in enumerate(rows) if i not in archived_idx]
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
    ap.add_argument("--max-mb", type=float, default=None,
                    help="cap the live CSV (MiB): archive older kept weekends, then played show dates")
    args = ap.parse_args()
    max_bytes = int(args.max_mb * 1024 * 1024) if args.max_mb else None
    rc = rotate(keep=args.keep, dry_run=args.dry_run, max_bytes=max_bytes)
    # seat-counts.csv has the same 100MB cliff (72MB on 2026-07-12, ~+9MB/weekend)
    rc |= rotate(keep=args.keep, dry_run=args.dry_run, max_bytes=max_bytes,
                 path=P.SEAT_CSV, archive_dir=P.SEAT_ARCHIVE_DIR,
                 archive_path_fn=P._seat_archive_path, label="seat-counts")
    raise SystemExit(rc)
