#!/usr/bin/env python3
"""
Box Office Seat-Map Tracker
Scrapes Polymarket for active box-office betting markets,
then checks AMC seat maps for occupancy data.
"""

import requests
import csv
import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SEAT_CSV = DATA_DIR / "seat-counts.csv"
POLY_CSV = DATA_DIR / "polymarket-markets.csv"
RUN_LOG  = DATA_DIR / "run-log.md"

THEATRES = {
    "ET": [
        {"name": "AMC Aventura 24",       "id": 610,  "slug": "amc-aventura-24",       "city": "Aventura, FL"},
        {"name": "AMC Neshaminy 24",      "id": 164,  "slug": "amc-neshaminy-24",      "city": "Bensalem, PA"},
        {"name": "AMC Veterans 24",       "id": 626,  "slug": "amc-veterans-24",       "city": "Tampa, FL"},
    ],
    "CT": [
        {"name": "AMC DINE-IN Mesquite 30", "id": 56, "slug": "amc-dine-in-mesquite-30", "city": "Mesquite, TX"},
        {"name": "AMC NorthPark 15",       "id": 58,  "slug": "amc-northpark-15",       "city": "Dallas, TX"},
        {"name": "AMC Gulf Pointe 30",     "id": 104, "slug": "amc-gulf-pointe-30",     "city": "Houston, TX"},
        {"name": "AMC River East 21",      "id": 322, "slug": "amc-river-east-21",      "city": "Chicago, IL"},
        {"name": "AMC DINE-IN Rosemont 12","id": 160, "slug": "amc-dine-in-rosemont-12","city": "Rosemont, IL"},
    ],
    "PT": [
        {"name": "AMC The Grove 14",      "id": 188, "slug": "amc-the-grove-14",      "city": "Los Angeles, CA"},
        {"name": "AMC Burbank 16",        "id": 2228,"slug": "amc-burbank-16",        "city": "Burbank, CA"},
    ],
}

# AMC format priority (higher = bigger room, more important)
FORMAT_PRIORITY = {
    "imax": 100,
    "dolby cinema": 90,
    "dolby": 90,
    "prime": 80,
    "prime at amc": 80,
    "laser at amc": 70,
    "reald 3d": 30,
    "standard": 10,
    "digital": 10,
}

# Headers to mimic browser requests to AMC
AMC_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.amctheatres.com/",
    "Origin": "https://www.amctheatres.com",
}


# ─── Polymarket Scraper ─────────────────────────────────────────────────────

def fetch_polymarket_box_office():
    """
    Query Polymarket Gamma API for active box-office / movie markets.
    Returns list of dicts with movie info.
    """
    print("\n📊 Checking Polymarket for active box office markets...")

    markets_found = []
    base_url = "https://gamma-api.polymarket.com/markets"

    # Search with multiple keyword strategies
    search_terms = ["box office", "opening weekend", "movie gross", "domestic gross", "weekend box office"]

    seen_ids = set()

    for term in search_terms:
        try:
            params = {
                "active": "true",
                "closed": "false",
                "limit": 50,
                "order": "volume24hr",
                "ascending": "false",
            }
            # The Gamma API supports text search via the 'tag' or general query
            # Try fetching all active markets and filtering
            resp = requests.get(base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for market in data:
                mid = market.get("id", "")
                if mid in seen_ids:
                    continue

                question = market.get("question", "").lower()
                description = market.get("description", "").lower()

                # Check if this market is about box office / movie performance
                box_office_keywords = [
                    "box office", "opening weekend", "gross", "domestic",
                    "million", "$", "movie", "film", "theater", "theatre",
                    "ticket", "blockbuster"
                ]

                is_box_office = any(kw in question for kw in box_office_keywords) or \
                                any(kw in description for kw in box_office_keywords)

                if is_box_office:
                    seen_ids.add(mid)

                    # Extract movie title from question
                    movie_title = extract_movie_title(market.get("question", ""))

                    outcome_prices = market.get("outcomePrices", "[]")
                    if isinstance(outcome_prices, str):
                        try:
                            outcome_prices = json.loads(outcome_prices)
                        except:
                            outcome_prices = []

                    markets_found.append({
                        "movie_title": movie_title,
                        "market_url": f"https://polymarket.com/event/{market.get('slug', mid)}",
                        "question": market.get("question", ""),
                        "current_odds": outcome_prices[0] if outcome_prices else "N/A",
                        "volume": market.get("volume", "N/A"),
                        "market_id": mid,
                    })
        except Exception as e:
            print(f"  ⚠️  Error searching Polymarket for '{term}': {e}")

    # Also try the events endpoint which groups related markets
    try:
        events_url = "https://gamma-api.polymarket.com/events"
        params = {"active": "true", "closed": "false", "limit": 100}
        resp = requests.get(events_url, params=params, timeout=15)
        resp.raise_for_status()
        events = resp.json()

        for event in events:
            title = event.get("title", "").lower()
            desc = event.get("description", "").lower()

            if any(kw in title or kw in desc for kw in ["box office", "opening weekend", "gross", "movie"]):
                # Get markets within this event
                event_markets = event.get("markets", [])
                for market in event_markets:
                    mid = market.get("id", "")
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)

                    outcome_prices = market.get("outcomePrices", "[]")
                    if isinstance(outcome_prices, str):
                        try:
                            outcome_prices = json.loads(outcome_prices)
                        except:
                            outcome_prices = []

                    markets_found.append({
                        "movie_title": extract_movie_title(market.get("question", event.get("title", ""))),
                        "market_url": f"https://polymarket.com/event/{event.get('slug', '')}",
                        "question": market.get("question", ""),
                        "current_odds": outcome_prices[0] if outcome_prices else "N/A",
                        "volume": market.get("volume", "N/A"),
                        "market_id": mid,
                    })
    except Exception as e:
        print(f"  ⚠️  Error fetching Polymarket events: {e}")

    print(f"  Found {len(markets_found)} box office market(s)")
    for m in markets_found:
        print(f"    • {m['movie_title']}: {m['question']}")

    return markets_found


