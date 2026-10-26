#!/usr/bin/env python3
"""Paper-trade our forecasts against Polymarket and keep score.

For every live forecast that has an odds snapshot beside it (prediction-log
poly_* columns + data/polymarket-odds-log.csv), price each bracket of the
film's main market with bracket_model (lognormal around the headline, fitted
on graded weekends BEFORE this one, excluding the film) and compare with the
market:

    YES on a bracket when our probability - ask  >= EDGE (0.10)
    NO  on a bracket when (1 - our prob) - (1 - bid) >= EDGE

Entry cost is the ask/bid when the snapshot has them, else the mid price
(backfilled snapshots). One $1 bet per (weekend, film, market, bracket, side,
forecast stage) at the first qualifying forecast of that stage; stages are
re-priced independently because the information set changes. Costs below
0.03 or above 0.90 are skipped (illiquid tails, nothing left to earn).

Settlement: the bracket containing calibration.json's actual_total (The
Numbers final 3-day, previews folded in - what the markets resolve on).
Until calibrate grades the weekend, the latest The Numbers dailies in
daily-actual-overrides.csv give a PROVISIONAL outcome, reported separately.
Fees are not modelled (PAPER_TRADE_FEE_BPS, default 0).

Writes data/paper-trades.csv (upsert by bet id), rewrites
data/bracket-probabilities.csv (our probability for every bracket at every
priced forecast, beside the market price) and prints a scorecard.
Runs in finalize after log_polymarket_odds.py; advisory (always exits 0).

    python3 scripts/paper_trade.py            # place + settle + report
    python3 scripts/paper_trade.py --report   # report only
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bracket_model as B  # noqa: E402
from log_polymarket_odds import ODDS_LOG, PREDICTION_LOG, bracket_range  # noqa: E402

DATA_DIR = B.DATA_DIR
TRADES_CSV = os.path.join(DATA_DIR, "paper-trades.csv")
PROBS_CSV = os.path.join(DATA_DIR, "bracket-probabilities.csv")
PROB_FIELDS = ["logged_at", "weekend_of", "movie", "forecast_stage", "headline_mid_m", "event_slug",
               "bracket", "our_prob", "market_price", "edge_yes", "fit_n", "fit_sigma", "fit_bias"]
OVERRIDES_CSV = os.path.join(DATA_DIR, "daily-actual-overrides.csv")
EDGE = float(os.environ.get("PAPER_TRADE_EDGE") or 0.10)
MIN_COST, MAX_COST = 0.03, 0.90
FEE_BPS = float(os.environ.get("PAPER_TRADE_FEE_BPS") or 0)
STAKE = 1.0
FIELDS = ["bet_id", "placed_at", "weekend_of", "movie", "event_slug", "bracket", "side",
          "forecast_stage", "headline_mid_m", "our_prob", "market_price", "cost", "entry_basis",
          "edge", "kelly_frac", "fit_n", "fit_sigma", "status", "actual_m", "outcome_bracket",
          "pnl", "settled_at"]
STAGES = ["presales", "after-previews", "after-friday", "after-saturday", "after-sunday", "complete"]


def _f(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def load_snapshots(path=ODDS_LOG):
    """{(weekend, movie_key, logged_at, slug): [row, ...]}"""
    snaps = defaultdict(list)
    if not os.path.exists(path):
        return snaps
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            snaps[(r["weekend_of"], B.movie_key(r["movie"]), r["logged_at"], r["event_slug"])].append(r)
    return snaps


def load_trades(path=TRADES_CSV):
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as f:
        return {r["bet_id"]: r for r in csv.DictReader(f)}


def save_trades(trades, path=TRADES_CSV):
    rows = sorted(trades.values(), key=lambda r: (r["placed_at"], r["movie"], r["bracket"], r["side"]))
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    os.replace(tmp, path)


def parsed_brackets(snapshot_rows):
    out = []
    for r in snapshot_rows:
        rng = bracket_range(r["bracket"])
        if rng is None:
            continue
        out.append((r["bracket"], rng[0], rng[1], r))
    out.sort(key=lambda b: b[1] if b[1] is not None else -1.0)
    return out


def candidate_bets(pred_row, snapshot_rows, fit):
    """Qualifying (side, bracket row, our_prob, market_price, cost, basis, edge)."""
    mid = _f(pred_row.get("headline_mid_m"), 0) or 0
    bias, sigma, n = fit
    brackets = parsed_brackets(snapshot_rows)
    probs = B.bracket_probabilities(mid, [(b, lo, hi) for b, lo, hi, _ in brackets], bias, sigma)
    out = []
    for label, lo, hi, r in brackets:
        p = probs.get(label)
        price = _f(r.get("yes_price"))
        if p is None or price is None:
            continue
        ask, bid = _f(r.get("best_ask")), _f(r.get("best_bid"))
        yes_cost, yes_basis = (ask, "ask") if ask else (price, "mid")
        no_cost, no_basis = ((1 - bid), "bid") if bid else ((1 - price), "mid")
        for side, our_p, cost, basis in (("YES", p, yes_cost, yes_basis), ("NO", 1 - p, no_cost, no_basis)):
            edge = our_p - cost
            if edge >= EDGE and MIN_COST <= cost <= MAX_COST:
                out.append((side, label, r, our_p, price, cost, basis, edge))
    return out


def kelly(p, cost):
    b = 1.0 / cost - 1.0
    return max(0.0, (p * b - (1 - p)) / b) if b > 0 else 0.0


def place_bets(pred_path=PREDICTION_LOG, odds_path=ODDS_LOG, trades=None, ratios=None):
    trades = {} if trades is None else trades
    snaps = load_snapshots(odds_path)
    ratios = B.graded_log_ratios() if ratios is None else ratios
    if not os.path.exists(pred_path):
        return trades, []
    with open(pred_path, newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r.get("logged_at", ""))
    fits, new, prob_rows = {}, [], []
    for r in rows:
        if not r.get("poly_logged_at") or not r.get("poly_event"):
            continue
        key = (r["weekend_of"], B.movie_key(r["movie"]), r["poly_logged_at"], r["poly_event"])
        snapshot = snaps.get(key)
        stage = r.get("forecast_stage") or ""
        if not snapshot or stage not in STAGES:
            continue
        fk = (stage, r["weekend_of"], key[1])
        if fk not in fits:
            fits[fk] = B.fit_stage(stage, r["weekend_of"], r["movie"], ratios=ratios)
        bias, sigma, n = fits[fk]
        if n < B.MIN_FIT_N:
            continue
        prob_rows.extend(probability_rows(r, snapshot, fits[fk]))
        for side, label, srow, p, price, cost, basis, edge in candidate_bets(r, snapshot, fits[fk]):
            bet_id = "|".join((r["weekend_of"], key[1], r["poly_event"], label, side, stage))
            if bet_id in trades:
                continue
            trades[bet_id] = {
                "bet_id": bet_id, "placed_at": r["logged_at"], "weekend_of": r["weekend_of"],
                "movie": r["movie"], "event_slug": r["poly_event"], "bracket": label, "side": side,
                "forecast_stage": stage, "headline_mid_m": r.get("headline_mid_m", ""),
                "our_prob": f"{p:.4f}", "market_price": f"{price:.4f}", "cost": f"{cost:.4f}",
                "entry_basis": basis, "edge": f"{edge:.4f}", "kelly_frac": f"{kelly(p, cost):.4f}",
                "fit_n": n, "fit_sigma": f"{sigma:.3f}", "status": "open", "actual_m": "",
                "outcome_bracket": "", "pnl": "", "settled_at": "",
            }
            new.append(trades[bet_id])
    return trades, new, prob_rows


def probability_rows(pred_row, snapshot_rows, fit):
    mid = _f(pred_row.get("headline_mid_m"), 0) or 0
    bias, sigma, n = fit
    brackets = parsed_brackets(snapshot_rows)
    probs = B.bracket_probabilities(mid, [(b, lo, hi) for b, lo, hi, _ in brackets], bias, sigma)
    out = []
    for label, lo, hi, r in brackets:
        p, price = probs.get(label), _f(r.get("yes_price"))
        if p is None:
            continue
        out.append({"logged_at": pred_row["logged_at"], "weekend_of": pred_row["weekend_of"],
                    "movie": pred_row["movie"], "forecast_stage": pred_row.get("forecast_stage", ""),
                    "headline_mid_m": pred_row.get("headline_mid_m", ""), "event_slug": pred_row["poly_event"],
                    "bracket": label, "our_prob": f"{p:.4f}",
                    "market_price": f"{price:.4f}" if price is not None else "",
                    "edge_yes": f"{p - price:+.4f}" if price is not None else "",
                    "fit_n": n, "fit_sigma": f"{sigma:.3f}", "fit_bias": f"{bias:+.3f}"})
    return out


def save_probabilities(rows, path=PROBS_CSV):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PROB_FIELDS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def final_actuals(cal_path=B.CALIBRATION_JSON):
    out = {}
    try:
        with open(cal_path) as f:
            for e in json.load(f).get("history", []) or []:
                if e.get("actual_total") and e.get("weekend_of") and e.get("movie"):
                    out[(e["weekend_of"], B.movie_key(e["movie"]))] = float(e["actual_total"])
    except (OSError, ValueError):
        pass
    return out


def provisional_actuals(path=OVERRIDES_CSV):
    """Latest The Numbers daily per (weekend, film, day); a total only when
    Friday, Saturday and Sunday are all present (Thursday added when split)."""
    latest = {}
    try:
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                g = _f(r.get("gross_m"))
                if g is None or (r.get("status") or "reported") != "reported":
                    continue
                k = (r["weekend_of"], B.movie_key(r["movie_title"]), r["day_of_week"])
                if r.get("as_of_date", "") >= latest.get(k, ("", 0))[0]:
                    latest[k] = (r.get("as_of_date", ""), g)
    except OSError:
        return {}
    days = defaultdict(dict)
    for (w, mk, d), (_, g) in latest.items():
        days[(w, mk)][d] = g
    return {k: sum(v.values()) for k, v in days.items() if {"Friday", "Saturday", "Sunday"} <= set(v)}


def outcome_bracket(actual, event_brackets):
    for label in event_brackets:
        rng = bracket_range(label)
        if rng and (rng[0] is None or actual >= rng[0]) and (rng[1] is None or actual < rng[1]):
            return label
    return None


def pnl(side, cost, won):
    fee = FEE_BPS / 10000.0
    if not won:
        return -STAKE
    return STAKE * (1.0 / cost - 1.0) * (1 - fee)


def settle(trades, snaps=None, finals=None, provisionals=None, now=None):
    snaps = load_snapshots() if snaps is None else snaps
    finals = final_actuals() if finals is None else finals
    provisionals = provisional_actuals() if provisionals is None else provisionals
    now = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    labels = defaultdict(set)
    for (w, mk, _, slug), rows in snaps.items():
        labels[(w, mk, slug)].update(r["bracket"] for r in rows)
    changed = 0
    for t in trades.values():
        if t.get("status") == "settled":
            continue
        k = (t["weekend_of"], B.movie_key(t["movie"]))
        actual, status = (finals.get(k), "settled") if k in finals else (provisionals.get(k), "provisional")
        if actual is None:
            continue
        ob = outcome_bracket(actual, labels.get((k[0], k[1], t["event_slug"]), ()))
        if ob is None:
            continue
        won = (ob == t["bracket"]) == (t["side"] == "YES")
        new = {"status": status, "actual_m": f"{actual:.2f}", "outcome_bracket": ob,
               "pnl": f"{pnl(t['side'], float(t['cost']), won):.4f}",
               "settled_at": now if status == "settled" else ""}
        if any(t.get(f) != v for f, v in new.items()):
            t.update(new)
            changed += 1
    return changed


def report(trades, new=()):
    lines = []
    if new:
        lines.append(f"Paper trades: {len(new)} new bet(s) this run: " + ", ".join(
            f"{t['movie']} {t['side']} {t['bracket']} @{float(t['cost']):.2f} (ours {float(t['our_prob']):.2f}, {t['forecast_stage']})"
            for t in new))
    for label, status in (("SETTLED (final actuals)", "settled"), ("PROVISIONAL (latest dailies)", "provisional")):
        rows = [t for t in trades.values() if t["status"] == status]
        if not rows:
            continue
        lines.append(f"\nPaper trades {label}: {len(rows)} bets, flat ${STAKE:.0f} each")
        lines.append(f"  {'stage':15} {'side':4} {'bets':>4} {'wins':>4} {'net $':>7} {'ROI':>6}")
        for stage in STAGES:
            for side in ("YES", "NO"):
                sub = [t for t in rows if t["forecast_stage"] == stage and t["side"] == side]
                if sub:
                    net = sum(float(t["pnl"]) for t in sub)
                    wins = sum(1 for t in sub if float(t["pnl"]) > 0)
                    lines.append(f"  {stage:15} {side:4} {len(sub):4d} {wins:4d} {net:+7.2f} {net / len(sub):+6.0%}")
        net = sum(float(t["pnl"]) for t in rows)
        lines.append(f"  {'TOTAL':15} {'':4} {len(rows):4d} {sum(1 for t in rows if float(t['pnl']) > 0):4d} {net:+7.2f} {net / len(rows):+6.0%}")
    open_rows = [t for t in trades.values() if t["status"] == "open"]
    lines.append(f"\nPaper trades open (no actuals yet): {len(open_rows)}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true", help="print the scorecard without placing or settling")
    args = ap.parse_args(argv)
    trades = load_trades()
    new = []
    try:
        if not args.report:
            trades, new, prob_rows = place_bets(trades=trades)
            settle(trades)
            save_trades(trades)
            save_probabilities(prob_rows)
    except Exception as exc:  # advisory
        print(f"::warning::paper_trade failed: {type(exc).__name__}: {exc}")
        return 0
    print(report(trades, new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
