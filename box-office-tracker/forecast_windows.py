"""Keep a Thu-Sun model subtotal separate from extended market settlement windows.

Verified rules (2026-09-19):
https://polymarket.com/event/minions-monsters-opening-weekend-box-office
https://polymarket.com/event/the-mandalorian-and-grogu-4-day-opening-weekend-box-office
"""
import re

KNOWN_EXTENDED = {
    ('minionsmonsters', '2026-07-03'): ('Wednesday-Sunday (5 days)', 'Wednesday'),
    ('themandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
    ('starwarsthemandalorianandgrogu', '2026-05-22'): ('Friday-Monday including previews (4 days)', 'Monday'),
}


def window_profile(movie, weekend_of, markets=()):
    key=re.sub(r'[^a-z0-9]','',movie.lower())
    extended=KNOWN_EXTENDED.get((key,weekend_of))
    if not extended:
        text=' '.join(str(m.get(k) or '') for m in markets or []
                      for k in ('question','market_question','market_url','description','rules','slug','notes'))
        match=re.search(r'\b(4|5|four|five)[\s-]*day\b',text,re.I)
        if match:extended=(f'{match[1]}-day opening', 'dates outside the model window')
    return {
        'model_gross_window': 'Thursday-Sunday',
        'market_window_compatible': not bool(extended),
        'market_gross_window': extended[0] if extended else 'standard opening assumed; previews included',
        'market_window_warning': (f'Model covers Thursday-Sunday; this market also needs {extended[1]}. '
                                  'Market comparison unavailable for this subtotal.') if extended else '',
    }
