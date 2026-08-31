#!/usr/bin/env python3
"""Cinemark DIRECT pre-reservation collector (split-lane Phase C scaling).

WHY DIRECT: the Fandango lane is capped by a per-Azure-range seat-backend
budget (~260 RC theatres/weekend ceiling, fan-out can't beat it). Cinemark's
own site is an independent rate-limit domain with no Cloudflare wall for real
browsers (probes 2026-08-31, runs 33420670022 / 33423747388): every showtime
on a theatre page is a deterministic seat-map link
    /TicketSeatMap/?TheaterId=..&ShowtimeId=..&Showtime=YYYY-MM-DDTHH:MM:SS
and the seat map renders WITHOUT login (819 seat elements, 124 seat buttons,
available/unavailable state classes, server-rendered DOM). Regal stays on
Fandango (its own site runs Cloudflare Turnstile).

ISOLATION CONTRACT: writes ONLY data/cinemark-pre-reservation-snapshots.csv —
same superset schema as the Fandango file (PRE_RESERVATION_FIELDS + chain),
chain="CNMK", scrape_run_id prefixed "cinemark-". Separate file from the
Fandango lane so overlapping CNMK coverage never double-counts at write time;
readers merge with explicit precedence later. Gated OUT of the model.

Discovery: --discover crawls the sitemap for /theatres/{state-city}/{slug}
URLs into data/theatres-cinemark.json. Collection loads that pool, renders
each theatre's showtimes page (dateless: current local day, rolls overnight —
the ?showDate param is ignored by the site, so dated pre-opening collection
needs date-picker interaction, NOT built yet), matches tracked titles via the
/movies/<slug> link nearest each seat-map anchor, then visits capped seat
maps and records reserved = total_seat_buttons - available.

Run:  python3 cinemark_collect.py --discover        # build/refresh the pool
      python3 cinemark_collect.py                   # tracked titles, capped
      python3 cinemark_collect.py --selftest        # offline logic checks
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from scraper import (
    PRE_RESERVATION_FIELDS,
    phase1_weekend_anchor,
    opening_weekend_show_dates,
    tracked_movie_titles_from_state,
    snapshot_bucket,
    should_record_pre_reservation_snapshot,
)
from fandango_collect import (
    slugify_title,
    _slug_tokens,
    FANDANGO_PRE_RESERVATION_FIELDS,
    FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
CINEMARK_CSV = DATA_DIR / "cinemark-pre-reservation-snapshots.csv"
THEATRES_JSON = DATA_DIR / "theatres-cinemark.json"
BASE = "https://www.cinemark.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CINEMARK_FIELDS = FANDANGO_PRE_RESERVATION_FIELDS
CINEMARK_DEDUPE_FIELDS = FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except (TypeError, ValueError):
        return default


CINEMARK_DEADLINE_SEC = _env_int("CINEMARK_DEADLINE_SEC", 2100)
CINEMARK_PER_THEATRE_CAP = _env_int("CINEMARK_PER_THEATRE_CAP", 2)
CINEMARK_MAX_THEATRES = _env_int("CINEMARK_MAX_THEATRES", 0)
CINEMARK_NUM_SHARDS = _env_int("CINEMARK_NUM_SHARDS", 0)
CINEMARK_SHARD = _env_int("CINEMARK_SHARD", 0)
CINEMARK_MIN_SEATS = 20      # completeness floor: a real auditorium has >= this
CINEMARK_POLITE_SEC = (1.0, 2.5)

# US state abbreviations -> IANA timezone (coarse; per-theatre showtime math
# only needs the LOCAL date/day, and each state's dominant zone is right for
# that purpose; split-zone states use their majority zone).
STATE_TZ = {
    "ct": "America/New_York", "de": "America/New_York", "fl": "America/New_York",
    "ga": "America/New_York", "ma": "America/New_York", "md": "America/New_York",
    "me": "America/New_York", "mi": "America/New_York", "nc": "America/New_York",
    "nh": "America/New_York", "nj": "America/New_York", "ny": "America/New_York",
    "oh": "America/New_York", "pa": "America/New_York", "ri": "America/New_York",
    "sc": "America/New_York", "va": "America/New_York", "vt": "America/New_York",
    "wv": "America/New_York", "in": "America/New_York", "ky": "America/New_York",
    "al": "America/Chicago", "ar": "America/Chicago", "ia": "America/Chicago",
    "il": "America/Chicago", "ks": "America/Chicago", "la": "America/Chicago",
    "mn": "America/Chicago", "mo": "America/Chicago", "ms": "America/Chicago",
    "nd": "America/Chicago", "ne": "America/Chicago", "ok": "America/Chicago",
    "sd": "America/Chicago", "tn": "America/Chicago", "tx": "America/Chicago",
    "wi": "America/Chicago",
    "az": "America/Phoenix", "co": "America/Denver", "id": "America/Denver",
    "mt": "America/Denver", "nm": "America/Denver", "ut": "America/Denver",
    "wy": "America/Denver",
    "ca": "America/Los_Angeles", "nv": "America/Los_Angeles",
    "or": "America/Los_Angeles", "wa": "America/Los_Angeles",
    "ak": "America/Anchorage", "hi": "Pacific/Honolulu",
}

THEATRE_URL_RE = re.compile(r"/theatres/([a-z]{2})-([a-z0-9\-]+)/([a-z0-9\-]+)/?$")


# ── Pure logic (offline-testable) ────────────────────────────────────────────

def parse_seatmap_href(href):
    """'/TicketSeatMap/?TheaterId=207&ShowtimeId=645731&...&Showtime=2026-08-31T22:50:00'
    -> {'theater_id': '207', 'showtime_id': '645731', 'sdate': '2026-08-31 22:50'} or None."""
    if not href or "TicketSeatMap" not in href:
        return None
    q = parse_qs(urlparse(href).query)
    theater_id = (q.get("TheaterId") or [None])[0]
    showtime_id = (q.get("ShowtimeId") or [None])[0]
    raw = (q.get("Showtime") or [None])[0]
    if not (theater_id and showtime_id and raw):
        return None
    try:
        dt = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return {"theater_id": theater_id, "showtime_id": showtime_id,
            "sdate": dt.strftime("%Y-%m-%d %H:%M")}


def match_movie_slug(movie_href, target_slugs):
    """'/movies/avengers-endgame-encore' -> canonical tracked title or None.

    Exact slug match first, then normalized token-set equality (reuses the
    Fandango lane's numeral normalization). Cinemark movie slugs carry no
    trailing id, so no suffix stripping is needed.
    """
    if not movie_href:
        return None
    m = re.search(r"/movies/([a-z0-9\-]+)", movie_href)
    if not m:
        return None
    core = m.group(1)
    hit = target_slugs.get(core)
    if hit:
        return hit
    tokens = _slug_tokens(core)
    for slug, title in target_slugs.items():
        if _slug_tokens(slug) == tokens:
            return title
    return None


def theatre_from_url(url):
    """Sitemap URL -> pool entry, or None."""
    m = THEATRE_URL_RE.search(urlparse(url).path if "//" in url else url)
    if not m:
        return None
    state, city, slug = m.groups()
    if slug in ("index",) or state not in STATE_TZ:
        return None
    return {
        "slug": f"{state}-{city}/{slug}",
        "name": slug.replace("-", " ").title(),
        "state": state,
        "city": city.replace("-", " ").title(),
        "timezone": STATE_TZ[state],
        "chain": "CNMK",
    }


# Post-show census window: a show that STARTED up to this many minutes ago is
# read as a day-of finals candidate (seats sold at/after showtime). Whether
# Cinemark still renders the seat map post-start is probed empirically; the
# completeness floor drops any page that no longer renders.
# 18h default: the single 06:20Z post pass then covers the WHOLE prior show
# day (matinees included, starts from ~12:20Z), not just evening shows.
# Whether Cinemark still renders maps that long after start is measured by
# the pass's own incomplete counts (render decay shows up per-lead there).
CINEMARK_POST_SHOW_WINDOW_MIN = _env_int("CINEMARK_POST_SHOW_WINDOW_MIN", 1080)


def select_showtimes(entries, target_slugs, window_dates, tz_name, now_utc, cap,
                     mode="pre"):
    """entries: [{'href','movie_href'}] -> capped in-window picks.

    mode='pre'  : still-upcoming shows (pre-reservation snapshots).
    mode='post' : shows that already STARTED (day-of finals census — seats
                  sold at/after showtime), newest first so near-final state
                  is preferred.
    Pre mode sorts prime-time first (distance from 7pm), mirroring Fandango."""
    from fandango_collect import showtime_timing
    wanted = []
    for e in entries:
        title = match_movie_slug(e.get("movie_href", ""), target_slugs)
        if not title:
            continue
        parsed = parse_seatmap_href(e.get("href", ""))
        if not parsed:
            continue
        parsed["href"] = e.get("href", "")
        m_after, m_until, show_date, dow = showtime_timing(
            parsed["sdate"], tz_name, now_utc)
        if m_after is None or show_date not in window_dates:
            continue
        if mode == "post":
            if not (0 <= m_after <= CINEMARK_POST_SHOW_WINDOW_MIN):
                continue
        elif not should_record_pre_reservation_snapshot(m_after):
            continue
        hour = int(parsed["sdate"][11:13])
        wanted.append({**parsed, "title": title, "minutes_until": m_until,
                       "post_show": mode == "post",
                       "show_date": show_date, "day_of_week": dow,
                       "_prime": abs(hour - 19)})
    if mode == "post":
        wanted.sort(key=lambda w: -w["minutes_until"])  # most recently started first
    else:
        wanted.sort(key=lambda w: (w["_prime"], w["show_date"]))
    counts = {}
    for w in wanted:
        key = (w["title"], w["show_date"])
        counts[key] = counts.get(key, 0) + 1
    for w in wanted:
        w["discovered"] = counts[(w["title"], w["show_date"])]
    return wanted[:cap] if cap and cap > 0 else wanted


def build_row(theatre, pick, seats, weekend_of, run_id, check_time):
    total = int(seats.get("total") or 0)
    available = int(seats.get("available") or 0)
    reserved = max(0, total - available)
    occupancy = round(reserved / total * 100, 1) if total else ""
    return {field: "" for field in CINEMARK_FIELDS} | {
        "weekend_of": weekend_of,
        "run_id": run_id,
        "snapshot_time": check_time,
        "snapshot_bucket": snapshot_bucket(check_time),
        "show_date": pick["show_date"],
        "day_of_week": pick["day_of_week"],
        "theatre_name": theatre["name"],
        "theatre_city": theatre.get("city", ""),
        "timezone": theatre.get("timezone", ""),
        "movie_title": pick["title"],
        "showtime": pick["sdate"][11:],
        "showtime_id": pick["sdate"],   # datetime identity, Fandango convention
        "minutes_until_showtime": pick["minutes_until"],
        "auditorium_type": "Standard",
        "total_seats": total,
        "reserved_seats": reserved,
        "available_seats": available,
        "occupancy_pct": occupancy,
        "amc_seat_map_url": (
            pick["href"] if str(pick.get("href", "")).startswith("http")
            else f"{BASE}/TicketSeatMap/?TheaterId={pick['theater_id']}"
                 f"&ShowtimeId={pick['showtime_id']}"),
        "notes": f"cinemark-direct{'; post-show-census' if pick.get('post_show') else ''}; "
                 f"discovered_showtimes={pick['discovered']}; "
                 f"unavailable={seats.get('unavailable', '')}",
        "chain": "CNMK",
    }


# ── Seat-map DOM reading (validated selectors from probe 33423747388) ────────

SEAT_COUNT_JS = r"""() => {
  const cls = el => String(el.className && el.className.baseVal !== undefined
                          ? el.className.baseVal : el.className || '').toLowerCase();
  // Vista EVG seat map (grid-class census, validation run 33426153254):
  // every physical seat is a 'seatblock' cell whose class carries a
  // CONCATENATED state prefix — seatavailable / seatunavailable /
  // leftloveseatavailable / dboxavailable / wheelchairavailable / ... —
  // while 'seatblank seatblock' cells are aisle gaps, not seats. NOTE:
  // 'unavailable' contains 'available' as a substring, so test unavailable
  // FIRST when classifying.
  let seats = [...document.querySelectorAll("[class*='seatblock' i]")]
      .filter(el => !cls(el).includes('seatblank'));
  // Fallback: button-rendered layout (seen on the original probe theatre).
  if (seats.length === 0) {
    const legendish = el => !!el.closest("[class*='legend' i], [class*='zoom' i]");
    seats = [...document.querySelectorAll("button[class*='seat' i]")]
        .filter(b => !legendish(b));
  }
  const unavailable = seats.filter(el => {
    const c = cls(el);
    return c.includes('unavailable') || c.includes('occupied')
        || c.includes('sold') || c.includes('taken') || c.includes('selected');
  });
  const available = seats.filter(el => cls(el).includes('available')
                                       && !cls(el).includes('unavailable'));
  // Debug census whenever the count is implausibly low.
  let census = null;
  if (seats.length < 20) {
    const grid = document.querySelector(
      ".evgseatcontainer, [class*='seatmap' i], [class*='seat-map' i]");
    const freq = {};
    if (grid) {
      for (const el of grid.querySelectorAll('*')) {
        const c = cls(el).trim();
        if (c) freq[c] = (freq[c] || 0) + 1;
      }
    }
    census = { gridClassFreq: Object.entries(freq).sort((a, b) => b[1] - a[1])
                 .slice(0, 12).map(([c, n]) => c.slice(0, 50) + ':' + n) };
  }
  return { total: seats.length, available: available.length,
           unavailable: unavailable.length, census,
           title: (document.querySelector('.seats-tickets-title') || {}).textContent || '' };
}"""

BLOCK_MARKERS = ("sorry, you have been blocked", "access denied", "cf-chl")


def looks_blocked_text(text):
    low = (text or "").lower()
    return any(m in low for m in BLOCK_MARKERS)


# ── Date navigation ──────────────────────────────────────────────────────────
# The site ignores ?showDate/?date URL params; upcoming days are reached by
# clicking the showtimes page's date control. The click is SELF-VERIFYING:
# harvested TicketSeatMap hrefs carry Showtime=YYYY-MM-DD..., so a click that
# landed on the wrong day yields zero picks for the wanted date (loud in
# stats), never wrong-date data.

DATE_NAV_JS = r"""(dateStr) => {
  const iso = dateStr;                       // YYYY-MM-DD
  const d = new Date(iso + 'T12:00:00');
  const dayNum = String(d.getDate());
  const sels = [
    // Cinemark's showtimes carousel (census, run 33427874238):
    // <a class="showdate-link" data-datevalue="YYYY-MM-DD">. 15 days deep.
    `a.showdate-link[data-datevalue='${iso}']`, `[data-datevalue='${iso}']`,
    `[data-date='${iso}']`, `[data-show-date='${iso}']`, `[data-day='${iso}']`,
    `a[href*='${iso}']`, `[data-date='${iso}T00:00:00']`,
  ];
  for (const s of sels) {
    const el = document.querySelector(s);
    if (el) { el.click(); return 'sel:' + s; }
  }
  // Date-carousel fallback: a control whose text is the bare day number,
  // inside something date/day/calendar-ish.
  const zones = document.querySelectorAll(
    "[class*='date' i], [class*='day' i], [class*='calendar' i]");
  for (const z of zones) {
    for (const el of z.querySelectorAll('a, button, li, span')) {
      if ((el.textContent || '').trim() === dayNum) { el.click(); return 'daynum'; }
    }
  }
  return null;
}"""

DATE_CENSUS_JS = r"""() =>
  [...document.querySelectorAll(
     "[data-date], [data-show-date], [class*='date' i] a, [class*='date' i] button, " +
     "[class*='day' i] a, [class*='day' i] button")]
    .slice(0, 15)
    .map(el => ({ tag: el.tagName.toLowerCase(),
                  cls: String(el.className || '').slice(0, 50),
                  attrs: [...el.attributes].filter(a => a.name.startsWith('data-'))
                           .map(a => a.name + '=' + String(a.value).slice(0, 24)).slice(0, 4),
                  text: (el.textContent || '').trim().slice(0, 20) }))"""


def harvest_entries(page):
    return page.evaluate(r"""() =>
      [...document.querySelectorAll("a[href*='TicketSeatMap']")].map(a => {
        let n = a, movie = '';
        for (let d = 0; d < 12 && n; d++, n = n.parentElement) {
          const mo = n.querySelector && n.querySelector("a[href*='/movies/']");
          if (mo) { movie = mo.getAttribute('href') || ''; break; }
        }
        return { href: a.getAttribute('href'), movie_href: movie };
      })""") or []


def entry_dates(entries):
    dates = set()
    for e in entries:
        parsed = parse_seatmap_href(e.get("href", ""))
        if parsed:
            dates.add(parsed["sdate"][:10])
    return dates


# ── Discovery ────────────────────────────────────────────────────────────────

def discover(page):
    """Crawl sitemap(s) in the browser context for theatre URLs."""
    found = {}
    candidates = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap-theatres.xml"]
    fetched = set()
    while candidates:
        path = candidates.pop(0)
        if path in fetched or len(fetched) > 12:
            continue
        fetched.add(path)
        try:
            body = page.evaluate(
                "async (p) => { const r = await fetch(p); "
                "return r.ok ? await r.text() : ''; }", path)
        except Exception:
            body = ""
        if not body:
            continue
        for loc in re.findall(r"<loc>([^<]+)</loc>", body):
            if loc.endswith(".xml"):
                sub = urlparse(loc).path
                if sub not in fetched:
                    candidates.append(sub)
            else:
                th = theatre_from_url(loc)
                if th:
                    found[th["slug"]] = th
        print(f"  sitemap {path}: cumulative theatres={len(found)}", flush=True)
    return sorted(found.values(), key=lambda t: t["slug"])


# ── Collection ───────────────────────────────────────────────────────────────

def collect(weekend_of=None, titles=None, headless=True, show_dates=None,
            mode="pre"):
    from playwright.sync_api import sync_playwright

    if not weekend_of:
        if mode == "post":
            # Census reads belong to the weekend whose shows JUST PLAYED.
            # phase1_weekend_anchor points Mon-Wed at the UPCOMING weekend,
            # which would silently drop every stored Sunday-evening row at
            # the Monday 06:20Z post pass (audit catch 2026-08-31).
            from scraper import opening_weekend_friday
            weekend_of = opening_weekend_friday(datetime.now())
        else:
            weekend_of = phase1_weekend_anchor(datetime.now(), full_weekend=True)
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    if not titles:
        try:
            from scraper import (fetch_polymarket_box_office,
                                 select_collection_markets, local_now)
            live = select_collection_markets(
                fetch_polymarket_box_office(), local_now("ET"),
                "Cinemark title fallback", weekend_override=weekend_of)
            titles = [m["movie_title"] for m in (live or [])]
        except Exception as e:
            print(f"⚠️  live title fallback failed: {e}")
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return {}
    target_slugs = {slugify_title(t): t for t in titles}

    if not THEATRES_JSON.exists():
        print("⚠️  data/theatres-cinemark.json missing — run --discover first.")
        return {}
    pool = json.load(open(THEATRES_JSON)).get("theatres", [])
    if CINEMARK_NUM_SHARDS > 1:
        pool = pool[CINEMARK_SHARD % CINEMARK_NUM_SHARDS::CINEMARK_NUM_SHARDS]
    random.shuffle(pool)
    if CINEMARK_MAX_THEATRES > 0:
        pool = pool[:CINEMARK_MAX_THEATRES]

    now_utc = datetime.now(timezone.utc)
    check_time = now_utc.isoformat()
    run_id = f"cinemark-{snapshot_bucket(check_time)}"
    # Ad-hoc test override (fandango --dates convention): capture arbitrary
    # dates, e.g. validating live seat capture on a Monday when the tracked
    # window (Thu-Sun of the UPCOMING weekend) is legitimately empty.
    window_dates = (set(show_dates) if show_dates
                    else set(opening_weekend_show_dates(weekend_of)))
    deadline = time.monotonic() + CINEMARK_DEADLINE_SEC
    totals = {"visited": 0, "matched": 0, "captured": 0, "written": 0,
              "skipped": 0, "blocks": 0, "incomplete": 0,
              "date_nav_ok": 0, "date_nav_empty": 0, "date_nav_failed": 0}
    rows = []

    print(f"Cinemark collect [{mode}] • weekend_of={weekend_of} • {len(pool)} theatres "
          f"• cap={CINEMARK_PER_THEATRE_CAP}/theatre • deadline={CINEMARK_DEADLINE_SEC}s "
          f"• titles={list(target_slugs.values())}", flush=True)

    # Post-show census, stage 1: revisit seat-map URLs stored by earlier PRE
    # runs for shows that have since started (mirrors AMC: Phase 1 collects
    # links, the post-show pass revisits them). The showtimes page drops
    # started shows from its listing, so stored URLs are the reliable source;
    # page harvest below stays as a best-effort supplement.
    revisit = []
    if mode == "post":
        src_path = Path(os.environ.get("CINEMARK_POST_SOURCE") or CINEMARK_CSV)
        if src_path.exists():
            seen_urls = set()
            with open(src_path, newline="") as f:
                for r in csv.DictReader(f):
                    url = (r.get("amc_seat_map_url") or "").strip()
                    sdate = (r.get("showtime_id") or "").strip()
                    tz = (r.get("timezone") or "America/Chicago").strip()
                    title = (r.get("movie_title") or "").strip()
                    if not url or not sdate or url in seen_urls:
                        continue
                    if title not in target_slugs.values():
                        continue
                    from fandango_collect import showtime_timing
                    m_after, m_until, show_date, dow = showtime_timing(
                        sdate, tz, now_utc)
                    if m_after is None or not (0 <= m_after <= CINEMARK_POST_SHOW_WINDOW_MIN):
                        continue
                    seen_urls.add(url)
                    revisit.append({
                        "theatre": {"name": r.get("theatre_name", ""),
                                    "city": r.get("theatre_city", ""),
                                    "timezone": tz},
                        "pick": {"title": title, "sdate": sdate,
                                 "show_date": show_date, "day_of_week": dow,
                                 "minutes_until": m_until, "post_show": True,
                                 "discovered": 1,
                                 "theater_id": "", "showtime_id": "",
                                 "href": url},
                    })
        print(f"  post-show revisit candidates from stored rows: {len(revisit)}",
              flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        for item in revisit:
            if time.monotonic() > deadline:
                break
            try:
                page.goto(item["pick"]["href"], wait_until="domcontentloaded",
                          timeout=30000)
                try:
                    page.wait_for_selector(
                        "[class*='seatblock' i], button[class*='seat' i]",
                        timeout=10000)
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                seats = page.evaluate(SEAT_COUNT_JS)
            except Exception as e:
                print(f"    revisit ERROR {str(e)[:60]}", flush=True)
                continue
            if not seats or int(seats.get("total") or 0) < CINEMARK_MIN_SEATS:
                totals["incomplete"] += 1
                print(f"    revisit incomplete (map gone post-start?): "
                      f"total={(seats or {}).get('total')} "
                      f"{item['pick']['sdate']}", flush=True)
                continue
            totals["captured"] += 1
            rows.append(build_row(item["theatre"], item["pick"], seats,
                                  weekend_of, run_id, check_time))
            time.sleep(random.uniform(*CINEMARK_POLITE_SEC))
        for th in pool:
            if time.monotonic() > deadline:
                print("⏱  deadline reached; stopping cleanly", flush=True)
                break
            totals["visited"] += 1
            try:
                page.goto(f"{BASE}/theatres/{th['slug']}",
                          wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
                if looks_blocked_text(page.inner_text("body")[:2000]):
                    totals["blocks"] += 1
                    print(f"  {th['slug']}: BLOCKED", flush=True)
                    continue
                entries = harvest_entries(page)
                # Remaining-weekend coverage (the AMC snapshot semantic): the
                # dateless page serves only the CURRENT local day, so reach
                # every other wanted date through the date picker.
                covered = entry_dates(entries)
                try:
                    from zoneinfo import ZoneInfo
                    today_local = datetime.now(
                        ZoneInfo(th.get("timezone", "America/Chicago"))
                    ).strftime("%Y-%m-%d")
                except Exception:
                    today_local = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                missing = ([] if mode == "post"
                           else sorted(d for d in window_dates
                                       if d not in covered and d > today_local))
                for want in missing[:4]:
                    if time.monotonic() > deadline:
                        break
                    try:
                        how = page.evaluate(DATE_NAV_JS, want)
                    except Exception:
                        how = None
                    if not how:
                        totals["date_nav_failed"] += 1
                        if not totals.get("_date_census_dumped"):
                            totals["_date_census_dumped"] = True
                            try:
                                census = page.evaluate(DATE_CENSUS_JS)
                            except Exception:
                                census = None
                            print(f"    date-nav: no control for {want}; "
                                  f"census={census}", flush=True)
                        continue
                    page.wait_for_timeout(3000)
                    extra = harvest_entries(page)
                    extra = [e for e in extra
                             if (parse_seatmap_href(e.get("href", "")) or {})
                             .get("sdate", "")[:10] == want]
                    if extra:
                        totals["date_nav_ok"] += 1
                        entries.extend(extra)
                    else:
                        totals["date_nav_empty"] += 1
            except Exception as e:
                print(f"  {th['slug']}: page ERROR {str(e)[:80]}", flush=True)
                continue
            picks = select_showtimes(entries or [], target_slugs, window_dates,
                                     th.get("timezone", "America/Chicago"),
                                     now_utc, CINEMARK_PER_THEATRE_CAP, mode=mode)
            totals["matched"] += len(picks)
            if mode == "post" and not picks:
                times = sorted((parse_seatmap_href(e.get("href", "")) or {})
                               .get("sdate", "")[11:] for e in (entries or []))[:8]
                print(f"  {th['slug']}: post-harvest empty — {len(entries or [])} "
                      f"listed showtimes, earliest {times[:4]} (page likely "
                      f"drops started shows)", flush=True)
            for pick in picks:
                if time.monotonic() > deadline:
                    break
                try:
                    # Navigate the ORIGINAL href — reconstructing it with
                    # CinemarkMovieId=0 broke the seat render (validation run
                    # 33424701048: 10/10 incomplete).
                    href = pick["href"]
                    page.goto(href if href.startswith("http") else BASE + href,
                              wait_until="domcontentloaded", timeout=30000)
                    try:
                        page.wait_for_selector(
                            "[class*='seatblock' i], button[class*='seat' i]",
                            timeout=12000)
                    except Exception:
                        pass
                    page.wait_for_timeout(1500)
                    seats = page.evaluate(SEAT_COUNT_JS)
                    if int((seats or {}).get("total") or 0) < CINEMARK_MIN_SEATS:
                        # "Performing security verification" interstitial: a
                        # transient JS challenge that auto-clears for real
                        # browsers (load-sensitive — ~55% of pages under the
                        # sustained scale run, 2/28 on a small run). Wait it
                        # out and retry once.
                        try:
                            body = (page.inner_text("body") or "")[:400].lower()
                        except Exception:
                            body = ""
                        if "security verification" in body or "verifies" in body:
                            totals["challenges"] = totals.get("challenges", 0) + 1
                            try:
                                page.wait_for_selector(
                                    "[class*='seatblock' i], button[class*='seat' i]",
                                    timeout=15000)
                            except Exception:
                                page.reload(wait_until="domcontentloaded",
                                            timeout=30000)
                                try:
                                    page.wait_for_selector(
                                        "[class*='seatblock' i], "
                                        "button[class*='seat' i]", timeout=12000)
                                except Exception:
                                    pass
                            page.wait_for_timeout(1200)
                            seats = page.evaluate(SEAT_COUNT_JS)
                    if int((seats or {}).get("total") or 0) < CINEMARK_MIN_SEATS:
                        # Seat grid may live in an embedded frame — evaluate()
                        # does not pierce iframes.
                        for fr in page.frames[1:]:
                            try:
                                alt = fr.evaluate(SEAT_COUNT_JS)
                            except Exception:
                                continue
                            if int((alt or {}).get("total") or 0) > \
                                    int((seats or {}).get("total") or 0):
                                alt["title"] = alt.get("title") or (seats or {}).get("title", "")
                                alt["from_frame"] = fr.url[:90]
                                seats = alt
                except Exception as e:
                    print(f"    seatmap ERROR {str(e)[:60]}", flush=True)
                    continue
                if not seats or int(seats.get("total") or 0) < CINEMARK_MIN_SEATS:
                    totals["incomplete"] += 1
                    snippet = ""
                    if not ((seats or {}).get("title") or "").strip():
                        try:
                            snippet = (page.inner_text("body") or "")[:180]
                            snippet = " ".join(snippet.split())[:160]
                        except Exception:
                            pass
                    print(f"    incomplete: total={seats.get('total') if seats else None} "
                          f"title={((seats or {}).get('title') or '')[:40]!r} "
                          f"census={(seats or {}).get('census')} "
                          f"url={page.url[:110]} body={snippet!r}", flush=True)
                    continue
                page_title = (seats.get("title") or "").strip()
                if page_title and slugify_title(page_title) != slugify_title(pick["title"]):
                    # seat page names a different film than the section walk —
                    # trust the seat page (it is authoritative for the showtime)
                    canon = match_movie_slug("/movies/" + slugify_title(page_title),
                                             target_slugs)
                    if not canon:
                        totals["skipped"] += 1
                        continue
                    pick = {**pick, "title": canon}
                totals["captured"] += 1
                rows.append(build_row(th, pick, seats, weekend_of, run_id, check_time))
                time.sleep(random.uniform(*CINEMARK_POLITE_SEC))
        browser.close()

    written, deduped = append_rows(rows)
    totals["written"] = written
    totals["skipped"] += deduped
    print(f"\n=== Cinemark collect summary ===\n"
          f"  visited={totals['visited']} matched={totals['matched']} "
          f"captured={totals['captured']} written={written} deduped={deduped} "
          f"incomplete={totals['incomplete']} blocks={totals['blocks']} "
          f"challenges={totals.get('challenges', 0)} "
          f"date_nav ok/empty/failed={totals['date_nav_ok']}/"
          f"{totals['date_nav_empty']}/{totals['date_nav_failed']}\n"
          f"  -> {CINEMARK_CSV}", flush=True)
    return totals


def append_rows(rows):
    if not rows:
        return 0, 0
    out_path = Path(os.environ.get("CINEMARK_OUTPUT") or CINEMARK_CSV)
    seen = set()
    if out_path.exists():
        with open(out_path, newline="") as f:
            for r in csv.DictReader(f):
                seen.add(tuple(str(r.get(k, "") or "") for k in CINEMARK_DEDUPE_FIELDS))
    pending = []
    for row in rows:
        key = tuple(str(row.get(k, "") or "") for k in CINEMARK_DEDUPE_FIELDS)
        if key in seen:
            continue
        seen.add(key)
        pending.append(row)
    is_new = not out_path.exists() or out_path.stat().st_size == 0
    with open(out_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CINEMARK_FIELDS)
        if is_new:
            w.writeheader()
        w.writerows(pending)
    return len(pending), len(rows) - len(pending)


# ── Selftest ─────────────────────────────────────────────────────────────────

def _selftest():
    p = parse_seatmap_href("/TicketSeatMap/?TheaterId=207&ShowtimeId=645731"
                           "&CinemarkMovieId=107537&Showtime=2026-08-31T22:50:00")
    assert p == {"theater_id": "207", "showtime_id": "645731",
                 "sdate": "2026-08-31 22:50"}, p
    assert parse_seatmap_href("/movies/foo") is None
    assert parse_seatmap_href("/TicketSeatMap/?TheaterId=207") is None

    targets = {slugify_title(t): t for t in ["Toy Story 5", "Coyote vs. Acme"]}
    assert match_movie_slug("/movies/toy-story-5", targets) == "Toy Story 5"
    assert match_movie_slug("/movies/coyote-vs-acme", targets) == "Coyote vs. Acme"
    assert match_movie_slug("/movies/some-other-film", targets) is None

    th = theatre_from_url("https://www.cinemark.com/theatres/tx-dallas/cinemark-17-and-imax")
    assert th and th["slug"] == "tx-dallas/cinemark-17-and-imax" and \
        th["timezone"] == "America/Chicago", th
    assert theatre_from_url("https://www.cinemark.com/theatres") is None

    now = datetime(2026, 8, 31, 20, 0, tzinfo=timezone.utc)
    entries = [
        {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=2&Showtime=2026-08-31T19:30:00",
         "movie_href": "/movies/toy-story-5"},          # 19:30 CT = future
        {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=3&Showtime=2026-08-31T10:00:00",
         "movie_href": "/movies/toy-story-5"},          # past -> dropped
        {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=4&Showtime=2026-08-31T21:00:00",
         "movie_href": "/movies/unrelated-film"},       # untracked -> dropped
    ]
    picks = select_showtimes(entries, targets, {"2026-08-31"},
                             "America/Chicago", now, cap=5)
    assert len(picks) == 1 and picks[0]["showtime_id"] == "2", picks

    row = build_row({"name": "Cinemark Test", "timezone": "America/Chicago"},
                    {**picks[0], "discovered": 1},
                    {"total": 124, "available": 100, "unavailable": 24},
                    "2026-08-28", "cinemark-x", now.isoformat())
    assert row["reserved_seats"] == 24 and row["total_seats"] == 124
    assert row["chain"] == "CNMK" and row["occupancy_pct"] == 19.4
    assert set(row) == set(CINEMARK_FIELDS), set(CINEMARK_FIELDS) ^ set(row)
    print("cinemark_collect selftest OK")


def main():
    ap = argparse.ArgumentParser(description="Cinemark direct pre-reservation collector")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--discover", action="store_true",
                    help="crawl the sitemap into data/theatres-cinemark.json")
    ap.add_argument("--weekend", help="weekend_of override (YYYY-MM-DD)")
    ap.add_argument("--titles", nargs="*",
                    help="override tracked titles (or env CINEMARK_TITLES, comma-sep)")
    ap.add_argument("--post-show", action="store_true",
                    help="day-of finals census: read shows that already started "
                         "(or env CINEMARK_MODE=post)")
    ap.add_argument("--dates", nargs="*",
                    help="ad-hoc test: capture these YYYY-MM-DD dates instead of "
                         "the weekend window (or env CINEMARK_SHOW_DATES)")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return 0
    if args.discover:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                args=["--disable-blink-features=AutomationControlled"])
            page = browser.new_context(user_agent=UA).new_page()
            page.goto(BASE + "/theatres", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            theatres = discover(page)
            browser.close()
        if not theatres:
            print("❌ discovery found no theatres — sitemap shape changed?")
            return 1
        with open(THEATRES_JSON, "w") as f:
            json.dump({"_updated": datetime.now(timezone.utc).isoformat(),
                       "theatres": theatres}, f, indent=1)
        print(f"✓ wrote {len(theatres)} theatres -> {THEATRES_JSON}")
        return 0
    titles = args.titles or [t.strip() for t in
                             (os.environ.get("CINEMARK_TITLES") or "").split(",")
                             if t.strip()]
    show_dates = args.dates or [d.strip() for d in
                                (os.environ.get("CINEMARK_SHOW_DATES") or "").split(",")
                                if d.strip()]
    mode = "post" if (args.post_show
                      or os.environ.get("CINEMARK_MODE") == "post") else "pre"
    totals = collect(weekend_of=args.weekend, titles=titles or None,
                     show_dates=show_dates or None, mode=mode)
    if totals and totals.get("written", 0) == 0 and totals.get("matched", 0) > 0:
        print("❌ Showtimes matched but zero rows written — failing loudly.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
