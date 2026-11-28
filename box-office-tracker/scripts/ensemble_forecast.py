#!/usr/bin/env python3
"""Combined forecast: seat model + Polymarket + published trade forecast.

Runs in finalize after log_polymarket_odds.py. For every prediction-log row it
writes one row to data/ensemble-log.csv with the three inputs and the combined
number. predict.py and its headline are NOT changed — this is a separate,
graded record (`--report`).

Evidence (study of 2026-11-27, all weights are the weight on OUR seat headline,
combined in log space):

* A film WITH a window-compatible Polymarket market. Matched-time average miss,
  2026 films: Thursday 4pm ours 36% / market 17% (n=20); Friday noon 21% / 7.5%
  (n=21); Saturday noon 18.5% / 9% (n=22). Across 101 films 2025-26 the market's
  Thursday-4pm median misses by 14%. Adding our number does not help before
  Saturday; it wins once Saturday is reported (2.5% vs 8% at the last
  after-Saturday call, n=10 — the market's bracket width is the floor there).
* A film with NO market but a published trade forecast (n=23-24 per stage):
  pre-sales ours 34% / trade 23% / 35-65 blend 19%; after-previews 24% / 23% /
  50-50 16-17%; after-Friday ours 11-17%, trade stale.
* Neither: the seat headline stands.

The weights are round numbers on a coarse grid from small samples. Checked by
picking each stage's weight on the OTHER weekends only (24 films): pre-sales
34% → 17-22%, after-previews 24% → 12-15%, after-Friday 10.7% → 8.6% (last
call), after-Saturday unchanged. Re-run `--report` as weekends accumulate
before trusting finer tuning.
"""
import csv
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), "data")
PREDICTION_LOG = os.path.join(DATA_DIR, "prediction-log.csv")
TRADE_CSV = os.path.join(DATA_DIR, "trade-forecasts.csv")
ENSEMBLE_LOG = os.path.join(DATA_DIR, "ensemble-log.csv")
CALIBRATION = os.path.join(DATA_DIR, "calibration.json")
ALIASES = os.path.join(DATA_DIR, "title-aliases.json")

# Weight on OUR headline by forecast stage.
W_MODEL_WITH_MARKET = {
    "presales": 0.0, "after-previews": 0.0, "after-friday": 0.4,
    "after-saturday": 0.85, "after-sunday": 1.0, "complete": 1.0,
}
W_MODEL_WITH_TRADE = {
    "presales": 0.35, "after-previews": 0.5, "after-friday": 0.85,
    "after-saturday": 1.0, "after-sunday": 1.0, "complete": 1.0,
}
TRADE_MAX_AGE_DAYS = 40          # a tracking number older than this is not used
FIELDS = [
    "logged_at", "weekend_of", "movie", "forecast_stage", "model_mid_m",
    "market_mid_m", "trade_mid_m", "trade_published_gmt", "trade_kind",
    "ensemble_mid_m", "ensemble_source", "w_model", "note", "frame",
]


