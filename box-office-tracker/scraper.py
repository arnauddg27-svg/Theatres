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
import re
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

THEATRES_JSON = DATA_DIR / "theatres-all.json"
LINKS_JSON    = DATA_DIR / "showtime-links.json"  # Phase 1 output / Phase 2 input


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

# Concurrency — how many browser tabs to run in parallel.
MAX_CONCURRENT_TABS = 5

# UTC offsets for each tz group (April = DST in effect for US)
TZ_UTC_OFFSET = {"ET": -4, "CT": -5, "MT": -6, "PT": -7}


def local_now(tz_group):
    """Return current datetime adjusted to the local time for a tz group."""
    offset = TZ_UTC_OFFSET.get(tz_group, 0)
    return datetime.now(timezone.utc) + timedelta(hours=offset)


def local_date_str(tz_group):
    """Return today's date string in the local timezone of the tz group."""
    return local_now(tz_group).strftime("%Y-%m-%d")


def opening_weekend_friday(dt=None):
    """Return the Friday that anchors this opening weekend.

    Thu→Sun all map to the same Friday. This is the 'weekend_of' key
    that lets predict.py group data from one opening weekend together
    and ignore data from previous weekends for the same movie.
    """
    dt = dt or datetime.now()
    weekday = dt.weekday()  # Mon=0 ... Sun=6
    if weekday == 3:    # Thursday
        friday = dt + timedelta(days=1)
    elif weekday == 4:  # Friday
        friday = dt
    elif weekday == 5:  # Saturday
        friday = dt - timedelta(days=1)
    elif weekday == 6:  # Sunday
        friday = dt - timedelta(days=2)
    else:
        friday = dt  # Mon-Wed shouldn't happen (day guard), but be safe
    return friday.strftime("%Y-%m-%d")


# ─── Polymarket Scraper ─────────────────────────────────────────────────────

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

    markets_found = []
    seen_movies = set()

    for event in events:
        title = event.get("title", "")
        title_lower = title.lower()

        # Same filter as trade.py: must have BOTH keywords
        if "opening weekend" not in title_lower or "box office" not in title_lower:
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

        if movie_name in seen_movies:
            continue
        seen_movies.add(movie_name)

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

        markets_found.append({
            "movie_title": movie_name,
            "market_url": event_url,
            "question": title,
            "current_odds": "N/A",
            "volume": total_volume,
            "market_id": str(event.get("id", "")),
            "bracket_markets": bracket_markets,
        })

    print(f"  Found {len(markets_found)} box office movie(s)")
    for m in markets_found:
        print(f"    • {m['movie_title']} (vol: ${m['volume']:,.0f})")

    return markets_found


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


# ─── AMC Playwright Scraper ─────────────────────────────────────────────────

async def fetch_amc_showtimes_pw(page, theatre, date_str):
    """
    Fetch showtimes for a theatre using Playwright.

    Navigates to AMC's showtime page and waits for movie <section> elements
    to appear (smart wait instead of fixed sleep). Falls back to a short
    sleep if sections never appear (empty showtime day).

    Returns list of showtime dicts.
    """
    theatre_slug = theatre["slug"]
    url = f"https://www.amctheatres.com/showtimes/all/{date_str}/{theatre_slug}/all"

    print(f"  🎬 {theatre['name']}...")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Smart wait: watch for the actual showtime sections to render
        try:
            await page.wait_for_selector(
                'section[aria-label^="Showtimes for"]', timeout=12000
            )
        except Exception:
            # No sections appeared — page may be empty or slow
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


