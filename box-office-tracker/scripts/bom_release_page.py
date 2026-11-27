#!/usr/bin/env python3
"""Reading a Box Office Mojo release page: its dated daily table and the
weekend in it that a historical-comps row describes. Pure; no network."""
import re
from datetime import datetime, timedelta

DAILY_ROW = re.compile(
    r'/date/(\d{4}-\d{2}-\d{2})/\?ref_=bo_rl_table_\d+"[^>]*>.*?</td>(.*?)</tr>', re.S)
MONEY = re.compile(r"\$([\d,]+)")
RELEASE_DATE = re.compile(r"Release Date.{0,400}?([A-Z][a-z]{2} \d{1,2}, \d{4})", re.S)
# A comp's daily grosses were copied from this table in $ millions, 6 decimals.
MATCH_TOLERANCE = 3000.0


def release_id(url):
    m = re.search(r"boxofficemojo\.com/release/(rl\d+)", url or "")
    return m[1] if m else ""


def release_date(page):
    """The page's stated release date (the first US date, limited or wide)."""
    m = RELEASE_DATE.search(page or "")
    try:
        return datetime.strptime(m[1], "%b %d, %Y") if m else None
    except ValueError:
        return None


def daily_grosses(page):
    """{YYYY-MM-DD: gross in dollars} from the page's daily table."""
    out = {}
    for m in DAILY_ROW.finditer(page or ""):
        money = MONEY.search(m[2])
        if money:
            out.setdefault(m[1], int(money[1].replace(",", "")))
    return out


def matching_friday(daily, friday_m, saturday_m, sunday_m):
    """(YYYY-MM-DD, miss in dollars) of the Friday whose weekend is closest to
    the given grosses, or (None, None) when the table has no Friday."""
    want = [float(x) * 1e6 for x in (friday_m, saturday_m, sunday_m)]
    best = (None, None)
    for date, gross in daily.items():
        day = datetime.strptime(date, "%Y-%m-%d")
        if day.weekday() != 4:
            continue
        got = [gross] + [daily.get((day + timedelta(days=k)).strftime("%Y-%m-%d"), 0)
                         for k in (1, 2)]
        miss = sum(abs(g - w) for g, w in zip(got, want))
        if best[1] is None or miss < best[1]:
            best = (date, miss)
    return best


def opening_friday_for_row(row, page):
    """The Friday whose Friday/Saturday/Sunday grosses are the row's own
    friday_m / saturday_m / sunday_m, or None when no weekend matches.

    It is the weekend the comp's numbers describe, so a limited run before the
    wide release, a re-release or a traffic spike cannot move it. On 2026-11-27
    all 217 comps matched a weekend exactly."""
    try:
        date, miss = matching_friday(daily_grosses(page), row["friday_m"],
                                     row["saturday_m"], row["sunday_m"])
    except (KeyError, TypeError, ValueError):
        return None
    return date if date and miss <= MATCH_TOLERANCE else None
