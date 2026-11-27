"""Distinguish independently reported daily grosses from model-derived labels.

Keep original records intact. These filters affect fitting and forecast anchors,
not the stored weekend totals or historical audit trail.
"""
from math import isfinite
from copy import deepcopy
import re

OPENING_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
# Written into a daily-actual-overrides Thursday row when The Numbers ranks the
# day (the film was already open): a full day, not previews.
REGULAR_THURSDAY_NOTE = "regular Thursday"
ESTIMATED_STATUSES = {"estimated", "imputed", "model-derived", "seat-derived"}


class ReportedDailyGrosses(dict):
    """A dict-compatible source result carrying the Thursday reporting convention."""
    def __init__(self, values, *, source_url="", non_preview_thursday=False):
        super().__init__(values)
        self.source_url = source_url
        self.non_preview_thursday = non_preview_thursday


def standard_opening_total(daily, non_preview_thursday=False):
    """The 3-day opening: Friday-Sunday with Thursday PREVIEWS folded in.

    This is the number The Numbers publishes as the weekend, the trades quote
    and Polymarket settles on. A regular Thursday (the film opened Thursday or
    earlier, the row is ranked instead of "P") is an extra day, not previews:
    summing it recorded a 4-day figure as the opening (Ramayana 2026-11-06
    $12.45M vs the $8.94M weekend; The Amazing Digital Circus 2026-06-05
    $20.27M vs $12.39M) and settled paper bets in the wrong bracket."""
    return sum(float(v) for day, v in (daily or {}).items()
               if not (non_preview_thursday and day == "Thursday"))


def model_window_actual(entry):
    """Thursday-Sunday total, the window the seat model's headline covers.

    Equal to actual_total except for a film that opened before Friday, whose
    full Thursday is in the headline but not in the 3-day opening. Grade a
    model headline against this; settle markets against actual_total."""
    entry = entry or {}
    for key in ("actual_thu_sun_total", "actual_total", "actual"):
        try:
            value = float(entry.get(key))
        except (TypeError, ValueError):
            continue
        if isfinite(value) and value > 0:
            return value
    return None


def actuals_as_of(entry, cutoff):
    """Restore the record known before a date; new corrections cannot time travel.

    Revisions retain the complete prior record, including its provenance flags.
    Date-only revisions become usable the following day in historical replays.
    """
    result = deepcopy(entry)
    while result.get("actuals_revision"):
        revision = result["actuals_revision"]
        known = str(revision.get("as_of_date") or "")
        if known and known < cutoff:
            break
        previous = revision.get("previous")
        if not isinstance(previous, dict):
            break
        result = deepcopy(previous)
    return result


def revise_reported_daily_actuals(entry, daily, source, as_of_date):
    """Replace a sourced daily breakdown while preserving the prior training record."""
    clean = {day: float(value) for day, value in daily.items() if day in OPENING_DAYS}
    if (not source or not as_of_date or not {"Friday", "Saturday", "Sunday"}.issubset(clean)
            or any(not isfinite(v) or v < 0 for v in clean.values())
            or sum(clean.values()) <= 0):
        raise ValueError("A complete, finite, sourced Fri-Sun breakdown is required")
    non_preview = bool(getattr(daily, "non_preview_thursday", False))
    total = round(standard_opening_total(clean, non_preview), 6)
    thu_sun = round(sum(clean.values()), 6)
    if (entry.get("daily_actuals") == clean and entry.get("daily_actuals_source") == source
            and entry.get("actual_total") == total
            and bool(entry.get("previews_folded_into_friday")) == (clean.get("Thursday", 0) <= 0)
            and (not non_preview or (entry.get("non_preview_thursday")
                                     and entry.get("exclude_from_calibration")
                                     and entry.get("actual_thu_sun_total") == thu_sun))
            and not estimated_actual_days(entry)):
        return False
    previous = deepcopy(entry)
    entry.update(daily_actuals=clean, actual_total=total,
                 actual_source=source, daily_actuals_source=source, actual_status="reported",
                 actuals_verified_at=as_of_date,
                 actuals_revision={"as_of_date": as_of_date, "previous": previous})
    entry.pop("estimated_daily_actual_days", None)
    entry.pop("actual_thu_sun_total", None)
    if non_preview:
        entry["non_preview_thursday"] = True
        entry["exclude_from_calibration"] = True
        entry["calibration_exclusion_reason"] = "Regular Thursday for a non-Friday opener; not preview revenue."
        entry["actual_thu_sun_total"] = thu_sun
    if clean.get("Thursday", 0) > 0:
        entry.pop("previews_folded_into_friday", None)
    else:
        entry["previews_folded_into_friday"] = True
    if "actual" in entry:
        entry["actual"] = entry["actual_total"]
    regrade_entry(entry)
    return True