def extract_movie_title(question):
    """
    Try to extract a movie title from a Polymarket question.
    e.g. "Will 'Thunderbolts' gross over $100M?" → "Thunderbolts"
    """
    # Look for quoted titles
    quoted = re.findall(r"['\"]([^'\"]+)['\"]", question)
    if quoted:
        return quoted[0]

    # Look for title patterns like "Will X gross..." or "X opening weekend"
    patterns = [
        r"(?:Will|Can)\s+(.+?)\s+(?:gross|earn|make|hit|reach|open)",
        r"(.+?)\s+(?:opening weekend|box office|domestic gross)",
    ]
    for pat in patterns:
        match = re.search(pat, question, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback: return the full question
    return question[:60]


def save_polymarket_data(markets):
    """Save Polymarket markets to CSV."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if today's data already exists
    existing = set()
    if POLY_CSV.exists():
        with open(POLY_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("date") == today:
                    existing.add(row.get("market_url", ""))

    new_count = 0
    with open(POLY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        for m in markets:
            if m["market_url"] not in existing:
                writer.writerow([
                    today,
                    m["movie_title"],
                    m["market_url"],
                    m["question"],
                    m["current_odds"],
                    m["volume"],
                    ""  # notes
                ])
                new_count += 1

    print(f"  Saved {new_count} new market entries to CSV")


# ─── AMC Scraper ─────────────────────────────────────────────────────────────

def fetch_amc_showtimes(theatre, date_str):
    """
    Fetch showtimes for a given AMC theatre on a given date.
    Tries the AMC website's internal API endpoints.
    Returns list of showtime dicts.
    """
    theatre_slug = theatre["slug"]
    theatre_id = theatre["id"]

    print(f"\n🎬 Fetching showtimes for {theatre['name']}...")

    # AMC's website fetches showtimes from their API
    # Try the v2 API endpoint (used by their frontend)
    urls_to_try = [
        f"https://www.amctheatres.com/api/v2/theatres/{theatre_id}/showtimes?date={date_str}",
        f"https://api.amctheatres.com/v2/theatres/{theatre_id}/showtimes?date={date_str}",
        # Their website also uses this pattern
        f"https://www.amctheatres.com/showtimes/all/{date_str}/{theatre_slug}/all",
    ]

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=AMC_HEADERS, timeout=15)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "")
                if "json" in content_type:
                    data = resp.json()
                    print(f"  ✅ Got JSON response from {url[:60]}...")
                    return parse_amc_json_showtimes(data, theatre)
                else:
                    # HTML response — parse it
                    print(f"  📄 Got HTML response from {url[:60]}...")
                    return parse_amc_html_showtimes(resp.text, theatre)
            else:
                print(f"  ❌ {resp.status_code} from {url[:60]}...")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

    print(f"  ❌ Could not fetch showtimes for {theatre['name']}")
    return []


def parse_amc_json_showtimes(data, theatre):
    """Parse JSON showtime response from AMC API."""
    showtimes = []

    # Handle different JSON structures
    if isinstance(data, dict):
        # Could be nested under various keys
        items = data.get("showtimes", data.get("_embedded", {}).get("showtimes", []))
        if not items and "movies" in data:
            items = data["movies"]
    elif isinstance(data, list):
        items = data
    else:
        return []

    for item in items:
        movie_name = item.get("movieName", item.get("title", item.get("name", "Unknown")))

        # Get showtime details
        performances = item.get("showtimes", item.get("performances", [item]))

        for perf in performances:
            showtime_str = perf.get("showtime", perf.get("startTime", perf.get("performanceTime", "")))
            auditorium = perf.get("auditorium", perf.get("theatreName", ""))
            format_type = perf.get("format", perf.get("movieFormat", perf.get("experienceType", "Standard")))
            perf_id = perf.get("id", perf.get("performanceId", perf.get("showtimeId", "")))

            showtimes.append({
                "movie": movie_name,
                "showtime": showtime_str,
                "auditorium": auditorium,
                "format": format_type,
                "performance_id": perf_id,
                "theatre": theatre,
            })

    return showtimes


def parse_amc_html_showtimes(html, theatre):
    """Parse HTML showtime page from AMC website."""
    showtimes = []

    # Look for JSON data embedded in the HTML (common pattern)
    # AMC often includes a __NEXT_DATA__ or similar JSON blob
    json_patterns = [
        r'__NEXT_DATA__\s*=\s*({.*?})\s*</script>',
        r'window\.__data\s*=\s*({.*?})\s*;',
        r'"showtimes"\s*:\s*(\[.*?\])',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                print(f"  📦 Found embedded JSON data")
                return parse_amc_json_showtimes(data, theatre)
            except json.JSONDecodeError:
                continue

    # Fallback: parse HTML with regex (basic approach)
    # Look for showtime links like <a href="/showtimes/..." data-showtime="7:00pm">
    showtime_blocks = re.findall(
        r'data-(?:showtime|time)=["\']([^"\']+)["\'].*?'
        r'(?:data-movie(?:name|title)=["\']([^"\']+)["\'])?',
        html, re.DOTALL | re.IGNORECASE
    )

    for time_str, movie in showtime_blocks:
        showtimes.append({
            "movie": movie or "Unknown",
            "showtime": time_str,
            "auditorium": "",
            "format": "Standard",
            "performance_id": "",
            "theatre": theatre,
        })

    if not showtimes:
        print(f"  ⚠️  Could not parse showtimes from HTML")

    return showtimes


def fetch_amc_seat_map(performance_id, theatre):
    """
    Fetch seat map for a specific performance.
    Returns dict with total_seats, seats_sold, seats_available.
    """
    if not performance_id:
        return None

    print(f"  🪑 Fetching seat map for performance {performance_id}...")

    urls_to_try = [
        f"https://www.amctheatres.com/api/v2/performances/{performance_id}/seats",
        f"https://api.amctheatres.com/v2/performances/{performance_id}/seats",
        f"https://www.amctheatres.com/api/v2/theatres/{theatre['id']}/performances/{performance_id}/seatmap",
    ]

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=AMC_HEADERS, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return parse_seat_map(data)
        except Exception as e:
            print(f"  ⚠️  Seat map error: {e}")

    return None


def parse_seat_map(data):
    """Parse seat map data and count seats."""
    total = 0
    sold = 0
    available = 0

    # Handle different data structures
    seats = data.get("seats", data.get("seatMap", {}).get("seats", []))

    if isinstance(seats, list):
        for seat in seats:
            if isinstance(seat, dict):
                total += 1
                status = seat.get("status", seat.get("seatStatus", "")).lower()
                if status in ("sold", "occupied", "taken", "held", "reserved", "unavailable"):
                    sold += 1
                elif status in ("available", "open", "free"):
                    available += 1
                else:
                    # Unknown status — count as available by default
                    available += 1

    # Sometimes seats are nested in rows
    if not seats and "rows" in data:
        for row in data.get("rows", []):
            row_seats = row.get("seats", [])
            for seat in row_seats:
                total += 1
                status = seat.get("status", seat.get("seatStatus", "")).lower()
                if status in ("sold", "occupied", "taken", "held", "reserved", "unavailable"):
                    sold += 1
                else:
                    available += 1

    return {
        "total_seats": total,
        "seats_sold": sold,
        "seats_available": available,
        "occupancy_pct": round(sold / total * 100, 1) if total > 0 else 0,
    }


def get_format_priority(format_str):
    """Get priority score for an auditorium format."""
    if not format_str:
        return 0
    fmt_lower = format_str.lower()
    for key, priority in FORMAT_PRIORITY.items():
        if key in fmt_lower:
            return priority
    return 10  # default standard


def find_main_show(showtimes, movie_title):
    """
    From a list of showtimes for a movie at a theatre,
    find the "main show" — biggest room, prime evening slot.
    """
    # Filter to this movie (fuzzy match)
    movie_lower = movie_title.lower().strip()
    matching = [s for s in showtimes if movie_lower in s.get("movie", "").lower() or
                s.get("movie", "").lower() in movie_lower]

    if not matching:
        return None, "Movie not showing at this theatre"

    # Filter to evening window (5 PM - 9:30 PM)
    evening = []
    for s in matching:
        hour = parse_showtime_hour(s.get("showtime", ""))
        if hour and 17 <= hour <= 21.5:
            evening.append(s)

    if not evening:
        # No evening shows — use whatever is available
        evening = matching

    # Sort by: format priority (descending), then closeness to 7 PM
    def sort_key(s):
        fmt_priority = get_format_priority(s.get("format", ""))
        hour = parse_showtime_hour(s.get("showtime", "")) or 19
        closeness_to_7pm = abs(hour - 19)  # how far from 7 PM
        return (-fmt_priority, closeness_to_7pm)

    evening.sort(key=sort_key)

    best = evening[0]
    reason = f"Selected {best.get('format', 'Standard')} at {best.get('showtime', '?')} — " \
             f"highest format priority, closest to prime time"

    # Also return runner-up if it's a different format (e.g. IMAX primary + Dolby secondary)
    runner_up = None
    if len(evening) > 1:
        second = evening[1]
        if get_format_priority(second.get("format", "")) >= 80 and \
           second.get("format", "").lower() != best.get("format", "").lower():
            runner_up = second

    return best, reason, runner_up


def parse_showtime_hour(time_str):
    """Parse a time string into decimal hours (e.g. '7:30 PM' → 19.5)."""
    if not time_str:
        return None

    # Handle various formats
    time_str = time_str.strip().upper()

    patterns = [
        r'(\d{1,2}):(\d{2})\s*(AM|PM)',       # "7:30 PM"
        r'(\d{1,2})(\d{2})\s*(AM|PM)',         # "730PM"
        r'T(\d{2}):(\d{2})',                     # ISO format "T19:30"
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

def run(tz_group="ALL"):
    """
    Main entry point.
    tz_group: "ET", "CT", "PT", or "ALL"
    """
    print(f"{'='*60}")
    print(f"🎬 Box Office Tracker — {tz_group} Group")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Step 1: Get Polymarket movies
    poly_markets = fetch_polymarket_box_office()
    save_polymarket_data(poly_markets)

    if not poly_markets:
        print("\n❌ No active box office markets on Polymarket. Nothing to track.")
        log_run(tz_group, [], [], ["No active Polymarket box office markets found"])
        return

    movie_titles = [m["movie_title"] for m in poly_markets]
    market_urls = {m["movie_title"]: m["market_url"] for m in poly_markets}

    # Step 2: Check theatres
    today = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().strftime("%A")

    groups_to_check = [tz_group] if tz_group != "ALL" else ["ET", "CT", "PT"]

    all_results = []
    all_issues = []

    for group in groups_to_check:
        theatres = THEATRES.get(group, [])
        print(f"\n{'─'*40}")
        print(f"🏛️  Checking {len(theatres)} {group} theatre(s)...")

        for theatre in theatres:
            showtimes = fetch_amc_showtimes(theatre, today)

            if not showtimes:
                issue = f"{theatre['name']}: No showtimes retrieved"
                print(f"  ⚠️  {issue}")
                all_issues.append(issue)
                continue

            print(f"  📋 Found {len(showtimes)} total showtime(s)")

            for movie_title in movie_titles:
                best_show, reason, *extra = find_main_show(showtimes, movie_title)
                runner_up = extra[0] if extra else None

                if best_show is None:
                    issue = f"{theatre['name']}: '{movie_title}' not showing"
                    print(f"  ⚠️  {issue}")
                    all_issues.append(issue)
                    continue

                print(f"  🎯 Main show: {movie_title} — {best_show.get('format', 'Std')} @ {best_show.get('showtime', '?')}")
                print(f"     Reason: {reason}")

                # Fetch seat map
                seat_data = fetch_amc_seat_map(best_show.get("performance_id"), theatre)

                check_time = datetime.now().strftime("%I:%M %p")
                showtime_hour = parse_showtime_hour(best_show.get("showtime", ""))
                current_hour = datetime.now().hour + datetime.now().minute / 60
                delta_minutes = int((current_hour - (showtime_hour or current_hour)) * 60)

                if seat_data:
                    print(f"  🪑 Seats: {seat_data['seats_sold']}/{seat_data['total_seats']} "
                          f"({seat_data['occupancy_pct']}% full)")

                    row = [
                        today, day_of_week, theatre["name"], theatre["city"], group,
                        movie_title, market_urls.get(movie_title, ""),
                        best_show.get("showtime", ""), check_time, delta_minutes,
                        best_show.get("auditorium", ""), best_show.get("format", "Standard"),
                        seat_data["total_seats"], seat_data["seats_sold"],
                        seat_data["seats_available"], seat_data["occupancy_pct"],
                        "", reason
                    ]
                    log_seat_data(row)

                    all_results.append({
                        "theatre": theatre["name"],
                        "movie": movie_title,
                        "format": best_show.get("format", "Standard"),
                        "showtime": best_show.get("showtime", "?"),
                        "occupancy": seat_data["occupancy_pct"],
                        "delta": delta_minutes,
                    })
                else:
                    issue = f"{theatre['name']}: Could not fetch seat map for {movie_title}"
                    print(f"  ⚠️  {issue}")
                    all_issues.append(issue)

                    # Still log what we know (without seat data)
                    row = [
                        today, day_of_week, theatre["name"], theatre["city"], group,
                        movie_title, market_urls.get(movie_title, ""),
                        best_show.get("showtime", ""), check_time, delta_minutes,
                        best_show.get("auditorium", ""), best_show.get("format", "Standard"),
                        "", "", "", "", "", f"Seat map unavailable. {reason}"
                    ]
                    log_seat_data(row)

                # Also check runner-up format if available
                if runner_up:
                    print(f"  🔄 Also checking secondary format: {runner_up.get('format', 'Std')} @ {runner_up.get('showtime', '?')}")
                    seat_data2 = fetch_amc_seat_map(runner_up.get("performance_id"), theatre)
                    if seat_data2:
                        row = [
                            today, day_of_week, theatre["name"], theatre["city"], group,
                            movie_title, market_urls.get(movie_title, ""),
                            runner_up.get("showtime", ""), check_time,
                            int((current_hour - (parse_showtime_hour(runner_up.get("showtime", "")) or current_hour)) * 60),
                            runner_up.get("auditorium", ""), runner_up.get("format", "Standard"),
                            seat_data2["total_seats"], seat_data2["seats_sold"],
                            seat_data2["seats_available"], seat_data2["occupancy_pct"],
                            "", f"Secondary format. {reason}"
                        ]
                        log_seat_data(row)

    # Step 3: Log the run
    log_run(tz_group, movie_titles, all_results, all_issues)

    # Step 4: Weekend summary (if Saturday and PT or ALL)
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

    # Read all seat count data
    rows = []
    if SEAT_CSV.exists():
        with open(SEAT_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Include rows from the past 3 days
                rows.append(row)

    if not rows:
        print("  ⚠️  No data to summarize")
        return

    summary_path = DATA_DIR / f"weekend-summary-{today_str}.md"

    with open(summary_path, "w") as f:
        f.write(f"# Weekend Box Office Summary — {today_str}\n\n")
        f.write(f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n")

        # Group by movie
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

if __name__ == "__main__":
    tz = sys.argv[1].upper() if len(sys.argv) > 1 else "ALL"

    if tz not in ("ET", "CT", "PT", "ALL"):
        print(f"Usage: python scraper.py [ET|CT|PT|ALL]")
        print(f"  ET  — Eastern theatres only")
        print(f"  CT  — Central theatres only")
        print(f"  PT  — Pacific theatres only")
        print(f"  ALL — All theatres (default)")
        sys.exit(1)

    run(tz)
