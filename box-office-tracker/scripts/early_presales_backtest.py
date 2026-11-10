#!/usr/bin/env python3
"""Early pre-sales backtest: does reading pre-sales more than four days before
a showtime help the presales-stage forecast? (2026-11-10)

predict.SNAPSHOT_MAX_LEAD_MINUTES (96h) drops a show's freshest pre-sale read
when it was taken more than four days before the showtime. Since 2026-09-18
the AMC lane reads opening-weekend shows from Monday on, so on Monday to
Wednesday the freshest Saturday/Sunday reads are mostly beyond that cap.

For every graded opening since FROM, the film is replayed as of noon ET on
Monday, Tuesday, Wednesday and Thursday of its opening week (pre-sale
snapshots captured before the checkpoint, the weekend's frozen leak-free
calibration, no seat days, no reported grosses) once per cap, and the
headline is graded against the actual weekend. The pickup multiplier for
reads beyond 96h comes from the fitted table's gt_96h bucket.

Actuals: calibration.json history plus, for the newest weekend not yet in it,
the reported Thursday-Sunday dailies. Read-only.

    python3 scripts/early_presales_backtest.py [--from 2026-09-18] [--caps 96,168]
"""
import argparse
import collections
import copy
import csv
import json
import math
import os
import statistics
import sys
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import holdover  # noqa: E402
import predict as P  # noqa: E402
from calibration_freeze import load_calibration_freeze  # noqa: E402
from forecast_evaluation import utc_timestamp  # noqa: E402

ET = ZoneInfo("America/New_York")
CHECKPOINTS = (("Mon", -4), ("Tue", -3), ("Wed", -2), ("Thu", -1))


def actuals():
    out = {}
    for e in json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]:
        if e.get("actual_total") and not e.get("data_outage"):
            out[(e["weekend_of"], e["movie"])] = float(e["actual_total"])
    latest = {}
    with open(os.path.join(P.DATA_DIR, "daily-actual-overrides.csv"), newline="") as f:
        for r in csv.DictReader(f):
            k = (r["weekend_of"], r["movie_title"], r["day_of_week"])
            if k not in latest or r["as_of_date"] >= latest[k][0]:
                latest[k] = (r["as_of_date"], float(r["gross_m"]))
    days = collections.defaultdict(dict)
    for (w, m, d), (_, g) in latest.items():
        days[(w, m)][d] = g
    have = {(w, P._movie_lookup_key(m)) for (w, m) in out}
    for (w, m), dd in days.items():
        if (w, P._movie_lookup_key(m)) in have or not {"Friday", "Saturday", "Sunday"} <= set(dd):
            continue
        out[(w, m)] = sum(dd.get(d, 0.0) for d in ("Thursday", "Friday", "Saturday", "Sunday"))
    return out


def calibration_for(weekend):
    try:
        return load_calibration_freeze(P.DATA_DIR, weekend)
    except (OSError, ValueError):
        # No freeze yet (newest weekend): today's calibration holds only
        # earlier weekends, so it is still leak-free for this one.
        cal = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))
        cal["history"] = [e for e in cal["history"] if e.get("weekend_of", "") < weekend]
        return cal


def captured(movie_snaps, cutoff):
    out = {}
    for day, rows in (movie_snaps or {}).items():
        keep = [r for r in rows if (s := utc_timestamp(r.get("snapshot_time"))) and s <= cutoff]
        if keep:
            out[day] = keep
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="since", default="2026-09-18")
    ap.add_argument("--caps", default="96,168")
    args = ap.parse_args(argv)
    caps = [int(c) for c in args.caps.split(",")]
    acts = actuals()
    metadata = P.load_movie_metadata()
    counts = P.load_theatre_counts()
    by_weekend = collections.defaultdict(list)
    for (w, m), a in acts.items():
        if w >= args.since:
            by_weekend[w].append((m, a))
    rows = []
    for w in sorted(by_weekend):
        cal0 = calibration_for(w)
        snaps = P.load_pre_reservation_data(weekend_of=w)
        friday = datetime.strptime(w, "%Y-%m-%d").date()
        for movie, actual in sorted(by_weekend[w]):
            if holdover.is_holdover(movie, w):
                continue
            ms = P.movie_mapping_get(snaps, movie, {})
            if not ms:
                continue
            for label, off in CHECKPOINTS:
                cutoff = datetime.combine(friday + timedelta(days=off), time(12), tzinfo=ET).astimezone(timezone.utc)
                prior_day = (friday + timedelta(days=off - 1)).isoformat()
                sn = captured(ms, cutoff)
                if not sn:
                    continue
                rec = {"weekend": w, "movie": movie, "actual": actual, "checkpoint": label}
                for cap in caps:
                    old = P.SNAPSHOT_MAX_LEAD_MINUTES
                    P.SNAPSHOT_MAX_LEAD_MINUTES = cap * 60
                    try:
                        pred = P.predict_movie(
                            movie, {}, [], copy.deepcopy(cal0),
                            national_theatre_count=P.national_theatre_count_for_movie(movie, counts, metadata=metadata),
                            snapshot_data=sn,
                            social_data=P.load_social_signal_data(weekend_of=w, through_date=prior_day),
                            daily_actual_overrides={},
                            showtime_link_profiles=P.movie_mapping_get(P.load_showtime_link_daypart_profiles(weekend_of=w), movie, {}),
                            cross_chain_data=P.load_cross_chain_occupancy(weekend_of=w, through_date=prior_day),
                        )
                        mid = (pred or {}).get("regression_mid_m")
                        days = sorted((pred or {}).get("snapshot_days") or [])
                    except Exception as exc:
                        mid, days = None, [f"error {type(exc).__name__}: {str(exc)[:60]}"]
                    finally:
                        P.SNAPSHOT_MAX_LEAD_MINUTES = old
                    rec[cap] = (mid, days)
                rows.append(rec)
                print(f"{w} {movie[:24]:24} {label} actual {actual:6.1f} | " + " | ".join(
                    f"{c}h: {('%.1f' % rec[c][0]) if rec[c][0] else '-':>6} ({len(rec[c][1])}d)" for c in caps), flush=True)

    def err(mid, a):
        return (mid / a - 1) * 100 if mid and a else None

    print("\n=== presales headline accuracy by checkpoint and lead cap ===")
    print(f"{'checkpoint':10} {'cap':>5} {'forecasts':>9} {'MAE':>7} {'median':>7} {'signed':>7}   (paired: films with a forecast under every cap)")
    for label, _ in CHECKPOINTS:
        sub = [r for r in rows if r["checkpoint"] == label]
        paired = [r for r in sub if all(r[c][0] for c in caps)]
        for c in caps:
            es = [err(r[c][0], r["actual"]) for r in sub if r[c][0]]
            ps = [err(r[c][0], r["actual"]) for r in paired]
            if es:
                print(f"{label:10} {c:>4}h {len(es):9d} {statistics.mean(abs(e) for e in es):6.1f}% "
                      f"{statistics.median(abs(e) for e in es):6.1f}% {statistics.mean(es):+6.1f}%   "
                      + (f"paired n={len(ps)}: MAE {statistics.mean(abs(e) for e in ps):5.1f}%  median {statistics.median(abs(e) for e in ps):5.1f}%" if ps else ""))
            else:
                print(f"{label:10} {c:>4}h {0:9d}   no forecast (pre-sales do not cover all four days)")
    print("\nRAW " + json.dumps([{**{k: v for k, v in r.items() if not isinstance(k, int)},
                                  **{str(c): r[c] for c in caps}} for r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