def regrade_entry(entry):
    """Recompute every stored error against the current actuals (pure).

    predicted_mid and the live headline cover Thursday-Sunday, so they are
    graded against model_window_actual; a corrected actual that left the old
    live_error_pct/checkpoint errors in place would keep reporting the stale
    grade (Primetime 2026-09-25: Sunday estimate $4.59M, final $4.22M)."""
    actual = model_window_actual(entry)
    if not actual:
        return entry
    if entry.get("predicted_mid"):
        entry["error_pct"] = round(100 * (entry["predicted_mid"] / actual - 1), 2)
    live = entry.get("live_headline")
    if isinstance(live, dict) and live.get("mid_m"):
        entry["live_error_pct"] = round(100 * (float(live["mid_m"]) / actual - 1), 1)
        if live.get("checkpoints"):
            from forecast_evaluation import grade_forecast_checkpoints
            live["checkpoints"] = grade_forecast_checkpoints(live["checkpoints"], actual)
    return entry


def model_derived_source(value):
    text = str(value or "").lower()
    return (any(word in text for word in ("derived", "imputed", "allocated", "estimated", "proportions"))
            and any(word in text for word in ("seat", "occupancy", "snapshot", "model")))


def estimated_actual_days(entry):
    """Explicit per-day flags first, with conservative legacy-source detection."""
    entry = entry or {}
    excluded = set(entry.get("estimated_daily_actual_days") or [])
    sources = entry.get("daily_actuals_source")
    if isinstance(sources, dict):
        excluded.update(day for day, source in sources.items() if model_derived_source(source))
    for source in (entry.get("actual_source"), sources if isinstance(sources, str) else ""):
        if not model_derived_source(source):
            continue
        # Legacy "Fri/Sat/Sun split derived from captured seat proportions"
        # leaves separately reported Thursday previews usable.
        text = str(source).lower()
        mentioned = {day for day in OPENING_DAYS
                     if re.search(r"\b(?:" + day.lower() + "|" + day[:3].lower() + r")\b", text)}
        excluded.update(mentioned or OPENING_DAYS)
    if str(entry.get("actual_status") or "").lower() in ESTIMATED_STATUSES:
        excluded.update(OPENING_DAYS)
    return excluded


def unusable_actual_days(entry):
    excluded = estimated_actual_days(entry)
    if (entry or {}).get("previews_folded_into_friday"):
        excluded.update(("Thursday", "Friday"))
    if (entry or {}).get("non_preview_thursday"):
        excluded.add("Thursday")
    return excluded


def independent_daily_actuals(entry):
    excluded = unusable_actual_days(entry)
    result = {}
    for day, raw in ((entry or {}).get("daily_actuals") or {}).items():
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if day in OPENING_DAYS and day not in excluded and isfinite(value) and value > 0:
            result[day] = value
    return result


def independent_daily_override(row):
    """Arithmetic subtraction of reported previews is valid; seat estimates aren't."""
    return (str(row.get("status") or "").lower() not in ESTIMATED_STATUSES
            and not model_derived_source(row.get("source"))
            and not model_derived_source(row.get("notes")))
