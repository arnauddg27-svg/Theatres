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
METADATA_CSV = Path(__file__).resolve().parent / "data" / "movie-metadata.csv"
LINKS_JSON = Path(__file__).resolve().parent / "data" / "showtime-links.json"
# A links file for the weekend with at least this many theatres counts as
# collect-links evidence that a title really is not booked anywhere on AMC.
MIN_LINKED_THEATRES_FOR_EVIDENCE = 50
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


def min_theatres():
    try:
        return int(os.environ.get("SMALL_FILM_MIN_THEATRES") or 100)
    except ValueError:
        return 100


def _opening_thursday_reached(weekend_of, today=None):
    from datetime import date, datetime, timedelta, timezone
    try:
        friday = date.fromisoformat(weekend_of)
    except ValueError:
        return False
    today = today or datetime.now(timezone.utc).date()
    return today >= friday - timedelta(days=1)


def tiny_release_titles(weekend_of, metadata_path=None, links_path=None, today=None):
    """{title key: reason} for films whose metadata theatre count is under
    min_theatres() AND that no AMC theatre lists in the weekend's links file.

    2026-11-03: Queen at Sea (BOM widest release: 1 theatre) was calendar-
    seeded, so every snapshot leg spent its 900 s repair budget rebuilding
    links that cannot exist. A $3M opening needs hundreds of theatres. The
    links file must cover the same weekend with ≥ MIN_LINKED_THEATRES_FOR_
    EVIDENCE theatres: a placeholder count on a real wide release is
    contradicted by the AMC listings and the film is kept.

    2026-11-12: Soul Patrol. Pre-release theatre counts are no longer trusted
    (cleared 2026-11-06), so its count was BLANK and the rule above could not
    fire: by opening Thursday no AMC theatre listed it while six other films
    had 279-442 theatres each, yet it kept a slate slot and every leg kept
    looking for its links. A film with no count and no AMC listing is gated
    too, but only from opening Thursday on — by then AMC has posted showtimes
    for every real wide release, and a title with no links yields no seats
    whether it is tracked or not."""
    if not enabled() or not weekend_of:
        return {}
    floor = min_theatres()
    candidates = {}
    unlisted_ok = _opening_thursday_reached(weekend_of, today)
    try:
        with open(metadata_path or METADATA_CSV, newline="") as f:
            for row in csv.DictReader(f):
                if (row.get("weekend_of") or "").strip() != weekend_of:
                    continue
                raw = (row.get("national_theatre_count") or "").strip()
                try:
                    count = int(float(raw))
                except ValueError:
                    if not raw and unlisted_ok:
                        candidates[title_key(row.get("movie"))] = None
                    continue
                if 0 < count < floor:
                    candidates[title_key(row.get("movie"))] = count
    except OSError:
        return {}
    if not candidates:
        return {}
    try:
        import json
        with open(links_path or LINKS_JSON) as f:
            links = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(links, dict) or (links.get("weekend_of") or links.get("date")) != weekend_of:
        return {}
    theatres = links.get("theatres") or {}
    if len(theatres) < MIN_LINKED_THEATRES_FOR_EVIDENCE:
        return {}
    linked = set()
    for entry in theatres.values():
        if not isinstance(entry, dict):
            continue
        for date_entry in (entry.get("dates") or {}).values():
            linked.update(title_key(m) for m in ((date_entry or {}).get("movies") or {}))
        linked.update(title_key(m) for m in (entry.get("movies") or {}))
    return {key: (f"{count} theatre(s) per metadata, no AMC listings" if count is not None
                  else "no theatre count and no AMC listings by opening Thursday")
            for key, count in candidates.items() if key not in linked}


def dropped_titles(weekend_of, path=None, metadata_path=None, links_path=None):
    """{title key: last mid $M, or a reason string} for films gated out of `weekend_of`."""
    if not enabled() or not weekend_of:
        return {}
    out = tiny_release_titles(weekend_of, metadata_path=metadata_path, links_path=links_path)
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
        return out
    floor, need = min_forecast_m(), consecutive()
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

        def why(t):
            v = dropped[title_key(t)]
            if isinstance(v, str):
                return v
            return f"${v:.2f}M — forecast under ${min_forecast_m():.1f}M on the last {consecutive()} calls"
        print(f"  ✂️  {label or 'slate'}: not collecting "
              f"{'; '.join(f'{t} ({why(t)})' for t in fresh)} (SMALL_FILM_GATE)")
    return kept