async def fetch_amc_seat_map_pw(page, showtime_id):
    """
    Fetch seat map for a specific showtime using Playwright.

    Navigates to /showtimes/{id} which redirects to /showtimes/{id}/seats.
    Waits for seat <input> elements to render, then counts them.

    Returns dict with total_seats, seats_sold, seats_available, occupancy_pct.
    """
    if not showtime_id:
        return None

    url = f"https://www.amctheatres.com/showtimes/{showtime_id}"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Smart wait: seat inputs appear once the seat map JS hydrates
        try:
            await page.wait_for_selector(
                'input[aria-label*="Recliner"], input[aria-label*="Seat"]',
                timeout=10000,
            )
        except Exception:
            # No seat inputs — general admission or broken page
            return None
    except Exception as e:
        print(f"      ⚠️  Seat page failed: {e}")
        return None

    seat_data = await page.evaluate(COUNT_SEATS_JS)

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
        if (!(/[a-z]\d+/.test(label) || label.includes('recliner') || label.includes('seat'))) {
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


def find_evening_shows(showtimes, movie_title, current_hour=None):
    """
    Find all past/in-progress evening shows (5pm-midnight) for a movie.

    Returns ALL shows per format that have already started (showtime <= now),
    so we capture actual attendance rather than advance bookings.
    If no shows have started yet (early run), falls back to all evening shows.

    current_hour: decimal hour in local theatre timezone (e.g. 21.5 = 9:30pm).
                  Defaults to now if not provided.
    """
    if current_hour is None:
        now = datetime.now()
        current_hour = now.hour + now.minute / 60

    movie_lower = movie_title.lower().strip()
    matching = [s for s in showtimes
                if movie_lower in s.get("movie", "").lower()
                or s.get("movie", "").lower() in movie_lower]

    if not matching:
        return []

    # Filter to evening window (5pm - midnight)
    evening = [s for s in matching
               if parse_showtime_hour(s.get("showtime", "")) is not None
               and 17 <= parse_showtime_hour(s.get("showtime", "")) <= 24]

    if not evening:
        evening = matching

    # Only keep shows that have already started (showtime <= now)
    started = [s for s in evening
               if (parse_showtime_hour(s.get("showtime", "")) or 25) <= current_hour]

    # If nothing has started yet, fall back to all evening shows
    if not started:
        started = evening

    # Return ALL started shows per format (not just one per format)
    results = []
    seen = set()
    for s in sorted(started,
                    key=lambda x: -(parse_showtime_hour(x.get("showtime", "")) or 0)):
        fmt = s.get("format", "Standard")
        st = s.get("showtime", "?")
        key = (fmt, st)
        if key in seen:
            continue
        seen.add(key)
        reason = f"{fmt} @ {st} (started, past showtime)"
        results.append((s, reason))

    # Sort by format priority
    results.sort(key=lambda x: -get_format_priority(x[0].get("format", "")))
    return results


# ─── Data Logging ────────────────────────────────────────────────────────────

def ensure_csv_header():
    """Create seat-counts.csv with header if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SEAT_CSV.exists():
        with open(SEAT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "weekend_of", "run_id",
                "date", "day_of_week", "theatre_name", "theatre_city",
                "timezone", "movie_title", "polymarket_market", "showtime",
                "check_time", "minutes_after_showtime", "auditorium_name",
                "auditorium_type", "total_seats", "seats_sold",
                "seats_available", "occupancy_pct", "ticket_price_estimate",
                "amc_seat_map_url", "notes",
            ])


def log_seat_data(row_data):
    """Append a row to the seat counts CSV."""
    with open(SEAT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row_data)


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


# ─── Main Orchestrator ───────────────────────────────────────────────────────

async def _scrape_theatre(browser, theatre, date_str, movie_titles, market_urls,
                          weekend_of="", run_id="", saved_movies=None):
    """
    Scrape one theatre's showtimes + seat maps on its own browser tab.

    saved_movies: if provided (Phase 2), skip the showtime page entirely and
                  use pre-saved {movie_title: [{showtime, showtime_id, format}]}
                  collected during Phase 1 (collect-links run).

    Returns (results_list, issues_list, csv_rows_list).
    """
    tz = theatre.get("_tz", "")
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    results = []
    issues = []
    csv_rows = []
    # Use the passed date_str (already adjusted to local TZ) as the CSV date stamp
    today = date_str
    day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")

    try:
        current_hour = datetime.now().hour + datetime.now().minute / 60
        check_time = datetime.now().isoformat()

        if saved_movies is not None:
            # ── Phase 2 path: use pre-collected showtime IDs ──────────────────
            # Build evening_shows directly from saved links (all started shows)
            movie_shows_map = {}
            for movie_title, entries in saved_movies.items():
                started = [
                    e for e in entries
                    if (parse_showtime_hour(e.get("showtime", "")) or 25) <= current_hour
                ]
                if not started:
                    started = entries  # fallback: nothing started yet
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
                movie_shows_map[movie_title] = shows
        else:
            # ── Phase 1 / standalone path: fetch showtime page live ───────────
            showtimes = await fetch_amc_showtimes_pw(page, theatre, date_str)

            if not showtimes:
                issues.append(f"{theatre['name']}: No showtimes retrieved")
                return results, issues, csv_rows

            movie_shows_map = {}
            for movie_title in movie_titles:
                evening_shows = find_evening_shows(showtimes, movie_title, current_hour)
                if not evening_shows:
                    issues.append(f"{theatre['name']}: '{movie_title}' not showing or no started shows")
                movie_shows_map[movie_title] = evening_shows

        for movie_title, evening_shows in movie_shows_map.items():
            if not evening_shows:
                continue

            for show, reason in evening_shows:
                fmt = show.get("format", "Standard")
                st = show.get("showtime", "?")
                flags = show.get("flags", "")

                seat_data = await fetch_amc_seat_map_pw(page, show.get("showtime_id"))

                showtime_hour = parse_showtime_hour(st)
                delta_minutes = int((current_hour - (showtime_hour or current_hour)) * 60)

                if seat_data:
                    occ = seat_data["occupancy_pct"]
                    print(f"    🪑 {theatre['name']}: {movie_title} {fmt} — "
                          f"{seat_data['seats_sold']}/{seat_data['total_seats']} ({occ}%)")

                    showtime_id = show.get("showtime_id", "")
                    amc_url = f"https://www.amctheatres.com/showtimes/{showtime_id}" if showtime_id else ""
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
                    issues.append(f"{theatre['name']}: No seat map for {movie_title} {fmt}")
                    showtime_id = show.get("showtime_id", "")
                    amc_url = f"https://www.amctheatres.com/showtimes/{showtime_id}" if showtime_id else ""
                    csv_rows.append([
                        weekend_of, run_id,
                        today, day_of_week, theatre["name"], theatre.get("city", theatre.get("dma", "")),
                        tz, movie_title, market_urls.get(movie_title, ""),
                        st, check_time, delta_minutes,
                        "", fmt, "", "", "", "", "",
                        amc_url, f"Seat map unavailable. {flags}. {reason}",
                    ])
    finally:
        await context.close()

    return results, issues, csv_rows


async def _collect_links_theatre(browser, theatre, date_str, movie_titles):
    """
    Phase 1: Visit a theatre's showtime page and save all evening showtime IDs.
    No seat maps fetched — just links for later.
    Returns dict: {movie_title: [{showtime, showtime_id, format}, ...]}
    """
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    collected = {}
    try:
        showtimes = await fetch_amc_showtimes_pw(page, theatre, date_str)
        for movie_title in movie_titles:
            movie_lower = movie_title.lower().strip()
            matching = [s for s in showtimes
                        if movie_lower in s.get("movie", "").lower()
                        or s.get("movie", "").lower() in movie_lower]
            evening = [s for s in matching
                       if parse_showtime_hour(s.get("showtime", "")) is not None
                       and 17 <= parse_showtime_hour(s.get("showtime", "")) <= 24]
            if evening:
                collected[movie_title] = [
                    {"showtime": s.get("showtime"), "showtime_id": s.get("showtime_id"),
                     "format": s.get("format", "Standard")}
                    for s in evening
                ]
    except Exception as e:
        print(f"  ⚠️  {theatre['name']}: {e}")
    finally:
        await context.close()
    return collected


async def run_collect_links_async(tz_group="ALL"):
    """
    Phase 1 main: Visit all theatres, save showtime IDs to showtime-links.json.
    Run at ~5-6pm ET before shows start.
    """
    print(f"{'='*60}")
    print(f"📋 Phase 1 — Collecting showtime links ({tz_group})")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    theatres_map = load_theatres()
    poly_markets = fetch_polymarket_box_office()
    save_polymarket_data(poly_markets)

    if not poly_markets:
        print("❌ No active Polymarket box office markets.")
        return

    movie_titles = [m["movie_title"] for m in poly_markets]
    ref_tz = tz_group if tz_group != "ALL" else "ET"
    today = local_date_str(ref_tz)
    groups = [tz_group] if tz_group != "ALL" else ["ET", "CT", "PT"]
    all_theatres = []
    for group in groups:
        for t in theatres_map.get(group, []):
            all_theatres.append({**t, "_tz": group, "_date": local_date_str(group)})

    print(f"\n🏛️  Visiting {len(all_theatres)} theatres to collect links...")

    links = {"date": today, "collected_at": datetime.now().isoformat(), "theatres": {}}
    sem = asyncio.Semaphore(MAX_CONCURRENT_TABS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        async def bounded(theatre):
            async with sem:
                t_date = theatre.get("_date", today)
                result = await _collect_links_theatre(browser, theatre, t_date, movie_titles)
                return theatre["name"], theatre.get("_tz", ""), result

        outcomes = await asyncio.gather(*[bounded(t) for t in all_theatres], return_exceptions=True)
        await browser.close()

    total_links = 0
    for outcome in outcomes:
        if isinstance(outcome, Exception):
            continue
        name, tz, collected = outcome
        if collected:
            links["theatres"][name] = {"tz": tz, "movies": collected}
            total_links += sum(len(v) for v in collected.values())

    DATA_DIR.mkdir(exist_ok=True)
    with open(LINKS_JSON, "w") as f:
        json.dump(links, f, indent=2)

    print(f"\n✅ Saved {total_links} showtime links from {len(links['theatres'])} theatres → {LINKS_JSON}")


async def run_async(tz_group="ALL"):
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
    groups_to_check = [tz_group] if tz_group != "ALL" else ["ET", "CT", "PT"]
    # For mixed-TZ runs use ET as the reference (most conservative, first to tick over)
    ref_tz = tz_group if tz_group != "ALL" else "ET"
    local = local_now(ref_tz)
    today = local.strftime("%Y-%m-%d")
    local_dow = local.strftime("%A")

    # Only collect data Thu-Sun (opening weekend). Mon-Wed data has no
    # day-weight in predict.py and would corrupt the weekend projection.
    if local_dow not in ("Thursday", "Friday", "Saturday", "Sunday"):
        print(f"\n⚠️  Today is {local_dow} ({ref_tz} local) — skipping collection.")
        print(f"   Seat data is only useful Thu-Sun (opening weekend).")
        print(f"   Use 'python scraper.py --force' to override.")
        if "--force" not in sys.argv:
            return

    theatres_map = load_theatres()

    # Step 1: Get Polymarket movies
    poly_markets = fetch_polymarket_box_office()
    save_polymarket_data(poly_markets)

    if not poly_markets:
        print("\n❌ No active box office markets on Polymarket. Nothing to track.")
        log_run(tz_group, [], [], ["No active Polymarket box office markets found"])
        return

    movie_titles = [m["movie_title"] for m in poly_markets]
    market_urls = {m["movie_title"]: m["market_url"] for m in poly_markets}

    # Step 2: Build flat list of theatres to scrape
    weekend = opening_weekend_friday(local)
    run_id = local.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]

    all_theatres = []
    for group in groups_to_check:
        # Each group uses its own local date for the AMC showtime URL
        for theatre in theatres_map.get(group, []):
            all_theatres.append({**theatre, "_tz": group, "_date": local_date_str(group)})

    # Check for Phase 1 links saved today (use per-group local date)
    saved_links = None
    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                links_data = json.load(f)
            if links_data.get("date") == today:
                saved_links = links_data.get("theatres", {})
                print(f"\n📂 Found Phase 1 links for today ({len(saved_links)} theatres) — skipping showtime pages")
            else:
                print(f"\n⚠️  showtime-links.json is from {links_data.get('date')}, not today — fetching live")
        except Exception as e:
            print(f"\n⚠️  Could not load showtime-links.json: {e} — fetching live")

    print(f"\n🏛️  Scraping {len(all_theatres)} theatres across {len(groups_to_check)} timezone(s)...")
    print(f"   Weekend: {weekend}  Run: {run_id}")

    # Step 3: Parallel scrape with semaphore
    all_results = []
    all_issues = []
    sem = asyncio.Semaphore(MAX_CONCURRENT_TABS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        async def bounded_scrape(theatre):
            async with sem:
                t_date = theatre.get("_date", today)
                theatre_saved = None
                if saved_links is not None:
                    entry = saved_links.get(theatre["name"])
                    if entry:
                        theatre_saved = entry.get("movies")
                return await _scrape_theatre(
                    browser, theatre, t_date, movie_titles, market_urls,
                    weekend_of=weekend, run_id=run_id,
                    saved_movies=theatre_saved,
                )

        tasks = [bounded_scrape(t) for t in all_theatres]
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        await browser.close()

    # Step 4: Collect results and write CSV rows
    for i, outcome in enumerate(outcomes):
        if isinstance(outcome, Exception):
            name = all_theatres[i]["name"]
            all_issues.append(f"{name}: {outcome}")
            print(f"  ❌ {name}: {outcome}")
            continue
        results, issues, csv_rows = outcome
        all_results.extend(results)
        all_issues.extend(issues)
        for row in csv_rows:
            log_seat_data(row)

    # Step 5: Log and summarize
    log_run(tz_group, movie_titles, all_results, all_issues)

    day_of_week = datetime.now().strftime("%A")
    if day_of_week == "Saturday" and tz_group in ("PT", "ALL"):
        generate_weekend_summary()

    print(f"\n{'='*60}")
    print(f"✅ Run complete — {len(all_results)} seat counts logged, {len(all_issues)} issues")
    print(f"{'='*60}")


def generate_weekend_summary():
    """Generate a weekend analysis from Thu-Sat data."""
    print("\n📊 Generating weekend summary...")

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    rows = []
    if SEAT_CSV.exists():
        with open(SEAT_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
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

def run(tz_group="ALL"):
    """Sync wrapper for the async pipeline."""
    asyncio.run(run_async(tz_group))


if __name__ == "__main__":
    args = sys.argv[1:]
    collect_links_mode = "--collect-links" in args
    args = [a for a in args if a != "--collect-links"]

    tz = args[0].upper() if args else "ALL"

    if tz not in ("ET", "CT", "PT", "ALL", "--FORCE"):
        print(f"Usage: python scraper.py [--collect-links] [ET|CT|PT|ALL]")
        print(f"  --collect-links  Phase 1: save showtime IDs to showtime-links.json (run at 5-6pm)")
        print(f"  ET               Eastern theatres only")
        print(f"  CT               Central theatres only")
        print(f"  PT               Pacific theatres only")
        print(f"  ALL              All theatres (default)")
        sys.exit(1)

    if collect_links_mode:
        asyncio.run(run_collect_links_async(tz))
    else:
        run(tz)
