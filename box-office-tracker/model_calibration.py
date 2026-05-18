"""
Shared calibration helpers for the box-office prediction model.

The main goal here is to keep calibration adaptive without letting a single bad
weekend blow up the model. Historical ratios are shrunk toward 1.0 based on how
complete the observation was, then clipped to a sane range before updating the
stored scale factor.
"""

from __future__ import annotations

MIN_SCALE_FACTOR = 0.5
MAX_SCALE_FACTOR = 2.0
MIN_MARKET_SHARE = 0.15
MAX_MARKET_SHARE = 0.40
MIN_DAILY_CALIBRATION_COVERAGE = 0.80
SNAPSHOT_LEAD_BUCKETS = ("same_day", "next_day", "multi_day", "long_lead")
SNAPSHOT_DAY_SCALE_PRIOR_WEIGHT = 4.0
SNAPSHOT_LEAD_SCALE_PRIOR_WEIGHT = 4.0
SNAPSHOT_INFERRED_DAILY_ACTUAL_WEIGHT = 0.50
OPENING_WEEKEND_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _as_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def excluded_calibration_days(entry: dict) -> set[str]:
    """Days that should not train calibration from this historical record."""
    excluded = set(entry.get("calibration_excluded_days", []) or [])
    daily_coverage = entry.get("daily_coverage_ratios", {}) or {}
    for day, ratio in daily_coverage.items():
        if _as_float(ratio, 0.0) < MIN_DAILY_CALIBRATION_COVERAGE:
            excluded.add(day)
    return excluded


def opening_day_actuals(daily_actuals: dict) -> dict[str, float]:
    """Return only real Thu/Fri/Sat/Sun daily actuals from a history row."""
    if not isinstance(daily_actuals, dict):
        return {}
    actuals = {}
    for day in OPENING_WEEKEND_DAYS:
        value = _as_float(daily_actuals.get(day), 0.0)
        if value > 0:
            actuals[day] = value
    return actuals


def complete_opening_day_actuals_for_weights(entry: dict,
                                             tolerance: float = 0.02
                                             ) -> dict[str, float]:
    """Daily actuals eligible for day-shape calibration.

    Manual weekend totals can arrive before the public daily table is final. In
    that case calibration stores the unresolved balance in ``WeekendRemainder``
    so the weekend total is correct, but the Thu/Fri/Sat/Sun split is not yet a
    complete day-shape datapoint. Do not let those partial splits move learned
    day weights.
    """
    daily_actuals = opening_day_actuals(entry.get("daily_actuals", {}) or {})
    if len(daily_actuals) < 3:
        return {}

    total_actual = _total_actual_for_entry(entry)
    if total_actual <= 0:
        return daily_actuals

    known_total = sum(daily_actuals.values())
    if known_total <= 0:
        return {}
    allowed_gap = max(0.05, total_actual * max(0.0, tolerance))
    if abs(total_actual - known_total) > allowed_gap:
        return {}
    return daily_actuals


def _total_actual_for_entry(entry: dict) -> float:
    total = _as_float(entry.get("actual_total", entry.get("actual")), 0.0)
    if total > 0:
        return total
    return sum(_as_float(v, 0.0) for v in (entry.get("daily_actuals", {}) or {}).values())


