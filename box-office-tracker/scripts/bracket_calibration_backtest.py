#!/usr/bin/env python3
"""Is the bracket model's stated probability honest? Replay every logged
headline that has a Polymarket snapshot through two error fits and score them.

  last-row   bracket_model.fit_stage: sigma from the LAST headline of each
             stage (the fit in use until 2026-11-10).
  every-row  bracket_model.fit_headline: sigma from every graded headline of
             the stage, same source path when enough films have one.

Both fits see only weekends before the one being priced, never the film
itself. Scored three ways:

  1. Bracket probabilities against the bracket that paid: Brier and log loss
     per listed bracket, one probability set per (film, stage, snapshot).
  2. Calibration of the bets the paper trader would place (first headline of a
     stage showing a 10-point edge): stated win probability vs wins.
  3. Flat $1 paper P&L by stage.

Finals come from calibration.json, the newest weekend from the reported
dailies (provisional). Read-only.

    python3 scripts/bracket_calibration_backtest.py
"""
import csv
import math
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bracket_model as B  # noqa: E402
import paper_trade as T  # noqa: E402


def replay(fit_for_row):
    snaps = T.load_snapshots(T.ODDS_LOG)
    with open(T.PREDICTION_LOG, newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r.get("logged_at", ""))
    trades, probs, fits = {}, [], {}
    for r in rows:
        if not r.get("poly_logged_at") or not r.get("poly_event"):
            continue
        mk = B.movie_key(r["movie"])
        snapshot = snaps.get((r["weekend_of"], mk, r["poly_logged_at"], r["poly_event"]))
        stage = r.get("forecast_stage") or ""
        if not snapshot or stage not in T.STAGES:
            continue
        fk = (stage, r.get("source") or "", r["weekend_of"], mk)
        if fk not in fits:
            fits[fk] = fit_for_row(r)
        bias, sigma, n = fits[fk]
        if n < B.MIN_FIT_N:
            continue
        for pr in T.probability_rows(r, snapshot, fits[fk]):
            probs.append((r["weekend_of"], mk, r["poly_event"], stage, pr["bracket"], float(pr["our_prob"])))
        for side, label, srow, p, price, cost, basis, edge in T.candidate_bets(r, snapshot, fits[fk]):
            bet_id = "|".join((r["weekend_of"], mk, r["poly_event"], label, side, stage))
            if bet_id not in trades:
                trades[bet_id] = {"bet_id": bet_id, "weekend_of": r["weekend_of"], "movie": r["movie"],
                                  "event_slug": r["poly_event"], "bracket": label, "side": side,
                                  "forecast_stage": stage, "our_prob": f"{p:.4f}", "cost": f"{cost:.4f}",
                                  "status": "open", "pnl": ""}
    T.settle(trades, snaps=snaps)
    return trades, probs, snaps


def outcomes(snaps):
    finals, prov = T.final_actuals(), T.provisional_actuals()
    labels = defaultdict(set)
    for (w, mk, _, slug), rows in snaps.items():
        labels[(w, mk, slug)].update(r["bracket"] for r in rows)
    out = {}
    for (w, mk, slug), ls in labels.items():
        actual = finals.get((w, mk), prov.get((w, mk)))
        if actual is not None:
            out[(w, mk, slug)] = T.outcome_bracket(actual, ls)
    return out


def score(name, trades, probs, won_bracket):
    print(f"\n=== {name} ===")
    brier, logloss, n = defaultdict(list), defaultdict(list), 0
    for w, mk, slug, stage, bracket, p in probs:
        ob = won_bracket.get((w, mk, slug))
        if ob is None:
            continue
        y = 1.0 if bracket == ob else 0.0
        brier[stage].append((p - y) ** 2)
        q = min(max(p, 1e-6), 1 - 1e-6)
        logloss[stage].append(-(y * math.log(q) + (1 - y) * math.log(1 - q)))
    print(f"  {'stage':15} {'bracket probs':>13} {'Brier':>7} {'log loss':>9}")
    allb, alll = [], []
    for stage in T.STAGES:
        if brier.get(stage):
            allb += brier[stage]
            alll += logloss[stage]
            print(f"  {stage:15} {len(brier[stage]):13d} {statistics.mean(brier[stage]):7.4f} {statistics.mean(logloss[stage]):9.4f}")
    if allb:
        print(f"  {'ALL':15} {len(allb):13d} {statistics.mean(allb):7.4f} {statistics.mean(alll):9.4f}")
    graded = [t for t in trades.values() if t["status"] in ("settled", "provisional")]
    print(f"  bets placed: {len(trades)}, graded: {len(graded)}")
    print(f"  {'stated win prob':16} {'bets':>4} {'stated':>7} {'won':>6} {'net $':>7}")
    for lo, hi in ((0.0, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 0.95), (0.95, 1.01)):
        sub = [t for t in graded if lo <= float(t["our_prob"]) < hi]
        if sub:
            wins = sum(1 for t in sub if float(t["pnl"]) > 0)
            print(f"  {f'{lo:.2f}-{min(hi, 1.0):.2f}':16} {len(sub):4d} {statistics.mean(float(t['our_prob']) for t in sub):7.2f} "
                  f"{wins / len(sub):6.2f} {sum(float(t['pnl']) for t in sub):+7.2f}")
    print(f"  {'stage':15} {'bets':>4} {'wins':>4} {'net $':>7}")
    for stage in T.STAGES:
        sub = [t for t in graded if t["forecast_stage"] == stage]
        if sub:
            print(f"  {stage:15} {len(sub):4d} {sum(1 for t in sub if float(t['pnl']) > 0):4d} {sum(float(t['pnl']) for t in sub):+7.2f}")
    if graded:
        net = sum(float(t["pnl"]) for t in graded)
        print(f"  {'TOTAL':15} {len(graded):4d} {sum(1 for t in graded if float(t['pnl']) > 0):4d} {net:+7.2f}  ROI {net / len(graded):+.0%}")


def main():
    last = B.graded_log_ratios()
    every = B.graded_row_ratios()
    runs = (
        ("last-row fit (fit_stage)", lambda r: B.fit_stage(r["forecast_stage"], r["weekend_of"], r["movie"], ratios=last)),
        ("every-row fit, by source (fit_headline)",
         lambda r: B.fit_headline(r["forecast_stage"], r.get("source"), r["weekend_of"], r["movie"], rows=every)),
        ("every-row fit, stage only",
         lambda r: B.fit_headline(r["forecast_stage"], None, r["weekend_of"], r["movie"], rows=every)),
    )
    for name, fit in runs:
        trades, probs, snaps = replay(fit)
        score(name, trades, probs, outcomes(snaps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
