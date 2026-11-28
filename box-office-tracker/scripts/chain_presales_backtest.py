#!/usr/bin/env python3
"""Backtest chain_presales.py: the pre-release estimate from the other chains'
pre-sales, leave-one-weekend-out, at each cutoff of opening week.

    python3 scripts/chain_presales_backtest.py [--films]

Beside it, on the films that have one: the published trade forecast on file at
the cutoff and a candidate mix. This trains on every OTHER weekend, later ones
included, so it flatters the estimate; `ensemble_forecast.py --report` after
raising the weights grades it on earlier weekends only. Read-only.
"""
import argparse
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chain_presales as CP  # noqa: E402
import ensemble_forecast as E  # noqa: E402


CANDIDATE_WEIGHT = 0.35      # not in use: ensemble_forecast.W_SEATS_WITH_TRADE is 0


def line(label, rows):
    if not rows:
        return f"  {label:34} n= 0"
    pct = [abs(v / a - 1) for v, a in rows]
    return (f"  {label:34} n={len(rows):2d}  mean miss {100 * st.mean(pct):5.1f}%  median {100 * st.median(pct):5.1f}%  "
            f"signed {100 * st.mean(v / a - 1 for v, a in rows):+5.1f}%")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--films", action="store_true")
    args = ap.parse_args(argv)
    table, actuals = CP.load_table(), CP.load_actuals()
    trade_rows, aliases = E.load_trade_rows(), E.load_aliases()
    films = sorted({(r["weekend_of"], r["movie"]) for r in table})
    for cutoff in ("mon", "tue", "wed", "thu"):
        seats, with_trade, detail = [], [], []
        for weekend, movie in films:
            actual = actuals.get((weekend, CP.movie_key(movie)))
            if not actual:
                continue
            est = CP.estimate(movie, weekend, cutoff, table, actuals, exclude_weekends={weekend})
            if not est:
                continue
            seats.append((est["mid_m"], actual))
            as_of = CP.cutoff_time(weekend, cutoff).strftime("%Y-%m-%dT%H:%M:%SZ")
            trade = E.trade_forecast(movie, weekend, as_of, trade_rows, aliases)
            if trade:
                with_trade.append((est["mid_m"], trade["mid_m"], actual))
            detail.append((weekend, movie, actual, est, trade))
        print(f"{cutoff} 16:00 ET")
        print(line("chains' pre-sales alone", seats))
        if with_trade:
            print(line("trade forecast, same films", [(t, a) for _s, t, a in with_trade]))
            w = CANDIDATE_WEIGHT
            print(line(f"trade {1 - w:.2f} + seats {w:.2f} (candidate)",
                       [(math.exp(w * math.log(s) + (1 - w) * math.log(t)), a) for s, t, a in with_trade]))
        if args.films:
            for weekend, movie, actual, est, trade in detail:
                print(f"    {weekend} {movie[:28]:28} actual {actual:7.2f}  seats {est['mid_m']:7.2f} "
                      f"({est['chains']})  trade {trade['mid_m'] if trade else '':>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
