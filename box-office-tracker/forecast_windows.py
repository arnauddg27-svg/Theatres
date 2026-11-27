"""Keep a Thu-Sun model subtotal separate from the window a market settles on.

Verified rules (2026-09-19):
https://polymarket.com/event/minions-monsters-opening-weekend-box-office
https://polymarket.com/event/the-mandalorian-and-grogu-4-day-opening-weekend-box-office

2026-11-27: a film that opens BEFORE Friday is also off-window on a standard
3-day market. The model's Thursday-Sunday subtotal then holds a full opening
Thursday that the Friday-Sunday opening excludes (Ramayana 2026-11-06: headline
$12.35M, market settled $8-9M on an $8.94M weekend, and 12 paper bets were
placed and scored against the wrong window).
"""
import json
import os
import re
from datetime import datetime

from actuals_quality import REGULAR_THURSDAY_NOTE

RELEASE_CALENDAR_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "data", "release-calendar.json")

KNOWN_EXTENDED = {
    ('minionsmonsters', '2026-07-03'): ('Wednesday-Sunday (5 days)', 'Wednesday'),
    ('themandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
    ('starwarsthemandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
}


def _key(title):
    text = re.sub(r'[^a-z0-9 ]', ' ', (title or '').lower())
    return re.sub(r'[^a-z0-9]', '', re.sub(r'^\s*(the|a|an)\s+', '', text))


def _calendar_release_date(movie, weekend_of, calendar_path=None):
    """Release date (date) from the BOM calendar fetched for this weekend."""
    try:
        with open(calendar_path or RELEASE_CALENDAR_JSON) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if data.get('weekend_of') != weekend_of:
        return None
    for item in data.get('titles') or []:
        if _key(item.get('title')) != _key(movie):
            continue
        for fmt in ('%B %d, %Y', '%b %d, %Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(str(item.get('date') or '').strip(), fmt).date()
            except ValueError:
                continue
    return None


def opened_before_friday(movie, weekend_of, overrides=None, calendar_path=None):
    """True when the film's first day precedes the opening Friday.

    Known before the weekend from the release calendar (refreshed by every
    collect-links run) and confirmed after it by The Numbers ranking the
    Thursday row (fetch_daily_actuals marks that row REGULAR_THURSDAY_NOTE)."""
    for title, days in (overrides or {}).items():
        if _key(title) != _key(movie) or not isinstance(days, dict):
            continue
        thursday = days.get('Thursday')
        if isinstance(thursday, dict) and REGULAR_THURSDAY_NOTE in str(thursday.get('notes') or ''):
            return True
    try:
        friday = datetime.strptime(str(weekend_of), '%Y-%m-%d').date()
    except ValueError:
        return False
    released = _calendar_release_date(movie, weekend_of, calendar_path)
    return bool(released and 0 < (friday - released).days <= 6)


def window_profile(movie, weekend_of, markets=(), early_opening=False):
    key=re.sub(r'[^a-z0-9]','',movie.lower())
    extended=KNOWN_EXTENDED.get((key,weekend_of))
    if not extended:
        text=' '.join(str(m.get(k) or '') for m in markets or []
                      for k in ('question','market_question','market_url','description','rules','slug','notes'))
        match=re.search(r'\b(4|5|four|five)[\s-]*day\b',text,re.I)
        if match:extended=(f'{match[1]}-day opening', 'dates outside the model window')
    if extended:
        market_window, warning = extended[0], (
            f'Model covers Thursday-Sunday; this market also needs {extended[1]}. '
            'Market comparison unavailable for this subtotal.')
    elif early_opening:
        market_window, warning = 'Friday-Sunday (3 days); the film opened before Friday', (
            'Model covers Thursday-Sunday including a full opening Thursday; the market '
            'counts Friday-Sunday. Market comparison unavailable for this subtotal.')
    else:
        market_window, warning = 'standard opening assumed; previews included', ''
    return {
        'model_gross_window': 'Thursday-Sunday',
        'market_window_compatible': not (extended or early_opening),
        'market_gross_window': market_window,
        'market_window_warning': warning,
    }
