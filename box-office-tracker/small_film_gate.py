"""Stop collecting films whose live forecast is clearly under $3M.

2026-10-23: the user only needs films that open above $3M, and the calendar
seeding (2026-10-18) pulls in every wide release — Klara and the Sun ($0.9M)
and A Talent for Murder ($0.4M) took ~25% of AMC's Friday seat reads. A title
is dropped for its weekend once its last SMALL_FILM_CONSECUTIVE logged live
forecasts (data/prediction-log.csv, positive mids only) are all under
SMALL_FILM_MIN_M. The floor is $1.5M, not $3M: early calls have run up to
2.7x low (Heart of the Beast after previews $7.4M -> $20.0M), so a $1.5M call
tops out near $4M. A film with no forecast yet (new, or no seat evidence) is
always kept. Once dropped, no new rows are logged for it, so the decision is
stable for the weekend. SMALL_FILM_GATE=0 turns it off.

Every collection lane funnels through scraper.tracked_movie_titles_from_state
/ select_collection_markets; collect_links_dedup_guard, predict.py (live runs)
and calibrate.py filter here too so a half-collected film is never forecast or
graded.
"""
import csv
import os
import re
from pathlib import Path

PREDICTION_LOG = Path(__file__).resolve().parent / "data" / "prediction-log.csv"
_REPORTED = set()


def title_key(title):
    text = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    text = re.sub(r"^(the|a|an)\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def enabled():
    return (os.environ.get("SMALL_FILM_GATE") or "1").strip().lower() not in ("0", "false", "off", "no")


def min_forecast_m():
    try:
        return float(os.environ.get("SMALL_FILM_MIN_M") or 1.5)
    except ValueError:
        return 1.5


def consecutive():
    try:
        return max(1, int(os.environ.get("SMALL_FILM_CONSECUTIVE") or 2))
    except ValueError:
        return 2


def dropped_titles(weekend_of, path=None):
    """{title key: last mid $M} for films gated out of `weekend_of`."""
    if not enabled() or not weekend_of:
        return {}
    mids = {}
    try:
        with open(path or PREDICTION_LOG, newline="") as f:
            for row in csv.DictReader(f):
                if (row.get("weekend_of") or "").strip() != weekend_of:
                    continue
                try:
                    mid = float(row.get("headline_mid_m") or 0)
                except ValueError:
                    continue
                if mid > 0:
                    mids.setdefault(title_key(row.get("movie")), []).append(((row.get("logged_at") or ""), mid))
    except OSError:
        return {}
    floor, need = min_forecast_m(), consecutive()
    out = {}
    for key, series in mids.items():
        last = [m for _, m in sorted(series)[-need:]]
        if len(last) >= need and all(m < floor for m in last):
            out[key] = last[-1]
    return out


def is_dropped(title, weekend_of, path=None):
    return title_key(title) in dropped_titles(weekend_of, path=path)


def filter_titles(titles, weekend_of, label="", path=None):
    """`titles` minus gated films (order kept); prints each drop once per process."""
    titles = list(titles or [])
    dropped = dropped_titles(weekend_of, path=path)
    if not dropped:
        return titles
    kept, gone = [], []
    for t in titles:
        (gone if title_key(t) in dropped else kept).append(t)
    fresh = [t for t in gone if (weekend_of, title_key(t)) not in _REPORTED]
    if fresh:
        _REPORTED.update((weekend_of, title_key(t)) for t in fresh)
        print(f"  ✂️  {label or 'slate'}: not collecting {', '.join(f'{t} (${dropped[title_key(t)]:.2f}M)' for t in fresh)}"
              f" — forecast under ${min_forecast_m():.1f}M on the last {consecutive()} calls (SMALL_FILM_GATE)")
    return kept
