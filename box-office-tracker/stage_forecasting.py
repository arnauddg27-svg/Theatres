"""Choose direct daily evidence as the opening weekend progresses.

The snapshot total already combines observed grosses with reservations for
remaining days. A second generic Friday multiplier can discard that evidence.
Only sufficiently covered, historically supported snapshots may replace it.
"""
from math import isfinite

OPENING_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
MIN_SNAPSHOT_COVERAGE = 0.50
MIN_SNAPSHOT_SUPPORT = 0.20


def number(value):
    try:
        value = float(value)
        return value if isfinite(value) else None
    except (TypeError, ValueError):
        return None


def forecast_stage(pred):
    days = pred.get("daily_details") or {}
    if set(OPENING_DAYS).issubset(days):
        return "complete"
    for day, stage in (("Sunday", "after-sunday"), ("Saturday", "after-saturday"),
                       ("Friday", "after-friday"), ("Thursday", "after-previews")):
        if day in days:
            return stage
    return "presales"


def daily_evidence_candidate(pred):
    """Return a supported partial-weekend estimate, or None for the old model.

    Do not extrapolate from tiny reservation samples, use uncalibrated daily
    forecasts, or override completed weekends. All values remain in $millions.
    """
    observed = set(pred.get("daily_details") or {}) & set(OPENING_DAYS)
    if not observed or len(observed) == len(OPENING_DAYS):
        return None
    mid = number(pred.get("snapshot_mid_m"))
    low = number(pred.get("snapshot_low_m"))
    high = number(pred.get("snapshot_high_m"))
    coverage = number(pred.get("snapshot_model_coverage_ratio"))
    support = number(pred.get("snapshot_calibration_support_factor"))
    if (mid is None or mid <= 0 or low is None or high is None
            or not 0 <= low <= mid <= high
            or coverage is None or coverage < MIN_SNAPSHOT_COVERAGE
            or support is None or support < MIN_SNAPSHOT_SUPPORT):
        return None
    return {"mid_m": mid, "low_m": low, "high_m": high,
            "stage": forecast_stage(pred), "coverage": coverage, "support": support}
