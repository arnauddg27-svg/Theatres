#!/usr/bin/env python3
"""Decisive validation for the Wikipedia anticipation signal.

The model already keys on the Thursday preview gross (the seat signal). Wiki
release-week pageviews are only worth wiring in if they reduce error BEYOND what
Thursday already tells us. So the core test is a leave-one-out bake-off:

    baseline : log(opening) ~ log(thursday_preview)
    +wiki    : log(opening) ~ log(thursday_preview) + log(wiki_views)

If LOO MAE drops materially with wiki added, build a calibrated factor. If not,
wiki is redundant with the Thursday number and stays diagnostic (be honest).

Also reports raw correlations (magnitude, multiple, Sunday legs) for context.
Read-only.
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

COMPS = os.path.join(P.DATA_DIR, "historical-comps.csv")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def ols(X, y):
    """Plain least squares with intercept. X = list of feature-rows."""
    k = len(X[0])
    A = [[1.0] + list(row) for row in X]
    cols = k + 1
    # normal equations (A^T A) b = A^T y via Gaussian elimination
    ata = [[sum(A[r][i] * A[r][j] for r in range(len(A))) for j in range(cols)] for i in range(cols)]
    aty = [sum(A[r][i] * y[r] for r in range(len(A))) for i in range(cols)]
    for i in range(cols):
        p = max(range(i, cols), key=lambda r: abs(ata[r][i]))
        ata[i], ata[p] = ata[p], ata[i]
        aty[i], aty[p] = aty[p], aty[i]
        if abs(ata[i][i]) < 1e-12:
            continue
        for r in range(cols):
            if r == i:
                continue
            f = ata[r][i] / ata[i][i]
            for c in range(cols):
                ata[r][c] -= f * ata[i][c]
            aty[r] -= f * aty[i]
    return [aty[i] / ata[i][i] if abs(ata[i][i]) > 1e-12 else 0.0 for i in range(cols)]


def predict_one(b, row):
    return b[0] + sum(b[i + 1] * row[i] for i in range(len(row)))


def loo_mae(rows, feat_idx):
    """Leave-one-out MAE (in % of actual) for log(opening) ~ features[feat_idx]."""
    errs = []
    for i in range(len(rows)):
        train = [r for j, r in enumerate(rows) if j != i]
        X = [[r[fi] for fi in feat_idx] for r in train]
        y = [r["log_open"] for r in train]
        b = ols(X, y)
        pred_log = predict_one(b, [rows[i][fi] for fi in feat_idx])
        pred = math.exp(pred_log)
        actual = rows[i]["open"]
        errs.append(abs(pred - actual) / actual * 100.0)
    errs.sort()
    n = len(errs)
    mae = sum(errs) / n
    med = errs[n // 2] if n % 2 else (errs[n // 2 - 1] + errs[n // 2]) / 2
    return mae, med


def main():
    rows = []
    for r in csv.DictReader(open(COMPS)):
        wiki = _f(r.get("wiki_release_week_views"))
        thu = _f(r.get("thursday_preview_m"))
        opening = _f(r.get("opening_weekend_m"))
        sun = _f(r.get("sunday_m"))
        thr = _f(r.get("national_theatre_count"))
        if not (wiki and wiki > 0 and thu and thu > 0 and opening and opening > 0):
            continue
        rows.append({
            "movie": r["movie"], "open": opening, "thu": thu, "wiki": wiki,
            "log_open": math.log(opening), "log_thu": math.log(thu),
            "log_wiki": math.log(wiki),
            "multiple": opening / thu,
            "sun_share": (sun / opening) if sun else None,
            "thr": thr,
        })
    print(f"comps usable (wiki+thursday+opening all present): {len(rows)}")
    if len(rows) < 20:
        print("not enough data to validate")
        return

    # ── raw correlations ────────────────────────────────────────────────────
    print("\n-- raw correlations --")
    print(f"  log(wiki) vs log(opening)        r = {pearson([r['log_wiki'] for r in rows], [r['log_open'] for r in rows]):+.3f}")
    print(f"  log(wiki) vs log(thursday)       r = {pearson([r['log_wiki'] for r in rows], [r['log_thu'] for r in rows]):+.3f}  (high => redundant w/ seat signal)")
    mrows = [r for r in rows if r["multiple"]]
    print(f"  log(wiki/thu) vs Thu->wknd mult  r = {pearson([math.log(r['wiki']/r['thu']) for r in mrows], [r['multiple'] for r in mrows]):+.3f}")
    srows = [r for r in rows if r["sun_share"]]
    print(f"  log(wiki) vs Sunday share        r = {pearson([r['log_wiki'] for r in srows], [r['sun_share'] for r in srows]):+.3f}  (n={len(srows)})")

    # ── decisive LOO bake-off ───────────────────────────────────────────────
    print("\n-- leave-one-out opening-weekend MAE --")
    b_mae, b_med = loo_mae(rows, ["log_thu"])
    w_mae, w_med = loo_mae(rows, ["log_thu", "log_wiki"])
    o_mae, o_med = loo_mae(rows, ["log_wiki"])
    print(f"  thursday only        : MAE {b_mae:5.1f}%   median {b_med:5.1f}%")
    print(f"  thursday + wiki      : MAE {w_mae:5.1f}%   median {w_med:5.1f}%")
    print(f"  wiki only            : MAE {o_mae:5.1f}%   median {o_med:5.1f}%")
    delta = b_mae - w_mae
    print(f"\n  >>> wiki adds {delta:+.1f} pts of MAE over thursday-only "
          f"({'BUILD the factor' if delta > 1.0 else 'REDUNDANT — keep diagnostic'})")


if __name__ == "__main__":
    main()
