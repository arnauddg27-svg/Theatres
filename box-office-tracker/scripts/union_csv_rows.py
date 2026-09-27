#!/usr/bin/env python3
"""Append rows from OURS that are missing in TARGET (exact-row union, order kept).

Parallel collectors (Cinemark slices, 2026-09-26) append to the same canonical
CSV. `git pull --rebase` then conflicts on the file's last line and the loser's
rows are dropped after three retries. Instead each runner saves its own copy,
resets to the latest main and re-applies its rows with this union — idempotent,
so a retry after a lost push race never duplicates.

  python3 scripts/union_csv_rows.py OURS.csv TARGET.csv [--key f1,f2,...]   -> prints rows added

--key dedupes on those columns instead of the whole row: two runners reading
the same showing in the same snapshot bucket write rows that differ only in
snapshot_time/run_id (three catch-up Alamo post passes at 02:10Z on
2026-09-27 wrote the same 57 showings three times).

--archived-dir DIR refuses rows whose weekend_of has already been rotated into
DIR (any *-<weekend>.csv.gz): a runner whose checkout predates a lane rotation
(scripts/rotate_lane_csv.py) must not re-import the archived weekend.
"""
import csv
import sys


def archived_weekends(archive_dir):
    """Pure-ish: {weekend} with an archive file in archive_dir."""
    import os
    import re
    if not archive_dir or not os.path.isdir(archive_dir):
        return set()
    out = set()
    for fn in os.listdir(archive_dir):
        m = re.search(r"-(\d{4}-\d{2}-\d{2})\.csv\.gz$", fn)
        if m:
            out.add(m.group(1))
    return out


def union_rows(ours_path, target_path, key=None, archived=None):
    with open(target_path, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        keyf = list(key) if key else fields
        have = {tuple((k, (r.get(k) or "")) for k in keyf) for r in reader}
    with open(ours_path, newline="") as f:
        ours = csv.DictReader(f)
        extra = [c for c in (ours.fieldnames or []) if c not in fields]
        fields_out = fields + extra
        new = []
        for r in ours:
            if archived and (r.get("weekend_of") or "").strip() in archived:
                continue
            k_ = tuple((k, (r.get(k) or "")) for k in keyf)
            if k_ in have:
                continue
            have.add(k_)
            new.append(r)
    if not new:
        return 0
    if extra:
        # widen the target header (superset schema) before appending
        with open(target_path, newline="") as f:
            rows = list(csv.DictReader(f))
        with open(target_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields_out, extrasaction="ignore")
            w.writeheader(); w.writerows(rows); w.writerows(new)
        return len(new)
    with open(target_path, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=fields_out, extrasaction="ignore").writerows(new)
    return len(new)


if __name__ == "__main__":
    key = None
    if "--key" in sys.argv:
        key = [k for k in sys.argv[sys.argv.index("--key") + 1].split(",") if k]
    archived = None
    if "--archived-dir" in sys.argv:
        archived = archived_weekends(sys.argv[sys.argv.index("--archived-dir") + 1])
    print(union_rows(sys.argv[1], sys.argv[2], key=key, archived=archived))
