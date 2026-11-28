#!/usr/bin/env python3
"""Backtest chain_forecast.py: the weekend forecast with AMC left out.

For every graded opening since the census started, the forecast is rebuilt at
six points of the weekend by hiding what was not known yet:

    previews-reported   Thursday previews reported, nothing else
    friday-seats        + the chains' Friday seat counts (Friday night)
    friday-reported     + Friday's gross (Saturday morning)
    saturday-seats      + Saturday seat counts (Saturday night)
    saturday-reported   + Saturday's gross (Sunday morning)
    sunday-seats        + Sunday seat counts (Sunday night)

Chain shares come from the OTHER weekends (--prior: earlier weekends only, as
live). AMC is never in the pool. Beside each stage: the live headline logged
at the same stage and the market's implied figure in that row, and the best
log-weight between the forecast and the market on films that have both.

    python3 scripts/chain_forecast_backtest.py [--since 2026-09-25] [--until 2026-11-20]
                                               [--prior] [--films] [--snapshots market.csv]
Read-only.
"""
import argparse
import csv
import json
import math
import os
import pickle
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chain_census as CC  # noqa: E402
import chain_forecast as CF  # noqa: E402
import chain_pace  # noqa: E402
import chain_presales  # noqa: E402
import holdover  # noqa: E402

STATES = (  # name, reported days, counted days
    ("previews-reported", ("Thursday",), ("Thursday",)),
    ("friday-seats", ("Thursday",), ("Thursday", "Friday")),
    ("friday-reported", ("Thursday", "Friday"), ("Thursday", "Friday")),
    ("saturday-seats", ("Thursday", "Friday"), ("Thursday", "Friday", "Saturday")),
    ("saturday-reported", ("Thursday", "Friday", "Saturday"), ("Thursday", "Friday", "Saturday")),
    ("sunday-seats", ("Thursday", "Friday", "Saturday"), CF.DAYS),
)
LIVE_STAGE = {"previews-reported": "after-previews", "friday-seats": "after-previews",
              "friday-reported": "after-friday", "saturday-seats": "after-friday",
              "saturday-reported": "after-saturday", "sunday-seats": "after-saturday"}
SNAPSHOT = {"previews-reported": "fri12", "friday-seats": "fri12", "friday-reported": "sat12",
            "saturday-seats": "sat12", "saturday-reported": "sat12", "sunday-seats": "sat12"}