def snapshot_calibration_actual_for_day(entry: dict, day: str) -> tuple[float, float]:
    """Actual gross and confidence multiplier for snapshot-day calibration.

    Prefer direct day actuals. If a row has only a weekend total plus some
    known reported days, allocate the remaining total across missing
    snapshot-covered days by the snapshot's own raw day proportions. This
    lets total-only weekend actuals teach the future snapshot layer without
    writing fabricated public daily grosses into history.
    """
    daily_actuals = opening_day_actuals(entry.get("daily_actuals", {}) or {})
    direct = _as_float(daily_actuals.get(day), 0.0)
    if direct > 0:
        return direct, 1.0

    total_actual = _total_actual_for_entry(entry)
    if total_actual <= 0:
        return 0.0, 0.0

    known_total = sum(daily_actuals.values())
    remaining_actual = total_actual - known_total
    if remaining_actual <= 0:
        return 0.0, 0.0

    snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
    if day not in snapshot_predictions:
        return 0.0, 0.0

    missing_days = [
        candidate
        for candidate in OPENING_WEEKEND_DAYS
        if candidate not in daily_actuals
        and _as_float(snapshot_predictions.get(candidate), 0.0) > 0
    ]
    predicted_remaining = sum(
        _as_float(snapshot_predictions.get(candidate), 0.0)
        for candidate in missing_days
    )
    predicted_day = _as_float(snapshot_predictions.get(day), 0.0)
    if predicted_remaining <= 0 or predicted_day <= 0:
        return 0.0, 0.0

    inferred_actual = remaining_actual * (predicted_day / predicted_remaining)
    if inferred_actual <= 0:
        return 0.0, 0.0
    return inferred_actual, SNAPSHOT_INFERRED_DAILY_ACTUAL_WEIGHT


def coverage_score(n_theatres: int | float = 0,
                   n_days: int | float = 0,
                   coverage_ratio: int | float | None = None) -> float:
    """How much we should trust a calibration datapoint, on a 0-1 scale."""
    if coverage_ratio is not None:
        theatre_component = clamp(_as_float(coverage_ratio, 0.0), 0.0, 1.0)
    else:
        theatre_component = clamp(_as_float(n_theatres, 0.0) / 400.0, 0.0, 1.0)
    day_component = clamp(_as_float(n_days, 0.0) / 4.0, 0.0, 1.0)
    return 0.6 * day_component + 0.4 * theatre_component


def bounded_scale_ratio(actual_total: float,
                        predicted_total: float,
                        n_theatres: int | float = 0,
                        n_days: int | float = 0,
                        coverage_ratio: int | float | None = None) -> float | None:
    """Convert one historical result into a bounded calibration ratio."""
    actual = _as_float(actual_total, 0.0)
    predicted = _as_float(predicted_total, 0.0)
    if actual <= 0 or predicted <= 0:
        return None

    raw_ratio = actual / predicted
    trust = coverage_score(
        n_theatres=n_theatres,
        n_days=n_days,
        coverage_ratio=coverage_ratio,
    )
    # Pull sparse / low-quality observations back toward 1.0.
    shrunk_ratio = 1.0 + (raw_ratio - 1.0) * trust
    return clamp(shrunk_ratio, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)


def recalibrate_scale_factor(history: list[dict],
                             default: float = 1.0,
                             alpha: float = 0.4) -> float:
    """Compute a stable overall scale factor from historical results."""
    scale = clamp(_as_float(default, 1.0), MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)
    if not history:
        return round(scale, 4)

    # Use recent history and support both predict.py and calibrate.py schemas.
    recent = history[-20:]
    for entry in recent:
        actual = entry.get("actual_total", entry.get("actual"))
        predicted = entry.get("predicted_mid")
        n_theatres = entry.get("n_theatres", 0)
        n_days = entry.get("n_days", entry.get("days_collected", 0))
        coverage_ratio = entry.get("coverage_ratio")
        excluded_days = excluded_calibration_days(entry)
        daily_actuals = entry.get("daily_actuals", {}) or {}
        daily_predictions = (
            entry.get("raw_daily_predictions")
            or entry.get("daily_predictions", {})
            or {}
        )
        if daily_actuals and daily_predictions and excluded_days:
            eligible_days = [
                day for day in OPENING_WEEKEND_DAYS
                if day not in excluded_days
                and _as_float(daily_actuals.get(day), 0.0) > 0
                and _as_float(daily_predictions.get(day), 0.0) > 0
            ]
            if eligible_days:
                actual = sum(_as_float(daily_actuals.get(day), 0.0) for day in eligible_days)
                predicted = sum(_as_float(daily_predictions.get(day), 0.0) for day in eligible_days)
                n_days = len(eligible_days)
                ratios = entry.get("daily_coverage_ratios", {}) or {}
                vals = [_as_float(ratios.get(day), 0.0) for day in eligible_days]
                vals = [v for v in vals if v > 0]
                coverage_ratio = sum(vals) / len(vals) if vals else coverage_ratio
        if coverage_ratio is None:
            ratios = entry.get("daily_coverage_ratios", {}) or {}
            vals = [_as_float(v, 0.0) for v in ratios.values() if _as_float(v, 0.0) > 0]
            coverage_ratio = sum(vals) / len(vals) if vals else None
        ratio = bounded_scale_ratio(
            actual_total=actual,
            predicted_total=predicted,
            n_theatres=n_theatres,
            n_days=n_days,
            coverage_ratio=coverage_ratio,
        )
        if ratio is None:
            continue
        scale = alpha * ratio + (1.0 - alpha) * scale

    return round(clamp(scale, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR), 4)


