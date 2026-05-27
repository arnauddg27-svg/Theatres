# seat_regression.py
"""Seat + snapshot regression calibration for box-office prediction.

Pure standard library (no numpy/scipy). Replaces the hand-built multiplicative
calibration layer with two coupled, leave-one-movie-out cross-validated ridge
regressions combined by inverse-variance precision weighting. See
docs/superpowers/specs/2026-05-26-seat-snapshot-regression-calibration-design.md
"""
from __future__ import annotations

from math import ceil, exp, isfinite, log
from statistics import median

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
        round(1.0 - float(coverage), 10),
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

    Single-movie fallback: when there is only one unique movie, leave-one-out
    yields no training data for any fold, so we degrade gracefully by fitting on
    all rows (no leave-out) and computing in-sample residuals for each l2.
    """
    if not rows:
        return None
    movies = _movies_in(rows)

    # Single-movie fallback: fit on all rows, evaluate in-sample residuals.
    if len(movies) == 1:
        best = None
        for l2 in LAMBDA_GRID:
            coef = fit_fn(rows, l2)
            if coef is None:
                continue
            resids = []
            sq = 0.0
            wsum = 0.0
            for r in rows:
                e = r["log_actual"] - pred_row_fn(coef, r)
                w = r.get("weight", 1.0)
                sq += w * e * e
                wsum += w
                resids.append((e, w))
            if wsum <= 0:
                continue
            mse = sq / wsum
            if best is None or mse < best[0]:
                var = sum(w * e * e for e, w in resids) / wsum
                best = (mse, l2, max(1e-6, var) ** 0.5, len(resids))
        if best is None:
            return None
        _, l2, sd, n = best
        return l2, sd, n

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


# Reporting-only target: whether the active tier's LOO MAE clears this bar.
# Tier SELECTION is by lowest LOO MAE (the 3-way bake-off), not a hard gate.
GATE_MAX_MAE_PCT = 20.0


def _global_ratio(seat_rows):
    """1-parameter fallback: weighted-mean log(actual/seat) across seat rows."""
    if not seat_rows:
        return {"log_ratio_mean": 0.0, "resid_scale": 0.35}
    wsum = sum(r["weight"] for r in seat_rows)
    mean = sum(r["weight"] * (r["log_actual"] - r["log_seat"]) for r in seat_rows) / wsum
    var = sum(r["weight"] * ((r["log_actual"] - r["log_seat"]) - mean) ** 2
              for r in seat_rows) / wsum
    return {"log_ratio_mean": mean, "resid_scale": max(0.05, var ** 0.5)}


# A day whose ONLY signal is a snapshot prediction this noisy (log-variance
# above this threshold; snapshots empirically sit near ~1.0) is dropped so the
# reliable day-share fallback fills it instead — a noisy sole-source snapshot
# produces worse weekend estimates than extrapolating from the observed days.
SNAPSHOT_MAX_SOLE_SOURCE_VAR = 0.5


def _finalize_day_sources(sources):
    """Combine a day's tagged sources into a (point_$M, log_variance) pair.

    sources: list of (logmean, variance, is_snapshot) tuples.

    Returns None when the day should be treated as unobserved — either no
    source at all, or the only source is a snapshot too noisy to trust
    (variance > SNAPSHOT_MAX_SOLE_SOURCE_VAR). The point estimate is the
    lognormal MEDIAN exp(logmean) — we deliberately do NOT add the +0.5*var
    mean correction, because `var` here is mostly estimation uncertainty
    (LOO residual + coverage/lead inflation), not true lognormal scatter, so
    adding it would systematically over-inflate noisy days.
    """
    if not sources:
        return None
    if len(sources) == 1 and sources[0][2] and sources[0][1] > SNAPSHOT_MAX_SOLE_SOURCE_VAR:
        return None
    combined = combine_sources([(lm, v) for lm, v, _is_snap in sources])
    if combined is None:
        return None
    logmean, var = combined
    return exp(logmean), var


def _raw_resid_sd(rows, key):
    """RMS of (log_actual - raw) around 0, for the identity & ratio tiers."""
    if not rows:
        return 0.35
    wsum = sum(r["weight"] for r in rows)
    if wsum <= 0:
        return 0.35
    sq = sum(r["weight"] * (r["log_actual"] - r[key]) ** 2 for r in rows)
    return max(0.05, (sq / wsum) ** 0.5)


def _seat_pred_row(coef, r):
    return predict_log(coef, seat_features(r["log_seat"], r["day"], r["coverage"]))


def _snap_pred_row(coef, r):
    return predict_log(coef, snapshot_features(r["log_snap"], r["day"], r["lead_bucket"]))


# ── Per-tier day-source builders ──────────────────────────────────────────────
# Each maps one day's live inputs to a list of tagged (logmean, variance,
# is_snapshot) sources. _finalize_day_sources then gates + combines them.

def _regression_day_sources(day, seat, cov, snap, lead, params):
    sources = []
    sc = params.get("seat_coef")
    if seat and seat > 0 and cov >= COVERAGE_FLOOR and sc is not None:
        sources.append((predict_log(sc, seat_features(log(seat), day, cov)),
                        inflate_variance(params["seat_sd"] ** 2, cov), False))
    nc = params.get("snap_coef")
    if snap and snap > 0 and nc is not None:
        sources.append((predict_log(nc, snapshot_features(log(snap), day, lead)),
                        (params.get("snap_sd") or 0.35) ** 2, True))
    return sources


def _identity_day_sources(day, seat, cov, snap, lead, params):
    """Raw seat-implied, no calibration (ratio = 1). Seat-only baseline."""
    if seat and seat > 0 and cov >= COVERAGE_FLOOR:
        return [(log(seat), inflate_variance(params["seat_sd"] ** 2, cov), False)]
    return []


def _global_ratio_day_sources(day, seat, cov, snap, lead, params):
    """Raw seat-implied * exp(mean log-ratio). Seat-only baseline."""
    if seat and seat > 0 and cov >= COVERAGE_FLOOR:
        return [(log(seat) + params["log_ratio_mean"],
                 inflate_variance(params["seat_sd"] ** 2, cov), False)]
    return []


def _fit_regression_params(history):
    seat_rows = build_seat_rows(history)
    snap_rows = build_snapshot_rows(history)
    # loo_select returns (lambda, LOO daily residual SD, n). Use the
    # out-of-sample LOO SD as the per-source noise for BOTH seat and snapshot,
    # so inverse-variance weighting compares them on the same honest basis.
    sl = loo_select(seat_rows, fit_seat, _seat_pred_row) or (1.0, 0.35, 0)
    nl = loo_select(snap_rows, fit_snapshot, _snap_pred_row) if snap_rows else None
    seat_l2, seat_sd = sl[0], sl[1]
    snap_l2 = nl[0] if nl else 1.0
    snap_sd = nl[1] if nl else None
    sc = fit_seat(seat_rows, seat_l2)
    nc = fit_snapshot(snap_rows, snap_l2) if snap_rows else None
    return {
        "seat_coef": sc,
        "snap_coef": nc,
        "seat_sd": seat_sd,
        "snap_sd": snap_sd,
        "seat_l2": seat_l2,
        "snap_l2": snap_l2,
        "snap_daily_resid_sd": (snap_sd if snap_sd is not None else 0.35),
    }


def _fit_identity_params(history):
    return {"seat_sd": _raw_resid_sd(build_seat_rows(history), "log_seat")}


def _fit_global_ratio_params(history):
    gr = _global_ratio(build_seat_rows(history))
    return {"log_ratio_mean": gr["log_ratio_mean"], "seat_sd": gr["resid_scale"]}


TIER_SOURCE_BUILDERS = {
    "regression": _regression_day_sources,
    "identity": _identity_day_sources,
    "global_ratio": _global_ratio_day_sources,
}
TIER_PARAM_FITTERS = {
    "regression": _fit_regression_params,
    "identity": _fit_identity_params,
    "global_ratio": _fit_global_ratio_params,
}


def _assemble_per_day(rdp, sdp, cov, leads, build_sources, params):
    """Per-day (point_$M, log_var) from live inputs via a tier source builder."""
    per_day = {}
    for day in OPENING_DAYS:
        seat = _f(rdp.get(day))
        c = _f(cov.get(day)) or 0.0
        snap = _f(sdp.get(day))
        lead = leads.get(day) if leads.get(day) in LEAD_BUCKETS else "same_day"
        fin = _finalize_day_sources(build_sources(day, seat, c, snap, lead, params))
        if fin is not None:
            per_day[day] = fin
    return per_day


def _assemble_entry(entry, build_sources, params):
    return _assemble_per_day(
        entry.get("raw_daily_predictions") or entry.get("daily_predictions") or {},
        entry.get("snapshot_daily_predictions") or {},
        entry.get("daily_coverage_ratios") or {},
        entry.get("snapshot_daily_lead_buckets") or {},
        build_sources, params,
    )


def _tier_loo(history, day_shares, tier):
    """Leave-one-movie-out weekend predictions for one tier.

    Returns list of (movie, pred_m, actual_m, observed_share, log_resid).
    """
    build_sources = TIER_SOURCE_BUILDERS[tier]
    fit_params = TIER_PARAM_FITTERS[tier]
    results = []
    for m in weekend_cv_movies(history):
        train = [e for e in history if e.get("movie") != m]
        if not build_seat_rows(train):
            continue
        params = fit_params(train)
        entry = next(e for e in history if e.get("movie") == m)
        actual_total = _f(entry.get("actual_total"))
        if not actual_total or actual_total <= 0:
            continue
        per_day = _assemble_entry(entry, build_sources, params)
        if not per_day:
            continue
        mid, _v, obs = assemble_weekend(per_day, day_shares)
        if mid <= 0:
            continue
        results.append((m, mid, actual_total, obs, log(actual_total) - log(mid)))
    return results


ROBUST_TARGET_COVERAGE = 0.90   # the prediction interval targets 90% coverage
_MAD_TO_SIGMA = 1.4826          # MAD -> Gaussian-equivalent SD


def _resid_stats(loo):
    """Robust, coverage-honest weekend residual stats for a tier's LOO.

    The bias correction is the MEDIAN log-residual (not the mean): a single
    anomalous movie — e.g. a title whose seat sample was evening-only and so
    mis-extrapolated by the fixed evening->daily multiplier — must not drag the
    global correction applied to every other forecast.

    The 90% interval half-width is the tightest that still covers
    ceil(0.90*n) of the LOO residuals about that median center
    (distribution-free / conformal-style), floored by a robust
    t * (1.4826*MAD) parametric width for smoothness at tiny n and a small
    absolute floor so a degenerate all-zero-residual set stays finite. This
    keeps realized coverage honest while resisting outliers.

    `resid_scale` is stored as half_width / t so the unchanged `weekend_interval`
    (which multiplies t * resid_scale) reproduces the intended half-width.
    """
    n = len(loo)
    resids = [r[4] for r in loo]
    df = max(1, n - 1)
    center = median(resids)
    dev = sorted(abs(r - center) for r in resids)
    mad = median(dev)
    t = t_quantile_95(df)
    k = min(n, max(1, ceil(ROBUST_TARGET_COVERAGE * n)))
    empirical_half = dev[k - 1]                       # covers ceil(0.9n) residuals
    parametric_half = t * (_MAD_TO_SIGMA * mad)       # robust-scale parametric floor
    half = max(empirical_half, parametric_half, 0.05 * t)
    rscale = half / t                                 # weekend_interval does t * rscale
    hits = 0
    ae = []
    for _m, pred, actual, obs, _lr in loo:
        _mid, low, high = weekend_interval(pred, rscale, df, obs, center)
        if low <= actual <= high:
            hits += 1
        ae.append(abs(pred * exp(center) - actual) / actual)
    return {
        "resid_scale": rscale,
        "resid_mean": center,
        "df": df,
        "loo_hit_rate": round(hits / n, 4),
        "loo_mae_pct": round(100.0 * sum(ae) / n, 2),
        "loo_median_ae_pct": round(100.0 * median(ae), 2),
        "n_movies": n,
        "loo_detail": [
            {"movie": m, "pred_m": round(p, 2), "actual_m": round(a, 2),
             "observed_share": round(s, 3)} for m, p, a, s, _ in loo
        ],
    }


def _params_from_block(block, tier):
    """Reconstruct a tier's predict-time params from a persisted block."""
    if tier == "regression" and block.get("seat"):
        snap = block.get("snapshot")
        return {"seat_coef": block["seat"]["coef"],
                "snap_coef": snap["coef"] if snap else None,
                "seat_sd": block["seat"]["daily_resid_sd"],
                "snap_sd": snap["daily_resid_sd"] if snap else None}
    if tier == "global_ratio":
        gr = block.get("global_ratio") or {"log_ratio_mean": 0.0, "resid_scale": 0.35}
        return {"log_ratio_mean": gr["log_ratio_mean"], "seat_sd": gr["resid_scale"]}
    return {"seat_sd": (block.get("identity") or {}).get("seat_sd", 0.40)}