def _f(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def line(label, rows):
    if not rows:
        return f"{label:42} n= 0"
    pct = [abs(v / t - 1) for v, t in rows]
    return (f"{label:42} n={len(rows):2d}  mean miss {100 * st.mean(pct):5.1f}%  median {100 * st.median(pct):5.1f}%  "
            f"signed {100 * st.mean(v / t - 1 for v, t in rows):+5.1f}%  worst {100 * max(pct):4.0f}%  "
            f"log-sd {st.pstdev([math.log(v / t) for v, t in rows]):.3f}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-09-25")
    ap.add_argument("--until", default="2026-11-20")
    ap.add_argument("--prior", action="store_true", help="shares from earlier weekends only")
    ap.add_argument("--films", action="store_true")
    ap.add_argument("--no-groups", action="store_true", help="all-film day ratios only (no audience type)")
    ap.add_argument("--no-pace", action="store_true", help="leave the pre-sales pace read of Friday out")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a chain_forecast constant for this run, e.g. SATURDAY_CARRY_WEIGHT=0.8")
    ap.add_argument("--snapshots", help="CSV of market snapshots (movie, snapshot, implied_median_m, definition_match)")
    ap.add_argument("--cache", help="directory to keep the per-weekend chain dollars between runs")
    args = ap.parse_args(argv)

    for item in args.set:
        name, value = item.split("=", 1)
        current = getattr(CF, name)
        setattr(CF, name, tuple(v for v in value.split("+") if v) if isinstance(current, tuple)
                else type(current)(value))
    with open(os.path.join(CF.DATA_DIR, "calibration.json")) as fh:
        hist = json.load(fh)["history"]
    midweek = {(e["weekend_of"], CC.movie_key(e["movie"])) for e in hist if e.get("non_preview_thursday")}
    actuals = CC.reported_daily()
    weekends = sorted({w for (w, _mk) in actuals if args.since <= w <= args.until})
    dollars = {}
    for w in weekends:
        path = os.path.join(args.cache, f"dollars-{w}.pkl") if args.cache else None
        if path and os.path.exists(path):
            dollars[w] = pickle.load(open(path, "rb"))
        else:
            dollars[w] = {m: {d: dict(c) for d, c in by.items()} for m, by in CC.chain_day_dollars(w).items()}
            if path:
                os.makedirs(args.cache, exist_ok=True)
                pickle.dump(dollars[w], open(path, "wb"))
    samples = CC.share_samples(weekends, dollars, actuals)
    library = CF.load_library()
    pace_table, openers = chain_pace.load_table(), set(chain_presales.load_actuals())
    metadata = CC.P.load_movie_metadata()

    with open(os.path.join(CF.DATA_DIR, "prediction-log.csv"), newline="") as fh:
        plog = list(csv.DictReader(fh))
    live = defaultdict(dict)
    for r in plog:
        if _f(r.get("headline_mid_m")):
            live[(r["weekend_of"], CC.movie_key(r["movie"]))][r.get("forecast_stage") or ""] = (
                _f(r["headline_mid_m"]), _f(r.get("poly_implied_mid_m")))
    snaps = {}
    if args.snapshots:
        with open(args.snapshots, newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("definition_match") == "True" and _f(r.get("implied_median_m")):
                    snaps[(CC.movie_key(r["movie"]), r["snapshot"])] = _f(r["implied_median_m"])

    res = defaultdict(list)          # label -> [(value, actual)]
    reached = defaultdict(lambda: defaultdict(int))     # state -> evidence stage actually reached
    paced = defaultdict(int)                            # state -> forecasts that had a pace read
    paired = defaultdict(list)       # state -> [(ours, market, actual)]
    per_film = []
    for w in weekends:
        dates = CC.weekend_dates(w)
        shares = CC.fit_shares([s for s in samples if (s[0] < w if args.prior else s[0] != w)])
        for movie, by_date in dollars[w].items():
            mk = CC.movie_key(movie)
            meta = CC.P.movie_mapping_get(metadata, movie, None)
            ratios = CF.shape_ratios(w, library, None if args.no_groups else getattr(meta, "audience_type", None))
            if holdover.is_holdover(movie, w) or (w, mk) in midweek:
                continue
            a = actuals.get((w, mk)) or {}
            if not all(a.get(d) for d in ("Friday", "Saturday", "Sunday")):
                continue
            total = sum(a.get(d) or 0.0 for d in CF.DAYS)
            cells = {dates[d]: c for d, c in by_date.items() if d in dates}
            row = {}
            for name, rep_days, seat_days in STATES:
                pace = None
                if not args.no_pace and "Friday" not in rep_days and a.get("Thursday"):
                    pace = chain_pace.friday_estimate(
                        movie, w, a["Thursday"], pace_table, actuals, openers,
                        exclude_weekends={x for x in weekends if x >= w} if args.prior else {w})
                fc = CF.weekend_forecast({d: a[d] for d in rep_days if d in a},
                                         {d: cells[d] for d in seat_days if d in cells}, shares, ratios,
                                         pace_friday=pace)
                paced[name] += bool(pace)
                if not fc:
                    continue
                res[name].append((fc["mid_m"], total))
                reached[name][fc["stage"]] += 1
                row[name] = (fc["mid_m"], fc["stage"])
                lv = live.get((w, mk), {}).get(LIVE_STAGE[name])
                if lv and lv[0]:
                    res[f"  live headline at {LIVE_STAGE[name]} | {name}"].append((lv[0], total))
                market = snaps.get((mk, SNAPSHOT[name])) if snaps else (lv[1] if lv else None)
                if market:
                    paired[name].append((fc["mid_m"], market, total))
            per_film.append((w, movie, total, row))

    print(f"openings {args.since}..{args.until}, shares from {'earlier' if args.prior else 'the other'} weekends, "
          f"pool {'+'.join(CF.POOL)} (no AMC)\n")
    for name, *_ in STATES:
        print(line(name, res[name]) + "  [" + ", ".join(f"{k} {v}" for k, v in sorted(reached[name].items()))
              + (f"; pace read {paced[name]}" if paced[name] else "") + "]")
        print(line(f"  live headline at {LIVE_STAGE[name]}", res[f"  live headline at {LIVE_STAGE[name]} | {name}"]))
        rows = paired[name]
        if rows:
            print(line("  market, same films", [(m, t) for _o, m, t in rows]))
            best = min((st.mean(abs(math.exp(wt * math.log(o) + (1 - wt) * math.log(m)) / t - 1) for o, m, t in rows), wt)
                       for wt in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0))
            print(f"  {'best weight on ours with the market':40} w={best[1]:.1f}  mean miss {100 * best[0]:5.1f}%  (n={len(rows)})")
    if args.films:
        print()
        for w, movie, total, row in per_film:
            print(f"{w} {movie[:26]:26} {total:7.2f}  " + "  ".join(
                f"{name.split('-')[0][:3]}-{name.split('-')[1][:4]} {100 * (v / total - 1):+4.0f}%" for name, (v, _s) in row.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
