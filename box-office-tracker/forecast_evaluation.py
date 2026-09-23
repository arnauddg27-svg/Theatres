"""Fixed-clock forecast checkpoints from immutable live logs."""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from math import isfinite

CHECKPOINTS = {"tuesday_noon_et": -3, "thursday_noon_et": -1,
               "friday_noon_et": 0, "saturday_noon_et": 1, "sunday_noon_et": 2}


def utc_timestamp(value):
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return stamp.astimezone(timezone.utc) if stamp.tzinfo is not None else None
    except (TypeError, ValueError):
        return None


def select_forecast_checkpoints(rows, weekend_of, max_age_hours=24):
    """Last valid run at or BEFORE each deadline; stale/missing stays missing.

    Rows must already be restricted to one film. Noon ET is explicit and
    daylight-saving aware. Later runs cannot replace earlier checkpoint calls.
    """
    try:
        friday = datetime.strptime(weekend_of, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return {}
    candidates = []
    for row in rows:
        if row.get("weekend_of") != weekend_of:
            continue
        stamp = utc_timestamp(row.get("logged_at"))
        try:
            mid = float(row.get("headline_mid_m"))
        except (TypeError, ValueError):
            continue
        if stamp and isfinite(mid) and mid > 0:
            candidates.append((stamp, row, mid))
    result = {}
    for name, offset in CHECKPOINTS.items():
        cutoff = datetime.combine(friday + timedelta(days=offset), time(12),
                                  tzinfo=ZoneInfo("America/New_York")).astimezone(timezone.utc)
        eligible = [r for r in candidates if cutoff - timedelta(hours=max_age_hours) <= r[0] <= cutoff]
        if not eligible:
            continue
        stamp, row, mid = max(eligible, key=lambda item: item[0])
        result[name] = {"mid_m": mid, "logged_at": stamp.isoformat().replace("+00:00", "Z"),
                        "cutoff": cutoff.isoformat().replace("+00:00", "Z"),
                        "source": row.get("source", "")}
        for field in ("model_version", "forecast_stage", "model_gross_window", "market_window_compatible"):
            if row.get(field):
                result[name][field] = row[field]
        try:
            baseline = float(row.get("baseline_mid_m"))
            if isfinite(baseline) and baseline > 0:
                result[name]["baseline_mid_m"] = baseline
        except (TypeError, ValueError):
            pass
        for field in ("low", "high"):
            try:
                value = float(row.get(f"headline_{field}_m"))
            except (TypeError, ValueError):
                continue
            if isfinite(value) and value >= 0:
                result[name][f"{field}_m"] = value
    return result


def grade_forecast_checkpoints(checkpoints, actual_total):
    """Grade saved checkpoints without substituting later forecasts or replays."""
    result = {}
    for name, checkpoint in (checkpoints or {}).items():
        item = dict(checkpoint)
        mid = item.get("mid_m")
        if actual_total > 0 and mid is not None and isfinite(float(mid)):
            item["error_pct"] = round(100 * (float(mid) / actual_total - 1), 2)
            baseline = item.get("baseline_mid_m")
            if baseline is not None:
                item["baseline_error_pct"] = round(100 * (baseline / actual_total - 1), 2)
                item["absolute_error_improvement_pp"] = round(
                    abs(item["baseline_error_pct"]) - abs(item["error_pct"]), 2)
            low, high = item.get("low_m"), item.get("high_m")
            item["in_range"] = low <= actual_total <= high if low is not None and high is not None else None
        result[name] = item
    return result
