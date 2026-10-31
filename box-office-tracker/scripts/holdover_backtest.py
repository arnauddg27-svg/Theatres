#!/usr/bin/env python3
"""Fit + backtest the holdover (2nd/3rd weekend) day shape on The Numbers.

holdover_forecast.py turns a known day of a later weekend into the rest of
that weekend through the film's OWN opening days: weekend-N day d is
    opening day d  x  r  x  u_d
where r is the ratio on the latest known day (weekend-N gross / base gross;
the base is the previous weekend when its dailies exist, else the opening
with Friday excluding previews) and u_d is how much better Saturday / Sunday
hold than that day. The constant-ratio guess (u = 1) runs low: an opening Friday
is front-loaded with fans, a 2nd Friday is not. Before any day is known the
prior is opening weekend x the median drop.

For every film in data/historical-comps.csv (opening weekends 2021-2026) this
fetches the daily table, finds the opening Fri-Sun, weekends 2 and 3, and
scores each estimator for the base -> target pairs 1->2, 1->3 and 2->3 leave-one-film-out on the reported 3-day weekend (what
Polymarket resolves on). The fitted medians go to data/holdover-day-shape.json.

    python3 scripts/holdover_backtest.py --write          # fetch, score, write
    python3 scripts/holdover_backtest.py --cache /tmp/hd.json
"""
import argparse
import csv
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
COMPS_CSV = os.path.join(DATA_DIR, "historical-comps.csv")
OUT_JSON = os.path.join(DATA_DIR, "holdover-day-shape.json")
DAYS = ("Friday", "Saturday", "Sunday")
OPENING_MATCH_TOL = 0.15     # table opening vs the comps file opening


def film_weekends(daily, opening_m=None):
    """{1: {day: gross}, 2: {...}, 3: {...}} from a daily table, opening Friday
    excluding previews; None when the opening can't be found or disagrees with
    the comps file by more than OPENING_MATCH_TOL."""
    if not daily:
        return None
    dates = sorted(daily)
    first = dates[0]
    fri = first + timedelta(days=(4 - first.weekday()) % 7)
    out = {}
    for n in (1, 2, 3):
        f = fri + timedelta(days=7 * (n - 1))
        days = {}
        for i, day in enumerate(DAYS):
            got = daily.get(f + timedelta(days=i))
            if got:
                days[day] = got[1]
        if len(days) == 3:
            out[n] = days
    if 1 not in out:
        return None
    thu = daily.get(fri - timedelta(days=1))
    previews = thu[1] if thu and thu[0] == "P" else 0.0
    out[1]["Friday"] -= previews
    out[1]["previews"] = previews
    total = sum(out[1][d] for d in DAYS) + previews
    if out[1]["Friday"] <= 0 or (opening_m and abs(total / opening_m - 1) > OPENING_MATCH_TOL):
        return None
    return out


def fetch_all(cache_path=None, log=print):
    import import_thenumbers_daily as N
    cache = {}
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)
    with open(COMPS_CSV, newline="") as f:
        comps = list(csv.DictReader(f))
    for r in comps:
        key = f"{r['movie']}|{r['release_year']}"
        if key in cache:
            continue
        try:
            daily = N.fetch_daily_table(r["movie"], int(r["release_year"])) or {}
        except Exception as exc:
            log(f"  {r['movie']}: fetch failed ({type(exc).__name__})")
            daily = {}
        cache[key] = {d.isoformat(): list(v) for d, v in daily.items()}
        time.sleep(0.3)
    if cache_path:
        with open(cache_path, "w") as f:
            json.dump(cache, f)
    films = []
    for r in comps:
        raw = cache.get(f"{r['movie']}|{r['release_year']}") or {}
        daily = {datetime.fromisoformat(d).date(): (v[0], float(v[1])) for d, v in raw.items()}
        try:
            opening_m = float(r.get("opening_weekend_m") or 0) or None
        except ValueError:
            opening_m = None
        w = film_weekends(daily, opening_m)
        if w:
            films.append({"movie": r["movie"], "year": r["release_year"],
                          "genre": r.get("genre", ""), "audience": r.get("audience_type", ""), "w": w})
    return films


def _total(days):
    return sum(days[d] for d in DAYS)


