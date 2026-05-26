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