def fit_regression_calibration(history):
    """Fit all calibration tiers, activate the leave-one-movie-out winner.

    Runs a 3-way out-of-sample bake-off (identity / global_ratio / regression)
    and activates whichever tier has the lowest LOO weekend MAE. The full
    regression is stored even when dormant, so it auto-activates once it beats
    the simpler tiers as history grows. Returns the `regression` calibration
    block persisted into calibration.json.
    """
    seat_rows = build_seat_rows(history)
    day_shares = learn_day_shares(history)
    block = {
        "version": 1,
        "active_tier": "identity",
        "day_shares": day_shares,
        "trained_on": _movies_in(seat_rows),
        "global_ratio": _global_ratio(seat_rows),
        "identity": _fit_identity_params(history),
    }

    # Persist full-data regression params (used when the regression tier wins).
    if seat_rows:
        reg = _fit_regression_params(history)
        block["seat"] = {"features": list(SEAT_FEATURES), "coef": reg["seat_coef"],
                         "prior": SEAT_PRIOR, "lambda": reg["seat_l2"],
                         "daily_resid_sd": reg["seat_sd"]}
        if reg["snap_coef"] is not None:
            block["snapshot"] = {"features": list(SNAP_FEATURES), "coef": reg["snap_coef"],
                                 "prior": SNAP_PRIOR, "lambda": reg["snap_l2"],
                                 "daily_resid_sd": reg["snap_daily_resid_sd"]}
        else:
            block["snapshot"] = None
    else:
        block["seat"] = None
        block["snapshot"] = None

    # 3-way leave-one-movie-out bake-off.
    bakeoff = {}
    stats_by_tier = {}
    for tier in ("identity", "global_ratio", "regression"):
        loo = _tier_loo(history, day_shares, tier)
        if len(loo) >= 2:
            stats = _resid_stats(loo)
            stats_by_tier[tier] = stats
            bakeoff[tier] = stats["loo_mae_pct"]

    if stats_by_tier:
        winner = min(bakeoff, key=bakeoff.get)
        win = stats_by_tier[winner]
        block["active_tier"] = winner
        block["weekend"] = {k: win[k] for k in
                            ("resid_scale", "resid_mean", "df",
                             "loo_hit_rate", "loo_mae_pct", "loo_median_ae_pct",
                             "n_movies")}
        block["loo_detail"] = win["loo_detail"]
        block["bakeoff"] = bakeoff
        block["bakeoff_winner"] = winner
        block["meets_mae_target"] = win["loo_mae_pct"] <= GATE_MAX_MAE_PCT
    else:
        # Too little data to cross-validate: ship raw seat-implied with a wide
        # default interval until a 2+-movie history exists.
        block["active_tier"] = "identity"
        block["weekend"] = {"resid_scale": 0.40, "resid_mean": 0.0, "df": 1,
                            "loo_hit_rate": None, "loo_mae_pct": None, "n_movies": 0}
        block["bakeoff"] = bakeoff
    return block