def fit(films, n, b=1):
    """Medians over films with weekends b and n: drop (weekend n / weekend b,
    the opening incl. previews), u_sat / u_sun (day ratio over the Friday
    ratio) and v_sun (Sunday ratio over the Saturday ratio)."""
    drop, u_sat, u_sun, v_sun = [], [], [], []
    for f in films:
        w = f["w"]
        if n not in w or b not in w:
            continue
        o, k = w[b], w[n]
        r = {d: k[d] / o[d] for d in DAYS}
        drop.append(_total(k) / (_total(o) + o.get("previews", 0)))
        u_sat.append(r["Saturday"] / r["Friday"])
        u_sun.append(r["Sunday"] / r["Friday"])
        v_sun.append(r["Sunday"] / r["Saturday"])
    if not drop:
        return None
    return {"n_films": len(drop), "drop": statistics.median(drop),
            "u_saturday": statistics.median(u_sat), "u_sunday": statistics.median(u_sun),
            "v_sunday": statistics.median(v_sun)}


def estimates(o, k, p):
    """{stage: estimate of the weekend-n 3-day} from opening days `o`, the
    actual weekend-n days `k` (only the 'known' ones are used per stage) and
    fitted parameters `p` (None = constant ratio)."""
    out = {"prior": (_total(o) + o.get("previews", 0)) * p["drop"]}
    rf = k["Friday"] / o["Friday"]
    u_sat, u_sun = (p["u_saturday"], p["u_sunday"]) if p.get("shape", True) else (1.0, 1.0)
    out["fri_known"] = k["Friday"] + o["Saturday"] * rf * u_sat + o["Sunday"] * rf * u_sun
    rs = k["Saturday"] / o["Saturday"]
    v = p["v_sunday"] if p.get("shape", True) else 1.0
    out["fri_sat_known"] = k["Friday"] + k["Saturday"] + o["Sunday"] * rs * v
    return out


def _quantile(xs, q):
    xs = sorted(xs)
    pos = q * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def bands(films, n, b=1):
    """{stage: [q10, q90]} of truth / shaped estimate, leave-one-film-out:
    the forecast band is estimate x these."""
    ratios = {}
    for i, f in enumerate(films):
        if n not in f["w"] or b not in f["w"]:
            continue
        p = fit(films[:i] + films[i + 1:], n, b)
        truth = _total(f["w"][n])
        for stage, est in estimates(f["w"][b], f["w"][n], p).items():
            ratios.setdefault(stage, []).append(truth / est)
    return {stage: [round(_quantile(xs, 0.1), 4), round(_quantile(xs, 0.9), 4)]
            for stage, xs in ratios.items()}


def backtest(films, n, b=1):
    """Leave-one-film-out mean |% error| per stage, shaped vs constant ratio."""
    errs = {}
    for i, f in enumerate(films):
        if n not in f["w"] or b not in f["w"]:
            continue
        rest = films[:i] + films[i + 1:]
        p = fit(rest, n, b)
        if not p:
            continue
        truth = _total(f["w"][n])
        for label, params in (("shaped", p), ("constant", dict(p, shape=False))):
            for stage, est in estimates(f["w"][b], f["w"][n], params).items():
                if label == "constant" and stage == "prior":
                    continue
                errs.setdefault(f"{stage}/{label}", []).append(abs(est / truth - 1) * 100)
    return {k: (statistics.mean(v), statistics.median(v), len(v)) for k, v in sorted(errs.items())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", help="JSON cache of fetched daily tables")
    ap.add_argument("--write", action="store_true", help=f"write {os.path.relpath(OUT_JSON)}")
    args = ap.parse_args(argv)
    films = fetch_all(args.cache)
    print(f"holdover backtest: {len(films)} films with a matched opening weekend")
    out = {"fitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source": "scripts/holdover_backtest.py over data/historical-comps.csv (The Numbers dailies)",
           "weekends": {}}
    for b, n in ((1, 2), (1, 3), (2, 3)):
        p = fit(films, n, b)
        if not p:
            continue
        bt = backtest(films, n, b)
        print(f"\nweekend {b} -> {n}: {p['n_films']} films — median drop {p['drop']:.3f}, "
              f"u_sat {p['u_saturday']:.3f}, u_sun {p['u_sunday']:.3f}, v_sun {p['v_sunday']:.3f}")
        for stage, (mean, med, cnt) in bt.items():
            print(f"  {stage:28s} mean |err| {mean:5.1f}%  median {med:5.1f}%  (n={cnt})")
        p["backtest_mean_abs_pct"] = {k: round(v[0], 2) for k, v in bt.items()}
        p["band_q10_q90"] = bands(films, n, b)
        print(f"  80% band (truth / estimate): {p['band_q10_q90']}")
        out["weekends"][f"{b}-{n}"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items()}
    if args.write:
        with open(OUT_JSON, "w") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
        print(f"\nwrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
