#!/usr/bin/env python3
"""Does pooling every chain's counted seats beat AMC alone? Leave-one-film-out
on census-era weekends with reported dailies.

For each graded film-day: AMC-only census estimate (AMC $ / s_AMC), the
pooled estimate (all present chains), and the model's recorded day forecast
(calibration.json daily_predictions, complete-stage replay). Shares are fit
on the OTHER films (LOO). Prints per film-day and per-day-of-week error
stats. Read-only.

    python3 scripts/chain_census_backtest.py [--since 2026-09-25]
"""
import argparse
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chain_census as CC  # noqa: E402
import predict as P  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-09-25")
    args = ap.parse_args(argv)
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    actuals = CC.reported_daily()
    weekends = sorted({w for (w, _mk) in actuals if w >= args.since})
    actuals = {k: v for k, v in actuals.items() if k[0] in weekends}
    dollars = {w: CC.chain_day_dollars(w) for w in weekends}
    samples = CC.share_samples(weekends, dollars, actuals)
    model_day = {(e["weekend_of"], CC.movie_key(e["movie"])): (e.get("daily_predictions") or {}) for e in hist}

    print(f"{'film':22}{'day':4}{'actual':>7}{'AMC-only':>9}{'pooled':>8}{'model':>7}  {'AMC':>5}{'CNMK':>6}{'ALMO':>6}{'HARK':>6}  pooled chains")
    errs = defaultdict(lambda: defaultdict(list))
    pair = defaultdict(dict)
    for w in weekends:
        dates = CC.weekend_dates(w)
        for movie, by_date in sorted(dollars[w].items()):
            mk = CC.movie_key(movie)
            shares = CC.fit_shares(samples, exclude={(w, mk)})
            for date in sorted(by_date):
                day = dates[date]
                gross = (actuals.get((w, mk)) or {}).get(day)
                if not gross:
                    continue
                est = CC.estimates(by_date[date], day, shares)
                amc = est["chains"].get("AMC")
                amc_only = amc["national_m"] if amc and amc["present"] else None
                pooled = est["pooled_m"]
                model = model_day.get((w, mk), {}).get(day)
                for name, v in (("AMC-only", amc_only), ("pooled", pooled), ("model", model)):
                    if v:
                        errs[name][day].append(math.log(v / gross))
                        errs[name]["all"].append(math.log(v / gross))
                        pair[name][(w, mk, day)] = math.log(v / gross)
                if pooled:
                    pair["pooled_m"][(w, mk, day)] = pooled
                f = lambda v: f"{v:6.2f}" if v else f"{'-':>6}"  # noqa: E731
                ch = est["chains"]
                print(f"{movie[:22]:22}{day[:3]:4}{gross:7.2f}{f(amc_only):>9}{f(pooled):>8}{f(model):>7}  "
                      + "".join(f"{(ch[c]['share'] * 100 if c in ch and ch[c]['present'] else 0):5.1f}%" for c in ("AMC", "CNMK", "ALMO", "HARK"))
                      + f"  {'+'.join(est['pooled_chains'])}")
    print()
    for name in ("AMC-only", "pooled", "model"):
        for day in ("Thursday", "Friday", "Saturday", "Sunday", "all"):
            xs = errs[name].get(day) or []
            if len(xs) < 2:
                continue
            print(f"  {name:9}{day:9} n={len(xs):2d}  MAE {st.mean(abs(math.expm1(x)) for x in xs):5.1%}  "
                  f"median {math.expm1(st.median(xs)):+5.1%}  sd(log) {st.pstdev(xs):.3f}")
    # Paired: same film-days, pooled vs the other two.
    print()
    for other in ("AMC-only", "model"):
        for day in ("Thursday", "Friday", "Saturday", "Sunday", "all"):
            ps = [(a, b) for (k, a) in pair["pooled"].items() for b in [pair[other].get(k)] if b is not None and k[2] == day or (day == "all" and b is not None)]
            if len(ps) < 3:
                continue
            mp = st.mean(abs(math.expm1(a)) for a, _ in ps); mo = st.mean(abs(math.expm1(b)) for _, b in ps)
            wins = sum(1 for a, b in ps if abs(a) < abs(b))
            print(f"  paired {day:9} pooled {mp:5.1%} vs {other:8} {mo:5.1%}  (n={len(ps)}, pooled closer {wins}/{len(ps)})")
    # Weekend totals where every reported day has a pooled estimate.
    print()
    tot = defaultdict(lambda: defaultdict(float))
    for (w, mk, day), v in pair["pooled_m"].items():
        tot[(w, mk)][day] = v
    for (w, mk), days in sorted(tot.items()):
        rep = actuals.get((w, mk)) or {}
        if set(rep) <= set(days) and len(rep) >= 3:
            est = sum(days[d] for d in rep); act = sum(rep.values())
            print(f"  weekend {w} {mk[:20]:20} pooled {est:6.2f} vs actual {act:6.2f} ({est / act - 1:+.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
