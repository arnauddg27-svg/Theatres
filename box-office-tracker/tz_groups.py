"""Timezone legs for AMC collection, including Mountain time (2026-09-26).

MT was "intentionally omitted" until 2026-09-26: 18 core AMC theatres in CO/NM/
UT/MT/AZ were never collected. Arizona does not observe daylight saving, so its
clock matches Pacific time in summer and Mountain time in winter; an AZ theatre
is assigned to whichever leg shares its CURRENT UTC offset, so every
local-time computation (minutes until showtime, post-show timing, dates) stays
exact in both seasons.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

COLLECTION_GROUPS = ("ET", "CT", "MT", "PT")
ZONES = {"ET": "America/New_York", "CT": "America/Chicago",
         "MT": "America/Denver", "PT": "America/Los_Angeles"}


def effective_group(theatre, file_group, now=None):
    """Leg a theatre is collected in. Only Arizona (state AZ, filed under MT)
    can move: to PT while Phoenix and Los Angeles share an offset."""
    if file_group == "MT" and str(theatre.get("state") or "").upper() == "AZ":
        now = now or datetime.now(timezone.utc)
        if now.astimezone(ZoneInfo("America/Phoenix")).utcoffset() == \
                now.astimezone(ZoneInfo(ZONES["PT"])).utcoffset():
            return "PT"
    return file_group
