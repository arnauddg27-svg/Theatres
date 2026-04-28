#!/usr/bin/env python3
"""
Box Office Seat-Map Tracker (Playwright Edition)
=================================================
Scrapes Polymarket for active box-office betting markets,
then uses Playwright headless Chrome to fetch AMC seat maps
for occupancy data.

Usage:
    python3 scraper.py              # All theatres
    python3 scraper.py PT           # Pacific theatres only
    python3 scraper.py ET           # Eastern theatres only
"""

import asyncio
import csv
import json
import os
import random
import re
import signal
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid

import requests
from playwright.async_api import async_playwright

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SEAT_CSV = DATA_DIR / "seat-counts.csv"
POLY_CSV = DATA_DIR / "polymarket-markets.csv"
RUN_LOG  = DATA_DIR / "run-log.md"

THEATRES_JSON    = DATA_DIR / "theatres-all.json"
LINKS_JSON       = DATA_DIR / "showtime-links.json"   # Phase 1 output / Phase 2 input
THEATRE_COUNTS_JSON = DATA_DIR / "theatre-counts.json"  # National theatre counts from BOM


def load_theatres():
    """Load theatre list from JSON. Falls back to a minimal default."""
    if THEATRES_JSON.exists():
        with open(THEATRES_JSON, "r") as f:
            data = json.load(f)
        # Strip metadata keys
        return {k: v for k, v in data.items() if not k.startswith("_")}
    # Fallback: minimal set if JSON is missing
    return {
        "ET": [{"name": "AMC Empire 25", "slug": "amc-empire-25"}],
        "CT": [{"name": "AMC River East 21", "slug": "amc-river-east-21"}],
        "MT": [{"name": "AMC Westminster 24", "slug": "amc-westminster-24"}],
        "PT": [{"name": "AMC The Grove 14", "slug": "amc-the-grove-14"}],
    }

# AMC format priority (higher = bigger room, more important)
FORMAT_PRIORITY = {
    "imax with laser": 110,
    "imax": 100,
    "dolby cinema": 90,
    "dolby": 90,
    "prime": 80,
    "prime at amc": 80,
    "xl": 75,
    "laser at amc": 70,
    "laser": 70,
    "reald 3d": 30,
    "open caption": 20,
    "standard": 10,
    "digital": 10,
}

# Concurrency — 3 tabs on the 2GB VPS (Chromium base ~150MB + 3×75MB = ~375MB, well within limits).
MAX_CONCURRENT_TABS = 3
MAX_CONCURRENT_TABS_PHASE1 = 2

# Phase 2 runtime guards. A single hung Playwright navigation (typically caused
# by AMC's Queue-It safety net redirecting the VPS IP) used to stall the whole
# scrape for hours. The per-theatre timeout caps each tab; the overall deadline
# stops launching new theatres early enough for in-flight work and the commit
# step to finish inside the workflow's 75-minute step budget.
PHASE1_THEATRE_TIMEOUT_SEC = 90
PHASE2_THEATRE_TIMEOUT_SEC = 180
PHASE2_DEADLINE_SEC = 60 * 60   # 60 min — leaves 15 min for commit + push
try:
    PHASE1_MIN_FRESH_LINK_RATIO = float(os.getenv("PHASE1_MIN_FRESH_LINK_RATIO", "0.80"))
except ValueError:
    PHASE1_MIN_FRESH_LINK_RATIO = 0.80

# After the opening weekend closes, we still collect Mon-Wed seat maps for the
# same tracked title. Those weekday curves are calibration data; they should not
# be displaced by whatever future box-office market Polymarket surfaces next.
POST_WEEKEND_COLLECTION_WEEKDAYS = {0, 1, 2}  # Mon, Tue, Wed

# Rotate through realistic Chrome user agents to reduce rate-limiting.
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# Launch args that suppress headless-browser fingerprints detected by sites like AMC
# and minimise memory on the 458MB VPS.
_CHROMIUM_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1280,800",
    # Memory-saving flags for low-RAM VPS
    "--disable-extensions",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-default-apps",
    "--no-first-run",
    "--js-flags=--max-old-space-size=128",
]

# Injected into every page before any script runs — removes the webdriver flag
_STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
window.chrome = { runtime: {} };
"""

_TZ_NAMES = {"ET": "America/New_York", "CT": "America/Chicago",
             "MT": "America/Denver",   "PT": "America/Los_Angeles"}


def local_now(tz_group):
    """Return current datetime in the local timezone for a tz group.
    Uses Python's zoneinfo (stdlib 3.9+) so DST is handled automatically.
    Falls back to a fixed -5h offset if the tz name is unknown.
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(_TZ_NAMES.get(tz_group, "America/New_York"))
        return datetime.now(tz)
    except Exception:
        # Fallback: approximate offset (ET=-4 DST / -5 STD)
        fallback = {"ET": -4, "CT": -5, "MT": -6, "PT": -7}
        return datetime.now(timezone.utc) + timedelta(hours=fallback.get(tz_group, -5))


def local_date_str(tz_group):
    """Return today's date string in the local timezone of the tz group."""
    return local_now(tz_group).strftime("%Y-%m-%d")


def phase1_expected_date(tz_group):
    """Return the show date Phase 2 expects Phase 1 to have collected."""
    return (local_now(tz_group) - timedelta(hours=12)).strftime("%Y-%m-%d")


def opening_weekend_friday(dt=None):
    """Return the Friday that anchors this opening weekend.

    Thu→Sun all map to the same Friday. This is the 'weekend_of' key
    that lets predict.py group data from one opening weekend together
    and ignore data from previous weekends for the same movie.
    """
    dt = dt or datetime.now()
    weekday = dt.weekday()  # Mon=0 ... Sun=6
    if weekday == 3:    # Thursday → next Friday (new opening weekend)
        friday = dt + timedelta(days=1)
    elif weekday == 4:  # Friday
        friday = dt
    elif weekday == 5:  # Saturday
        friday = dt - timedelta(days=1)
    elif weekday == 6:  # Sunday
        friday = dt - timedelta(days=2)
    elif weekday == 0:  # Monday
        friday = dt - timedelta(days=3)
    elif weekday == 1:  # Tuesday
        friday = dt - timedelta(days=4)
    else:               # Wednesday
        friday = dt - timedelta(days=5)
    return friday.strftime("%Y-%m-%d")


# ─── Polymarket Scraper ─────────────────────────────────────────────────────

def _market_question_ceiling(question):
    """Approximate the highest bracket endpoint in a market question."""
    q = (question or "").lower()
    amounts = re.findall(r'\$(\d+(?:\.\d+)?)', q)
    if not amounts:
        amounts = re.findall(r'(?<![\w.])(\d+(?:\.\d+)?)\s*(?:m|million|mil)\b', q)
    amounts = [float(a) for a in amounts if float(a) >= 10]
    if not amounts:
        return 0.0

    if len(amounts) >= 2:
        return max(amounts)

    val = amounts[0]
    if any(w in q for w in ("over", "above", "more than", "higher than", "greater than", "exceed")):
        return val + 30.0
    return val


def _polymarket_event_score(market):
    """Score duplicate active events for the same movie."""
    bracket_markets = market.get("bracket_markets", [])
    max_ceiling = max(
        (_market_question_ceiling(b.get("market_question", "")) for b in bracket_markets),
        default=0.0,
    )
    is_ladder = len(bracket_markets) >= 3
    return (
        is_ladder,
        max_ceiling,
        len(bracket_markets),
        float(market.get("volume", 0) or 0),
    )


