#!/usr/bin/env python3
"""Rotate settled weekends out of a LANE snapshot CSV into per-weekend gzip archives.

2026-09-27: the lane CSVs (fandango, cinemark, alamo, harkins, webedia,
cinemark-showtime-links) were never rotated, and the every-showing Cinemark
census plus the Webedia lane add ~3 MB/day each — GitHub hard-rejects pushes
over 100 MB (the AMC snapshot CSV already broke finalize on 2026-07-12 and
2026-09-24). Each lane rotates ITS OWN file inside its own commit step, right
after re-applying its rows onto the latest main, so finalize never touches lane
files and every committer computes the same result.

Policy: keep the `keep` newest weekend_of values whole (the current or upcoming
weekend and the previous one); archive older weekends WHOLE into
<archive_dir>/<csv stem>-<weekend>.csv.gz. No mid-weekend cuts — that is what
made the AMC merge guard drop live rows on 2026-09-26. The union step refuses
rows for archived weekends (union_csv_rows.py --archived-dir) so a runner whose
checkout predates a rotation cannot re-import them.

  python3 scripts/rotate_lane_csv.py CSV --archive-dir DIR [--keep 2] [--dry-run]
"""
import argparse
import csv
import gzip
import os
import sys

csv.field_size_limit(10 ** 9)


def plan(rows, keep):
    """Pure: -> (weekends to archive, weekends kept)."""
    weekends = sorted({(r.get("weekend_of") or "").strip() for r in rows} - {""})
    kept = set(weekends[-keep:]) if keep > 0 else set()
    return [w for w in weekends if w not in kept], kept


def archive_path(archive_dir, csv_path, weekend):
    stem = os.path.splitext(os.path.basename(csv_path))[0]
    return os.path.join(archive_dir, f"{stem}-{weekend}.csv.gz")


def rotate(csv_path, archive_dir, keep=2, dry_run=False):
    if not os.path.exists(csv_path):
        print(f"{csv_path}: no file; nothing to rotate")
        return 0
    with open(csv_path, newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    to_archive, kept = plan(rows, keep)
    print(f"{os.path.basename(csv_path)}: {os.path.getsize(csv_path)/1e6:.1f}MB, {len(rows)} rows; "
          f"keep {sorted(kept)}; archive {to_archive}")
    if not to_archive or dry_run:
        return len(to_archive)
    os.makedirs(archive_dir, exist_ok=True)
    for w in to_archive:
        w_rows = [r for r in rows if (r.get("weekend_of") or "").strip() == w]
        apath = archive_path(archive_dir, csv_path, w)
        existing, afields = [], fields
        if os.path.exists(apath):
            with gzip.open(apath, "rt", newline="") as f:
                rd = csv.DictReader(f)
                afields = list(rd.fieldnames or fields)
                existing = list(rd)
        out_fields = afields + [c for c in fields if c not in afields]
        seen = {tuple((k, r.get(k) or "") for k in out_fields) for r in existing}
        merged = existing + [r for r in w_rows if tuple((k, r.get(k) or "") for k in out_fields) not in seen]
        tmp = apath + ".tmp"
        with gzip.open(tmp, "wt", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
            wr.writeheader(); wr.writerows(merged)
        os.replace(tmp, apath)
        print(f"  archived {w}: {len(w_rows)} rows -> {os.path.basename(apath)} ({len(merged)} total)")
    kept_rows = [r for r in rows if (r.get("weekend_of") or "").strip() not in set(to_archive)]
    tmp = csv_path + ".tmp"
    with open(tmp, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        wr.writeheader(); wr.writerows(kept_rows)
    os.replace(tmp, csv_path)
    print(f"  live now {os.path.getsize(csv_path)/1e6:.1f}MB, {len(kept_rows)} rows")
    return len(to_archive)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--archive-dir", required=True)
    ap.add_argument("--keep", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    rotate(a.csv, a.archive_dir, keep=a.keep, dry_run=a.dry_run)
    sys.exit(0)