def recalibrate_day_scale_factors(history: list[dict],
                                  alpha: float = 0.4) -> dict[str, float]:
    """Per-day EMA scale factors trained from history.

    For each opening-weekend day (Thursday/Friday/Saturday/Sunday), we compute
    one EMA over the historical (actual / predicted) ratios for that specific
    day. This lets the model learn day-specific biases — e.g. that our
    Thursday extrapolation is structurally high (preview-only night) or that
    Saturday is under-scraped — without averaging those biases away into one
    global scale factor.

    Always starts the EMA at 1.0 per day so the function is idempotent: the
    same history produces the same scales regardless of how many times this
    runs. (Re-seeding from the previously-persisted scales would compound the
    same history into an ever-growing bias on each calibration load.)

    Returns a dict {day_name: scale_factor} for Thu/Fri/Sat/Sun.
    """
    scales: dict[str, float] = {day: 1.0 for day in OPENING_WEEKEND_DAYS}

    if not history:
        return {d: round(s, 4) for d, s in scales.items()}

    for entry in history[-20:]:
        da = entry.get("daily_actuals", {}) or {}
        dp = (
            entry.get("raw_daily_predictions")
            or entry.get("daily_predictions", {})
            or {}
        )
        daily_coverage = entry.get("daily_coverage_ratios", {}) or {}
        daily_counts = entry.get("daily_theatre_counts", {}) or {}
        excluded_days = excluded_calibration_days(entry)
        n_theatres = entry.get("n_theatres", 0)

        for day in OPENING_WEEKEND_DAYS:
            if day in excluded_days:
                continue
            actual = _as_float(da.get(day), 0.0)
            predicted = _as_float(dp.get(day), 0.0)
            if actual <= 0 or predicted <= 0:
                continue
            # Single-day trust: use that day's coverage if available. Falling
            # back to the all-weekend count would over-trust a day where one
            # timezone was missing but other days reached near-full coverage.
            if day in daily_coverage:
                trust = clamp(_as_float(daily_coverage.get(day), 0.0), 0.0, 1.0)
            elif day in daily_counts:
                trust = clamp(_as_float(daily_counts.get(day), 0.0) / 400.0, 0.0, 1.0)
            else:
                trust = clamp(_as_float(n_theatres, 0.0) / 400.0, 0.0, 1.0)
            raw_ratio = actual / predicted
            shrunk = 1.0 + (raw_ratio - 1.0) * trust
            ratio = clamp(shrunk, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)
            scales[day] = alpha * ratio + (1.0 - alpha) * scales[day]

    return {d: round(clamp(s, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR), 4)
            for d, s in scales.items()}


