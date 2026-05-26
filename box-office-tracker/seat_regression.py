# seat_regression.py
"""Seat + snapshot regression calibration for box-office prediction.

Pure standard library (no numpy/scipy). Replaces the hand-built multiplicative
calibration layer with two coupled, leave-one-movie-out cross-validated ridge
regressions combined by inverse-variance precision weighting. See
docs/superpowers/specs/2026-05-26-seat-snapshot-regression-calibration-design.md
"""
from __future__ import annotations

from math import exp, log, isfinite

OPENING_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
COVERAGE_FLOOR = 0.60          # per-day admissibility for seat rows
MIN_WEEKEND_CV_DAYS = 2        # a movie needs >=2 admissible days for weekend CV
LAMBDA_GRID = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
LEAD_BUCKETS = ("same_day", "next_day", "multi_day", "long_lead")

# t_{0.95, df} (one-tailed 95% => two-sided 90% interval half-width multiplier)
_T95 = {
    1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 7: 1.895,
    8: 1.860, 9: 1.833, 10: 1.812, 12: 1.782, 15: 1.753, 20: 1.725, 30: 1.697,
}


def t_quantile_95(df: int) -> float:
    """Two-sided 90% interval multiplier (t_{0.95,df}); ~1.645 as df->inf."""
    df = int(max(1, df))
    if df in _T95:
        return _T95[df]
    keys = sorted(_T95)
    if df > keys[-1]:
        # Linearly approach the normal quantile 1.645.
        return max(1.645, 1.697 - (df - 30) * 0.0005) if df < 200 else 1.645
    # Interpolate between bracketing table entries.
    lo = max(k for k in keys if k <= df)
    hi = min(k for k in keys if k >= df)
    if lo == hi:
        return _T95[lo]
    frac = (df - lo) / (hi - lo)
    return _T95[lo] + frac * (_T95[hi] - _T95[lo])


def _solve(matrix, vector):
    """Solve A x = b by Gaussian elimination with partial pivoting. Pure Python.

    `matrix` is a list of n row-lists (mutated copy made internally), `vector`
    length n. Returns the solution list, or None if singular.
    """
    n = len(vector)
    A = [row[:] for row in matrix]
    b = vector[:]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(A[r][i]))
        if abs(A[pivot][i]) < 1e-12:
            return None
        if pivot != i:
            A[i], A[pivot] = A[pivot], A[i]
            b[i], b[pivot] = b[pivot], b[i]
        piv = A[i][i]
        for j in range(i, n):
            A[i][j] /= piv
        b[i] /= piv
        for k in range(n):
            if k == i:
                continue
            f = A[k][i]
            if f == 0.0:
                continue
            for j in range(i, n):
                A[k][j] -= f * A[i][j]
            b[k] -= f * b[i]
    return b


def weighted_ridge(X, y, w, prior, penalize, l2):
    """Weighted ridge regression with a per-coefficient prior mean.

    Minimizes  sum_i w_i (y_i - x_i . beta)^2  +  l2 * sum_j penalize_j (beta_j - prior_j)^2

    X: list of feature rows (each length p); y, w: length n; prior, penalize:
    length p (penalize_j in {0,1}; intercept must have penalize=0). Returns beta
    (length p) or None.

    Normal equations:  (X'WX + l2*D) beta = X'Wy + l2*D*prior   where D=diag(penalize)
    """
    n = len(X)
    if n == 0:
        return None
    p = len(X[0])
    A = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    for i in range(n):
        wi = w[i]
        if wi <= 0:
            continue
        xi = X[i]
        yi = y[i]
        for a in range(p):
            rhs[a] += wi * xi[a] * yi
            wa = wi * xi[a]
            for b_ in range(p):
                A[a][b_] += wa * xi[b_]
    for a in range(p):
        if penalize[a]:
            A[a][a] += l2
            rhs[a] += l2 * prior[a]
    return _solve(A, rhs)
