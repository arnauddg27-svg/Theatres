# Seat + Snapshot Regression Calibration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the box-office model's calibration layer with two coupled, leave-one-movie-out cross-validated ridge regressions (seat-implied→actual and snapshot-implied→actual), combined per-day by inverse-variance precision weighting, summed to a weekend total with snapshot-first missing-day handling and a learned day-share fallback, emitting Student-t calibrated 90% intervals.

**Architecture:** A new self-contained pure-stdlib module `seat_regression.py` holds all regression math, CV, combination, and interval logic. `model_calibration.py` calls its `fit_regression_calibration(history)` to persist a `regression` block into `calibration.json`. `predict.py`'s `days_to_weekend` and `select_regression_prediction` call `predict_weekend(...)` from the same module and the stacked multiplicative layers are removed. An out-of-sample acceptance gate decides whether the full regression, a global-ratio baseline, or identity calibration is active.

**Tech Stack:** Python 3.14, standard library only (`math`, `statistics`, `json`). Tests via `unittest`. No numpy/scipy (not project dependencies).

**Spec:** `docs/superpowers/specs/2026-05-26-seat-snapshot-regression-calibration-design.md`

---

## Conventions for every test in this plan

Each test file starts with this exact preamble (matches `tests/test_prediction_normalization.py`):

```python
import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))
```

Run a single test: `python3 -m unittest tests.test_seat_regression -v`
Run the whole suite: `python3 -m unittest discover -s tests -p "test_*.py" -v`
(The ` 2.py` duplicate files are iCloud artifacts; ignore them — the discover glob `test_*.py` still matches them, so if they error, run targeted modules instead.)

---

## File structure

- **Create `seat_regression.py`** — all regression math, CV, combination, intervals, fit + predict entry points. One cohesive subsystem (~450 lines).
- **Create `tests/test_seat_regression.py`** — unit tests for the module.
- **Modify `model_calibration.py`** — add `fit_regression_calibration` call inside `sanitize_calibration`; deprecate/remove EMA recalibrate functions.
- **Modify `calibrate.py`** — update imports; `auto_calibrate` writes the regression block, stops writing `day_scale_factors`/`overall_scale_factor`/snapshot scale factors; print block.
- **Modify `predict.py`** — `get_day_scale`/`days_to_weekend`/`select_regression_prediction` use the new combiner; remove stacked layers; update imports.
- **Modify `data/calibration.json`** — gains a `regression` block (written by code, not by hand).

---

## Data contract (read once before starting)

Each `history[]` entry in `data/calibration.json` provides, per movie:
- `movie` (str), `weekend_of` (str)
- `raw_daily_predictions`: `{day: seat_implied_gross_m}` — **seat predictor**
- `snapshot_daily_predictions`: `{day: snapshot_implied_gross_m}` — **snapshot predictor** (may be absent/partial)
- `daily_actuals`: `{day: actual_gross_m}` — **target** (may omit days)
- `daily_coverage_ratios`: `{day: 0..1}` — seat coverage
- `snapshot_daily_lead_buckets`: `{day: "same_day"|"next_day"|"multi_day"|"long_lead"}`
- `actual_total` (float) — reported weekend gross

Days are from `("Thursday","Friday","Saturday","Sunday")`. All gross values are in **$M**.

---

## Task 1: Module scaffold + constants

**Files:**
- Create: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_seat_regression.py
import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

import seat_regression as sr


class TestConstants(unittest.TestCase):
    def test_constants_present(self):
        self.assertEqual(sr.COVERAGE_FLOOR, 0.60)
        self.assertEqual(sr.OPENING_DAYS, ("Thursday", "Friday", "Saturday", "Sunday"))
        self.assertEqual(sr.MIN_WEEKEND_CV_DAYS, 2)
        # t_{0.95, df} table for two-sided 90% interval
        self.assertAlmostEqual(sr.t_quantile_95(5), 2.015, places=3)
        self.assertAlmostEqual(sr.t_quantile_95(1), 6.314, places=3)
        self.assertAlmostEqual(sr.t_quantile_95(100), 1.660, places=2)  # ~normal


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'seat_regression'`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): module scaffold + t-quantile table"
```

---

