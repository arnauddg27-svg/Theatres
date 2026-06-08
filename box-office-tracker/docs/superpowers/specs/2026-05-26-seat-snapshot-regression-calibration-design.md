# Seat + Snapshot Regression Calibration — Design

**Date:** 2026-05-26
**Status:** Approved (design); pending implementation plan
**Scope:** Replace the box-office model's *calibration layer* with two coupled,
cross-validated regressions driven by AMC seat-count and pre-reservation
snapshot data. The mechanical `seats → revenue → AMC → domestic` computation is
retained as the regression *input*.

---

## 1. Problem & motivation

The current model is a hand-built multiplicative pipeline:

```
seat → AMC → domestic → × footprint → × preview_residual → × day_scale (EMA)
     → snapshot blend (fixed weight) → × historical_residual → × social
```

Measured against the 8 settled movies in `data/calibration.json`:

- **MAE ≈ 20%**, mean signed error **+8.5%** (systematic over-prediction).
- **3 of 8 actuals fall outside the predicted `[low, high]` band** (realized
  coverage 62% for an interval implicitly sold as tight). Two predictions had
  *zero-width* bands and both were large misses.
- Several "learned" layers stack multiplicative corrections trained on the same
  small history, with no joint bound and no out-of-sample validation.
- The largest systematic error is **title-size dependent**: big wide releases
  over-predict (Prada +25%, Mortal Kombat +20%, Sheep Detectives +40%) while
  small/indie titles under-predict (Animal Farm −30%, In the Grey −6.5%).

Goal: a **statistically honest, regression-based calibration** with
**cross-validated** uncertainty, built primarily on seat-count and snapshot
data.

---

