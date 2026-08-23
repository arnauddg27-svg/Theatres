#!/usr/bin/env python3
"""Capture-completeness watchdog: turn "green but empty" into a loud warning.

Every silent-loss incident this month shared one shape — lanes exited 0 while
producing no rows for the current weekend (the Regal/Cinemark lane skipped
GREEN for two days on 2026-08-21; collect-links "clean skips" left state
stale; -X ours discarded whole commits) — and nothing watched OUTPUT VOLUME.
Exit codes lie; row counts do not.

For each lane (AMC seats, AMC snapshots, Fandango/RC snapshots) this compares
the current weekend's per-day-offset row counts against the median of settled
weekends. Any day that should have data by now but sits under
WARN_FRACTION x median gets a ::warning:: line (GitHub Actions surfaces these
on the run page). Informational by design: ALWAYS exits 0 — a watchdog that
can brick finalize would repeat the clean_canonical_data incident.

Run:  python3 scripts/capture_completeness.py [--today YYYY-MM-DD]
"""
import argparse
import csv
import datetime as dt
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

WARN_FRACTION = 0.25       # under a quarter of the historical median -> warn
BASELINE_WEEKENDS = 4      # most recent settled weekends form the baseline
OFFSETS = (-1, 0, 1, 2)    # Thu, Fri, Sat, Sun relative to the opening Friday

FANDANGO_CSV = os.path.join(P.DATA_DIR, "fandango-pre-reservation-snapshots.csv")


def _offset(weekend_of, day):
    try:
        return (dt.date.fromisoformat(day) - dt.date.fromisoformat(weekend_of)).days
    except ValueError:
        return None


def lane_counts(weekend_of):
    """({lane: {offset: rows}}, n_films) for one weekend, archive-aware.

    Row counts scale with how many films a weekend tracks, so comparisons are
    PER FILM: a legit 1-film weekend after 2-film weekends would otherwise
    read as a ~50% capture gap (alarm fatigue), while a real 60% loss on a
    2-film weekend after quiet ones would pass clean.
    """
    films = set()
    out = {"amc_seat": defaultdict(int), "amc_snapshot": defaultdict(int),
           "fandango": defaultdict(int)}
    seat = P.load_seat_data(weekend_of=weekend_of)
    films.update(seat.keys())
    for movie_days in seat.values():
        for day, rows in movie_days.items():
            off = _offset(weekend_of, day)
            if off in OFFSETS:
                out["amc_seat"][off] += len(rows)
    snap = P.load_pre_reservation_data(weekend_of=weekend_of)
    films.update(snap.keys())
    for movie_days in snap.values():
        for rows in movie_days.values():
            for r in rows:
                cap = (r.get("snapshot_time") or "")[:10]
                off = _offset(weekend_of, cap)
                if off in OFFSETS:
                    out["amc_snapshot"][off] += 1
    # Archive-tolerant: the Fandango CSV is not rotated today, but the day it
    # is, a bare open() here would silently lose every baseline weekend — the
    # exact archive-blind class from the cross-chain loader incident.
    import glob
    import gzip
    fandango_sources = ([FANDANGO_CSV] if os.path.exists(FANDANGO_CSV) else []) +         sorted(glob.glob(os.path.join(P.DATA_DIR, "fandango-archive", "*.csv.gz")))
    for src in fandango_sources:
        op = gzip.open if src.endswith(".gz") else open
        with op(src, "rt", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("weekend_of") or "") != weekend_of:
                    continue
                cap = (r.get("snapshot_time") or "")[:10]
                off = _offset(weekend_of, cap)
                if off in OFFSETS:
                    films.add(r.get("movie_title", ""))
                    out["fandango"][off] += 1
    films.discard("")
    return out, max(1, len(films))


def settled_weekends(current):
    """Most recent BASELINE_WEEKENDS weekends before `current`, from history."""
    import json
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    wks = sorted({e.get("weekend_of") for e in hist
                  if e.get("weekend_of") and e["weekend_of"] < current})
    return wks[-BASELINE_WEEKENDS:]


def median(xs):
    s = sorted(xs)
    n = len(s)
    return 0 if not n else (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--weekend", default=None)
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.today)

    current = args.weekend or P._current_weekend_friday()
    friday = dt.date.fromisoformat(current)

    base_wks = settled_weekends(current)
    if not base_wks:
        print("no settled baseline weekends; nothing to compare")
        return 0
    baselines, base_films = {}, {}
    for wk in base_wks:
        baselines[wk], base_films[wk] = lane_counts(wk)
    now_counts, now_films = lane_counts(current)

    print(f"capture completeness — weekend {current} vs median of {base_wks}")
    warned = 0
    for lane in ("amc_seat", "amc_snapshot", "fandango"):
        for off in OFFSETS:
            cap_day = friday + dt.timedelta(days=off)
            if cap_day >= today:
                continue          # that day's capture windows haven't finished
            base = median([baselines[wk][lane].get(off, 0) / base_films[wk]
                           for wk in base_wks])
            got = now_counts[lane].get(off, 0) / now_films
            if base <= 0:
                # A lane/day with a zero median is either one that never
                # produces (fine) or one that has been DEAD for every baseline
                # weekend — which would otherwise normalize into permanent
                # silence. Say which, once, instead of skipping mutely.
                if got == 0 and any(
                        sum(baselines[wk][lane].values()) > 0 for wk in base_wks):
                    print(f"  {lane:<13} day {off:+d} ({cap_day}): quiet, and the "
                          f"baseline is also zero — dead-lane normalization risk")
                continue
            status = "ok"
            if got < WARN_FRACTION * base:
                status = "LOW"
                warned += 1
                print(f"::warning::capture gap — {lane} day {off:+d} "
                      f"({cap_day}): {got:.0f} rows/film vs median {base:.0f} "
                      f"({got / base:.0%}); every run may still be green — "
                      f"check the lane's skip messages")
            print(f"  {lane:<13} day {off:+d} ({cap_day}): {got:>8.0f} vs median {base:>7.0f} rows/film  {status}")
    if not warned:
        print("all lanes at or above the completeness floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