def predict_weekend(block, daily_seat_m, coverage, daily_snapshot_m, lead_buckets):
    """Production forecast from a fitted regression block.

    daily_seat_m: {day: raw seat-implied daily gross $M} (observed days).
    coverage:     {day: 0..1}.
    daily_snapshot_m: {day: snapshot-implied daily gross $M} (future or observed).
    lead_buckets: {day: lead bucket str}.

    Returns {mid_m, low_m, high_m, observed_share, per_day, tier}.
    """
    tier = block.get("active_tier", "identity")
    if tier not in TIER_SOURCE_BUILDERS:
        tier = "identity"
    day_shares = block.get("day_shares") or {d: 0.25 for d in OPENING_DAYS}
    params = _params_from_block(block, tier)
    per_day = _assemble_per_day(daily_seat_m or {}, daily_snapshot_m or {},
                                coverage or {}, lead_buckets or {},
                                TIER_SOURCE_BUILDERS[tier], params)
    mid, _logvar, obs_share = assemble_weekend(per_day, day_shares)
    wk = block.get("weekend") or {"resid_scale": 0.40, "resid_mean": 0.0, "df": 1}
    lo_hi = weekend_interval(mid, wk["resid_scale"], wk.get("df", 1),
                             obs_share, wk.get("resid_mean", 0.0))
    return {"mid_m": lo_hi[0], "low_m": lo_hi[1], "high_m": lo_hi[2],
            "observed_share": obs_share, "tier": tier,
            "per_day": {d: round(v[0], 3) for d, v in per_day.items()}}
