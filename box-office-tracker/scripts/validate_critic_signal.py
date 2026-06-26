#!/usr/bin/env python3
"""Does the RT critic score add predictive value BEYOND the RT audience score the
review factor already uses?

The review factor models the Sunday hold (sunday_share = sunday_m / opening). So
the decisive test is a leave-one-out bake-off predicting sunday_share:

    audience only      vs   audience + critic

If adding critic materially cuts LOO error, fold it in. If it's redundant with
audience (they're correlated), say so. Also tests the audience-critic GAP — a
'critic-proof crowd-pleaser' divergence signal — and reports raw correlations.
Read-only.
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from validate_wiki_signal import pearson, ols, predict_one  # noqa: E402

COMPS = os.path.join(P.DATA_DIR, "historical-comps.csv")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def loo_mae(rows, feat_keys, target="sun_share"):
    errs = []
    for i in range(len(rows)):
        train = [r for j, r in enumerate(rows) if j != i]
        X = [[r[k] for k in feat_keys] for r in train]
        y = [r[target] for r in train]
        b = ols(X, y)
        pred = predict_one(b, [rows[i][k] for k in feat_keys])
        actual = rows[i][target]
        errs.append(abs(pred - actual) / actual * 100.0)
    errs.sort()
    n = len(errs)
    return sum(errs) / n, (errs[n // 2] if n % 2 else (errs[n // 2 - 1] + errs[n // 2]) / 2)


def main():
    rows = []
    for r in csv.DictReader(open(COMPS)):
        aud = _f(r.get("rt_audience_score"))
        crit = _f(r.get("rt_critic_score"))
        opening = _f(r.get("opening_weekend_m"))
        sun = _f(r.get("sunday_m"))
        thu = _f(r.get("thursday_preview_m"))
        if not (aud and crit and opening and opening > 0 and sun and sun > 0):
            continue
        rows.append({
            "movie": r["movie"], "aud": aud, "crit": crit, "gap": aud - crit,
            "open": opening, "sun_share": sun / opening,
            "mult": (opening / thu) if (thu and thu > 0) else None,
        })
    print(f"comps usable (audience + critic + sunday all present): {len(rows)}")
    if len(rows) < 20:
        print("not enough critic data yet"); return

    A = [r["aud"] for r in rows]
    C = [r["crit"] for r in rows]
    S = [r["sun_share"] for r in rows]
    print("\n-- raw correlations vs Sunday share (the review factor's target) --")
    print(f"  audience        vs sunday_share   r = {pearson(A, S):+.3f}")
    print(f"  critic          vs sunday_share   r = {pearson(C, S):+.3f}")
    print(f"  audience-critic vs sunday_share   r = {pearson([r['gap'] for r in rows], S):+.3f}  (crowd-pleaser gap)")
    print(f"  audience        vs critic         r = {pearson(A, C):+.3f}  (how redundant they are)")
    mrows = [r for r in rows if r["mult"]]
    if mrows:
        print(f"  critic          vs Thu->wknd mult r = {pearson([r['crit'] for r in mrows], [r['mult'] for r in mrows]):+.3f}")

    print("\n-- leave-one-out MAE predicting sunday_share --")
    a_mae, a_med = loo_mae(rows, ["aud"])
    ac_mae, ac_med = loo_mae(rows, ["aud", "crit"])
    c_mae, c_med = loo_mae(rows, ["crit"])
    g_mae, g_med = loo_mae(rows, ["aud", "gap"])
    print(f"  audience only        : MAE {a_mae:5.2f}%   median {a_med:5.2f}%")
    print(f"  audience + critic    : MAE {ac_mae:5.2f}%   median {ac_med:5.2f}%")
    print(f"  audience + gap       : MAE {g_mae:5.2f}%   median {g_med:5.2f}%")
    print(f"  critic only          : MAE {c_mae:5.2f}%   median {c_med:5.2f}%")
    delta = a_mae - ac_mae
    print(f"\n  >>> critic adds {delta:+.2f} pts over audience-only "
          f"({'FOLD IT IN' if delta > 0.3 else 'REDUNDANT — keep audience-only'})")


if __name__ == "__main__":
    main()