def recalibrate_snapshot_day_scale_factors(history: list[dict],
                                           alpha: float = 0.35) -> dict[str, float]:
    """Per-day EMA for pre-reservation snapshot → final day gross.

    This learns the snapshot layer across all movies with reliable snapshot
    coverage. It is separate from day_scale_factors so early reservation probes
    cannot contaminate post-show seat-count calibration.
    """
    scales: dict[str, float] = {day: 1.0 for day in OPENING_WEEKEND_DAYS}
    if not history:
        return {d: round(s, 4) for d, s in scales.items()}

    ratios: dict[str, list[tuple[float, float]]] = {day: [] for day in scales}
    for entry in history[-20:]:
        snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
        snapshot_coverage = entry.get("snapshot_daily_coverage_ratios", {}) or {}

        for day in OPENING_WEEKEND_DAYS:
            actual, actual_weight = snapshot_calibration_actual_for_day(entry, day)
            predicted = _as_float(snapshot_predictions.get(day), 0.0)
            if actual <= 0 or predicted <= 0:
                continue
            coverage = clamp(_as_float(snapshot_coverage.get(day), 0.0), 0.0, 1.0)
            coverage *= actual_weight
            if coverage < 0.10:
                continue
            raw_ratio = actual / predicted
            ratio = clamp(raw_ratio, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)
            ratios[day].append((ratio, coverage))

    for day, values in ratios.items():
        support = sum(weight for _, weight in values)
        if support <= 0:
            continue
        weighted_ratio = sum(ratio * weight for ratio, weight in values) / support
        strength = min(
            clamp(_as_float(alpha, 0.35), 0.0, 1.0),
            support / (support + SNAPSHOT_DAY_SCALE_PRIOR_WEIGHT),
        )
        scales[day] = 1.0 + (weighted_ratio - 1.0) * strength

    return {d: round(clamp(s, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR), 4)
            for d, s in scales.items()}


def recalibrate_snapshot_lead_scale_factors(history: list[dict],
                                            day_scales: dict[str, float] | None = None,
                                            alpha: float = 0.30) -> dict[str, float]:
    """Lead-time residual EMA for pre-reservation snapshot → final day gross.

    Day scales learn Friday-vs-Saturday type bias. This second layer learns the
    remaining bias from how far before showtime the snapshot was taken, so a
    same-day reservation read does not train the same correction as a two-day
    lead read. Ratios are computed after applying the per-day snapshot scale to
    avoid double-counting day effects.
    """
    scales: dict[str, float] = {bucket: 1.0 for bucket in SNAPSHOT_LEAD_BUCKETS}
    if not history:
        return {bucket: round(scale, 4) for bucket, scale in scales.items()}

    day_scales = day_scales or {}
    ratios: dict[str, list[tuple[float, float]]] = {bucket: [] for bucket in scales}
    for entry in history[-20:]:
        snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
        snapshot_coverage = entry.get("snapshot_daily_coverage_ratios", {}) or {}
        snapshot_leads = entry.get("snapshot_daily_lead_buckets", {}) or {}

        for day in OPENING_WEEKEND_DAYS:
            actual, actual_weight = snapshot_calibration_actual_for_day(entry, day)
            predicted = _as_float(snapshot_predictions.get(day), 0.0)
            bucket = str(snapshot_leads.get(day, "") or "").strip()
            if bucket not in scales or actual <= 0 or predicted <= 0:
                continue
            coverage = clamp(_as_float(snapshot_coverage.get(day), 0.0), 0.0, 1.0)
            coverage *= actual_weight
            if coverage < 0.10:
                continue
            baseline = predicted * _as_float(day_scales.get(day), 1.0)
            if baseline <= 0:
                continue
            raw_ratio = actual / baseline
            ratio = clamp(raw_ratio, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)
            ratios[bucket].append((ratio, coverage))

    for bucket, values in ratios.items():
        support = sum(weight for _, weight in values)
        if support <= 0:
            continue
        weighted_ratio = sum(ratio * weight for ratio, weight in values) / support
        strength = min(
            clamp(_as_float(alpha, 0.30), 0.0, 1.0),
            support / (support + SNAPSHOT_LEAD_SCALE_PRIOR_WEIGHT),
        )
        scales[bucket] = 1.0 + (weighted_ratio - 1.0) * strength

    return {
        bucket: round(clamp(scale, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR), 4)
        for bucket, scale in scales.items()
    }


