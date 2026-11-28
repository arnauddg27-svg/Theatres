"""Keep a Thu-Sun model subtotal separate from extended market settlement windows.

Verified rules (2026-09-19):
https://polymarket.com/event/minions-monsters-opening-weekend-box-office
https://polymarket.com/event/the-mandalorian-and-grogu-4-day-opening-weekend-box-office

2026-11-27: the rules now spell the settlement dates out -- "3-day opening
weekend (November 13 - 15)", "5-day Thanksgiving opening weekend (Wednesday,
November 25 - Sunday, November 29)" -- so market_frame() reads the window
itself instead of only flagging "not ours". predict.py uses it to state the
model's number over the market's own dates for films that open before Friday.
"""
import re
from datetime import date, datetime, timedelta

KNOWN_EXTENDED = {
    ('minionsmonsters', '2026-07-03'): ('Wednesday-Sunday (5 days)', 'Wednesday'),
    ('themandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
    ('starwarsthemandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
}
KNOWN_FRAMES = {
    ('minionsmonsters', '2026-07-03'): ('2026-07-01', '2026-07-05'),
}
TEXT_FIELDS = ('question', 'market_question', 'market_url', 'description', 'rules', 'slug', 'notes')
_MONTHS = {m: i for i, m in enumerate(
    ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
     'september', 'october', 'november', 'december'), 1)}
_MONTH_RE = '|'.join(_MONTHS)
_DAY_RE = r'(?:(?:mon|tues|wednes|thurs|fri|satur|sun)day,?\s+)?'
# "(Wednesday, November 25 - Sunday, November 29)" / "(November 13 - 15)" / "(December 31 - January 2)"
_FRAME_RE = re.compile(
    rf'\(\s*{_DAY_RE}({_MONTH_RE})\s+(\d{{1,2}})\s*[-–—]\s*{_DAY_RE}(?:({_MONTH_RE})\s+)?(\d{{1,2}})\s*\)',
    re.I)


def _markets_text(markets):
    return ' '.join(str(m.get(k) or '') for m in markets or [] if isinstance(m, dict) for k in TEXT_FIELDS)


def market_frame(movie, weekend_of, markets=()):
    """(start, end) ISO dates the market settles on, or None when not stated.

    Only a window that touches the opening week (the Friday within it, at most
    ten days long) is accepted; anything else is prose, not a settlement frame."""
    key = re.sub(r'[^a-z0-9]', '', (movie or '').lower())
    if (key, weekend_of) in KNOWN_FRAMES:
        return KNOWN_FRAMES[(key, weekend_of)]
    try:
        friday = datetime.strptime(str(weekend_of), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None
    for match in _FRAME_RE.finditer(_markets_text(markets)):
        m1, d1, m2, d2 = match.groups()
        month1 = _MONTHS[m1.lower()]
        month2 = _MONTHS[m2.lower()] if m2 else month1
        for year in (friday.year, friday.year - 1):
            try:
                start = date(year, month1, int(d1))
                end = date(year + (1 if month2 < month1 else 0), month2, int(d2))
            except ValueError:
                continue
            if start <= friday <= end and (end - start).days < 10:
                return start.isoformat(), end.isoformat()
    return None


def window_profile(movie, weekend_of, markets=()):
    key = re.sub(r'[^a-z0-9]', '', movie.lower())
    extended = KNOWN_EXTENDED.get((key, weekend_of))
    frame = market_frame(movie, weekend_of, markets)
    if not extended:
        match = re.search(r'\b(4|5|four|five)[\s-]*day\b', _markets_text(markets), re.I)
        if match:
            extended = (f'{match[1]}-day opening', 'dates outside the model window')
    if not extended and frame:
        # Stated dates that run past the model's Thursday-Sunday on either side.
        friday = datetime.strptime(weekend_of, '%Y-%m-%d').date()
        if frame[0] < (friday - timedelta(days=1)).isoformat() or frame[1] > (friday + timedelta(days=2)).isoformat():
            extended = (f'{frame[0]} to {frame[1]}', 'dates outside the model window')
    return {
        'model_gross_window': 'Thursday-Sunday',
        'market_window_compatible': not bool(extended),
        'market_gross_window': extended[0] if extended else 'standard opening assumed; previews included',
        'market_window_warning': (f'Model covers Thursday-Sunday; this market also needs {extended[1]}. '
                                  'Market comparison unavailable for this subtotal.') if extended else '',
        'market_frame_start': frame[0] if frame else '',
        'market_frame_end': frame[1] if frame else '',
    }
