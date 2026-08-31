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
CINEMARK_CSV = os.path.join(P.DATA_DIR, "cinemark-pre-reservation-snapshots.csv")


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
           "fandango": defaultdict(int), "cinemark": defaultdict(int)}
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
    rc_lanes = {
        "fandango": ([FANDANGO_CSV] if os.path.exists(FANDANGO_CSV) else []) +
        sorted(glob.glob(os.path.join(P.DATA_DIR, "fandango-archive", "*.csv.gz"))),
        # Cinemark DIRECT lane (2026-08-31): green-but-empty is the exact
        # failure class this monitor exists for, and this lane now carries
        # all CNMK coverage.
        "cinemark": ([CINEMARK_CSV] if os.path.exists(CINEMARK_CSV) else []) +
        sorted(glob.glob(os.path.join(P.DATA_DIR, "cinemark-archive", "*.csv.gz"))),
    }
    for lane, sources in rc_lanes.items():
        for src in sources:
            op = gzip.open if src.endswith(".gz") else open
            with op(src, "rt", newline="") as f:
                for r in csv.DictReader(f):
                    if (r.get("weekend_of") or "") != weekend_of:
                        continue
                    cap = (r.get("snapshot_time") or "")[:10]
                    off = _offset(weekend_of, cap)
                    if off in OFFSETS:
                        films.add(r.get("movie_title", ""))
                        out[lane][off] += 1
    films.discard("")
    return out, films


def settled_weekends(current, n=BASELINE_WEEKENDS):
    """Most recent `n` settled weekends before `current`, from history."""
    import json
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    wks = sorted({e.get("weekend_of") for e in hist
                  if e.get("weekend_of") and e["weekend_of"] < current})
    return wks[-n:]


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
        counts, film_set = lane_counts(wk)
        baselines[wk], base_films[wk] = counts, max(1, len(film_set))
    now_counts, now_film_set = lane_counts(current)
    now_films = max(1, len(now_film_set))

    print(f"capture completeness — weekend {current} vs median of {base_wks}")
    warned = 0
    for lane in ("amc_seat", "amc_snapshot", "fandango", "cinemark"):
        for off in OFFSETS:
            cap_day = friday + dt.timedelta(days=off)
            if cap_day > today:
                continue
            if cap_day == today:
                # The day is unfinished, but the snapshot lanes' overnight +
                # core slots all end by ~11Z: past 15Z a stone-zero on a
                # producing lane deserves a same-day heads-up instead of
                # tomorrow's post-mortem (the 2026-08-21 Thursday gap was only
                # flagged after the preview window had closed for good).
                # amc_seat is EXCLUDED: its rows for show-day D are only ever
                # written by the NEXT morning's 07Z regular scrape, so a
                # same-day zero is the healthy state, not silence — the first
                # production run (2026-08-23, a healthy Sunday) fired this
                # warning spuriously on every weekend day by construction.
                if lane == "amc_seat":
                    continue
                now_utc = dt.datetime.now(dt.timezone.utc)
                got_today = now_counts[lane].get(off, 0) / now_films
                base_today = median(
                    [baselines[wk][lane].get(off, 0) / base_films[wk]
                     for wk in base_wks])
                if (now_utc.hour >= 15 and got_today == 0 and base_today > 0
                        and str(today) == now_utc.date().isoformat()):
                    print(f"::warning::capture SILENT TODAY — {lane} day "
                          f"{off:+d} ({cap_day}): 0 rows so far vs median "
                          f"{base_today:.0f}/film; the day is not over, but "
                          f"the overnight and core slots have all run")
                continue
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

    # DRIFT GUARD: the trailing-4 median normalizes a gradual bleed — with a
    # steady per-weekend decay r, current/median ~ r^2.5, so the 0.25 floor
    # only trips below r~0.5 and a lane losing 20%/weekend never warns while
    # reaching ~10% volume in 10 weeks. Compare the baseline window against
    # the 4 weekends BEFORE it: a halving between windows is drift, not noise.
    all_wks = settled_weekends(current, n=2 * BASELINE_WEEKENDS)
    if len(all_wks) >= 2 * BASELINE_WEEKENDS:
        prior_wks = all_wks[:BASELINE_WEEKENDS]
        prior, prior_films = {}, {}
        for wk in prior_wks:
            counts, film_set = lane_counts(wk)
            prior[wk], prior_films[wk] = counts, max(1, len(film_set))
        for lane in ("amc_seat", "amc_snapshot", "fandango", "cinemark"):
            recent_med = median([sum(baselines[wk][lane].values()) / base_films[wk]
                                 for wk in base_wks])
            prior_med = median([sum(prior[wk][lane].values()) / prior_films[wk]
                                for wk in prior_wks])
            if prior_med > 0 and recent_med < 0.5 * prior_med:
                print(f"::warning::capture DRIFT — {lane}: trailing-4-weekend "
                      f"median {recent_med:.0f} rows/film is under half the "
                      f"prior window's {prior_med:.0f}; a gradual bleed "
                      f"normalizes into the baseline and never trips the "
                      f"per-day floor")

    # Side data (advisory only): these feed layers that go silently neutral
    # when their files stop accruing, and nothing else counts them.
    try:
        import glob
        poly_rows = 0
        poly_titles = set()
        with open(os.path.join(P.DATA_DIR, "polymarket-markets.csv"), newline="") as f:
            for r in csv.DictReader(f):
                notes = (r.get("notes") or "")
                wk = (notes.split("=", 1)[1].strip()
                      if notes.startswith("weekend_of=") else "")
                if wk == current or (not wk and (r.get("date") or "") >= current):
                    poly_rows += 1
                    if (r.get("movie_title") or "").strip():
                        poly_titles.add(r["movie_title"].strip())
        # FILM-COUNT BLINDNESS GUARD: rows are normalized per OBSERVED film,
        # so a tracked title that produced nothing anywhere (links never
        # materialized, run_async filtered it out, every leg green) simply
        # vanishes from the denominator and every lane reads "ok". From
        # opening Friday onward a market-tracked title must exist in at least
        # one lane.
        if today >= friday:
            observed = {f: True for f in now_film_set}
            ghosts = [t for t in sorted(poly_titles)
                      if not P.movie_mapping_get(observed, t, None)]
            for t in ghosts:
                print(f"::warning::tracked film ABSENT from every capture "
                      f"lane — '{t}' has a {current} market but zero rows in "
                      f"seat, snapshot, and fandango data; per-film "
                      f"normalization cannot see this loss")
        films = sorted(P.load_seat_data(weekend_of=current).keys())
        reviews = P.load_reviews_data(weekend_of=current)
        missing_reviews = [m for m in films if not P.movie_mapping_get(reviews, m, None)]
        print(f"side data: polymarket rows for {current}: {poly_rows}"
              f"{' (NONE — market context will be absent)' if not poly_rows else ''}")
        if films and missing_reviews:
            print(f"side data: no review rows for: {', '.join(missing_reviews)}"
                  f" — the word-of-mouth layer is neutral for these")
    except Exception as e:
        print(f"side-data advisory failed: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