def _f(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out > 0 and math.isfinite(out) else None


def norm_title(title):
    t = (title or "").lower()
    t = re.sub(r"\(\s*(19|20)\d\d\s*\)", " ", t)          # "(2026)"
    t = re.sub(r"\((limited|re-?issue|wide)[^)]*\)", " ", t)
    t = t.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def titles_match(a, b):
    """Exact after normalising, or one is the other's leading words
    ("Ramayana" / "Ramayana: Rise of A Legend", "Ebenezer" / "Ebenezer: A
    Christmas Carol"). Hyphens and spaces are equivalent."""
    na, nb = norm_title(a), norm_title(b)
    if not na or not nb:
        return False
    if na == nb or na.replace(" ", "") == nb.replace(" ", ""):
        return True
    short, long_ = (na, nb) if len(na) <= len(nb) else (nb, na)
    return len(short) >= 5 and long_.startswith(short + " ")


def load_aliases(path=ALIASES):
    try:
        with open(path) as fh:
            raw = json.load(fh)
    except (OSError, ValueError):
        return {}
    out = {}
    for weekend, films in (raw or {}).items():
        if isinstance(films, dict):
            for movie, names in films.items():
                out[(weekend, movie)] = list(names or [])
    return out


def load_trade_rows(path=TRADE_CSV):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _frame_days(label):
    match = re.search(r"\((\d+) days?\)", label or "")
    return int(match.group(1)) if match else None


def _frame_row_value(row, frame_days):
    """$M one trade row carries for an N-day market frame, or None.

    3 days: the Friday-Sunday number of a weekend post. Longer: the row's own
    multi-day number, only when it names the same number of days."""
    if frame_days == 3:
        return _f(row.get("three_day_m")) if row.get("kind") == "weekend" and row.get("is_opener") == "1" else None
    declared = re.search(r"\d+", row.get("multi_day_frame") or "")
    if not declared or int(declared.group(0)) != frame_days:
        return None
    if row.get("kind") == "weekend":
        return _f(row.get("multi_day_m")) if row.get("is_opener") == "1" else None
    if row.get("kind") == "range":
        low, high = _f(row.get("low_m")), _f(row.get("high_m"))
        return math.sqrt(low * high) if low and high else _f(row.get("point_m"))
    return None


def _row_value(row):
    """3-day opening $M carried by one trade row, or None."""
    if (row.get("multi_day_frame") or "") and row.get("kind") == "range":
        return None                              # a 4-/5-day holiday range
    kind = row.get("kind")
    if kind == "weekend":
        if (row.get("multi_day_frame") or "") or _f(row.get("multi_day_m")):
            return None                          # holiday week: the film opened midweek
        return _f(row.get("three_day_m")) if row.get("is_opener") == "1" else None
    point = _f(row.get("point_m"))
    if point:
        return point
    low, high = _f(row.get("low_m")), _f(row.get("high_m"))
    if low and high:
        return math.sqrt(low * high)
    return None


KIND_RANK = {"weekend": 0, "tracking": 1, "range": 2}    # a pinpoint beats a range midpoint


def trade_forecast(movie, weekend_of, as_of_utc, trade_rows, aliases=None, frame_days=None):
    """Newest usable published forecast for the film as of `as_of_utc`
    (ISO, UTC). Posts dated on/after opening Friday 00:00 ET are rejected.
    With frame_days, the number the post gives for that many days."""
    try:
        friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    opening_cut = (friday + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S")   # 00:00 ET ≈ 05:00Z
    earliest = (friday - timedelta(days=TRADE_MAX_AGE_DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
    as_of = (as_of_utc or "")[:19]
    names = [movie] + list((aliases or {}).get((weekend_of, movie), []))
    best = None
    for row in trade_rows:
        published = (row.get("published_gmt") or "")[:19]
        if not published or published > as_of or published >= opening_cut or published < earliest:
            continue
        release = row.get("release_date") or ""
        if release:
            try:
                if abs((datetime.strptime(release, "%Y-%m-%d") - friday).days) > 4:
                    continue
            except ValueError:
                pass
        elif published < (friday - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S"):
            continue                              # an undated weekend post from an earlier week
        if not any(titles_match(name, row.get("film") or "") for name in names):
            continue
        value = _frame_row_value(row, frame_days) if frame_days else _row_value(row)
        if not value:
            continue
        key = (published[:10], -KIND_RANK.get(row.get("kind"), 9), published)
        if best is None or key > best[0]:
            best = (key, {"mid_m": round(value, 3), "published_gmt": published, "kind": row.get("kind") or ""})
    return best[1] if best else None


def combine(model_mid, market_mid, trade, stage):
    """Return (ensemble_mid, source, w_model)."""
    stage = (stage or "").strip() or "presales"
    if market_mid and model_mid:
        w = W_MODEL_WITH_MARKET.get(stage, 0.0)
        mid = math.exp(w * math.log(model_mid) + (1 - w) * math.log(market_mid))
        source = "model" if w >= 1 else ("market" if w <= 0 else "market+model")
        return mid, source, w
    if market_mid:
        return market_mid, "market", 0.0
    if trade and model_mid:
        w = W_MODEL_WITH_TRADE.get(stage, 1.0)
        mid = math.exp(w * math.log(model_mid) + (1 - w) * math.log(trade["mid_m"]))
        return mid, ("model" if w >= 1 else "trade+model"), w
    if trade:
        return trade["mid_m"], "trade", 0.0
    if model_mid:
        return model_mid, "model", 1.0
    return None, "", ""


def ensemble_row(pred, trade_rows, aliases=None):
    model_mid = _f(pred.get("headline_mid_m"))
    compatible = (pred.get("market_window_compatible") or "").strip()
    market_mid = _f(pred.get("poly_implied_mid_m")) if compatible == "1" else None
    note = ""
    frame = (pred.get("market_frame_window") or "").strip()
    frame_mid = _f(pred.get("market_frame_mid_m")) if compatible == "0" and frame else None
    trade = None
    if frame_mid:
        # A film that opened before Friday: predict.py restates the model over
        # the market's own dates (5-day Wednesday-Sunday, or Friday-Sunday), so
        # model, market and trade are compared and combined on those dates.
        model_mid = frame_mid
        market_mid = _f(pred.get("poly_implied_mid_m"))
        trade = trade_forecast(pred.get("movie"), pred.get("weekend_of"), pred.get("logged_at"),
                               trade_rows, aliases, frame_days=_frame_days(frame))
        note = f"all numbers on the market's dates: {frame}"
    else:
        frame = ""
        if _f(pred.get("poly_implied_mid_m")) and compatible != "1":
            note = "holiday frame: market and trade windows differ from the model's; model only"
        if compatible != "0":            # "0" = a midweek/holiday opener: no published number shares the model's window
            trade = trade_forecast(pred.get("movie"), pred.get("weekend_of"), pred.get("logged_at"), trade_rows, aliases)
    mid, source, w = combine(model_mid, market_mid, trade, pred.get("forecast_stage"))
    return {
        "logged_at": pred.get("logged_at"), "weekend_of": pred.get("weekend_of"),
        "movie": pred.get("movie"), "forecast_stage": pred.get("forecast_stage"),
        "model_mid_m": model_mid if model_mid else "",
        "market_mid_m": market_mid if market_mid else "",
        "trade_mid_m": trade["mid_m"] if trade else "",
        "trade_published_gmt": trade["published_gmt"] if trade else "",
        "trade_kind": trade["kind"] if trade else "",
        "ensemble_mid_m": round(mid, 2) if mid else "",
        "ensemble_source": source, "w_model": w, "note": note, "frame": frame,
    }


def load_predictions(path=PREDICTION_LOG):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def build(predictions, trade_rows, aliases=None):
    return [ensemble_row(p, trade_rows, aliases) for p in predictions if _f(p.get("headline_mid_m"))]


def write_log(rows, path=ENSEMBLE_LOG):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_actuals(path=CALIBRATION):
    try:
        with open(path) as fh:
            history = json.load(fh).get("history") or []
    except (OSError, ValueError):
        return {}
    # A film that opened before Friday is left out: its model number covers
    # Thursday-Sunday, the market and trade numbers Friday-Sunday.
    return {(h.get("movie"), h.get("weekend_of")): float(h["actual_total"])
            for h in history if h.get("actual_total") and not h.get("non_preview_thursday")}


def report(rows, actuals, out=sys.stdout):
    """Average miss of the seat headline vs the combined number, first and last
    call of each stage, on graded films."""
    by = {}
    for row in rows:
        key = (row["movie"], row["weekend_of"])
        if key not in actuals or not _f(row.get("ensemble_mid_m")) or not _f(row.get("model_mid_m")):
            continue
        if row.get("frame"):
            continue      # stated on the market's dates; the recorded actual is Thursday-Sunday
        by.setdefault((row.get("forecast_stage") or "", key), []).append(row)
    lines = []
    for stage in ("presales", "after-previews", "after-friday", "after-saturday", "complete"):
        for which in ("first", "last"):
            picked = []
            for (st, key), calls in by.items():
                if st != stage:
                    continue
                calls = sorted(calls, key=lambda r: r["logged_at"])
                picked.append((calls[0] if which == "first" else calls[-1], actuals[key]))
            if not picked:
                continue
            model = [abs(float(r["model_mid_m"]) / a - 1) for r, a in picked]
            ens = [abs(float(r["ensemble_mid_m"]) / a - 1) for r, a in picked]
            better = sum(1 for m, e in zip(model, ens) if e < m - 1e-9)
            worse = sum(1 for m, e in zip(model, ens) if e > m + 1e-9)
            lines.append(f"{stage:15s} {which:5s} n={len(picked):2d}  model {100 * sum(model) / len(model):5.1f}%  "
                         f"combined {100 * sum(ens) / len(ens):5.1f}%  (better {better}, worse {worse})")
    print("\n".join(lines) if lines else "no graded rows", file=out)
    return lines


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    predictions = load_predictions()
    rows = build(predictions, load_trade_rows(), load_aliases())
    if "--report" in argv:
        report(rows, load_actuals())
        return 0
    write_log(rows)
    latest = {}
    for row in rows:
        key = (row["weekend_of"], row["movie"])
        if key not in latest or row["logged_at"] > latest[key]["logged_at"]:
            latest[key] = row
    newest_weekend = max((k[0] for k in latest), default="")
    print(f"combined forecast: {len(rows)} rows → {os.path.relpath(ENSEMBLE_LOG)}")
    for (weekend, movie), row in sorted(latest.items()):
        if weekend != newest_weekend:
            continue
        print(f"  {movie}: combined ${row['ensemble_mid_m']}M ({row['ensemble_source']}; "
              f"model ${row['model_mid_m'] or '—'}M, market ${row['market_mid_m'] or '—'}M, "
              f"trade ${row['trade_mid_m'] or '—'}M){' — ' + row['note'] if row['note'] else ''}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:          # advisory step: never fail finalize
        print(f"⚠️  combined forecast crashed ({type(exc).__name__}: {exc})")
        sys.exit(0)