def snapshot_calibration_support(history: list[dict]) -> dict[str, dict[str, dict[str, float | int]]]:
    """Coverage-weighted support behind each snapshot day and lead bucket.

    Scale factors can remain at the neutral prior (1.0) when a bucket has no
    settled actuals. Prediction needs to know that difference so an untrained
    future-day reservation read does not receive the same model weight as a
    well-calibrated same-day read.
    """
    days = {
        day: {"n": 0, "support": 0.0}
        for day in OPENING_WEEKEND_DAYS
    }
    leads = {
        bucket: {"n": 0, "support": 0.0}
        for bucket in SNAPSHOT_LEAD_BUCKETS
    }

    for entry in (history or [])[-20:]:
        snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
        snapshot_coverage = entry.get("snapshot_daily_coverage_ratios", {}) or {}
        snapshot_leads = entry.get("snapshot_daily_lead_buckets", {}) or {}

        for day in OPENING_WEEKEND_DAYS:
            actual, actual_weight = snapshot_calibration_actual_for_day(entry, day)
            predicted = _as_float(snapshot_predictions.get(day), 0.0)
            if actual <= 0 or predicted <= 0:
                continue
            coverage = clamp(_as_float(snapshot_coverage.get(day), 0.0), 0.0, 1.0)
            coverage *= actual_weight
            if coverage < 0.10:
                continue

            days[day]["n"] += 1
            days[day]["support"] += coverage

            bucket = str(snapshot_leads.get(day, "") or "").strip()
            if bucket in leads:
                leads[bucket]["n"] += 1
                leads[bucket]["support"] += coverage

    def _rounded(section: dict[str, dict[str, float | int]]) -> dict[str, dict[str, float | int]]:
        return {
            key: {
                "n": int(value["n"]),
                "support": round(float(value["support"]), 4),
            }
            for key, value in section.items()
        }

    return {"days": _rounded(days), "leads": _rounded(leads)}


def normalize_day_weights(day_weights: dict | None,
                          defaults: dict[str, float]) -> dict[str, float]:
    """Fill missing day weights from defaults and normalize the whole set."""
    normalized = {}
    for day, default_weight in defaults.items():
        weight = default_weight
        if isinstance(day_weights, dict) and day in day_weights:
            weight = _as_float(day_weights.get(day), default_weight)
        normalized[day] = max(0.0, weight)

    total = sum(normalized.values())
    if total <= 0:
        return dict(defaults)

    return {day: round(weight / total, 4) for day, weight in normalized.items()}


def sanitize_calibration(cal: dict,
                         day_weights_default: dict[str, float],
                         default_market_share: float) -> dict:
    """Normalize calibration payloads loaded from disk."""
    if not isinstance(cal, dict):
        cal = {}

    history = cal.setdefault("history", [])
    factors = cal.setdefault("calibration_factors", {})
    factors.setdefault("format_scale_factors", {})
    factors.setdefault("historical_accuracy", [])

    market_share = _as_float(
        factors.get("amc_market_share", default_market_share),
        default_market_share,
    )
    factors["amc_market_share"] = round(
        clamp(market_share, MIN_MARKET_SHARE, MAX_MARKET_SHARE),
        4,
    )
    factors["day_weights"] = normalize_day_weights(
        factors.get("day_weights"),
        day_weights_default,
    )

    current_scale = _as_float(factors.get("overall_scale_factor", 1.0), 1.0)
    if history:
        factors["overall_scale_factor"] = recalibrate_scale_factor(
            history,
            default=1.0,
        )
    else:
        factors["overall_scale_factor"] = round(
            clamp(current_scale, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR),
            4,
        )

    # Per-day scale factors. These supersede overall_scale_factor for prediction —
    # see predict.get_day_scale. Recomputed deterministically from history on
    # every load (idempotent — always EMAs from 1.0), so a stale persisted
    # value can never silently compound across reloads.
    factors["day_scale_factors"] = recalibrate_day_scale_factors(history)
    snapshot_day_scales = recalibrate_snapshot_day_scale_factors(history)
    factors["snapshot_to_day_scale_factors"] = snapshot_day_scales
    factors["snapshot_to_lead_scale_factors"] = recalibrate_snapshot_lead_scale_factors(
        history,
        day_scales=snapshot_day_scales,
    )
    factors["snapshot_calibration_support"] = snapshot_calibration_support(history)

    return cal
