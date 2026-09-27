#!/usr/bin/env python3
"""Census scorecard: how many of America's seats sold did we COUNT, per day?

For each opening-weekend day with a reported national gross
(data/daily-actual-overrides.csv), compare seats counted at/after showtime —
AMC post-show seat counts plus the post-show census rows of the Cinemark,
Alamo and Harkins lanes — with national seats sold (reported gross / assumed
average ticket). Informational; prints a table and writes
data/census-coverage.csv. Goal (2026-09-26): push the counted share up.
"""
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
csv.field_size_limit(10 ** 9)
AVG_TICKET = float(os.environ.get("CENSUS_AVG_TICKET", "13.0"))
LANES = {"CNMK": "cinemark-pre-reservation-snapshots.csv", "ALMO": "alamo-pre-reservation-snapshots.csv",
         "HARK": "harkins-pre-reservation-snapshots.csv"}
DAYS = {"Thursday": -1, "Friday": 0, "Saturday": 1, "Sunday": 2}


def reported(weekend_of):
    out = {}
    path = os.path.join(DATA, "daily-actual-overrides.csv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            if r.get("weekend_of") == weekend_of:
                out[(r["movie_title"], r["day_of_week"])] = float(r["gross_m"])
    return out


def counted(weekend_of):
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    date_day = {(fri + timedelta(days=o)).strftime("%Y-%m-%d"): d for d, o in DAYS.items()}
    seats = defaultdict(lambda: defaultdict(int))
    latest = {}
    for r in csv.DictReader(open(os.path.join(DATA, "seat-counts.csv"), errors="replace")):
        day = date_day.get(r.get("date"))
        if not day:
            continue
        try:
            seats[(r["movie_title"], day)]["AMC"] += int(float(r["seats_sold"]))
        except (KeyError, ValueError):
            pass
    for chain, fn in LANES.items():
        path = os.path.join(DATA, fn)
        if not os.path.exists(path):
            continue
        for r in csv.DictReader(open(path, errors="replace")):
            day = date_day.get(r.get("show_date"))
            if not day or r.get("row_kind") != "post-show-census" or r.get("weekend_of") != weekend_of:
                continue
            k = (chain, r["showtime_id"], r["movie_title"], day)
            if k not in latest or r["snapshot_time"] > latest[k][0]:
                latest[k] = (r["snapshot_time"], int(float(r.get("reserved_seats") or 0)))
    for (chain, _sid, movie, day), (_t, sold) in latest.items():
        seats[(movie, day)][chain] += sold
    return seats


def main():
    from scraper import opening_weekend_friday
    weekend_of = sys.argv[1] if len(sys.argv) > 1 else opening_weekend_friday(datetime.now())
    rep, cnt = reported(weekend_of), counted(weekend_of)
    rows = []
    for (movie, day), gross in sorted(rep.items(), key=lambda x: (x[0][0], DAYS.get(x[0][1], 9))):
        national = gross * 1e6 / AVG_TICKET
        by = cnt.get((movie, day), {})
        total = sum(by.values())
        rows.append({"weekend_of": weekend_of, "movie": movie, "day": day, "national_seats_est": round(national),
                     **{f"{c}_seats": by.get(c, 0) for c in ("AMC", "CNMK", "ALMO", "HARK")},
                     "counted_seats": total, "counted_pct": round(total * 100 / national, 1) if national else 0})
    if not rows:
        print(f"census coverage: no reported days yet for {weekend_of}")
        return 0
    print(f"Census coverage {weekend_of} (avg ticket ${AVG_TICKET:.2f}):")
    for r in rows:
        print(f"  {r['movie'][:20]:20s} {r['day']:9s} national~{r['national_seats_est']:>9,} counted {r['counted_seats']:>8,} "
              f"({r['counted_pct']:4.1f}%)  AMC {r['AMC_seats']:,} CNMK {r['CNMK_seats']:,} ALMO {r['ALMO_seats']:,} HARK {r['HARK_seats']:,}")
    out = os.path.join(DATA, "census-coverage.csv")
    keep = []
    if os.path.exists(out):
        keep = [r for r in csv.DictReader(open(out)) if r.get("weekend_of") != weekend_of]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(keep + rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