## 2. Design decisions (locked)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Replacement scope | **Calibration layer only.** Keep `seats → revenue → AMC → domestic` as the regression input; replace all downstream correction machinery. |
| 2 | Unit of analysis | **Per-day gross, summed to weekend.** ~24 movie-day rows vs 8 weekend rows. CV is **leave-one-MOVIE-out** (a movie's days are correlated). |
| 3 | Missing (future) days | **Snapshot-first, then day-share fallback.** Snapshot-covered future days run through the snapshot regression as real observations; days with neither seat nor snapshot data use a learned day-share with steeply inflated variance. |
| 4 | Uncertainty target | **Calibrated 90% interval**, verified by realized leave-one-movie-out hit-rate. |
| 5 | Training admissibility | Per-day **coverage ≥ 0.6**; coverage-weighted; a movie needs **≥ 2 admissible days** to contribute a weekend-level CV point. |
| 6 | Regression form | **Direct log-linear with a ridge-shrunk slope** (form B). Generalizes the anchor model; can capture the title-size slope bias; degrades safely when data is thin. |

---

## 3. Data & admissibility

- **Source of truth for training:** `data/calibration.json` `history[]` entries,
  which already carry `raw_daily_predictions` (seat-implied daily gross),
  `daily_actuals` (reported actual), `daily_coverage_ratios`,
  `daily_theatre_counts`, and `snapshot_daily_predictions` /
  `snapshot_daily_coverage_ratios` / `snapshot_daily_lead_buckets`.
- **Target:** reported actual daily gross (complete by construction; sourced from
  The Numbers).
- **Predictor (seat):** `raw_daily_predictions[day]` — the coverage-normalized
  seat-implied daily gross *before* any calibration correction.
- **Predictor (snapshot):** `snapshot_daily_predictions[day]`.
- **Admissibility floor:** a movie-day enters the **seat** regression iff
  `daily_coverage_ratios[day] ≥ 0.60`. → **16 rows across 6 movies**
  (drops Hokum entirely, Animal Farm's 2% Saturday, In the Grey's 38–39% days,
  Obsession's 44% Saturday).
- **Snapshot admissibility:** a movie-day enters the **snapshot** regression iff
  it has a positive `snapshot_daily_predictions[day]` and a recorded lead bucket.
  (Snapshot coverage is separately tracked and feeds the variance, not a hard
  floor, because snapshots are sparse.)
- **Row weights:** precision ∝ coverage (seat) — a 1.0-coverage day outweighs a
  0.6 day.
- **Weekend-CV gate:** a movie needs ≥ 2 admissible seat-days to yield a
  weekend-level leave-one-out residual.

### Empirical justification for the 0.6 floor
Log-ratio standard deviation of `actual/seat_implied` barely moves as the floor
rises (0.34 at cov≥0.4 → 0.30 at cov≥0.7): the low-coverage rows add
extrapolation-biased points without reducing spread. The seat-implied number on
a 2%-coverage day is ~6 theatres scaled ×50, so its ratio is dominated by
sampling noise, not the calibration relationship. Even at full coverage the
*daily* log-ratio SD ≈ 0.30 (≈ ±35% one-sigma per day) — irreducible daily
noise that the weekend sum averages down.

---

## 4. Model

### 4.1 Seat regression (per admissible seat-day)

```
log(actual_day) = β0
                + β1 · log(seat_implied_day)
                + β_thu·is_thu + β_fri·is_fri + β_sat·is_sat   (Sunday = baseline)
                + β_cov · (1 − coverage)
```

- **Ridge** penalty on all coefficients except the intercept; `β1` shrunk
  toward 1 (penalize `β1 − 1`, not `β1 − 0`, so the prior is "seat-implied is
  unbiased" and deviations must be earned).
- Features standardized (mean 0, unit SD) before the solve; coefficients
  un-standardized for storage.
- λ chosen by **leave-one-movie-out** CV minimizing weighted log-residual error.
- Feature budget ≤ ~1 parameter per 3–4 rows. If LOO prefers it, day effects
  collapse to `is_thursday` (previews) + weekend baseline.

### 4.2 Snapshot regression (per admissible snapshot-day)

```
log(actual_day) = γ0
                + γ1 · log(snapshot_implied_day)
                + γ_day·[day dummies]
                + γ_lead·[lead-bucket dummies: same_day / next_day / multi_day / long_lead]
```

- Same ridge + LOO-movie machinery. Independent of the seat model.
- Replaces the hand-set `snapshot_to_day_scale_factors` /
  `snapshot_to_lead_scale_factors`.

### 4.3 Per-day combination — inverse-variance (precision) weighting

For each day, each available source `i` gives a prediction `yᵢ` (in log space)
and a LOO-estimated variance `σᵢ²` inflated by that day's reliability
(coverage for seat; lead bucket + snapshot coverage for snapshot):

```
ŷ_day = Σ(yᵢ / σᵢ²) / Σ(1 / σᵢ²)
Var(ŷ_day) = 1 / Σ(1 / σᵢ²)
```

- One source present → that source is used.
- Both present → both contribute; the more reliable dominates automatically.
- Neither present → §5 fallback.

This replaces the fixed `snapshot_model_weight` with a principled, data-driven
blend.

---

## 5. Weekend assembly & missing days

- **Weekend total = sum of per-day predictions** (exponentiated from log space
  with the standard `+½σ²` lognormal mean correction).
- **Observed day:** seat (± snapshot) prediction via §4.3.
- **Future day with snapshot:** snapshot-model prediction (snapshot-first
  forward engine).
- **Future day with neither:** learned **day-share fallback** — distribute the
  observed calibrated subtotal across missing days using the day-share
  distribution, with per-missing-day variance inflated steeply so a
  Thursday-only forecast is honestly wide (no 8.7× single-day leverage).

---

## 6. Uncertainty — calibrated 90% interval

- Compute **leave-one-movie-out weekend predictions** for the 6 eligible movies;
  take log-residuals `r_m = log(actual_m) − log(pred_m)`.
- Model residuals with a **Student-t** distribution (df ≈ n−1 ≈ 5) rather than
  normal — honest heavy tails for small n.
- Weekend interval = `mid × exp(± t_{0.95, df} · s)` where `s` is the weekend-level
  LOO residual scale (captures within-movie correlation; *not* a naive sum of
  daily variances).
- **Widen** by the missing-day variance from §5 when days are unobserved.
- Emit `low / mid / high` at **90%**, and always report the realized LOO
  hit-rate next to the prediction so calibration is auditable.

---

## 7. Validation & acceptance gate

Under leave-one-movie-out, before replacing the current model the new model must:

1. **Realized 90% interval hit-rate ≥ ~85%** (current: 62%).
2. **Weekend MAE ≤ current (~20%)** on the clean 6-movie subset; target: beat it.
3. Produce a diagnostic table: per-movie LOO predicted vs actual, interval,
   in/out flag, and the fitted coefficients (`β1`, day effects, λ).

If the model cannot beat the current one out-of-sample, **it is not shipped**;
the run reports why and the existing model stays.

---

## 8. Code integration

- **New module `seat_regression.py`** — the two regressions, standardization,
  ridge solve, leave-one-movie-out CV, precision combination, day-share
  fallback, and t-interval logic. Self-contained and unit-testable.
- **`model_calibration.py`** — replace the EMA `recalibrate_*` functions with
  fit-and-persist of regression coefficients + CV variances; keep
  `sanitize_calibration` deterministic and idempotent.
- **`data/calibration.json`** — add a `regression` block:
  `{ seat: {coef, lambda, feature_means, feature_sds}, snapshot: {...},
  weekend_residual: {scale, df, loo_hit_rate, n}, day_shares: {...},
  trained_on: [movie list], trained_at }`.
  Remove `day_scale_factors`, `overall_scale_factor`,
  `snapshot_to_day_scale_factors`, `snapshot_to_lead_scale_factors`, and the
  residual-regression inputs.
- **`predict.py`** — `days_to_weekend` and `select_regression_prediction` call
  the new combiner. Remove the stacked multiplicative layers
  (`historical_residual_regression`, `learned_preview_seat_residual`,
  social factor, hand-set snapshot weight, `model_component_disagreement`
  buffer). Keep Stage A–C plumbing (revenue, AMC sum, AMC→domestic) intact.
- **Retraining cadence unchanged:** coefficients recomputed deterministically
  from `history` on each `calibrate.py` run (Tuesdays).

---

## 9. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Tiny n (6 movies for weekend CV) | Ruthless parsimony, ridge, Student-t intervals, explicit "insufficient data → widen" path. |
| 0.6 floor shrinks the training set | Coupled snapshot model recovers signal on snapshot days; floor revisited as history grows. |
| Slope (β1 ≠ 1) bias spurious at n=6 | β1 shrunk toward 1; LOO rejects it if it doesn't generalize out-of-sample. |
| New model worse than current | Hard acceptance gate (§7); do not ship on failure. |
| Schema migration breaks old reads | `sanitize_calibration` tolerates absent `regression` block and falls back to identity calibration (ratio = 1) until first fit. |

---

## 10. Out of scope

- Changing the raw revenue computation (ticket prices, evening→daily multiplier,
  AMC share, footprint factor).
- Polymarket / trading logic (consumes the forecast; unchanged).
- Social-signal collection (the *layer* is removed from the forecast; data
  collection untouched).