## Task 2: Pure-Python linear solve + weighted ridge

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestRidge(unittest.TestCase):
    def test_solve_identity(self):
        # 2x2 solve: [[2,0],[0,4]] x = [2,8] -> [1,2]
        x = sr._solve([[2.0, 0.0], [0.0, 4.0]], [2.0, 8.0])
        self.assertAlmostEqual(x[0], 1.0, places=9)
        self.assertAlmostEqual(x[1], 2.0, places=9)

    def test_ridge_recovers_line_with_unit_slope_prior(self):
        # y = 0.5 + 1.0*x exactly; intercept unpenalized, slope prior=1.
        # With perfect data and any lambda, slope should stay ~1, intercept ~0.5.
        X = [[1.0, 0.0], [1.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
        y = [0.5, 1.5, 2.5, 3.5]
        w = [1.0, 1.0, 1.0, 1.0]
        beta = sr.weighted_ridge(X, y, w, prior=[0.0, 1.0],
                                 penalize=[0, 1], l2=1.0)
        self.assertAlmostEqual(beta[1], 1.0, places=6)
        self.assertAlmostEqual(beta[0], 0.5, places=6)

    def test_ridge_shrinks_slope_toward_one_when_noisy(self):
        # Slope of raw OLS would be ~2; with strong prior=1 + big lambda it shrinks toward 1.
        X = [[1.0, 0.0], [1.0, 1.0]]
        y = [0.0, 2.0]   # OLS slope = 2
        beta = sr.weighted_ridge(X, y, [1.0, 1.0], prior=[0.0, 1.0],
                                 penalize=[0, 1], l2=100.0)
        self.assertLess(beta[1], 1.5)   # pulled toward prior 1
        self.assertGreater(beta[1], 1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestRidge -v`
Expected: FAIL with `AttributeError: module 'seat_regression' has no attribute '_solve'`

- [ ] **Step 3: Write minimal implementation** (append to `seat_regression.py`)

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestRidge -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): pure-Python solver + prior-aware weighted ridge"
```

---

## Task 3: Training-row extraction + admissibility

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestTrainingRows(unittest.TestCase):
    def _history(self):
        return [
            {  # good movie: 2 admissible seat-days (Thu, Sun), Fri below floor
                "movie": "A", "weekend_of": "2026-01-02", "actual_total": 40.0,
                "raw_daily_predictions": {"Thursday": 5.0, "Friday": 10.0, "Sunday": 8.0},
                "daily_actuals": {"Thursday": 6.0, "Friday": 9.0, "Sunday": 9.0},
                "daily_coverage_ratios": {"Thursday": 1.0, "Friday": 0.40, "Sunday": 0.90},
                "snapshot_daily_predictions": {"Sunday": 7.5},
                "snapshot_daily_lead_buckets": {"Sunday": "same_day"},
            },
            {  # unusable: 1 admissible day only
                "movie": "B", "weekend_of": "2026-01-09", "actual_total": 2.0,
                "raw_daily_predictions": {"Sunday": 2.0},
                "daily_actuals": {"Sunday": 1.5},
                "daily_coverage_ratios": {"Sunday": 0.03},
            },
        ]

    def test_seat_rows_respect_coverage_floor(self):
        rows = sr.build_seat_rows(self._history())
        # A: Thu(1.0) and Sun(0.90) pass; Fri(0.40) excluded. B: Sun(0.03) excluded.
        keys = {(r["movie"], r["day"]) for r in rows}
        self.assertEqual(keys, {("A", "Thursday"), ("A", "Sunday")})

    def test_seat_row_fields_and_weight(self):
        rows = sr.build_seat_rows(self._history())
        thu = next(r for r in rows if r["day"] == "Thursday")
        self.assertAlmostEqual(thu["log_seat"], log(5.0))
        self.assertAlmostEqual(thu["log_actual"], log(6.0))
        self.assertAlmostEqual(thu["coverage"], 1.0)
        self.assertAlmostEqual(thu["weight"], 1.0)   # weight == coverage

    def test_snapshot_rows(self):
        rows = sr.build_snapshot_rows(self._history())
        keys = {(r["movie"], r["day"]) for r in rows}
        self.assertEqual(keys, {("A", "Sunday")})
        r = rows[0]
        self.assertAlmostEqual(r["log_snap"], log(7.5))
        self.assertEqual(r["lead_bucket"], "same_day")

    def test_weekend_cv_movies(self):
        movies = sr.weekend_cv_movies(self._history())
        self.assertEqual(movies, ["A"])   # B has <2 admissible days
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestTrainingRows -v`
Expected: FAIL — `build_seat_rows` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def _f(value):
    try:
        v = float(value)
        return v if isfinite(v) else None
    except (TypeError, ValueError):
        return None


def build_seat_rows(history):
    """Admissible per-day seat training rows (coverage >= COVERAGE_FLOOR)."""
    rows = []
    for e in history or []:
        rdp = e.get("raw_daily_predictions") or e.get("daily_predictions") or {}
        da = e.get("daily_actuals") or {}
        cov = e.get("daily_coverage_ratios") or {}
        for day in OPENING_DAYS:
            seat = _f(rdp.get(day))
            actual = _f(da.get(day))
            c = _f(cov.get(day)) or 0.0
            if not seat or seat <= 0 or not actual or actual <= 0:
                continue
            if c < COVERAGE_FLOOR:
                continue
            rows.append({
                "movie": e.get("movie", ""),
                "day": day,
                "log_seat": log(seat),
                "log_actual": log(actual),
                "coverage": c,
                "weight": c,            # precision proportional to coverage
            })
    return rows


def build_snapshot_rows(history):
    """Admissible per-day snapshot training rows (positive snapshot + lead bucket)."""
    rows = []
    for e in history or []:
        sdp = e.get("snapshot_daily_predictions") or {}
        da = e.get("daily_actuals") or {}
        leads = e.get("snapshot_daily_lead_buckets") or {}
        for day in OPENING_DAYS:
            snap = _f(sdp.get(day))
            actual = _f(da.get(day))
            lead = leads.get(day)
            if not snap or snap <= 0 or not actual or actual <= 0:
                continue
            if lead not in LEAD_BUCKETS:
                lead = "same_day"
            rows.append({
                "movie": e.get("movie", ""),
                "day": day,
                "log_snap": log(snap),
                "log_actual": log(actual),
                "lead_bucket": lead,
                "weight": 1.0,
            })
    return rows


def weekend_cv_movies(history):
    """Movies with >= MIN_WEEKEND_CV_DAYS admissible seat-days (eligible for weekend CV)."""
    rows = build_seat_rows(history)
    counts = {}
    for r in rows:
        counts[r["movie"]] = counts.get(r["movie"], 0) + 1
    return [m for m, n in counts.items() if n >= MIN_WEEKEND_CV_DAYS]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestTrainingRows -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): admissibility + training-row extraction"
```

---

## Task 4: Feature vectors

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestFeatures(unittest.TestCase):
    def test_seat_features(self):
        # [intercept, log_seat, is_thu, is_fri, is_sat, one_minus_cov]; Sunday baseline
        v = sr.seat_features(log_seat=2.0, day="Friday", coverage=0.8)
        self.assertEqual(v, [1.0, 2.0, 0.0, 1.0, 0.0, 0.2])
        v2 = sr.seat_features(log_seat=1.0, day="Sunday", coverage=1.0)
        self.assertEqual(v2, [1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(sr.SEAT_PRIOR, [0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(sr.SEAT_PENALIZE, [0, 1, 1, 1, 1, 1])

    def test_snapshot_features(self):
        # [intercept, log_snap, is_thu, is_fri, is_sat, lead_next, lead_multi, lead_long]
        # same_day is the lead baseline
        v = sr.snapshot_features(log_snap=1.5, day="Thursday", lead_bucket="next_day")
        self.assertEqual(v, [1.0, 1.5, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        v2 = sr.snapshot_features(log_snap=1.5, day="Sunday", lead_bucket="same_day")
        self.assertEqual(v2, [1.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestFeatures -v`
Expected: FAIL — `seat_features` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
SEAT_FEATURES = ("intercept", "log_seat", "is_thu", "is_fri", "is_sat", "one_minus_cov")
SEAT_PRIOR = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]      # slope prior = 1
SEAT_PENALIZE = [0, 1, 1, 1, 1, 1]                # intercept unpenalized

SNAP_FEATURES = ("intercept", "log_snap", "is_thu", "is_fri", "is_sat",
                 "lead_next_day", "lead_multi_day", "lead_long_lead")
SNAP_PRIOR = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
SNAP_PENALIZE = [0, 1, 1, 1, 1, 1, 1, 1]


def seat_features(log_seat, day, coverage):
    return [
        1.0,
        float(log_seat),
        1.0 if day == "Thursday" else 0.0,
        1.0 if day == "Friday" else 0.0,
        1.0 if day == "Saturday" else 0.0,
        1.0 - float(coverage),
    ]


def snapshot_features(log_snap, day, lead_bucket):
    return [
        1.0,
        float(log_snap),
        1.0 if day == "Thursday" else 0.0,
        1.0 if day == "Friday" else 0.0,
        1.0 if day == "Saturday" else 0.0,
        1.0 if lead_bucket == "next_day" else 0.0,
        1.0 if lead_bucket == "multi_day" else 0.0,
        1.0 if lead_bucket == "long_lead" else 0.0,
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestFeatures -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): seat + snapshot feature vectors"
```

---

## Task 5: Fit one regression + predicted log-mean

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestFitOne(unittest.TestCase):
    def test_recovers_planted_relationship(self):
        # actual = exp(0.3) * seat^1.0 exactly, across days -> intercept 0.3, slope 1.
        rows = []
        for day, s in [("Thursday", 2.0), ("Friday", 10.0), ("Saturday", 12.0),
                       ("Sunday", 8.0), ("Friday", 5.0), ("Sunday", 20.0)]:
            rows.append({"day": day, "log_seat": log(s),
                         "log_actual": 0.3 + log(s), "coverage": 1.0, "weight": 1.0})
        coef = sr.fit_seat(rows, l2=0.1)
        # predicted log-mean for a Sunday with log_seat=log(10) ~ 0.3 + log(10)
        pred = sr.predict_log(coef, sr.seat_features(log(10.0), "Sunday", 1.0))
        self.assertAlmostEqual(pred, 0.3 + log(10.0), places=2)

    def test_fit_seat_handles_empty(self):
        self.assertIsNone(sr.fit_seat([], l2=1.0))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestFitOne -v`
Expected: FAIL — `fit_seat` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def predict_log(coef, features):
    """Dot product coef . features (prediction in log space)."""
    return sum(c * f for c, f in zip(coef, features))


def fit_seat(rows, l2):
    """Fit the seat regression; returns coef list or None."""
    if not rows:
        return None
    X = [seat_features(r["log_seat"], r["day"], r["coverage"]) for r in rows]
    y = [r["log_actual"] for r in rows]
    w = [r["weight"] for r in rows]
    return weighted_ridge(X, y, w, SEAT_PRIOR, SEAT_PENALIZE, l2)


def fit_snapshot(rows, l2):
    """Fit the snapshot regression; returns coef list or None."""
    if not rows:
        return None
    X = [snapshot_features(r["log_snap"], r["day"], r["lead_bucket"]) for r in rows]
    y = [r["log_actual"] for r in rows]
    w = [r["weight"] for r in rows]
    return weighted_ridge(X, y, w, SNAP_PRIOR, SNAP_PENALIZE, l2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestFitOne -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): fit_seat / fit_snapshot + log prediction"
```

---

## Task 6: Leave-one-movie-out λ selection + daily residual SD

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestLOO(unittest.TestCase):
    def _rows(self):
        # 3 movies, clean unit-slope relationship with intercept 0.2
        rows = []
        plan = {"A": [("Thursday", 3.0), ("Sunday", 9.0)],
                "B": [("Friday", 8.0), ("Saturday", 11.0)],
                "C": [("Thursday", 2.0), ("Sunday", 7.0)]}
        for movie, days in plan.items():
            for day, s in days:
                rows.append({"movie": movie, "day": day, "log_seat": log(s),
                             "log_actual": 0.2 + log(s), "coverage": 1.0, "weight": 1.0})
        return rows

    def test_loo_returns_lambda_and_resid_sd(self):
        best_l2, resid_sd, n = sr.loo_select(
            self._rows(), sr.fit_seat,
            lambda coef, r: sr.predict_log(coef, sr.seat_features(r["log_seat"], r["day"], r["coverage"])),
        )
        self.assertIn(best_l2, sr.LAMBDA_GRID)
        self.assertLess(resid_sd, 0.05)   # near-perfect data -> tiny residuals
        self.assertEqual(n, 6)

    def test_loo_handles_single_movie(self):
        rows = [r for r in self._rows() if r["movie"] == "A"]
        out = sr.loo_select(rows, sr.fit_seat,
                            lambda coef, r: sr.predict_log(coef, sr.seat_features(r["log_seat"], r["day"], r["coverage"])))
        self.assertIsNotNone(out)   # degrades gracefully, no crash
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestLOO -v`
Expected: FAIL — `loo_select` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def _movies_in(rows):
    seen = []
    for r in rows:
        if r["movie"] not in seen:
            seen.append(r["movie"])
    return seen


def loo_select(rows, fit_fn, pred_row_fn):
    """Leave-one-movie-out CV. Returns (best_l2, daily_resid_sd, n_residuals).

    fit_fn(rows, l2) -> coef ; pred_row_fn(coef, row) -> predicted log_actual.
    Picks the l2 in LAMBDA_GRID minimizing weighted mean squared LOO residual,
    then returns the weighted residual SD at that l2.
    """
    if not rows:
        return None
    movies = _movies_in(rows)
    best = None
    for l2 in LAMBDA_GRID:
        sq = 0.0
        wsum = 0.0
        resids = []
        for m in movies:
            train = [r for r in rows if r["movie"] != m]
            test = [r for r in rows if r["movie"] == m]
            if not train:
                continue
            coef = fit_fn(train, l2)
            if coef is None:
                continue
            for r in test:
                e = r["log_actual"] - pred_row_fn(coef, r)
                w = r.get("weight", 1.0)
                sq += w * e * e
                wsum += w
                resids.append((e, w))
        if wsum <= 0:
            continue
        mse = sq / wsum
        if best is None or mse < best[0]:
            # weighted SD of residuals
            var = sum(w * e * e for e, w in resids) / wsum
            best = (mse, l2, max(1e-6, var) ** 0.5, len(resids))
    if best is None:
        return None
    _, l2, sd, n = best
    return l2, sd, n
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestLOO -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): leave-one-movie-out lambda selection"
```

---

## Task 7: Per-day precision combination

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestCombine(unittest.TestCase):
    def test_inverse_variance_combine(self):
        # two sources: logmean 1.0 (var 0.04) and 2.0 (var 0.01)
        mean, var = sr.combine_sources([(1.0, 0.04), (2.0, 0.01)])
        # precision-weighted: w1=25, w2=100 -> (25*1+100*2)/125 = 1.8 ; var=1/125
        self.assertAlmostEqual(mean, 1.8, places=6)
        self.assertAlmostEqual(var, 1.0 / 125.0, places=6)

    def test_single_source(self):
        self.assertEqual(sr.combine_sources([(1.5, 0.04)]), (1.5, 0.04))

    def test_no_source(self):
        self.assertIsNone(sr.combine_sources([]))

    def test_seat_variance_inflated_by_coverage(self):
        base = 0.09
        # lower coverage -> larger variance
        v_full = sr.inflate_variance(base, coverage=1.0)
        v_partial = sr.inflate_variance(base, coverage=0.6)
        self.assertAlmostEqual(v_full, base, places=9)
        self.assertGreater(v_partial, v_full)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestCombine -v`
Expected: FAIL — `combine_sources` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def combine_sources(items):
    """Inverse-variance combine of (logmean, variance) pairs.

    Returns (combined_logmean, combined_variance) or None if empty.
    """
    items = [(m, v) for m, v in items if v is not None and v > 0]
    if not items:
        return None
    if len(items) == 1:
        return items[0]
    prec = sum(1.0 / v for _, v in items)
    mean = sum(m / v for m, v in items) / prec
    return mean, 1.0 / prec


def inflate_variance(base_var, coverage):
    """Inflate a source's variance when coverage < 1 (sampling argument).

    Var scales ~ 1/coverage: a half-covered day's estimate is ~twice as noisy.
    """
    c = max(0.05, min(1.0, float(coverage)))
    return base_var / c
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestCombine -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): inverse-variance combine + coverage inflation"
```

---

## Task 8: Day-share learning + weekend assembly with missing-day inflation

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestWeekend(unittest.TestCase):
    def test_learn_day_shares_normalized(self):
        hist = [
            {"daily_actuals": {"Thursday": 1.0, "Friday": 3.0, "Saturday": 4.0, "Sunday": 2.0}},
            {"daily_actuals": {"Friday": 3.0, "Saturday": 3.0, "Sunday": 4.0}},
        ]
        shares = sr.learn_day_shares(hist)
        self.assertAlmostEqual(sum(shares.values()), 1.0, places=6)
        for d in sr.OPENING_DAYS:
            self.assertIn(d, shares)
            self.assertGreater(shares[d], 0.0)

    def test_full_weekend_sum(self):
        shares = {"Thursday": 0.1, "Friday": 0.3, "Saturday": 0.35, "Sunday": 0.25}
        # all four days observed -> weekend = plain sum, no inflation
        per_day = {d: (10.0, 0.01) for d in sr.OPENING_DAYS}  # (dollars_m, log_var)
        mid, log_var, obs_share = sr.assemble_weekend(per_day, shares)
        self.assertAlmostEqual(mid, 40.0, places=6)
        self.assertAlmostEqual(obs_share, 1.0, places=6)

    def test_partial_weekend_extrapolates_and_inflates(self):
        shares = {"Thursday": 0.1, "Friday": 0.3, "Saturday": 0.35, "Sunday": 0.25}
        per_day = {"Thursday": (10.0, 0.01)}   # only Thursday in hand (share 0.1)
        mid, log_var, obs_share = sr.assemble_weekend(per_day, shares)
        self.assertAlmostEqual(obs_share, 0.1, places=6)
        self.assertAlmostEqual(mid, 10.0 / 0.1, places=4)   # 100
        # variance inflated ~ 1/obs_share vs a fully-observed equivalent
        _, log_var_full, _ = sr.assemble_weekend({d: (10.0, 0.01) for d in sr.OPENING_DAYS}, shares)
        self.assertGreater(log_var, log_var_full)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestWeekend -v`
Expected: FAIL — `learn_day_shares` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def learn_day_shares(history):
    """Average per-movie normalized daily-actual shares -> Thu/Fri/Sat/Sun weights."""
    acc = {d: 0.0 for d in OPENING_DAYS}
    cnt = {d: 0 for d in OPENING_DAYS}
    for e in history or []:
        da = e.get("daily_actuals") or {}
        vals = {d: _f(da.get(d)) for d in OPENING_DAYS if _f(da.get(d)) and _f(da.get(d)) > 0}
        total = sum(vals.values())
        if total <= 0:
            continue
        for d, v in vals.items():
            acc[d] += v / total
            cnt[d] += 1
    shares = {d: (acc[d] / cnt[d] if cnt[d] else 0.0) for d in OPENING_DAYS}
    tot = sum(shares.values())
    if tot <= 0:
        # uniform fallback
        return {d: 0.25 for d in OPENING_DAYS}
    return {d: shares[d] / tot for d in OPENING_DAYS}


def assemble_weekend(per_day, day_shares):
    """Sum observed per-day predictions to a weekend total; extrapolate missing days.

    per_day: {day: (dollars_m, log_variance)} for days we have a prediction for.
    Returns (weekend_mid_m, weekend_log_variance, observed_share).

    Observed days contribute their dollars directly. Missing days are filled by
    scaling up via observed day-share: weekend = observed_sum / observed_share.
    Weekend log-variance starts from the observed days' precision and is inflated
    by 1/observed_share (each unobserved day adds extrapolation uncertainty).
    """
    if not per_day:
        return 0.0, 1.0, 0.0
    observed_sum = sum(v[0] for v in per_day.values())
    observed_share = sum(day_shares.get(d, 0.0) for d in per_day)
    observed_share = max(1e-3, min(1.0, observed_share))
    weekend_mid = observed_sum / observed_share if observed_share < 0.999 else observed_sum
    # Base log-variance: precision-weighted mean of observed-day log-variances.
    inv = sum(1.0 / max(1e-9, v[1]) for v in per_day.values())
    base_log_var = 1.0 / inv if inv > 0 else 1.0
    log_var = base_log_var / observed_share        # inflate for missing weekend share
    return weekend_mid, log_var, observed_share
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestWeekend -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): day-share learning + weekend assembly"
```

---

## Task 9: Weekend interval (Student-t, empirical scale + bias)

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestInterval(unittest.TestCase):
    def test_interval_multiplicative_t(self):
        # mid 50, weekend resid scale 0.2 log, df 5, full observation, zero bias
        mid, low, high = sr.weekend_interval(50.0, resid_scale=0.2, df=5,
                                             observed_share=1.0, resid_mean=0.0)
        t = sr.t_quantile_95(5)   # 2.015
        self.assertAlmostEqual(mid, 50.0, places=6)
        self.assertAlmostEqual(high, 50.0 * exp(t * 0.2), places=4)
        self.assertAlmostEqual(low, 50.0 * exp(-t * 0.2), places=4)
        self.assertLess(low, mid)
        self.assertGreater(high, mid)

    def test_interval_applies_bias_and_inflation(self):
        # nonzero resid_mean shifts mid; partial observation widens band.
        mid, low, high = sr.weekend_interval(50.0, resid_scale=0.2, df=5,
                                             observed_share=0.5, resid_mean=0.1)
        self.assertAlmostEqual(mid, 50.0 * exp(0.1), places=4)
        full = sr.weekend_interval(50.0, 0.2, 5, 1.0, 0.1)
        self.assertGreater(high - low, full[2] - full[1])   # wider when partial
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestInterval -v`
Expected: FAIL — `weekend_interval` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def weekend_interval(mid_m, resid_scale, df, observed_share, resid_mean=0.0):
    """Calibrated 90% interval (Student-t in log space).

    mid_m: summed per-day point prediction ($M).
    resid_scale: SD of weekend LOO log-residuals (empirical).
    df: t degrees of freedom (n_cv_movies - 1).
    observed_share: fraction of the weekend actually observed (widens band when <1).
    resid_mean: mean weekend LOO log-residual (bias correction, applied to mid).

    Returns (mid_m, low_m, high_m).
    """
    if mid_m is None or mid_m <= 0:
        return mid_m, mid_m, mid_m
    mid = mid_m * exp(resid_mean)
    share = max(1e-3, min(1.0, observed_share))
    scale = resid_scale / (share ** 0.5)    # inflate for missing weekend share
    half = t_quantile_95(df) * scale
    return mid, mid * exp(-half), mid * exp(half)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestInterval -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): Student-t weekend prediction interval"
```

---

## Task 10: `fit_regression_calibration` — full fit + weekend LOO + gate

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

This is the top-level training entry point. It fits both regressions, learns
day-shares, runs weekend-level LOO over eligible movies (the production assembly
path), computes the empirical weekend residual mean/scale, the 90% hit-rate and
MAE, decides the active tier via the acceptance gate, and returns the
`regression` block dict.

- [ ] **Step 1: Write the failing test**

```python
class TestFitCalibration(unittest.TestCase):
    def test_block_on_real_history(self):
        import json
        from pathlib import Path
        hist = json.loads(Path("data/calibration.json").read_text())["history"]
        block = sr.fit_regression_calibration(hist)
        self.assertEqual(block["version"], 1)
        self.assertIn(block["active_tier"], ("regression", "global_ratio", "identity"))
        self.assertIn("seat", block)
        self.assertEqual(len(block["seat"]["coef"]), len(sr.SEAT_FEATURES))
        self.assertIn("day_shares", block)
        self.assertAlmostEqual(sum(block["day_shares"].values()), 1.0, places=4)
        wk = block["weekend"]
        self.assertGreaterEqual(wk["n_movies"], 5)
        self.assertGreater(wk["resid_scale"], 0.0)
        self.assertGreaterEqual(wk["loo_hit_rate"], 0.0)
        self.assertLessEqual(wk["loo_hit_rate"], 1.0)
        # global-ratio fallback always present
        self.assertIn("global_ratio", block)

    def test_empty_history_identity(self):
        block = sr.fit_regression_calibration([])
        self.assertEqual(block["active_tier"], "identity")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestFitCalibration -v`
Expected: FAIL — `fit_regression_calibration` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
GATE_MIN_HIT_RATE = 0.85
GATE_MAX_MAE_PCT = 20.0


def _global_ratio(seat_rows):
    """1-parameter fallback: weighted-mean log(actual/seat) across seat rows."""
    if not seat_rows:
        return {"log_ratio_mean": 0.0, "resid_scale": 0.35, "df": 1}
    wsum = sum(r["weight"] for r in seat_rows)
    mean = sum(r["weight"] * (r["log_actual"] - r["log_seat"]) for r in seat_rows) / wsum
    var = sum(r["weight"] * ((r["log_actual"] - r["log_seat"]) - mean) ** 2
              for r in seat_rows) / wsum
    return {"log_ratio_mean": mean, "resid_scale": max(0.05, var ** 0.5),
            "df": max(1, len(_movies_in(seat_rows)) - 1)}


def _weekend_loo(history, seat_l2, snap_l2, day_shares):
    """Leave-one-movie-out weekend predictions over eligible movies.

    For each eligible movie, refit both regressions WITHOUT it, predict each of
    its admissible seat-days (+ snapshot days via combine), assemble the weekend
    via the production path, and compare to actual_total. Returns list of
    (movie, pred_m, actual_m, observed_share, log_resid).
    """
    eligible = weekend_cv_movies(history)
    results = []
    for m in eligible:
        train = [e for e in history if e.get("movie") != m]
        seat_coef = fit_seat(build_seat_rows(train), seat_l2)
        snap_coef = fit_snapshot(build_snapshot_rows(train), snap_l2)
        if seat_coef is None:
            continue
        entry = next(e for e in history if e.get("movie") == m)
        actual_total = _f(entry.get("actual_total"))
        if not actual_total or actual_total <= 0:
            continue
        # daily resid SDs of the held-out fit (reuse training rows' spread)
        seat_sd = _resid_sd(build_seat_rows(train), seat_coef, "seat")
        snap_sd = _resid_sd(build_snapshot_rows(train), snap_coef, "snap") if snap_coef else None
        per_day = _predict_entry_days(entry, seat_coef, snap_coef, seat_sd, snap_sd)
        if not per_day:
            continue
        mid, _logvar, obs_share = assemble_weekend(per_day, day_shares)
        if mid <= 0:
            continue
        results.append((m, mid, actual_total, obs_share, log(actual_total) - log(mid)))
    return results


def _resid_sd(rows, coef, kind):
    if not rows or coef is None:
        return 0.35
    sq = 0.0
    wsum = 0.0
    for r in rows:
        if kind == "seat":
            p = predict_log(coef, seat_features(r["log_seat"], r["day"], r["coverage"]))
        else:
            p = predict_log(coef, snapshot_features(r["log_snap"], r["day"], r["lead_bucket"]))
        e = r["log_actual"] - p
        w = r.get("weight", 1.0)
        sq += w * e * e
        wsum += w
    return max(0.05, (sq / wsum) ** 0.5) if wsum else 0.35


def _predict_entry_days(entry, seat_coef, snap_coef, seat_sd, snap_sd):
    """Per-day combined ($M, log_var) for one movie's admissible days."""
    rdp = entry.get("raw_daily_predictions") or entry.get("daily_predictions") or {}
    sdp = entry.get("snapshot_daily_predictions") or {}
    cov = entry.get("daily_coverage_ratios") or {}
    leads = entry.get("snapshot_daily_lead_buckets") or {}
    per_day = {}
    for day in OPENING_DAYS:
        sources = []
        seat = _f(rdp.get(day))
        c = _f(cov.get(day)) or 0.0
        if seat and seat > 0 and c >= COVERAGE_FLOOR and seat_coef is not None:
            lm = predict_log(seat_coef, seat_features(log(seat), day, c))
            sources.append((lm, inflate_variance(seat_sd ** 2, c)))
        snap = _f(sdp.get(day))
        if snap and snap > 0 and snap_coef is not None:
            lead = leads.get(day) if leads.get(day) in LEAD_BUCKETS else "same_day"
            lm = predict_log(snap_coef, snapshot_features(log(snap), day, lead))
            sources.append((lm, (snap_sd or 0.35) ** 2))
        combined = combine_sources(sources)
        if combined is None:
            continue
        logmean, var = combined
        per_day[day] = (exp(logmean + 0.5 * var), var)   # lognormal mean
    return per_day


def fit_regression_calibration(history):
    seat_rows = build_seat_rows(history)
    snap_rows = build_snapshot_rows(history)
    day_shares = learn_day_shares(history)
    block = {
        "version": 1,
        "active_tier": "identity",
        "day_shares": day_shares,
        "trained_on": _movies_in(seat_rows),
        "global_ratio": _global_ratio(seat_rows),
    }
    if not seat_rows:
        block["weekend"] = {"resid_scale": 0.35, "resid_mean": 0.0, "df": 1,
                            "loo_hit_rate": 0.0, "loo_mae_pct": None, "n_movies": 0}
        return block

    seat_l2, seat_sd, _ = loo_select(
        seat_rows, fit_seat,
        lambda coef, r: predict_log(coef, seat_features(r["log_seat"], r["day"], r["coverage"])),
    ) or (1.0, 0.35, 0)
    snap_sel = loo_select(
        snap_rows, fit_snapshot,
        lambda coef, r: predict_log(coef, snapshot_features(r["log_snap"], r["day"], r["lead_bucket"])),
    ) if snap_rows else None
    snap_l2 = snap_sel[0] if snap_sel else 1.0

    seat_coef = fit_seat(seat_rows, seat_l2)
    snap_coef = fit_snapshot(snap_rows, snap_l2) if snap_rows else None
    block["seat"] = {"features": list(SEAT_FEATURES), "coef": seat_coef,
                     "prior": SEAT_PRIOR, "lambda": seat_l2, "daily_resid_sd": seat_sd}
    if snap_coef is not None:
        block["snapshot"] = {"features": list(SNAP_FEATURES), "coef": snap_coef,
                             "prior": SNAP_PRIOR, "lambda": snap_l2,
                             "daily_resid_sd": (snap_sel[1] if snap_sel else 0.35)}
    else:
        block["snapshot"] = None

    loo = _weekend_loo(history, seat_l2, snap_l2, day_shares)
    n = len(loo)
    if n >= 2:
        resids = [r[4] for r in loo]
        rmean = sum(resids) / n
        rscale = max(0.05, (sum((x - rmean) ** 2 for x in resids) / n) ** 0.5)
        df = max(1, n - 1)
        hits = 0
        ae = []
        for _m, pred, actual, obs_share, _lr in loo:
            mid, low, high = weekend_interval(pred, rscale, df, obs_share, rmean)
            if low <= actual <= high:
                hits += 1
            ae.append(abs(mid - actual) / actual)
        hit_rate = hits / n
        mae_pct = 100.0 * sum(ae) / n
        block["weekend"] = {"resid_scale": rscale, "resid_mean": rmean, "df": df,
                            "loo_hit_rate": round(hit_rate, 4),
                            "loo_mae_pct": round(mae_pct, 2), "n_movies": n}
        block["loo_detail"] = [
            {"movie": m, "pred_m": round(p, 2), "actual_m": round(a, 2),
             "observed_share": round(s, 3)} for m, p, a, s, _ in loo
        ]
        # Acceptance gate
        if hit_rate >= GATE_MIN_HIT_RATE and mae_pct <= GATE_MAX_MAE_PCT:
            block["active_tier"] = "regression"
        else:
            block["active_tier"] = "global_ratio"
        block["gate"] = {"min_hit_rate": GATE_MIN_HIT_RATE, "max_mae_pct": GATE_MAX_MAE_PCT,
                         "passed": block["active_tier"] == "regression"}
    else:
        block["weekend"] = {"resid_scale": 0.35, "resid_mean": 0.0, "df": 1,
                            "loo_hit_rate": 0.0, "loo_mae_pct": None, "n_movies": n}
        block["active_tier"] = "global_ratio"
    return block
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression.TestFitCalibration -v`
Expected: PASS. Also run the whole module: `python3 -m unittest tests.test_seat_regression -v`

- [ ] **Step 5: Inspect the real gate result (diagnostic, not a test)**

Run:
```bash
python3 -c "import json,seat_regression as sr; b=sr.fit_regression_calibration(json.load(open('data/calibration.json'))['history']); print('tier',b['active_tier']); print('weekend',b['weekend']); print('seat slope (coef[1])',round(b['seat']['coef'][1],3)); [print(d) for d in b.get('loo_detail',[])]"
```
Expected: prints the active tier, weekend hit-rate/MAE, the learned seat slope (β1 — watch whether it deviates from 1.0, confirming the size bias), and the per-movie LOO table. **Record this output in the commit message.**

- [ ] **Step 6: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): fit_regression_calibration + weekend LOO + acceptance gate"
```

---

## Task 11: `predict_weekend` — production prediction entry point

**Files:**
- Modify: `seat_regression.py`
- Test: `tests/test_seat_regression.py`

- [ ] **Step 1: Write the failing test**

```python
class TestPredictWeekend(unittest.TestCase):
    def _block(self):
        import json
        from pathlib import Path
        hist = json.loads(Path("data/calibration.json").read_text())["history"]
        return sr.fit_regression_calibration(hist)

    def test_predict_weekend_full(self):
        block = self._block()
        # Provide raw seat-implied daily estimates ($M) for all four days.
        daily_seat = {"Thursday": 3.0, "Friday": 12.0, "Saturday": 14.0, "Sunday": 9.0}
        coverage = {d: 1.0 for d in sr.OPENING_DAYS}
        out = sr.predict_weekend(block, daily_seat_m=daily_seat, coverage=coverage,
                                 daily_snapshot_m={}, lead_buckets={})
        self.assertGreater(out["mid_m"], 0.0)
        self.assertLess(out["low_m"], out["mid_m"])
        self.assertGreater(out["high_m"], out["mid_m"])
        self.assertAlmostEqual(out["observed_share"], 1.0, places=3)
        self.assertIn("per_day", out)

    def test_predict_weekend_thursday_only_is_wide(self):
        block = self._block()
        full = sr.predict_weekend(block, {"Thursday": 3.0, "Friday": 12.0,
                                          "Saturday": 14.0, "Sunday": 9.0},
                                  {d: 1.0 for d in sr.OPENING_DAYS}, {}, {})
        thu = sr.predict_weekend(block, {"Thursday": 3.0}, {"Thursday": 1.0}, {}, {})
        full_w = (full["high_m"] - full["low_m"]) / full["mid_m"]
        thu_w = (thu["high_m"] - thu["low_m"]) / thu["mid_m"]
        self.assertGreater(thu_w, full_w)   # honest: Thursday-only much wider
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestPredictWeekend -v`
Expected: FAIL — `predict_weekend` undefined.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def predict_weekend(block, daily_seat_m, coverage, daily_snapshot_m, lead_buckets):
    """Production forecast from a fitted regression block.

    daily_seat_m: {day: raw seat-implied daily gross $M} (observed days).
    coverage:     {day: 0..1}.
    daily_snapshot_m: {day: snapshot-implied daily gross $M} (future or observed).
    lead_buckets: {day: lead bucket str}.

    Returns {mid_m, low_m, high_m, observed_share, per_day, tier}.
    """
    tier = block.get("active_tier", "identity")
    day_shares = block.get("day_shares") or {d: 0.25 for d in OPENING_DAYS}

    if tier == "regression" and block.get("seat", {}).get("coef"):
        seat_coef = block["seat"]["coef"]
        seat_sd = block["seat"].get("daily_resid_sd", 0.3)
        snap = block.get("snapshot")
        snap_coef = snap["coef"] if snap else None
        snap_sd = snap.get("daily_resid_sd", 0.35) if snap else None
        per_day = {}
        for day in OPENING_DAYS:
            sources = []
            s = _f((daily_seat_m or {}).get(day))
            c = _f((coverage or {}).get(day)) or 0.0
            if s and s > 0 and c >= COVERAGE_FLOOR:
                lm = predict_log(seat_coef, seat_features(log(s), day, c))
                sources.append((lm, inflate_variance(seat_sd ** 2, c)))
            sn = _f((daily_snapshot_m or {}).get(day))
            if sn and sn > 0 and snap_coef is not None:
                lead = (lead_buckets or {}).get(day)
                lead = lead if lead in LEAD_BUCKETS else "same_day"
                lm = predict_log(snap_coef, snapshot_features(log(sn), day, lead))
                sources.append((lm, (snap_sd or 0.35) ** 2))
            combined = combine_sources(sources)
            if combined is None:
                continue
            logmean, var = combined
            per_day[day] = (exp(logmean + 0.5 * var), var)
        mid, _logvar, obs_share = assemble_weekend(per_day, day_shares)
        wk = block["weekend"]
        lo_hi = weekend_interval(mid, wk["resid_scale"], wk["df"], obs_share,
                                 wk.get("resid_mean", 0.0))
        return {"mid_m": lo_hi[0], "low_m": lo_hi[1], "high_m": lo_hi[2],
                "observed_share": obs_share, "tier": tier,
                "per_day": {d: round(v[0], 3) for d, v in per_day.items()}}

    # ---- global-ratio / identity fallback ----
    gr = block.get("global_ratio") or {"log_ratio_mean": 0.0, "resid_scale": 0.35, "df": 1}
    ratio = exp(gr["log_ratio_mean"]) if tier == "global_ratio" else 1.0
    per_day = {}
    for day in OPENING_DAYS:
        s = _f((daily_seat_m or {}).get(day))
        if s and s > 0:
            per_day[day] = (s * ratio, gr["resid_scale"] ** 2)
    mid, _lv, obs_share = assemble_weekend(per_day, day_shares)
    lo_hi = weekend_interval(mid, gr["resid_scale"], gr["df"], obs_share, 0.0)
    return {"mid_m": lo_hi[0], "low_m": lo_hi[1], "high_m": lo_hi[2],
            "observed_share": obs_share, "tier": tier,
            "per_day": {d: round(v[0], 3) for d, v in per_day.items()}}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_seat_regression -v`
Expected: PASS (all classes)

- [ ] **Step 5: Commit**

```bash
git add seat_regression.py tests/test_seat_regression.py
git commit -m "feat(seat_regression): predict_weekend production entry point"
```

---

## Task 12: Wire fitting into `model_calibration.py` + `calibrate.py`

**Files:**
- Modify: `model_calibration.py` (function `sanitize_calibration`, ~line 146-189)
- Modify: `calibrate.py` (imports ~line 32-38; `auto_calibrate` factor writes ~line 645-689; print ~line 1023-1024)
- Test: `tests/test_seat_regression.py` (add `TestSanitizeIntegration`)

- [ ] **Step 1: Write the failing test**

```python
class TestSanitizeIntegration(unittest.TestCase):
    def test_sanitize_adds_regression_block(self):
        import json
        from pathlib import Path
        import model_calibration as mc
        cal = json.loads(Path("data/calibration.json").read_text())
        out = mc.sanitize_calibration(
            cal,
            day_weights_default={"Thursday": 0.1, "Friday": 0.3, "Saturday": 0.35, "Sunday": 0.25},
            default_market_share=0.30,
        )
        self.assertIn("regression", out["calibration_factors"])
        self.assertIn(out["calibration_factors"]["regression"]["active_tier"],
                      ("regression", "global_ratio", "identity"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestSanitizeIntegration -v`
Expected: FAIL — `KeyError: 'regression'`.

- [ ] **Step 3: Implement — `model_calibration.py`**

At the top of `model_calibration.py`, add:
```python
import seat_regression
```

In `sanitize_calibration`, replace the per-day scale-factor recompute block (currently the final lines that set `factors["day_scale_factors"] = recalibrate_day_scale_factors(history)`) with:
```python
    # Regression calibration (replaces EMA day_scale_factors / overall_scale_factor).
    factors["regression"] = seat_regression.fit_regression_calibration(history)
    # Remove superseded EMA blocks if present (one-time migration).
    for dead in ("day_scale_factors", "overall_scale_factor",
                 "snapshot_to_day_scale_factors", "snapshot_to_lead_scale_factors"):
        factors.pop(dead, None)
```

- [ ] **Step 4: Implement — `calibrate.py`**

Update imports (lines ~32-38): remove `recalibrate_scale_factor`, `recalibrate_day_scale_factors`, `recalibrate_snapshot_day_scale_factors`, `recalibrate_snapshot_lead_scale_factors` from the `from model_calibration import (...)` block; add `import seat_regression` near the other imports.

In `auto_calibrate` (lines ~645-661), replace the four `factors[...] = recalibrate_*` assignments with:
```python
    factors["regression"] = seat_regression.fit_regression_calibration(cal["history"])
    for dead in ("day_scale_factors", "overall_scale_factor",
                 "snapshot_to_day_scale_factors", "snapshot_to_lead_scale_factors"):
        factors.pop(dead, None)
```
(Leave the `day_weights` recompute at ~669-689 intact — day-shares for missing-day fallback are also learned inside the regression block, but `day_weights` is still consumed elsewhere; the regression block's `day_shares` is authoritative for prediction.)

Update the print block (~1023-1024) from the `Day scales:` line to:
```python
    reg = factors.get("regression", {})
    wk = reg.get("weekend", {})
    print(f"  Calibration tier: {reg.get('active_tier')}")
    print(f"  Weekend LOO: hit-rate={wk.get('loo_hit_rate')} "
          f"MAE%={wk.get('loo_mae_pct')} n={wk.get('n_movies')}")
    if reg.get("seat", {}).get("coef"):
        print(f"  Seat slope (beta1): {round(reg['seat']['coef'][1], 3)}")
```

- [ ] **Step 5: Run test + suite to verify pass**

Run: `python3 -m unittest tests.test_seat_regression.TestSanitizeIntegration -v`
Expected: PASS
Run: `python3 -m unittest tests.test_prediction_normalization -v` (ensure calibrate import still works)
Expected: PASS or only failures tied to removed EMA functions (addressed in Task 14).

- [ ] **Step 6: Commit**

```bash
git add model_calibration.py calibrate.py tests/test_seat_regression.py
git commit -m "feat(calibration): fit regression block in sanitize + calibrate; drop EMA scale factors"
```

---

## Task 13: Rewire `predict.py` to use the regression combiner

**Files:**
- Modify: `predict.py` — imports (~44-50); `days_to_weekend` (4518-4572); `select_regression_prediction` (4145-4332); `get_day_scale` (848-870)
- Test: `tests/test_seat_regression.py` (add `TestPredictIntegration`)

**Context:** `predict_movie` computes `daily_estimates` (raw domestic $ per day) and
`daily_coverage_ratios`, then calls `days_to_weekend`. The snapshot daily estimates
are produced by `build_snapshot_future_layer` into `snapshot_daily_details`. We route
all of these through `seat_regression.predict_weekend`.

- [ ] **Step 1: Write the failing test**

```python
class TestPredictIntegration(unittest.TestCase):
    def test_days_to_weekend_uses_regression(self):
        import json
        from pathlib import Path
        import predict
        cal = json.loads(Path("data/calibration.json").read_text())
        # sanitize to populate the regression block
        cal = predict.sanitize_calibration(
            cal,
            day_weights_default={"Thursday": 0.1, "Friday": 0.3, "Saturday": 0.35, "Sunday": 0.25},
            default_market_share=0.30,
        ) if hasattr(predict, "sanitize_calibration") else cal
        daily_estimates = {  # raw domestic dollars (not $M)
            "Thursday": 3_000_000.0, "Friday": 12_000_000.0,
            "Saturday": 14_000_000.0, "Sunday": 9_000_000.0,
        }
        cov = {d: 1.0 for d in ("Thursday", "Friday", "Saturday", "Sunday")}
        mid, low, high, detail = predict.days_to_weekend(daily_estimates, cal,
                                                         daily_coverage_ratios=cov)
        self.assertGreater(mid, 0)
        self.assertLessEqual(low, mid)
        self.assertGreaterEqual(high, mid)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seat_regression.TestPredictIntegration -v`
Expected: FAIL (current `days_to_weekend` returns the old 4-tuple shape with per-day-scale `calibrated_daily`; the assertion on regression behavior won't match, or signature detail differs).

- [ ] **Step 3: Implement — `predict.py` imports**

In the `from model_calibration import (...)` block (~44-50), remove `recalibrate_scale_factor`, `recalibrate_day_scale_factors`, `recalibrate_snapshot_day_scale_factors`, `recalibrate_snapshot_lead_scale_factors`. Add near the imports:
```python
import seat_regression
```

- [ ] **Step 4: Implement — replace `days_to_weekend`**

Replace the body of `days_to_weekend` (4518-4572) with a regression-driven version that keeps the 4-tuple return contract `(mid, low, high, calibrated_daily)` so callers are unaffected:
```python
def days_to_weekend(daily_estimates, cal, daily_coverage_ratios=None,
                    daily_snapshot_estimates=None, daily_lead_buckets=None):
    """Stage D: regression calibration -> weekend total + 90% interval.

    daily_estimates: {day: raw domestic daily mid in DOLLARS}.
    Returns (mid_dollars, low_dollars, high_dollars, per_day_dict).
    """
    if not daily_estimates:
        return 0, 0, 0, {}
    block = (cal or {}).get("calibration_factors", {}).get("regression")
    if not block:
        block = seat_regression.fit_regression_calibration((cal or {}).get("history", []))
    daily_seat_m = {d: v / 1_000_000.0 for d, v in daily_estimates.items()}
    coverage = daily_coverage_ratios or {d: 1.0 for d in daily_seat_m}
    snap_m = {d: v / 1_000_000.0 for d, v in (daily_snapshot_estimates or {}).items()}
    out = seat_regression.predict_weekend(
        block, daily_seat_m=daily_seat_m, coverage=coverage,
        daily_snapshot_m=snap_m, lead_buckets=daily_lead_buckets or {},
    )
    mid = out["mid_m"] * 1_000_000.0
    low = out["low_m"] * 1_000_000.0
    high = out["high_m"] * 1_000_000.0
    per_day = {d: {"mid": m * 1_000_000.0} for d, m in out["per_day"].items()}
    return mid, low, high, per_day
```

- [ ] **Step 5: Implement — simplify `get_day_scale`**

`get_day_scale` (848-870) is now only referenced by legacy paths. Replace its body with a constant so any remaining caller is neutral:
```python
def get_day_scale(cal, day_name):
    """Deprecated: per-day scaling is now handled by the regression block.
    Returns 1.0 (identity) so any legacy reference is a no-op."""
    return 1.0
```

- [ ] **Step 6: Implement — strip stacked layers in `select_regression_prediction`**

In `select_regression_prediction` (4145-4332), remove the post-hoc multiplicative
adjustments now subsumed by the regression: the `historical_residual_regression`
block (4259-4288), the `social` factor block (4290-4315), and the
`model_component_disagreement` range buffer (4253-4257). Keep the seat/snapshot
source selection and the `regression_*`/`model_forecast_*` field assignments.
Concretely, delete those three blocks and leave `mid/low/high` as produced by the
snapshot-primary / blend logic, which now derives from `days_to_weekend`'s
regression output. After edits, the function must still set:
`regression_mid_m/low_m/high_m`, `regression_source`, `regression_basis`,
`model_forecast_mid_m/low_m/high_m`, and `forecast_feature_importance`.

Set `regression_source = "seat-snapshot-regression"` and
`regression_basis = f"regression calibration (tier={block.get('active_tier')})"`
where `block = cal["calibration_factors"]["regression"]`.

- [ ] **Step 7: Run test + module suite**

Run: `python3 -m unittest tests.test_seat_regression -v`
Expected: PASS
Run: `python3 -m unittest tests.test_prediction_normalization -v`
Expected: PASS (may need updates handled in Task 14)

- [ ] **Step 8: Commit**

```bash
git add predict.py tests/test_seat_regression.py
git commit -m "feat(predict): route days_to_weekend + forecast through regression combiner; remove stacked layers"
```

---

## Task 14: Fix fallout in `record_actual` and existing tests

**Files:**
- Modify: `predict.py` — `record_actual` (5824-5968), remove `recalibrate_*` calls (5933-5951)
- Modify: existing tests that import/assert removed functions: `tests/test_prediction_normalization.py`, `tests/test_strategy_confidence.py` (grep first)

- [ ] **Step 1: Identify breakages**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" 2>/dev/null; grep -rn "recalibrate_scale_factor\|recalibrate_day_scale_factors\|recalibrate_snapshot_day_scale_factors\|recalibrate_snapshot_lead_scale_factors\|day_scale_factors\|overall_scale_factor" predict.py calibrate.py tests/*.py | grep -v " 2.py"
```
Expected: lists `record_actual` (predict.py ~5933-5951) and any tests referencing the removed names. **Read each hit before editing.**

- [ ] **Step 2: Implement — `record_actual`**

Replace the scale-factor recompute block in `record_actual` (5933-5951) with:
```python
    history = cal["history"]
    if history:
        cal["calibration_factors"]["regression"] = (
            seat_regression.fit_regression_calibration(history)
        )
        for dead in ("day_scale_factors", "overall_scale_factor",
                     "snapshot_to_day_scale_factors", "snapshot_to_lead_scale_factors"):
            cal["calibration_factors"].pop(dead, None)
```
Keep the AMC market-share refinement block (5953-5965) and `last_updated` write unchanged.

- [ ] **Step 3: Implement — update existing tests**

For each test hit from Step 1 that imports a removed `recalibrate_*` symbol or asserts `day_scale_factors`/`overall_scale_factor`, update it: drop the removed import, and replace assertions about per-day scale factors with assertions about `calibration_factors["regression"]["active_tier"]` and `["weekend"]["loo_hit_rate"]`. Show the actual edited assertion in the commit. Do **not** weaken a test to pass — if a test encoded real behavior (e.g. partial-week extrapolation), re-express it against `days_to_weekend`'s new 4-tuple (dollars) output.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s tests -p "test_*.py" 2>&1 | tail -30`
(If the ` 2.py` iCloud duplicates raise import errors, run the canonical modules explicitly:
`python3 -m unittest tests.test_prediction_normalization tests.test_strategy_confidence tests.test_seat_regression -v`)
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add predict.py tests/
git commit -m "fix: route record_actual through regression fit; update tests for regression calibration"
```

---

## Task 15: End-to-end calibration run + acceptance report

**Files:**
- Modify: `data/calibration.json` (regenerated by running the calibrator)
- No new code unless the run surfaces a bug.

- [ ] **Step 1: Regenerate the calibration block from real history**

Run:
```bash
python3 -c "
import json, model_calibration as mc
cal = json.load(open('data/calibration.json'))
cal = mc.sanitize_calibration(cal,
    day_weights_default={'Thursday':0.1,'Friday':0.3,'Saturday':0.35,'Sunday':0.25},
    default_market_share=0.30)
json.dump(cal, open('data/calibration.json','w'), indent=2)
r = cal['calibration_factors']['regression']
print('TIER:', r['active_tier'])
print('WEEKEND:', r['weekend'])
print('SEAT beta1 (slope):', round(r['seat']['coef'][1],3))
print('DAY SHARES:', r['day_shares'])
for d in r.get('loo_detail',[]): print(' ', d)
"
```
Expected: prints the tier, weekend hit-rate/MAE/n, the learned slope, day-shares, and the per-movie LOO table.

- [ ] **Step 2: Evaluate the acceptance gate (decision point)**

Compare against the spec gate (§7): hit-rate ≥ 0.85 and MAE ≤ 20%.
- If `active_tier == "regression"`: the gate passed — proceed.
- If `active_tier == "global_ratio"`: the regression did **not** beat the bar out-of-sample. This is the spec-mandated honest outcome. **Stop and report to the user** the LOO table and metrics; do not hand-tune to force a pass. The global-ratio baseline ships in the meantime.

- [ ] **Step 3: Sanity-check a live prediction path**

Run the existing prediction CLI for one weekend of seat data and confirm it produces a finite mid/low/high with the new `regression_source`:
```bash
python3 predict.py 2>&1 | head -40   # or the project's usual predict invocation
```
Expected: a prediction prints with `regression_source = seat-snapshot-regression` and a low < mid < high band noticeably wider than the old ±5%.

- [ ] **Step 4: Full suite green**

Run: `python3 -m unittest tests.test_seat_regression tests.test_prediction_normalization tests.test_strategy_confidence -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add data/calibration.json
git commit -m "data: regenerate calibration with seat+snapshot regression block

LOO weekend hit-rate / MAE / tier recorded in commit body:
<paste the Step 1 output here>"
```

---

## Self-review against the spec

- **§2 scope (calibration layer only):** Tasks 13/14 keep Stage A–C revenue/AMC/domestic plumbing; only `days_to_weekend` + the post-hoc layers change. ✓
- **§2 per-day → weekend, LOO-movie CV:** Tasks 6, 10 (`loo_select`, `_weekend_loo`) group by movie. ✓
- **§3 admissibility (cov ≥ 0.6, weights, ≥2-day gate):** Task 3. ✓
- **§4.1 seat regression, slope prior = 1:** Tasks 2, 4, 5 (`SEAT_PRIOR=[...,1,...]`, prior-aware ridge). ✓
- **§4.2 snapshot regression w/ lead buckets:** Tasks 4, 5. ✓
- **§4.3 inverse-variance combine:** Task 7. ✓
- **§5 weekend assembly, snapshot-first, day-share fallback, inflation:** Tasks 8, 11 (`predict_weekend` adds snapshot days as sources; `assemble_weekend` extrapolates + inflates). ✓
- **§6 Student-t 90% interval, empirical scale + bias, missing-day widening:** Task 9. ✓
- **§7 acceptance gate, refuse to ship:** Tasks 10 (`GATE_*`, tier selection), 15 (decision point + stop-and-report). ✓
- **§8 new module, schema block, removals, retrain cadence:** Tasks 1-11 (module), 12/14 (sanitize + record_actual + calibrate), 13 (predict), 15 (regenerate). ✓
- **§9 risks (tiny n, fallback tiers):** global-ratio + identity tiers in Tasks 10/11. ✓

**Type/name consistency:** `fit_regression_calibration`, `predict_weekend`, `build_seat_rows`, `build_snapshot_rows`, `seat_features`, `snapshot_features`, `fit_seat`, `fit_snapshot`, `predict_log`, `loo_select`, `combine_sources`, `inflate_variance`, `learn_day_shares`, `assemble_weekend`, `weekend_interval`, `t_quantile_95` — used consistently across tasks. Block schema keys (`active_tier`, `seat.coef`, `snapshot`, `day_shares`, `weekend.{resid_scale,resid_mean,df,loo_hit_rate,loo_mae_pct,n_movies}`, `global_ratio`) consistent between Tasks 10, 11, 12, 13, 15.

**No placeholders:** every code step contains complete code; every run step has an exact command + expected result.
