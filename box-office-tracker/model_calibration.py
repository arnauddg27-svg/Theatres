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
                day for day in ("Thursday", "Friday", "Saturday", "Sunday")
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
    scales: dict[str, float] = {
        day: 1.0 for day in ("Thursday", "Friday", "Saturday", "Sunday")
    }

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

        for day in ("Thursday", "Friday", "Saturday", "Sunday"):
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

    return cal
