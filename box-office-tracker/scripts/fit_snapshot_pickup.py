#!/usr/bin/env python3
"""Fit the pre-sale pickup curve: final seats sold / reserved at lead.

The snapshot layer projects reserved seats to final attendance with
`predict.snapshot_reservation_multiplier` — a hard-coded table written in May
(<=1h 1.15, <=3h 1.35, <=6h 1.60, <=24h 2.20, <=48h 3.00, >48h 4.00) that
was never fitted. Every archived weekend has matched pairs: a snapshot row
(reserved_seats at minutes_until_showtime) and the post-show seat-count row
for the same showtime (seats_sold). This script sums them per weekend x day
x lead bucket into a cache, fits sum(final)/sum(reserved) per bucket (and per
day when the bucket has enough pairs), and writes the table predict.py reads
(data/snapshot-pickup-table.json via the calibrate step).

    python3 scripts/fit_snapshot_pickup.py --out data/snapshot-pickup-table.json
    python3 scripts/fit_snapshot_pickup.py --cache /tmp/pickup-cache.json --exclude 2026-10-09 --out /tmp/t.json

Leave-one-weekend-out tables for backtests come from `loo_table(cache, weekend)`.
"""
import argparse
import collections
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict as P  # noqa: E402

LEAD_BUCKETS = P.SNAPSHOT_PICKUP_LEAD_BUCKETS
BUCKET_ORDER = [name for _, name in LEAD_BUCKETS]
DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
TABLE = {"le_1h": 1.15, "le_3h": 1.35, "le_6h": 1.60, "le_12h": 2.20,
         "le_24h": 2.20, "le_48h": 3.00, "le_96h": 4.00, "gt_96h": 4.00}
MIN_PAIRS_ALL = 300
MIN_PAIRS_DAY = 1000


def weekend_pairs(weekend_of):
    """Yield (movie, day, lead_min, reserved, final) for one weekend."""
    snaps = P.load_pre_reservation_data(weekend_of=weekend_of)
    seats = P.load_seat_data(weekend_of=weekend_of)
    for movie, by_date in snaps.items():
        seat_by_date = P.movie_mapping_get(seats, movie, None) or {}
        for date_str, rows in by_date.items():
            finals = P._latest_seat_showtime_rows(seat_by_date.get(date_str) or [])
            if not finals:
                continue
            day = P._snapshot_day_name(date_str, rows)
            for row in rows:
                if (row.get("chain") or "").strip().upper() not in ("", "AMC"):
                    continue
                final = finals.get(P._showtime_match_key(row))
                if not final:
                    continue
                lead = P._parse_numeric(row.get("minutes_until_showtime"), default=None)
                reserved = P._parse_numeric(row.get("reserved_seats"), default=None)
                sold = P._parse_numeric(final.get("seats_sold"), default=None)
                if lead is None or lead <= 0 or reserved is None or sold is None:
                    continue
                yield movie, day, float(lead), float(reserved), float(sold)


def build_cache(weekends, existing=None, log=print):
    """{weekend: {"day|bucket": [reserved, final, n]}} — incremental."""
    cache = dict(existing or {})
    for w in weekends:
        if w in cache:
            continue
        sums = collections.defaultdict(lambda: [0.0, 0.0, 0])
        for _movie, day, lead, reserved, sold in weekend_pairs(w):
            cell = sums[f"{day}|{P.snapshot_pickup_lead_bucket(lead)}"]
            cell[0] += reserved
            cell[1] += sold
            cell[2] += 1
        cache[w] = {k: v for k, v in sums.items()}
        log(f"  {w}: {sum(v[2] for v in sums.values())} matched pairs")
    return cache


def fitted_table(cache, exclude=()):
    """{"all": {bucket: ratio}, "by_day": {day: {bucket: ratio}}, "n": ...}."""
    excluded = set(exclude or ())
    agg = collections.defaultdict(lambda: [0.0, 0.0, 0])
    agg_day = collections.defaultdict(lambda: [0.0, 0.0, 0])
    used = []
    for w, cells in cache.items():
        if w in excluded:
            continue
        used.append(w)
        for key, (reserved, final, n) in cells.items():
            day, bucket = key.split("|", 1)
            for store in (agg[bucket], agg_day[(day, bucket)]):
                store[0] += reserved
                store[1] += final
                store[2] += n
    table = {"all": {}, "by_day": {}, "n": {"all": {}, "by_day": {}}, "weekends": sorted(used)}
    for bucket in BUCKET_ORDER:
        reserved, final, n = agg[bucket]
        if n >= MIN_PAIRS_ALL and reserved > 0:
            table["all"][bucket] = round(max(1.0, final / reserved), 4)
            table["n"]["all"][bucket] = n
    for day in DAYS:
        for bucket in BUCKET_ORDER:
            reserved, final, n = agg_day[(day, bucket)]
            if n >= MIN_PAIRS_DAY and reserved > 0:
                table["by_day"].setdefault(day, {})[bucket] = round(max(1.0, final / reserved), 4)
                table["n"]["by_day"].setdefault(day, {})[bucket] = n
    return table


def loo_table(cache, weekend):
    return fitted_table(cache, exclude=(weekend,))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exclude", action="append", default=[], help="weekend(s) to leave out")
    ap.add_argument("--out", help="write the fitted table JSON here")
    ap.add_argument("--cache", help="per-weekend sums cache (read + updated)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    import calibrate
    cal = calibrate.load_calibration()
    weekends = sorted({h["weekend_of"] for h in cal.get("history", []) if h.get("weekend_of")})
    existing = None
    if args.cache and os.path.exists(args.cache):
        with open(args.cache) as f:
            existing = json.load(f)
    log = (lambda *_: None) if args.quiet else (lambda m: print(m, file=sys.stderr))
    cache = build_cache(weekends, existing, log=log)
    if args.cache:
        with open(args.cache, "w") as f:
            json.dump(cache, f)
    table = fitted_table(cache, exclude=args.exclude)

    print(f"pickup curve — {len(table['weekends'])} weekends, final/reserved (sum-based)")
    print(f"{'bucket':8} {'table':>6} {'fitted':>7} {'pairs':>8}  " + "  ".join(f"{d[:3]:>9}" for d in DAYS))
    for bucket in BUCKET_ORDER:
        fitted = table["all"].get(bucket)
        if fitted is None:
            continue
        cells = []
        for day in DAYS:
            v = table["by_day"].get(day, {}).get(bucket)
            cells.append(f"{v:9.2f}" if v is not None else f"{'-':>9}")
        print(f"{bucket:8} {TABLE[bucket]:6.2f} {fitted:7.2f} {table['n']['all'][bucket]:8d}  " + "  ".join(cells))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(table, f, indent=2, sort_keys=True)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