def fetch_polymarket_box_office():
    """
    Find active opening-weekend box office bracket events on Polymarket.

    Uses the same logic as trade.py: searches the Gamma events API for
    events with "opening weekend" AND "box office" in the title, then
    extracts the quoted movie name. This ensures scraper.py collects
    seat data for exactly the movies trade.py will try to trade.

    Returns list of dicts with movie info.
    """
    print("\n📊 Checking Polymarket for active box office markets...")

    url = "https://gamma-api.polymarket.com/events"
    params = {
        "active": "true",
        "closed": "false",
        "limit": 500,
        "order": "volume24hr",
        "ascending": "false",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        events = resp.json()
    except Exception as e:
        print(f"  ❌ Polymarket API error: {e}")
        return []

    candidates_by_movie = {}

    for event in events:
        title = event.get("title", "")
        title_lower = title.lower()

        # Same filter as trade.py: must have BOTH keywords
        if "opening weekend" not in title_lower or "box office" not in title_lower:
            continue
        if is_comparison_box_office_market(title):
            print(f"    ↷ Skipping comparison market: {title}")
            continue

        # Extract movie name from quoted title (e.g. "Thunderbolts" Opening Weekend...)
        raw_title = title.replace("\u201c", '"').replace("\u201d", '"')
        movie_name = None
        if '"' in raw_title:
            parts = raw_title.split('"')
            if len(parts) >= 3:
                movie_name = parts[1]

        if not movie_name:
            movie_name = extract_movie_title(title)

        slug = event.get("slug", "")
        event_url = f"https://polymarket.com/event/{slug}"
        total_volume = 0

        # Extract individual bracket markets (one per question/price pair)
        bracket_markets = []
        for m in event.get("markets", []):
            vol = float(m.get("volume", 0) or 0)
            total_volume += vol
            bracket_markets.append({
                "market_question": m.get("question", ""),
                "outcome_prices": m.get("outcomePrices", ""),
                "volume": vol,
                "market_id": str(m.get("id", "")),
            })

        market = {
            "movie_title": movie_name,
            "market_url": event_url,
            "question": title,
            "current_odds": "N/A",
            "volume": total_volume,
            "market_id": str(event.get("id", "")),
            "bracket_markets": bracket_markets,
        }
        candidates_by_movie.setdefault(movie_name, []).append(market)

    markets_found = []
    for movie_name, candidates in candidates_by_movie.items():
        best = max(candidates, key=_polymarket_event_score)
        skipped = [c for c in candidates if c is not best]
        if skipped:
            print(
                f"    ↷ {movie_name}: selected {best['market_url'].rsplit('/', 1)[-1]} "
                f"over {len(skipped)} older/alternate event(s)"
            )
        markets_found.append(best)

    print(f"  Found {len(markets_found)} box office movie(s)")
    for m in markets_found:
        print(f"    • {m['movie_title']} (vol: ${m['volume']:,.0f})")

    return markets_found


def load_movies_from_csv(weekend_of):
    """
    Fallback: read movie titles and market URLs from polymarket-markets.csv
    for the given opening weekend. Used Mon-Wed after the Polymarket market
    has closed but we still want to collect seat data through Wednesday.

    Filters rows by matching their date's opening_weekend_friday() to
    weekend_of, so we never bleed in movies from prior weekends.

    Returns list of dicts with movie_title and market_url (same shape as
    fetch_polymarket_box_office(), minus bracket_markets).
    """
    if not POLY_CSV.exists():
        return []
    seen = {}
    with open(POLY_CSV, "r") as f:
        for row in csv.DictReader(f):
            date_str = row.get("date", "").strip()
            title    = row.get("movie_title", "").strip()
            url      = row.get("market_url", "").strip()
            question = row.get("market_question", "").strip()
            if not title or not date_str:
                continue
            if is_comparison_box_office_market(question or title):
                continue
            try:
                row_dt = datetime.strptime(date_str, "%Y-%m-%d")
                row_weekend = opening_weekend_friday(row_dt)
            except ValueError:
                continue
            if row_weekend != weekend_of:
                continue
            if title not in seen:
                seen[title] = url
    if not seen:
        return []
    markets = [{"movie_title": t, "market_url": u, "bracket_markets": []}
               for t, u in seen.items()]
    print(f"  ↩️  Polymarket market closed — falling back to {len(markets)} movie(s) "
          f"from saved CSV (weekend_of={weekend_of})")
    for m in markets:
        print(f"    • {m['movie_title']}")
    return markets


def latest_market_urls_from_csv():
    """Return latest known Polymarket event URL per movie title."""
    urls = {}
    if not POLY_CSV.exists():
        return urls
    with open(POLY_CSV, "r") as f:
        for row in csv.DictReader(f):
            title = row.get("movie_title", "").strip()
            url = row.get("market_url", "").strip()
            question = row.get("market_question", "").strip()
            if not title or is_comparison_box_office_market(question or title):
                continue
            urls[title] = url
    return urls


def unique_preserving_order(values):
    seen = set()
    ordered = []
    for value in values:
        cleaned = (value or "").strip()
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered


def tracked_movie_titles_from_state(weekend_of):
    """Load the current collection-window movie list from durable state.

    The Polymarket CSV date is the date we observed a market, not the movie's
    release weekend. Persisted Phase 1 links and theatre-count metadata are the
    reliable source for "what title are we still collecting this week?"
    """
    titles = []

    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                links_data = json.load(f)
            links_weekend = links_data.get("weekend_of") or links_data.get("date", "")
            if links_weekend == weekend_of:
                for entry in links_data.get("theatres", {}).values():
                    titles.extend((entry.get("movies") or {}).keys())
        except Exception as e:
            print(f"  ⚠️  Could not read tracked movies from showtime links: {e}")

    if THEATRE_COUNTS_JSON.exists():
        try:
            with open(THEATRE_COUNTS_JSON) as f:
                counts_data = json.load(f)
            updated = counts_data.get("_updated", "")
            updated_weekend = ""
            if updated:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                updated_weekend = opening_weekend_friday(updated_dt)
            if updated_weekend == weekend_of:
                titles.extend(counts_data.get("_requested_movies") or [])
        except Exception as e:
            print(f"  ⚠️  Could not read tracked movies from theatre counts: {e}")

    return unique_preserving_order(titles)


def markets_for_tracked_titles(movie_titles, live_markets=None):
    """Build market records for tracked titles, reusing live bracket data when available."""
    live_by_title = {
        m.get("movie_title", "").lower(): m
        for m in (live_markets or [])
        if m.get("movie_title")
    }
    latest_urls = latest_market_urls_from_csv()
    markets = []
    for title in unique_preserving_order(movie_titles):
        live_market = live_by_title.get(title.lower())
        if live_market:
            markets.append(live_market)
            continue
        markets.append({
            "movie_title": title,
            "market_url": latest_urls.get(title, ""),
            "question": "",
            "current_odds": "N/A",
            "volume": 0,
            "market_id": "",
            "bracket_markets": [],
        })
    return markets


def select_collection_markets(live_markets, ref_dt, phase_label):
    """Choose which movie markets drive the data-collection run."""
    weekend = opening_weekend_friday(ref_dt)
    tracked_titles = tracked_movie_titles_from_state(weekend)

    if ref_dt.weekday() in POST_WEEKEND_COLLECTION_WEEKDAYS and tracked_titles:
        markets = markets_for_tracked_titles(tracked_titles, live_markets)
        live_titles = unique_preserving_order(m.get("movie_title", "") for m in live_markets)
        if live_titles and set(t.lower() for t in live_titles) != set(t.lower() for t in tracked_titles):
            print(
                f"  ↩️  {phase_label}: continuing tracked collection title(s) "
                f"{', '.join(tracked_titles)} for weekend {weekend}; "
                f"ignoring live future/other market(s): {', '.join(live_titles)}"
            )
        else:
            print(
                f"  ↩️  {phase_label}: continuing tracked collection title(s) "
                f"{', '.join(tracked_titles)} for weekend {weekend}"
            )
        return markets

    if live_markets:
        return live_markets

    if tracked_titles:
        print(
            f"  ↩️  {phase_label}: no live Polymarket event; continuing tracked "
            f"title(s) {', '.join(tracked_titles)} for weekend {weekend}"
        )
        return markets_for_tracked_titles(tracked_titles)

    return load_movies_from_csv(weekend)


def extract_movie_title(question):
    """Extract a movie title from a Polymarket question."""
    quoted = re.findall(r'[\'"\u201c\u201d]([^\'"\u201c\u201d]+)[\'"\u201c\u201d]', question)
    if quoted:
        return quoted[0]

    patterns = [
        r"(?:Will|Can)\s+(.+?)\s+(?:gross|earn|make|hit|reach|open)",
        r"(.+?)\s+(?:opening weekend|box office|domestic gross)",
    ]
    for pat in patterns:
        match = re.search(pat, question, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return question[:60]


def is_comparison_box_office_market(title):
    """Return True for head-to-head box-office markets, not movie brackets.

    We only want real per-movie opening-weekend bracket markets for data
    collection. A comparison market like "A vs. B Opening Weekend Box Office"
    does not name an actual film playing at AMC, but the previous fallback title
    parser treated the whole comparison as a movie and caused Phase 1/2 to
    collect duplicate seat rows under that fake title.
    """
    if not title:
        return False
    normalized = title.replace("\u201c", '"').replace("\u201d", '"')
    lowered = normalized.lower()
    if "opening weekend" not in lowered or "box office" not in lowered:
        return False

    # A normal per-movie market is often quoted:
    #   "Michael" Opening Weekend Box Office
    # A comparison can also be quoted:
    #   "Movie A" vs. "Movie B" Opening Weekend Box Office
    # Strip quoted spans before looking for a joiner, so a title like
    # "Alien vs. Predator" does not get mistaken for a comparison market.
    quoted_spans = re.findall(r'"[^"]+"', normalized)
    outside_quotes = re.sub(r'"[^"]+"', " ", normalized).lower()
    if re.search(r"\bvs\.?\b", outside_quotes):
        return True
    return len(quoted_spans) >= 2 and bool(re.search(r"\bvs\.?\b", lowered))


def save_polymarket_data(markets):
    """Save Polymarket bracket markets to CSV — one row per bracket question."""
    today = datetime.now().strftime("%Y-%m-%d")

    existing = set()
    if POLY_CSV.exists():
        with open(POLY_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("date") == today:
                    existing.add(row.get("market_id", ""))

    new_count = 0
    write_header = not POLY_CSV.exists()
    with open(POLY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["date", "movie_title", "market_url",
                             "market_question", "outcome_prices",
                             "volume", "market_id", "notes"])
        for m in markets:
            for bkt in m.get("bracket_markets", []):
                if bkt["market_id"] in existing:
                    continue
                writer.writerow([
                    today, m["movie_title"], m["market_url"],
                    bkt["market_question"], bkt["outcome_prices"],
                    bkt["volume"], bkt["market_id"], "",
                ])
                new_count += 1

    print(f"  Saved {new_count} new bracket market entries to CSV")


# ─── Box Office Mojo — National Theatre Counts ──────────────────────────────

def fetch_bom_theatre_counts(movie_titles):
    """
    Scrape Box Office Mojo's current weekend chart to get national theatre counts.
    Saves results to theatre-counts.json.
    Returns dict: {movie_title: theatre_count}
    """
    print("\n🎭 Fetching national theatre counts from Box Office Mojo...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }
    counts = {}
    try:
        resp = requests.get(
            "https://www.boxofficemojo.com/weekend/chart/",
            headers=headers, timeout=15
        )
        resp.raise_for_status()
        html = resp.text

        # BOM renders a table: Title | Studio | Weekend | % Change | Theaters | ...
        # Parse <td> cells — theatre count appears in the "Theaters" column
        # Each row: rank, title, studio, weekend_gross, ..., theater_count, ...
        rows = re.findall(
            r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>.*?</td>(?:.*?<td[^>]*>([^<]+)</td>){3,5}.*?'
            r'<td[^>]*>\s*([\d,]+)\s*</td>',
            html, re.DOTALL
        )

        # Fallback: simpler extraction — find all title+theater_count pairs
        # BOM table columns (typical): Rank | Title | Studio | Weekend | %Chg | Theaters | Avg | Total | Wks
        # Extract all numbers that look like theatre counts (1,000–10,000 range)
        title_blocks = re.findall(
            r'release/rl\d+[^"]*"[^>]*>([^<]{3,60})</a>.*?'
            r'<td[^>]*>\s*([\d,]{1,6})\s*</td>',
            html, re.DOTALL
        )

        parsed = {}
        for title, count_str in title_blocks:
            title = title.strip()
            try:
                count = int(count_str.replace(',', ''))
                if 10 <= count <= 12000:  # plausible theatre count range
                    parsed[title.lower()] = count
            except ValueError:
                continue

        # Match our movie titles to BOM titles (fuzzy)
        for movie in movie_titles:
            movie_lower = movie.lower().strip()
            best_match = None
            best_score = 0
            for bom_title, count in parsed.items():
                # Simple word overlap score
                m_words = set(movie_lower.split())
                b_words = set(bom_title.split())
                overlap = len(m_words & b_words) / max(len(m_words), 1)
                if overlap > best_score and overlap >= 0.5:
                    best_score = overlap
                    best_match = (bom_title, count)
            if best_match:
                counts[movie] = best_match[1]
                print(f"  ✅ {movie}: {best_match[1]:,} theatres (matched '{best_match[0]}')")
            else:
                print(f"  ⚠️  {movie}: no BOM match found")

    except Exception as e:
        print(f"  ❌ BOM fetch failed: {e}")

    # Save only the movies in this collection window. Keeping stale counts for
    # prior weekends makes theatre-counts.json look like active metadata and
    # can feed an old exact/fuzzy match into future predictions if BOM is down.
    existing = {}
    if THEATRE_COUNTS_JSON.exists():
        try:
            with open(THEATRE_COUNTS_JSON) as f:
                existing = json.load(f)
        except Exception as e:
            print(f"  ⚠️  Could not load existing theatre-counts.json ({e}) — will overwrite")

    current_counts = {
        movie: counts.get(movie, existing.get(movie))
        for movie in movie_titles
        if counts.get(movie, existing.get(movie)) is not None
    }
    current_counts["_requested_movies"] = movie_titles
    current_counts["_updated"] = datetime.now().isoformat()
    with open(THEATRE_COUNTS_JSON, "w") as f:
        json.dump(current_counts, f, indent=2)

    saved_count = len([k for k in current_counts if not k.startswith("_")])
    print(f"  Saved theatre counts for {saved_count} movies → {THEATRE_COUNTS_JSON}")
    return counts


# ─── AMC Playwright Scraper ─────────────────────────────────────────────────

# AMC's Queue-It Global Safety Net — if the VPS IP gets flagged for bot traffic,
# AMC redirects every request here. The redirect target never produces seat maps
# or showtime sections, so further work on the page is wasted. Detect early and
# bail so one theatre's queue doesn't stall the whole run.
QUEUE_HOST = "queue.amctheatres.com"


def _is_queue_url(url):
    return bool(url) and QUEUE_HOST in url


async def fetch_amc_showtimes_pw(page, theatre, date_str):
    """
    Fetch showtimes for a theatre using Playwright.

    Navigates to AMC's showtime page and waits for movie <section> elements
    to appear (smart wait instead of fixed sleep). Falls back to a short
    sleep if sections never appear (empty showtime day).

    Returns list of showtime dicts. A dedicated empty-list is returned when the
    request is redirected to AMC's queue so callers can treat it as a soft skip.
    """
    theatre_slug = theatre["slug"]
    url = f"https://www.amctheatres.com/showtimes/all/{date_str}/{theatre_slug}/all"

    print(f"  🎬 {theatre['name']}...")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if _is_queue_url(page.url):
            print(f"    🚧 AMC queue redirect — {theatre['name']} skipped")
            return []
        # Smart wait: watch for the actual showtime sections to render
        try:
            await page.wait_for_selector(
                'section[aria-label^="Showtimes for"]', timeout=12000
            )
        except Exception:
            # No sections appeared — page may be empty, slow, or now in queue
            if _is_queue_url(page.url):
                print(f"    🚧 AMC queue redirect mid-load — {theatre['name']} skipped")
                return []
            await asyncio.sleep(2)
    except Exception as e:
        print(f"    ❌ Navigation failed: {e}")
        return []

    showtimes = await page.evaluate(EXTRACT_SHOWTIMES_JS)
    print(f"    📋 {len(showtimes)} showtime(s)")
    return showtimes


# Extracted to a constant so it's not duplicated across calls
EXTRACT_SHOWTIMES_JS = r'''() => {
    const results = [];
    const sections = document.querySelectorAll('section[aria-label^="Showtimes for"]');

    for (const section of sections) {
        const ariaLabel = section.getAttribute('aria-label') || '';
        const movieName = ariaLabel.replace('Showtimes for ', '');

        const formatItems = section.querySelectorAll('li[aria-label$="Showtimes"]');

        for (const fmtItem of formatItems) {
            const fmtLabel = fmtItem.getAttribute('aria-label') || '';
            const formatName = fmtLabel.replace(' Showtimes', '');

            const links = fmtItem.querySelectorAll('a[href*="/showtimes/"]');

            for (const link of links) {
                const href = link.href || '';
                const match = href.match(/\/showtimes\/(\d+)$/);
                if (!match) continue;

                const text = link.textContent.trim();
                const timeMatch = text.match(/(\d{1,2}:\d{2}\s*(?:am|pm))/i);
                const timeStr = timeMatch ? timeMatch[1] : text.split('\n')[0].trim();

                let flags = '';
                if (text.includes('Almost Full')) flags = 'Almost Full';
                else if (text.includes('Sold Out')) flags = 'Sold Out';
                else if (text.includes('Reserved')) flags = 'Reserved';

                results.push({
                    movie: movieName,
                    showtime: timeStr,
                    showtime_id: match[1],
                    format: formatName,
                    flags: flags,
                });
            }
        }
    }
    return results;
}'''


def _extract_seats_from_next_data(props, showtime_id):
    """
    Recursively search window.__NEXT_DATA__ pageProps for seat count data.
    AMC SSRs seat layout for in-progress/imminent shows — this is the fast path
    that avoids RSC requests entirely.
    Returns seat dict or None.
    """
    if not isinstance(props, dict):
        return None

    # Look for common seat count field names
    seat_keys = {"totalSeats", "total_seats", "seatsAvailable", "seats_available",
                 "availableCount", "seatCount", "capacity"}
    if any(k in props for k in seat_keys):
        total = props.get("totalSeats") or props.get("total_seats") or props.get("seatCount") or props.get("capacity") or 0
        avail = props.get("seatsAvailable") or props.get("seats_available") or props.get("availableCount") or 0
        if total > 0:
            sold = total - avail
            return {
                "total_seats": int(total),
                "seats_sold": int(sold),
                "seats_available": int(avail),
                "occupancy_pct": round(sold / total * 100, 1) if total else 0,
            }

    # Recurse into nested dicts/lists
    for v in props.values():
        if isinstance(v, dict):
            result = _extract_seats_from_next_data(v, showtime_id)
            if result:
                return result
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    result = _extract_seats_from_next_data(item, showtime_id)
                    if result:
                        return result
    return None


QUEUE_SENTINEL = {"__queue__": True}


async def fetch_amc_seat_map_pw(page, showtime_id):
    """
    Navigate to /showtimes/{id}/seats and count seat inputs.

    AMC uses Next.js RSC (React Server Components). From datacenter IPs those
    RSC requests get 403'd, breaking React hydration. We intercept and silence
    them so the seat map (which IS server-rendered in the initial HTML for
    in-progress/imminent shows) can render without errors.

    Returns dict with total_seats, seats_sold, seats_available, occupancy_pct,
    QUEUE_SENTINEL when AMC queues the VPS IP, or None otherwise.
    """
    if not showtime_id:
        return None

    url = f"https://www.amctheatres.com/showtimes/{showtime_id}/seats"

    # Silence Next.js RSC requests — they 403 from cloud IPs and break hydration.
    # The seat map data is SSR'd into the page for active shows, so we don't need them.
    async def block_rsc(route):
        if "_rsc=" in route.request.url:
            await route.fulfill(status=200, content_type="text/plain", body="")
        else:
            await route.continue_()

    await page.route("**/*", block_rsc)

    try:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"      ⚠️  Goto failed: {str(e)[:120]}")
            return None
        final_url = page.url
        if _is_queue_url(final_url):
            print(f"      🚧 AMC queue redirect on seat map — aborting theatre")
            return QUEUE_SENTINEL
        try:
            title = await page.title()
        except Exception:
            title = ""
        print(f"      🔍 Landed on: {final_url} | title: {title[:60]}")
        try:
            await page.wait_for_selector(
                'input[aria-label*="Recliner"], input[aria-label*="Seat"], input[aria-label*="Club Rocker"]',
                timeout=12000,
            )
        except Exception:
            if _is_queue_url(page.url):
                print(f"      🚧 AMC queue redirect mid-load — aborting theatre")
                return QUEUE_SENTINEL
            try:
                body_snippet = await page.evaluate("() => document.body?.innerText?.slice(0,200) || ''")
            except Exception:
                body_snippet = ""
            print(f"      ⚠️  No seat inputs. Page: {body_snippet[:120]}")
            return None
    finally:
        try:
            await page.unroute("**/*")
        except Exception:
            pass

    try:
        seat_data = await page.evaluate(COUNT_SEATS_JS)
    except Exception as e:
        print(f"      ⚠️  Seat count evaluate failed: {str(e)[:120]}")
        return None

    if seat_data["total_seats"] == 0:
        return None

    return seat_data


COUNT_SEATS_JS = r'''() => {
    const inputs = document.querySelectorAll('input[aria-label]');
    let total = 0;
    let sold = 0;
    let available = 0;

    for (const input of inputs) {
        const label = (input.getAttribute('aria-label') || '').toLowerCase();

        // Skip non-seat inputs (filters, search, etc)
        // AMC seat types: "Recliner A1", "Seat A1", "AMC Club Rocker A1" (IMAX/Dolby)
        if (!(/[a-z]\d+/.test(label) || label.includes('recliner') || label.includes('seat') || label.includes('club rocker'))) {
            continue;
        }
        // Skip wheelchair and companion seats
        if (label.includes('wheelchair') || label.includes('companion')) {
            continue;
        }

        total++;
        if (input.disabled) {
            sold++;
        } else {
            available++;
        }
    }

    return {
        total_seats: total,
        seats_sold: sold,
        seats_available: available,
        occupancy_pct: total > 0 ? Math.round(sold / total * 1000) / 10 : 0,
    };
}'''


# ─── Showtime Selection ─────────────────────────────────────────────────────

def get_format_priority(format_str):
    """Get priority score for an auditorium format."""
    if not format_str:
        return 0
    fmt_lower = format_str.lower()
    for key, priority in FORMAT_PRIORITY.items():
        if key in fmt_lower:
            return priority
    return 10


def parse_showtime_hour(time_str):
    """Parse a time string into decimal hours (e.g. '7:30pm' -> 19.5)."""
    if not time_str:
        return None

    time_str = time_str.strip().upper()

    patterns = [
        r'(\d{1,2}):(\d{2})\s*(AM|PM)',
        r'(\d{1,2})(\d{2})\s*(AM|PM)',
        r'T(\d{2}):(\d{2})',
    ]

    for pat in patterns:
        match = re.search(pat, time_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                h, m, ampm = int(groups[0]), int(groups[1]), groups[2]
                if ampm == "PM" and h != 12:
                    h += 12
                elif ampm == "AM" and h == 12:
                    h = 0
                return h + m / 60
            elif len(groups) == 2:
                return int(groups[0]) + int(groups[1]) / 60

    return None


# ─── Data Logging ────────────────────────────────────────────────────────────

SEAT_FIELDS = [
    "weekend_of", "run_id",
    "date", "day_of_week", "theatre_name", "theatre_city",
    "timezone", "movie_title", "polymarket_market", "showtime",
    "check_time", "minutes_after_showtime", "auditorium_name",
    "auditorium_type", "total_seats", "seats_sold",
    "seats_available", "occupancy_pct",
    "amc_seat_map_url", "notes",
]

SEAT_DEDUPE_FIELDS = (
    "weekend_of",
    "date",
    "theatre_name",
    "movie_title",
    "showtime",
    "auditorium_type",
    "amc_seat_map_url",
    "total_seats",
    "seats_sold",
    "seats_available",
)


def ensure_csv_header():
    """Create seat-counts.csv with header if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SEAT_CSV.exists():
        with open(SEAT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(SEAT_FIELDS)


def _seat_row_dict(row_data):
    return dict(zip(SEAT_FIELDS, row_data))


def _seat_row_key(row):
    if isinstance(row, list):
        row = _seat_row_dict(row)
    return tuple(str(row.get(field, "") or "") for field in SEAT_DEDUPE_FIELDS)


def append_unique_seat_rows(rows):
    """Append only rows we haven't already logged for this showtime snapshot."""
    if not rows:
        return 0, 0

    existing_keys = set()
    if SEAT_CSV.exists():
        with open(SEAT_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                existing_keys.add(_seat_row_key(row))

    pending = []
    seen_keys = set(existing_keys)
    skipped = 0
    for row in rows:
        key = _seat_row_key(row)
        if key in seen_keys:
            skipped += 1
            continue
        pending.append(row)
        seen_keys.add(key)

    if pending:
        with open(SEAT_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(pending)

    return len(pending), skipped


def log_run(tz_group, movies, results, issues):
    """Append to the run log."""
    now = datetime.now()

    with open(RUN_LOG, "a") as f:
        f.write(f"\n## {now.strftime('%Y-%m-%d %H:%M')} — {tz_group} Group\n\n")
        f.write(f"**Polymarket movies tracked:** {', '.join(movies) if movies else 'None found'}\n\n")

        if results:
            f.write("| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |\n")
            f.write("|---------|-------|--------|----------|-----------|-------------|\n")
            for r in results:
                f.write(f"| {r['theatre']} | {r['movie']} | {r['format']} | "
                       f"{r['showtime']} | {r['occupancy']}% | {r['delta']} min |\n")

        if issues:
            f.write(f"\n**Issues:** {'; '.join(issues)}\n")

        f.write("\n---\n")


def fail_phase(message, exit_code=1):
    """Abort the phase with a non-zero exit so Actions can retry or fail."""
    print(message)
    raise SystemExit(exit_code)


def phase1_groups(tz_group):
    return [tz_group] if tz_group != "ALL" else ["ET", "CT", "MT", "PT"]


def phase1_link_coverage(saved_links, theatres_map, groups, expected_dates):
    """Count fresh Phase 1 theatre entries against the configured theatre universe."""
    expected_total = 0
    fresh_names = []
    stale_entries = []
    missing_entries = []

    for group in groups:
        expected_date = expected_dates.get(group)
        for theatre in theatres_map.get(group, []):
            expected_total += 1
            name = theatre["name"]
            entry = saved_links.get(name)
            if not entry:
                missing_entries.append(f"{name} ({group}: missing)")
                continue
            entry_date = entry.get("show_date")
            if entry_date == expected_date and entry.get("movies"):
                fresh_names.append(name)
            else:
                stale_entries.append(
                    f"{name} ({group}: show_date={entry_date or '?'}, expected={expected_date})"
                )

    ratio = (len(fresh_names) / expected_total) if expected_total else 1.0
    return {
        "expected_total": expected_total,
        "fresh_count": len(fresh_names),
        "missing_count": len(missing_entries),
        "stale_count": len(stale_entries),
        "fresh_names": fresh_names,
        "missing_entries": missing_entries,
        "stale_entries": stale_entries,
        "ratio": ratio,
    }


def print_phase1_coverage(report, label, min_ratio=PHASE1_MIN_FRESH_LINK_RATIO):
    expected = report["expected_total"]
    fresh = report["fresh_count"]
    ratio = report["ratio"]
    print(f"\n🧯 {label}: {fresh}/{expected} fresh theatres ({ratio:.1%}); minimum {min_ratio:.0%}")
    samples = report["stale_entries"][:3] + report["missing_entries"][:3]
    if samples:
        print("   Sample gaps:")
        for sample in samples[:5]:
            print(f"    - {sample}")


def require_phase1_coverage(report, label, min_ratio=PHASE1_MIN_FRESH_LINK_RATIO):
    print_phase1_coverage(report, label, min_ratio=min_ratio)
    if report["expected_total"] and report["ratio"] < min_ratio:
        fail_phase(
            f"❌ {label} below reliability threshold: "
            f"{report['fresh_count']}/{report['expected_total']} fresh theatres "
            f"({report['ratio']:.1%}, need {min_ratio:.0%})."
        )


def phase1_movie_link_counts(saved_links, groups=None, expected_dates=None):
    counts = {}
    for entry in saved_links.values():
        tz = entry.get("tz")
        if groups is not None and tz not in groups:
            continue
        if expected_dates is not None:
            expected_date = expected_dates.get(tz)
            if expected_date and entry.get("show_date") != expected_date:
                continue
        for movie, shows in (entry.get("movies") or {}).items():
            if shows:
                counts[movie] = counts.get(movie, 0) + 1
    return counts


def filter_markets_with_phase1_links(poly_markets, saved_links, min_theatres=1,
                                     groups=None, expected_dates=None):
    """Drop Polymarket markets that have no fresh AMC Phase 1 links."""
    if not poly_markets:
        return []

    linked_counts = phase1_movie_link_counts(
        saved_links,
        groups=groups,
        expected_dates=expected_dates,
    )
    filtered = []
    skipped = []
    for market in poly_markets:
        title = market.get("movie_title", "")
        count = linked_counts.get(title, 0)
        if count >= min_theatres:
            filtered.append(market)
        else:
            skipped.append(title or market.get("question", "unknown market"))

    if skipped:
        print("\n↷ Skipping Polymarket market(s) with no current AMC Phase 1 links:")
        for title in skipped:
            print(f"    - {title}")
    return filtered


# ─── Main Orchestrator ───────────────────────────────────────────────────────

async def _scrape_theatre(browser, theatre, date_str, movie_titles, market_urls,
                          weekend_of="", run_id="", saved_movies=None, test_mode=False):
    """
    Scrape one theatre's seat maps using pre-collected Phase 1 showtime IDs.

    saved_movies: required — {movie_title: [{showtime, showtime_id, format}]}
                  collected during Phase 1 (collect-links run).
                  If None the theatre is skipped (Phase 1 must run first).

    Returns (results_list, issues_list, csv_rows_list).
    """
    if saved_movies is None:
        return [], [f"{theatre['name']}: no Phase 1 links — skipped"], []

    tz = theatre.get("_tz", "")
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=random.choice(_USER_AGENTS),
        locale="en-US",
    )
    await context.add_init_script(_STEALTH_INIT_SCRIPT)
    # Pre-accept OneTrust cookie consent so the banner never blocks the seat map
    await context.add_cookies([
        {"name": "OptanonAlertBoxClosed", "value": "2026-01-01T00:00:00.000Z",
         "domain": ".amctheatres.com", "path": "/", "sameSite": "Lax"},
        {"name": "OptanonConsent", "value": "isGpcEnabled=0&datestamp=Wed+Jan+01+2026+00%3A00%3A00+GMT&version=6.37.0&isIABGlobal=false&hosts=&consentId=abc&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false",
         "domain": ".amctheatres.com", "path": "/", "sameSite": "Lax"},
    ])
    page = await context.new_page()
    results = []
    issues = []
    csv_rows = []
    # Use the passed date_str (already adjusted to local TZ) as the CSV date stamp
    today = date_str
    day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")

    try:
        # current_hour must be in LOCAL time for this theatre's timezone and
        # relative to the show date. Some Phase 2 runs happen after local
        # midnight (especially ET Sunday night), while the showtime IDs still
        # belong to the previous calendar day. Without the day offset, a
        # Monday 00:50 scrape of a Sunday 19:45 show looks like -18.9 hours
        # before showtime instead of +5.1 hours after showtime.
        tz_local = local_now(tz)
        try:
            show_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_offset = (tz_local.date() - show_date).days
        except ValueError:
            day_offset = 0
        current_hour = tz_local.hour + tz_local.minute / 60 + day_offset * 24
        check_time = datetime.now(timezone.utc).isoformat()

        # Build evening_shows from saved Phase 1 links.
        # Phase 1 already selected the right shows at 5pm local — use all of them
        # regardless of what time Phase 2 runs (avoids cross-midnight filter failures).
        # Only use titles from the current discovery/fallback list. The saved
        # links file is merged across runs, so stale bad titles should not be
        # re-scraped just because they are still present in showtime-links.json.
        movie_shows_map = {}
        for movie_title in movie_titles:
            entries = saved_movies.get(movie_title, [])
            if not entries:
                continue
            started = entries
            seen = set()
            shows = []
            for e in sorted(started,
                            key=lambda x: -(parse_showtime_hour(x.get("showtime", "")) or 0)):
                key = (e.get("format", "Standard"), e.get("showtime", "?"))
                if key in seen:
                    continue
                seen.add(key)
                shows.append((
                    {"showtime": e["showtime"], "showtime_id": e["showtime_id"],
                     "format": e.get("format", "Standard"), "flags": ""},
                    f"{e.get('format','Standard')} @ {e['showtime']} (saved link)",
                ))
            shows.sort(key=lambda x: -get_format_priority(x[0].get("format", "")))
            # In test mode, only try the single highest-priority show per movie
            if test_mode:
                shows = shows[:1]
            movie_shows_map[movie_title] = shows

        queue_blocked = False
        for movie_title, evening_shows in movie_shows_map.items():
            if queue_blocked:
                break
            if not evening_shows:
                continue

            for show, reason in evening_shows:
                fmt = show.get("format", "Standard")
                st = show.get("showtime", "?")
                flags = show.get("flags", "")

                await asyncio.sleep(random.uniform(0.5, 1.5))
                seat_data = await fetch_amc_seat_map_pw(page, show.get("showtime_id"))
                if seat_data is QUEUE_SENTINEL:
                    issues.append(f"{theatre['name']}: AMC queue redirect — theatre skipped")
                    queue_blocked = True
                    break
                if seat_data is None:
                    # One retry with a short delay to work around transient blocks
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                    seat_data = await fetch_amc_seat_map_pw(page, show.get("showtime_id"))
                    if seat_data is QUEUE_SENTINEL:
                        issues.append(f"{theatre['name']}: AMC queue redirect — theatre skipped")
                        queue_blocked = True
                        break

                showtime_hour = parse_showtime_hour(st)
                delta_minutes = int((current_hour - (showtime_hour or current_hour)) * 60)

                if seat_data:
                    occ = seat_data["occupancy_pct"]
                    print(f"    🪑 {theatre['name']}: {movie_title} {fmt} — "
                          f"{seat_data['seats_sold']}/{seat_data['total_seats']} ({occ}%)")

                    showtime_id = show.get("showtime_id", "")
                    amc_url = f"https://www.amctheatres.com/showtimes/{showtime_id}/seats" if showtime_id else ""
                    csv_rows.append([
                        weekend_of, run_id,
                        today, day_of_week, theatre["name"], theatre.get("city", theatre.get("dma", "")),
                        tz, movie_title, market_urls.get(movie_title, ""),
                        st, check_time, delta_minutes,
                        "", fmt,
                        seat_data["total_seats"], seat_data["seats_sold"],
                        seat_data["seats_available"], occ,
                        amc_url, f"{flags}. {reason}" if flags else reason,
                    ])
                    results.append({
                        "theatre": theatre["name"], "movie": movie_title,
                        "format": fmt, "showtime": st,
                        "occupancy": occ, "delta": delta_minutes,
                    })
                else:
                    # Seat map unavailable — log to issues only, never write to CSV.
                    # Writing empty rows pollutes downstream analysis and wastes dedup keys.
                    showtime_id = show.get("showtime_id", "")
                    issues.append(
                        f"{theatre['name']}: No seat map for {movie_title} {fmt} @ {st} "
                        f"(https://www.amctheatres.com/showtimes/{showtime_id}/seats)"
                    )
    finally:
        try:
            await asyncio.wait_for(context.close(), timeout=10)
        except Exception:
            pass

    return results, issues, csv_rows


async def _collect_links_theatre(browser, theatre, date_str, movie_titles):
    """
    Phase 1: Visit a theatre's showtime page and save all evening showtime IDs.
    No seat maps fetched — just links for later.
    Returns dict: {movie_title: [{showtime, showtime_id, format}, ...]}
    """
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=random.choice(_USER_AGENTS),
        locale="en-US",
    )
    await context.add_init_script(_STEALTH_INIT_SCRIPT)
    page = await context.new_page()
    collected = {}
    try:
        await asyncio.sleep(random.uniform(0.5, 2.5))
        showtimes = await fetch_amc_showtimes_pw(page, theatre, date_str)
        for movie_title in movie_titles:
            movie_lower = movie_title.lower().strip()
            matching = [s for s in showtimes
                        if movie_lower in s.get("movie", "").lower()
                        or s.get("movie", "").lower() in movie_lower]
            evening = [s for s in matching
                       if parse_showtime_hour(s.get("showtime", "")) is not None
                       and 17 <= parse_showtime_hour(s.get("showtime", "")) <= 23]
            if evening:
                collected[movie_title] = [
                    {"showtime": s.get("showtime"), "showtime_id": s.get("showtime_id"),
                     "format": s.get("format", "Standard")}
                    for s in evening
                ]
    except Exception as e:
        print(f"  ⚠️  {theatre['name']}: {e}")
    finally:
        try:
            await asyncio.wait_for(context.close(), timeout=10)
        except Exception:
            pass
    return collected


async def run_collect_links_async(tz_group="ALL", target_date=None):
    """
    Phase 1 main: Visit all theatres, save showtime IDs to showtime-links.json.
    Run in the local Phase 1 window before shows start.
    """
    print(f"{'='*60}")
    print(f"📋 Phase 1 — Collecting showtime links ({tz_group})")
    if target_date:
        print(f"   Target show date: {target_date}")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    theatres_map = load_theatres()
    ref_tz = tz_group if tz_group != "ALL" else "ET"
    ref_local = local_now(ref_tz)
    if target_date:
        try:
            target_ref_dt = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            fail_phase(f"❌ Invalid Phase 1 target date: {target_date}")
    else:
        target_ref_dt = ref_local
    live_markets = fetch_polymarket_box_office()
    poly_markets = select_collection_markets(live_markets, target_ref_dt, "Phase 1")

    if not poly_markets:
        fail_phase("❌ No active Polymarket box office markets and no saved CSV fallback.")

    movie_titles = [m["movie_title"] for m in poly_markets]
    today = target_date or ref_local.strftime("%Y-%m-%d")
    current_weekend = opening_weekend_friday(target_ref_dt)
    groups = phase1_groups(tz_group)
    expected_dates = {group: (target_date or local_date_str(group)) for group in groups}
    all_theatres = []
    for group in groups:
        for t in theatres_map.get(group, []):
            all_theatres.append({**t, "_tz": group, "_date": expected_dates[group]})

    print(f"\n🏛️  Visiting {len(all_theatres)} theatres to collect links...")

    # Store the opening-weekend Friday anchor, not the calendar day. Thursday
    # Phase 1 runs collect links for Friday's opening weekend and must merge
    # with later TZ-group runs and pass Phase 2 validation that same night.
    links = {
        "date": current_weekend,
        "weekend_of": current_weekend,
        "collected_local_date": today,
        "collected_at": datetime.now().isoformat(),
        "theatres": {},
    }
    sem = asyncio.Semaphore(MAX_CONCURRENT_TABS_PHASE1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=_CHROMIUM_ARGS)

        async def bounded(theatre):
            async with sem:
                t_date = theatre.get("_date", today)
                try:
                    result = await asyncio.wait_for(
                        _collect_links_theatre(browser, theatre, t_date, movie_titles),
                        timeout=PHASE1_THEATRE_TIMEOUT_SEC,
                    )
                except asyncio.TimeoutError:
                    print(f"  ⏱️  {theatre['name']}: Phase 1 timeout — skipping")
                    result = {}
                except Exception as e:
                    print(f"  ❌ {theatre['name']}: {e}")
                    result = {}
                return theatre["name"], theatre.get("_tz", ""), t_date, result

        outcomes = await asyncio.gather(*[bounded(t) for t in all_theatres], return_exceptions=True)

        # Retry theatres that returned 0 showtimes — likely hit rate-limit on first pass.
        failed = [
            t for t, outcome in zip(all_theatres, outcomes)
            if isinstance(outcome, Exception) or (not isinstance(outcome, Exception) and not outcome[3])
        ]
        if failed:
            print(f"\n🔄 Retrying {len(failed)} theatres that returned 0 showtimes (5s delay)...")
            await asyncio.sleep(5)
            retry_outcomes = await asyncio.gather(*[bounded(t) for t in failed], return_exceptions=True)
            # Splice retry results back in place of the failed slots
            fi = 0
            outcomes = list(outcomes)
            for i, outcome in enumerate(outcomes):
                if isinstance(outcome, Exception) or (not isinstance(outcome, Exception) and not outcome[3]):
                    outcomes[i] = retry_outcomes[fi]
                    fi += 1

        try:
            await asyncio.wait_for(browser.close(), timeout=15)
        except Exception:
            pass

    total_links = 0
    for outcome in outcomes:
        if isinstance(outcome, Exception):
            continue
        name, tz, show_date, collected = outcome
        if collected:
            links["theatres"][name] = {"tz": tz, "show_date": show_date, "movies": collected}
            total_links += sum(len(v) for v in collected.values())

    fresh_report = phase1_link_coverage(links["theatres"], theatres_map, groups, expected_dates)
    require_phase1_coverage(fresh_report, f"Phase 1 collected links for {tz_group}")

    poly_markets = filter_markets_with_phase1_links(
        poly_markets,
        links["theatres"],
        groups=groups,
        expected_dates=expected_dates,
    )
    if not poly_markets:
        fail_phase("❌ No active Polymarket box office markets have current AMC showtime links.")
    movie_titles = [m["movie_title"] for m in poly_markets]
    fetch_bom_theatre_counts(movie_titles)
    save_polymarket_data(poly_markets)

    DATA_DIR.mkdir(exist_ok=True)

    # Merge into existing file so ET/CT/PT Phase 1 runs accumulate in the same file.
    # Each TZ group runs Phase 1 separately and would otherwise overwrite the others.
    # We keep the latest successful collected_at timestamp and update individual
    # theatre entries. Theatres from previous weekends are replaced.
    existing = {}
    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                existing = json.load(f)
            # Only merge if the existing file is from the same opening weekend.
            # Wipe only if the file is from a previous weekend (different weekend_of date),
            # NOT just because it's >14h old — different TZ Phase 1 runs are spread across
            # the day and would wipe each other if we used a time-based cutoff.
            existing_weekend = existing.get("weekend_of") or existing.get("date", "")
            if existing_weekend and existing_weekend != current_weekend:
                existing = {}  # previous weekend — start fresh
        except Exception as e:
            print(f"  ⚠️  Could not load existing showtime-links.json ({e}) — starting fresh")
            existing = {}

    # Drop stale same-TZ entries before merging. Theatres from OTHER TZ groups
    # (i.e. ETs that ran 6h ago on this same Friday) are kept, but anything in
    # the TZ group(s) we just refreshed is replaced wholesale — even theatres
    # that returned no showtimes in this run get dropped.
    #
    # Why: Phase 1 yesterday (Thursday) collected Thursday-evening showtime IDs
    # with show_date=2026-04-23. If today's Phase 1 fails to refresh some of
    # those same-TZ theatres (rate-limit, timeout, 0 showtimes), the old
    # Thursday entries would otherwise carry into showtime-links.json and
    # Phase 2 would scrape Thursday's already-elapsed showtime IDs — yielding
    # duplicate Thursday seat snapshots tagged with stale dates while skipping
    # the Friday showtimes those theatres should have produced.
    refreshed_tzs = set(groups)
    merged_theatres = {
        name: entry
        for name, entry in existing.get("theatres", {}).items()
        if entry.get("tz") not in refreshed_tzs
    }
    merged_theatres.update(links["theatres"])   # fresh same-TZ entries win
    links["theatres"] = merged_theatres
    if existing.get("weekend_of"):
        links["weekend_of"] = existing["weekend_of"]
    if existing.get("date"):
        links["date"] = existing["date"]
    # Use the latest successful Phase 1 refresh time. Weekend Phase 2 runs for
    # MT/PT happen more than 12h after the ET/noon collection window, so keeping
    # the earliest timestamp would incorrectly mark fresh same-day links as stale.
    links["collected_at"] = datetime.now(timezone.utc).isoformat()

    with open(LINKS_JSON, "w") as f:
        json.dump(links, f, indent=2)

    print(f"\n✅ Saved {total_links} showtime links from {len(links['theatres'])} theatres total → {LINKS_JSON}")


async def ensure_phase1_links_async(tz_group="ALL"):
    """Self-heal Phase 1 links for the Phase 2 show date when coverage is low."""
    if tz_group == "ALL":
        for group in phase1_groups(tz_group):
            await ensure_phase1_links_async(group)
        return

    theatres_map = load_theatres()
    target_date = phase1_expected_date(tz_group)
    expected_dates = {tz_group: target_date}
    target_weekend = opening_weekend_friday(datetime.strptime(target_date, "%Y-%m-%d"))
    saved_links = {}

    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                links_data = json.load(f)
            links_weekend = links_data.get("weekend_of") or links_data.get("date", "")
            if links_weekend == target_weekend:
                saved_links = links_data.get("theatres", {})
            elif links_weekend:
                print(
                    f"\n⚠️  Phase 1 links are from weekend {links_weekend}, "
                    f"but {tz_group} needs {target_weekend}."
                )
        except Exception as e:
            print(f"\n⚠️  Could not inspect Phase 1 links before scrape: {e}")

    report = phase1_link_coverage(saved_links, theatres_map, [tz_group], expected_dates)
    if not report["expected_total"] or report["ratio"] >= PHASE1_MIN_FRESH_LINK_RATIO:
        print_phase1_coverage(report, f"Phase 1 preflight for {tz_group}")
        return

    print_phase1_coverage(report, f"Phase 1 preflight for {tz_group}")
    print(f"\n🔧 Rebuilding Phase 1 links for {tz_group} show date {target_date} before scraping.")
    await run_collect_links_async(tz_group, target_date=target_date)

    with open(LINKS_JSON) as f:
        repaired_links = json.load(f).get("theatres", {})
    repaired_report = phase1_link_coverage(repaired_links, theatres_map, [tz_group], expected_dates)
    require_phase1_coverage(repaired_report, f"Phase 1 repaired links for {tz_group}")


async def run_async(tz_group="ALL", force=False, test_max=None):
    """
    Main entry point (async).
    Parallelizes across MAX_CONCURRENT_TABS browser tabs using a semaphore.
    """
    print(f"{'='*60}")
    print(f"🎬 Box Office Tracker (Playwright) — {tz_group} Group")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Concurrency: {MAX_CONCURRENT_TABS} tabs")
    print(f"{'='*60}")

    ensure_csv_header()

    # Use tz-adjusted local date (server clock is UTC; runs after midnight UTC
    # would otherwise stamp tomorrow's date on tonight's data).
    groups_to_check = phase1_groups(tz_group)
    # For mixed-TZ runs use ET as the reference (most conservative, first to tick over)
    ref_tz = tz_group if tz_group != "ALL" else "ET"
    local = local_now(ref_tz)
    today = local.strftime("%Y-%m-%d")
    local_dow = local.strftime("%A")


    theatres_map = load_theatres()

    # Step 1: Get Polymarket movies
    # Step 2: Build flat list of theatres to scrape
    weekend = opening_weekend_friday(local)
    live_markets = fetch_polymarket_box_office()
    poly_markets = select_collection_markets(live_markets, local, "Phase 2")

    if not poly_markets:
        log_run(tz_group, [], [], ["No active Polymarket box office markets found"])
        fail_phase("\n❌ No active box office markets on Polymarket and no saved CSV fallback.")

    run_id = local.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]

    all_theatres = []
    for group in groups_to_check:
        # Each group uses its own local date for the AMC showtime URL
        for theatre in theatres_map.get(group, []):
            all_theatres.append({**theatre, "_tz": group, "_date": local_date_str(group)})

    # Phase 2 requires Phase 1 links — abort if missing, from the wrong opening
    # weekend, or older than 12 hours unless explicitly forced.
    saved_links = {}
    links_meta = {}
    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                links_data = json.load(f)
            links_meta = links_data
            links_weekend = links_data.get("weekend_of") or links_data.get("date", "")
            current_weekend = weekend
            collected_at_str = links_data.get("collected_at", "")
            if links_weekend and links_weekend == current_weekend:
                saved_links = links_data.get("theatres", {})
                age_str = ""
                if collected_at_str:
                    collected_at = datetime.fromisoformat(collected_at_str.replace("Z", "+00:00"))
                    if collected_at.tzinfo is None:
                        collected_at = collected_at.replace(tzinfo=timezone.utc)
                    age_hours = (datetime.now(timezone.utc) - collected_at).total_seconds() / 3600
                    age_str = f" from {age_hours:.1f}h ago"
                    if age_hours > 12:
                        if not force:
                            fail_phase(f"\n❌ showtime-links.json is stale ({age_hours:.1f}h old) — run Phase 1 first.")
                        print(f"\n⚠️  showtime-links.json is stale ({age_hours:.1f}h old) — proceeding because --force was set.")
                print(f"\n📂 Phase 1 links{age_str} ({len(saved_links)} theatres)")
            elif links_weekend:
                fail_phase(f"\n❌ showtime-links.json is from weekend {links_weekend} (current: {current_weekend}) — run Phase 1 first.")
            else:
                # Old-format file: fall back to date comparison
                if links_data.get("date") == today:
                    saved_links = links_data.get("theatres", {})
                    print(f"\n📂 Phase 1 links for today ({len(saved_links)} theatres)")
                else:
                    fail_phase(f"\n❌ showtime-links.json is from {links_data.get('date')}, not today — run Phase 1 first.")
        except Exception as e:
            fail_phase(f"\n❌ Could not load showtime-links.json: {e} — run Phase 1 first.")
    else:
        fail_phase("\n❌ showtime-links.json not found — run Phase 1 first.")

    expected_dates = {group: phase1_expected_date(group) for group in groups_to_check}
    poly_markets = filter_markets_with_phase1_links(
        poly_markets,
        saved_links,
        groups=groups_to_check,
        expected_dates=expected_dates,
    )
    if not poly_markets:
        log_run(tz_group, [], [], ["No active Polymarket markets have current Phase 1 links"])
        fail_phase("\n❌ No active box office markets have current AMC Phase 1 links.")
    save_polymarket_data(poly_markets)

    movie_titles = [m["movie_title"] for m in poly_markets]
    market_urls = {m["movie_title"]: m["market_url"] for m in poly_markets}

    # Only scrape theatres that have saved links — skip anything Phase 1 didn't visit
    all_theatres = [t for t in all_theatres if t["name"] in saved_links]

    # Per-theatre staleness guard: drop theatres whose Phase 1 entry's show_date
    # doesn't match the local date Phase 1 was last run for in that theatre's TZ.
    #
    # The file-level 12h `collected_at` check above gets refreshed by ANY
    # Phase 1 leg (e.g. ET ran 2h ago), so it can't catch the case where a
    # specific TZ's Phase 1 didn't fire today and that TZ's entries are >24h
    # old. Without this guard, Phase 2 would scrape yesterday's already-
    # elapsed showtime IDs and stamp the resulting post-show seat snapshots
    # with yesterday's `show_date` — producing duplicate-day rows that
    # collide with yesterday's correctly-captured Phase 2 data.
    #
    # We compute `expected_date` as `local_now(tz) - 12h` rather than just
    # `local_date_str(tz)` because at the 04:00 UTC Phase 2 schedule, ET has
    # already rolled past local midnight (00:00 EDT) while CT/PT haven't —
    # so a naive `local_date_str("ET")` returns *tomorrow*, never matching
    # Phase 1's afternoon stamp. Subtracting 12h snaps each TZ back to the
    # date Phase 1 ran for, robust to TZ rollover at the standard scrape time.
    fresh_theatres = []
    stale_skipped = []
    for t in all_theatres:
        entry = saved_links[t["name"]]
        entry_date = entry.get("show_date")
        ref_tz = t.get("_tz") or entry.get("tz") or "ET"
        expected_date = phase1_expected_date(ref_tz)
        if entry_date and entry_date != expected_date:
            stale_skipped.append(
                f"{t['name']} ({t.get('_tz','?')}: show_date={entry_date}, expected={expected_date})"
            )
            continue
        fresh_theatres.append(t)
    if stale_skipped:
        print(f"\n⚠️  Skipping {len(stale_skipped)} theatres with stale Phase 1 entries "
              f"(Phase 1 didn't refresh this TZ today):")
        for s in stale_skipped[:5]:
            print(f"    {s}")
        if len(stale_skipped) > 5:
            print(f"    ... and {len(stale_skipped)-5} more")
    all_theatres = fresh_theatres

    coverage_report = phase1_link_coverage(saved_links, theatres_map, groups_to_check, expected_dates)
    if not test_max:
        require_phase1_coverage(coverage_report, f"Phase 1 scrape preflight for {tz_group}")

    # Test mode: cap to N theatres
    if test_max:
        all_theatres = all_theatres[:test_max]
        print(f"\n🧪 TEST MODE — limiting to {test_max} theatres, time filter bypassed")

    print(f"\n🏛️  Scraping {len(all_theatres)} theatres with saved links "
          f"(across {len(groups_to_check)} timezone(s))...")
    print(f"   Weekend: {weekend}  Run: {run_id}")

    if not all_theatres:
        fail_phase("❌ No theatres found in saved links for this timezone group.")

    # Step 3: Parallel scrape with semaphore — flush each theatre to CSV immediately
    all_results = []
    all_issues = []
    sem = asyncio.Semaphore(MAX_CONCURRENT_TABS)
    write_lock = asyncio.Lock()
    written_rows = 0
    skipped_rows = 0

    # Per-theatre and overall deadlines. The workflow's step timeout caps us at
    # 75 min, but we stop accepting new work earlier so in-flight theatres can
    # finish and commit. Per-theatre wait_for prevents one hung tab (usually
    # from AMC's queue-it redirect) from stalling the whole run.
    overall_deadline = asyncio.get_event_loop().time() + PHASE2_DEADLINE_SEC
    theatre_timeout_sec = PHASE2_THEATRE_TIMEOUT_SEC

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=_CHROMIUM_ARGS)

        async def bounded_scrape(theatre):
            nonlocal written_rows, skipped_rows
            name = theatre["name"]
            if asyncio.get_event_loop().time() >= overall_deadline:
                all_issues.append(f"{name}: overall deadline reached — skipped")
                return
            async with sem:
                if asyncio.get_event_loop().time() >= overall_deadline:
                    all_issues.append(f"{name}: overall deadline reached — skipped")
                    return
                saved_entry = saved_links[name]
                t_date = (
                    saved_entry.get("show_date")
                    or links_meta.get("collected_local_date")
                    or theatre.get("_date", today)
                )
                theatre_saved = saved_entry.get("movies")
                try:
                    outcome = await asyncio.wait_for(
                        _scrape_theatre(
                            browser, theatre, t_date, movie_titles, market_urls,
                            weekend_of=weekend, run_id=run_id,
                            saved_movies=theatre_saved,
                            test_mode=bool(test_max),
                        ),
                        timeout=theatre_timeout_sec,
                    )
                except asyncio.TimeoutError:
                    all_issues.append(f"{name}: timeout after {theatre_timeout_sec}s — skipped")
                    print(f"  ⏱️  {name}: timeout after {theatre_timeout_sec}s — moving on")
                    return
                except Exception as e:
                    all_issues.append(f"{name}: {e}")
                    print(f"  ❌ {name}: {e}")
                    return
            results, issues, csv_rows = outcome
            all_results.extend(results)
            all_issues.extend(issues)
            # Flush to disk immediately so data survives a mid-run kill
            if csv_rows:
                async with write_lock:
                    w, s = append_unique_seat_rows(csv_rows)
                    written_rows += w
                    skipped_rows += s

        tasks = [bounded_scrape(t) for t in all_theatres]
        await asyncio.gather(*tasks, return_exceptions=True)

        try:
            await asyncio.wait_for(browser.close(), timeout=15)
        except Exception:
            pass
    if skipped_rows:
        print(f"↺ Skipped {skipped_rows} duplicate seat row(s)")

    # Step 5: Log and summarize
    log_run(tz_group, movie_titles, all_results, all_issues)

    # Use local time for the day check — PT phase 2 runs at 7am UTC which is
    # already "Sunday" UTC, but still "Saturday" PT local time.
    ref_tz_for_day = tz_group if tz_group != "ALL" else "PT"
    local_day = local_now(ref_tz_for_day).strftime("%A")
    if local_day in ("Saturday", "Sunday") and tz_group in ("PT", "ALL"):
        generate_weekend_summary()

    print(f"\n{'='*60}")
    print(f"✅ Run complete — {written_rows} seat counts logged, {len(all_issues)} issues")
    print(f"{'='*60}")


def generate_weekend_summary():
    """Generate a weekend analysis from Thu-Sat data for the current weekend only."""
    print("\n📊 Generating weekend summary...")

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # Compute the Friday anchor for the current opening weekend so we only
    # include rows from this weekend, not all historical data.
    current_weekend = opening_weekend_friday()

    rows = []
    if SEAT_CSV.exists():
        with open(SEAT_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_weekend = row.get("weekend_of", "")
                # Accept rows that match this weekend, or rows without weekend_of (old data)
                if row_weekend and row_weekend != current_weekend:
                    continue
                rows.append(row)

    if not rows:
        print("  ⚠️  No data to summarize")
        return

    summary_path = DATA_DIR / f"weekend-summary-{today_str}.md"

    with open(summary_path, "w") as f:
        f.write(f"# Weekend Box Office Summary — {today_str}\n\n")
        f.write(f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n")

        movies = {}
        for row in rows:
            movie = row.get("movie_title", "Unknown")
            if movie not in movies:
                movies[movie] = []
            movies[movie].append(row)

        for movie, data in movies.items():
            f.write(f"## {movie}\n\n")

            occupancies = []
            for d in data:
                try:
                    occ = float(d.get("occupancy_pct", 0))
                    if occ > 0:
                        occupancies.append(occ)
                except (ValueError, TypeError):
                    pass

            if occupancies:
                avg_occ = sum(occupancies) / len(occupancies)
                f.write(f"- **Average Occupancy**: {avg_occ:.1f}%\n")
                f.write(f"- **Highest**: {max(occupancies):.1f}%\n")
                f.write(f"- **Lowest**: {min(occupancies):.1f}%\n")
                f.write(f"- **Data Points**: {len(occupancies)}\n")

            f.write("\n")

        f.write("---\n\n*This summary feeds the box office estimation model.*\n")

    print(f"  ✅ Weekend summary saved to {summary_path}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

async def run_with_preflight_async(tz_group="ALL", force=False, test_max=None, ensure_links=False):
    if ensure_links and not test_max:
        await ensure_phase1_links_async(tz_group)
    await run_async(tz_group, force=force, test_max=test_max)


def run(tz_group="ALL", force=False, test_max=None, ensure_links=False):
    """Sync wrapper for the async pipeline."""
    asyncio.run(run_with_preflight_async(
        tz_group,
        force=force,
        test_max=test_max,
        ensure_links=ensure_links,
    ))


if __name__ == "__main__":
    # Install SIGTERM handler at the very top so it covers both Phase 1 and Phase 2.
    # Without this, GitHub Actions job cancellations leave zombie Chromium processes
    # on the VPS that block the runner from accepting the next job.
    def _handle_sigterm(signum, frame):
        print("\n⚠️  SIGTERM received — shutting down gracefully", flush=True)
        # Standard SIGTERM exit code (128 + 15) so GitHub Actions and the
        # workflow's step outcome clearly reflect an external cancellation
        # rather than a normal success.
        sys.exit(143)
    signal.signal(signal.SIGTERM, _handle_sigterm)

    args = sys.argv[1:]
    collect_links_mode = "--collect-links" in args
    force_mode = "--force" in args
    ensure_links_mode = "--ensure-links" in args

    # --test N  →  run Phase 2 on N theatres only, bypass time filter
    test_max = None
    if "--test" in args:
        idx = args.index("--test")
        try:
            test_max = int(args[idx + 1])
            args = args[:idx] + args[idx + 2:]
        except (IndexError, ValueError):
            print("Usage: --test N  (N = number of theatres to test)")
            sys.exit(1)
        force_mode = True  # --test implies --force

    args = [a for a in args if a not in ("--collect-links", "--force", "--ensure-links")]

    tz = args[0].upper() if args else "ALL"

    if tz not in ("ET", "CT", "MT", "PT", "ALL"):
        print(f"Usage: python scraper.py [--collect-links] [--ensure-links] [--force] [--test N] [ET|CT|MT|PT|ALL]")
        print(f"  --collect-links  Phase 1: save showtime IDs to showtime-links.json (run at 5-6pm)")
        print(f"  --ensure-links   Phase 2: repair missing/stale Phase 1 links for this TZ before scraping")
        print(f"  --force          Force re-scrape even if showtime-links.json is stale")
        print(f"  --test N         Phase 2 test: run N theatres only, skip time filter")
        print(f"  ET               Eastern theatres only")
        print(f"  CT               Central theatres only")
        print(f"  MT               Mountain theatres only")
        print(f"  PT               Pacific theatres only")
        print(f"  ALL              All theatres (default)")
        sys.exit(1)

    if collect_links_mode:
        asyncio.run(run_collect_links_async(tz))
    else:
        run(tz, force=force_mode, test_max=test_max, ensure_links=ensure_links_mode)
