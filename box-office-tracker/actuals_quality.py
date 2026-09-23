"""Distinguish independently reported daily grosses from model-derived labels.

Keep original records intact. These filters affect fitting and forecast anchors,
not the stored weekend totals or historical audit trail.
"""
from math import isfinite
from copy import deepcopy
import re

OPENING_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
ESTIMATED_STATUSES = {"estimated", "imputed", "model-derived", "seat-derived"}


class ReportedDailyGrosses(dict):
    """A dict-compatible source result carrying the Thursday reporting convention."""
    def __init__(self, values, *, source_url="", non_preview_thursday=False):
        super().__init__(values)
        self.source_url = source_url
        self.non_preview_thursday = non_preview_thursday


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
    non_preview = getattr(daily, "non_preview_thursday", False)
    if (entry.get("daily_actuals") == clean and entry.get("daily_actuals_source") == source
            and entry.get("actual_total") == round(sum(clean.values()), 6)
            and bool(entry.get("previews_folded_into_friday")) == (clean.get("Thursday", 0) <= 0)
            and (not non_preview or (entry.get("non_preview_thursday")
                                     and entry.get("exclude_from_calibration")))
            and not estimated_actual_days(entry)):
        return False
    previous = deepcopy(entry)
    entry.update(daily_actuals=clean, actual_total=round(sum(clean.values()), 6),
                 actual_source=source, daily_actuals_source=source, actual_status="reported",
                 actuals_verified_at=as_of_date,
                 actuals_revision={"as_of_date": as_of_date, "previous": previous})
    entry.pop("estimated_daily_actual_days", None)
    if non_preview:
        entry["non_preview_thursday"] = True
        entry["exclude_from_calibration"] = True
        entry["calibration_exclusion_reason"] = "Regular Thursday for a non-Friday opener; not preview revenue."
    if clean.get("Thursday", 0) > 0:
        entry.pop("previews_folded_into_friday", None)
    else:
        entry["previews_folded_into_friday"] = True
    if "actual" in entry:
        entry["actual"] = entry["actual_total"]
    if entry.get("predicted_mid"):
        entry["error_pct"] = round(100 * (entry["predicted_mid"] / entry["actual_total"] - 1), 2)
    return True


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
