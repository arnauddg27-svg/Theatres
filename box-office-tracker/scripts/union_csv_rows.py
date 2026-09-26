#!/usr/bin/env python3
"""Append rows from OURS that are missing in TARGET (exact-row union, order kept).

Parallel collectors (Cinemark slices, 2026-09-26) append to the same canonical
CSV. `git pull --rebase` then conflicts on the file's last line and the loser's
rows are dropped after three retries. Instead each runner saves its own copy,
resets to the latest main and re-applies its rows with this union — idempotent,
so a retry after a lost push race never duplicates.

  python3 scripts/union_csv_rows.py OURS.csv TARGET.csv   -> prints rows added
"""
import csv
import sys


def union_rows(ours_path, target_path):
    with open(target_path, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        have = {tuple((k, (r.get(k) or "")) for k in fields) for r in reader}
    with open(ours_path, newline="") as f:
        ours = csv.DictReader(f)
        extra = [c for c in (ours.fieldnames or []) if c not in fields]
        fields_out = fields + extra
        new = []
        for r in ours:
            key = tuple((k, (r.get(k) or "")) for k in fields)
            if key in have:
                continue
            have.add(key)
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
    print(union_rows(sys.argv[1], sys.argv[2]))
