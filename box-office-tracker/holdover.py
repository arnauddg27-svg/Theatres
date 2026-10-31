"""2nd/3rd-weekend (holdover) films that have a live Polymarket market.

2026-10-31: Polymarket lists "<film>" 2nd / 3rd Weekend Box Office markets
(Wildwood, Clayface, You Can See Everything), but every lane collected
opening weekends only, and the small-film gate had just emptied the slate.
A holdover with a live market is now collected on every lane like an opener
and forecast by holdover_forecast.py against its own opening weekend.

data/holdover-titles.csv is the append-only registry: one row per (weekend,
film). Every lane (via scraper.tracked_movie_titles_from_state) reads it and,
once per process, refreshes it from Polymarket, so a market listed mid-
weekend is picked up by the next run of any lane. Capacity: holdovers only
fill the slate up to MAX_TRACKED_TITLES films (6 = the most a weekend has
carried, 2026-10-23), openers first, then holdovers by market volume.

The opening-weekend model must never see these rows as an opening:
is_holdover() is checked by predict.py, calibrate.py and chain_census.py. It
is true for a registered (weekend, film) and, as a backstop when the registry
row never got committed, for any film with reported daily grosses from an
EARLIER weekend (it has already opened).

    python3 holdover.py --refresh     # registry from Polymarket, print slate
HOLDOVER_COLLECTION=0 turns collection off (the guards stay on).
"""
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
REGISTRY_CSV = DATA_DIR / "holdover-titles.csv"
DAILY_ACTUALS_CSV = DATA_DIR / "daily-actual-overrides.csv"
FIELDS = ["weekend_of", "movie", "weekend_num", "opening_weekend_of", "event_slug",
          "volume", "first_seen"]
SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
TITLE_RE = re.compile(r'^\s*"([^"]+)"\s+(\d+)(?:st|nd|rd|th)\s+weekend\s+box\s+office\s*$', re.I)
_LIVE_DONE = set()


def _env_int(name, default):
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def enabled():
    return (os.environ.get("HOLDOVER_COLLECTION") or "1").strip().lower() not in ("0", "false", "off", "no")


def max_week():
    return _env_int("HOLDOVER_MAX_WEEK", 3)


def max_tracked_titles():
    return _env_int("HOLDOVER_MAX_TRACKED_TITLES", 6)


