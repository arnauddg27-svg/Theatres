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


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _as_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coverage_score(n_theatres: int | float = 0,
                   n_days: int | float = 0) -> float:
    """How much we should trust a calibration datapoint, on a 0-1 scale."""
    theatre_component = clamp(_as_float(n_theatres, 0.0) / 400.0, 0.0, 1.0)
    day_component = clamp(_as_float(n_days, 0.0) / 4.0, 0.0, 1.0)
    return 0.6 * day_component + 0.4 * theatre_component


def bounded_scale_ratio(actual_total: float,
                        predicted_total: float,
                        n_theatres: int | float = 0,
                        n_days: int | float = 0) -> float | None:
    """Convert one historical result into a bounded calibration ratio."""
    actual = _as_float(actual_total, 0.0)
    predicted = _as_float(predicted_total, 0.0)
    if actual <= 0 or predicted <= 0:
        return None

    raw_ratio = actual / predicted
    trust = coverage_score(n_theatres=n_theatres, n_days=n_days)
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
        ratio = bounded_scale_ratio(
            actual_total=actual,
            predicted_total=predicted,
            n_theatres=n_theatres,
            n_days=n_days,
        )
        if ratio is None:
            continue
        scale = alpha * ratio + (1.0 - alpha) * scale

    return round(clamp(scale, MIN_SCALE_FACTOR, MAX_SCALE_FACTOR), 4)


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

    return cal