def title_key(title):
    text = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    text = re.sub(r"^(the|a|an)\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def parse_event_title(title):
    """'"Wildwood" 2nd Weekend Box Office' -> ('Wildwood', 2); else None."""
    m = TITLE_RE.match((title or "").replace("“", '"').replace("”", '"'))
    if not m:
        return None
    n = int(m.group(2))
    return (m.group(1).strip(), n) if n >= 2 else None


def event_weekend(end_date):
    """The Friday on or before the market's end (markets end Sun/Mon)."""
    try:
        end = datetime.fromisoformat(str(end_date).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return (end - timedelta(days=(end.weekday() - 4) % 7)).strftime("%Y-%m-%d")


def entries_from_events(events, now=None):
    """Registry rows for active Nth-weekend events (2 <= N <= max_week())."""
    now = now or datetime.now(timezone.utc)
    out = {}
    for ev in events or []:
        if ev.get("closed") or ev.get("archived"):
            continue
        parsed = parse_event_title(ev.get("title"))
        if not parsed or parsed[1] > max_week():
            continue
        movie, n = parsed
        weekend = event_weekend(ev.get("endDate"))
        if not weekend:
            continue
        opening = (datetime.strptime(weekend, "%Y-%m-%d") - timedelta(days=7 * (n - 1))).strftime("%Y-%m-%d")
        try:
            volume = round(float(ev.get("volume") or 0), 2)
        except (TypeError, ValueError):
            volume = 0.0
        key = (weekend, title_key(movie))
        if key not in out or volume > out[key]["volume"]:
            out[key] = {"weekend_of": weekend, "movie": movie, "weekend_num": n,
                        "opening_weekend_of": opening, "event_slug": ev.get("slug", ""),
                        "volume": volume, "first_seen": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    return list(out.values())


def fetch_events(timeout=20):
    params = {"q": "weekend box office", "limit_per_type": 50, "events_status": "active"}
    req = urllib.request.Request(f"{SEARCH_URL}?{urllib.parse.urlencode(params)}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return data.get("events", []) if isinstance(data, dict) else (data or [])


def load(path=None):
    path = Path(path or REGISTRY_CSV)
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def register(entries, path=None):
    """Append entries not yet in the registry; returns the new rows."""
    path = Path(path or REGISTRY_CSV)
    have = {(r.get("weekend_of"), title_key(r.get("movie"))) for r in load(path)}
    new = [e for e in entries if (e["weekend_of"], title_key(e["movie"])) not in have]
    if new:
        fresh = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if fresh:
                w.writeheader()
            w.writerows(new)
    return new


def refresh(path=None, events=None, now=None):
    """Registry rows from Polymarket (best effort); returns the new rows."""
    try:
        events = fetch_events() if events is None else events
    except Exception as exc:
        print(f"  ⚠️  holdover markets: Polymarket fetch failed ({type(exc).__name__}: {exc})")
        return []
    new = register(entries_from_events(events, now), path)
    for e in new:
        print(f"  🎟️  holdover market: {e['movie']} weekend {e['weekend_num']} ({e['weekend_of']}, "
              f"opened {e['opening_weekend_of']}, vol ${float(e['volume']):,.0f})")
    return new


def entries(weekend_of, path=None):
    """Registry rows for `weekend_of`, highest market volume first."""
    rows = [r for r in load(path) if r.get("weekend_of") == weekend_of]

    def vol(r):
        try:
            return float(r.get("volume") or 0)
        except ValueError:
            return 0.0
    return sorted(rows, key=vol, reverse=True)


def _opened_before(weekend_of, path=None):
    """{title key} with reported daily grosses from a weekend before this one."""
    out = set()
    try:
        with open(path or DAILY_ACTUALS_CSV, newline="") as f:
            for r in csv.DictReader(f):
                w = (r.get("weekend_of") or "").strip()
                try:
                    gross = float(r.get("gross_m") or 0)
                except ValueError:
                    continue
                if w and w < weekend_of and gross > 0:
                    out.add(title_key(r.get("movie_title")))
    except OSError:
        pass
    return out


def holdover_keys(weekend_of, path=None, actuals_path=None):
    if not weekend_of:
        return set()
    return ({title_key(r.get("movie")) for r in entries(weekend_of, path)}
            | _opened_before(weekend_of, actuals_path))


def is_holdover(title, weekend_of, path=None, actuals_path=None):
    return title_key(title) in holdover_keys(weekend_of, path, actuals_path)


def without_holdovers(titles, weekend_of, label="", path=None, actuals_path=None):
    """`titles` minus holdovers (order kept), for the opening-weekend model."""
    titles = list(titles or [])
    keys = holdover_keys(weekend_of, path, actuals_path)
    kept = [t for t in titles if title_key(t) not in keys]
    gone = [t for t in titles if title_key(t) in keys]
    if gone and label:
        print(f"  ↷ {label}: {', '.join(gone)} — holdover (not an opening), see holdover_forecast.py")
    return kept


def collection_titles(weekend_of, openers, path=None, live=True):
    """Holdover titles to collect on top of `openers` for `weekend_of`."""
    if not enabled() or not weekend_of:
        return []
    if live and weekend_of not in _LIVE_DONE:
        _LIVE_DONE.add(weekend_of)
        refresh(path)
    have = {title_key(t) for t in openers or []}
    room = max(0, max_tracked_titles() - len(have))
    picked, skipped = [], []
    for r in entries(weekend_of, path):
        if title_key(r["movie"]) in have:
            continue
        (picked if len(picked) < room else skipped).append(r["movie"])
        have.add(title_key(r["movie"]))
    if skipped:
        print(f"  ↷ holdover: no room for {', '.join(skipped)} "
              f"(slate capped at {max_tracked_titles()} films, HOLDOVER_MAX_TRACKED_TITLES)")
    return picked


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--refresh" in argv:
        refresh()
    now = datetime.now(timezone.utc)
    fri = now - timedelta(days=(now.weekday() - 4) % 7)
    weekend = fri.strftime("%Y-%m-%d")
    rows = entries(weekend)
    print(f"holdover markets for weekend {weekend}: "
          + (", ".join(f"{r['movie']} (wk {r['weekend_num']})" for r in rows) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
