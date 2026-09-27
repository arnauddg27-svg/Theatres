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
from html import unescape
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
    migrate_header,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
CINEMARK_CSV = DATA_DIR / "cinemark-pre-reservation-snapshots.csv"
# Every tracked showtime link seen by a pre pass (2026-09-27). The post-show
# census used to revisit only the 1-2 showings per film a pre pass happened to
# LOAD; the page lists them all, so they are stored for free and the census
# picks from the full set.
CINEMARK_LINKS_CSV = DATA_DIR / "cinemark-showtime-links.csv"
LINK_FIELDS = ["weekend_of", "theatre_name", "theatre_city", "timezone", "movie_title",
               "sdate", "show_date", "href", "seen_at"]
THEATRES_JSON = DATA_DIR / "theatres-cinemark.json"
BASE = "https://www.cinemark.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

import proxy_egress  # noqa: E402  (residential-proxy egress + byte budget)

CINEMARK_FIELDS = FANDANGO_PRE_RESERVATION_FIELDS
CINEMARK_DEDUPE_FIELDS = FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except (TypeError, ValueError):
        return default


CINEMARK_DEADLINE_SEC = _env_int("CINEMARK_DEADLINE_SEC", 2100)
# Showtimes captured PER FILM per theatre: a 2-film weekend censuses both
# films at every theatre (up to 2 seat loads/theatre at cap 1) — the
# operator's census contract beats tarpit caution; the streak breaker pauses
# on a throttle and a red exit buys a fresh-IP retry. If runs tarpit anyway,
# the fallback lever is dropping to the BIGGER film only (by national
# theatre count), not starving one film silently.
CINEMARK_PER_THEATRE_CAP = _env_int("CINEMARK_PER_THEATRE_CAP", 1)
# Residential-proxy egress (2026-09-12). The "security verification"
# interstitial that forced cap=1 is per-ADDRESS, so a rotating pool lifts it —
# at the price of metered bytes, hence CINEMARK_MAX_MB (0 = unmetered/direct).
CINEMARK_MAX_MB = _env_int("CINEMARK_MAX_MB", 0)
CINEMARK_PROXY_PER_THEATRE_CAP = _env_int("CINEMARK_PROXY_PER_THEATRE_CAP", 0)
CINEMARK_MAX_THEATRES = _env_int("CINEMARK_MAX_THEATRES", 0)
CINEMARK_NUM_SHARDS = _env_int("CINEMARK_NUM_SHARDS", 0)
CINEMARK_SHARD = _env_int("CINEMARK_SHARD", 0)
CINEMARK_MIN_SEATS = 20      # completeness floor: a real auditorium has >= this
CINEMARK_POLITE_SEC = (1.0, 2.5)

# US state abbreviations -> IANA timezone. The tz drives MINUTE-level pre/post
# windows (showtime_timing), not just the local date, so split-zone states get
# city-level overrides below for pool theatres on the minority side.
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

# split-zone corrections, keyed on "state-city" (audit: El Paso is Mountain,
# Paducah is Central — the state majority zone is wrong for both).
CITY_TZ = {
    "tx-el-paso": "America/Denver",
    "ky-paducah": "America/Chicago",
    "in-valparaiso": "America/Chicago",   # Porter County IN is Central
    "tn-oak-ridge": "America/New_York",   # Knoxville area is Eastern
}

THEATRE_URL_RE = re.compile(r"/theatres/([a-z]{2})-([a-z0-9\-]+)/([a-z0-9\-]+)/?$")


# ── Pure logic (offline-testable) ────────────────────────────────────────────

def parse_seatmap_href(href):
    """'/TicketSeatMap/?TheaterId=207&ShowtimeId=645731&...&Showtime=2026-08-31T22:50:00'
    -> {'theater_id': '207', 'showtime_id': '645731', 'sdate': '2026-08-31 22:50'} or None."""
    if not href or "TicketSeatMap".lower() not in href.lower():
        return None
    # Keys are matched case-insensitively: the 2026-09-23 site redesign moved
    # from TheaterId/ShowtimeId/Showtime to theaterId/showtimeId/showtime (plus
    # cinemarkMovieId/linkedShowtimeId), and the exact-case lookup silently
    # matched ZERO showtimes on every pre pass for three days.
    q = {k.lower(): v for k, v in parse_qs(urlparse(href).query).items()}
    theater_id = (q.get("theaterid") or [None])[0]
    showtime_id = (q.get("showtimeid") or [None])[0]
    raw = (q.get("showtime") or [None])[0]
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
    # Near-miss visibility (the Fandango lane's lesson, paid for twice): a
    # variant slug that silently zeroes a tracked film must show up in logs.
    for slug, title in target_slugs.items():
        t = _slug_tokens(slug)
        if t and tokens and (t <= tokens or len(t & tokens) / len(t) >= 0.6):
            if core not in _NEAR_MISS_SEEN:
                _NEAR_MISS_SEEN.add(core)
                print(f"  slug near-miss: {core!r} vs tracked {slug!r} "
                      f"({title}) — matcher variant?", flush=True)
            break
    return None


_NEAR_MISS_SEEN = set()


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
        "timezone": CITY_TZ.get(f"{state}-{city}", STATE_TZ[state]),
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
# INVARIANT: censuses run ~24h apart but dispatch jitter is real (watchdog
# fires 30-75 min late), and the dedupe key includes snapshot_bucket
# (differs per day) — this window staying comfortably under a day is the
# ONLY thing preventing yesterday's census rows from being re-captured as
# today's. Ceiling 1350 = 1440 minus ~90 min of worst realistic skew
# (round-5 audit: a 1439 ceiling re-captured rows whenever day N ran ~70
# min late and day N+1 on time).
# Showings re-read per (theatre, film, show date) by the post-show census,
# spread across the day (first, last, evenly between). 3 -> 6 on 2026-09-27
# once proxy reads lifted the 70-maps-per-address cap (pre slices captured
# ~98% of picks at ~7 MB each) and seat maps proved readable 12.6+ h after
# showtime, so the nightly pass reaches the day's matinees.
# 6 -> 0 (= EVERY showing) on 2026-09-27: Sunday's link set had a median of
# 10 showings per theatre-film-day, so 6 left ~39% of showings (3,234 of
# 8,363) uncounted. Cost ~36 KB/proxy read; post runs as 12 slices so each
# stays ~700 reads (~55 min, ~23 MB) inside the 90-min deadline / 40 MB cap.
CINEMARK_POST_PER_FILM = _env_int("CINEMARK_POST_PER_FILM", 0)
_CINEMARK_WINDOW_RAW = _env_int("CINEMARK_POST_SHOW_WINDOW_MIN", 1080)
CINEMARK_POST_SHOW_WINDOW_MIN = min(_CINEMARK_WINDOW_RAW, 1350)
if _CINEMARK_WINDOW_RAW > 1350:
    print(f"CINEMARK_POST_SHOW_WINDOW_MIN={_CINEMARK_WINDOW_RAW} clamped to "
          f"1350 (duplicate-capture ceiling)", flush=True)


# ── HTTP seat reads (2026-09-27) ─────────────────────────────────────────────
# TicketSeatMap is server-rendered: one <button available="True|False"
# class="seat... seatBlock"> per seat. A plain GET reads the whole map in ~1 s.
# cinemark.com throttles per address (429 "Just a moment") after a ~15-read
# burst; at a 5 s pace a GitHub runner read 60/60 maps with zero throttles
# (run 36292945533), vs the browser lane's 2-3 good maps/min with 44-67% of
# pages coming back as the client-side "Something went wrong" error. The
# browser stays for the theatre listings (built client-side).
CINEMARK_SEAT_FETCH = (os.environ.get("CINEMARK_SEAT_FETCH") or "http").strip().lower()
CINEMARK_HTTP_PACE_SEC = float(os.environ.get("CINEMARK_HTTP_PACE_SEC", "5"))
# A browser load after a failed HTTP read doubles the traffic that triggered
# the failure; off by default in http mode (set 1 to restore).
CINEMARK_BROWSER_FALLBACK = os.environ.get("CINEMARK_BROWSER_FALLBACK", "0") == "1"
_SEAT_BTN_RE = re.compile(r'<button[^>]*?available="(True|False)"[^>]*?class="[^"]*seatBlock', re.I)
_TITLE_RE = re.compile(r'class="[^"]*seats-tickets-title[^"]*"[^>]*>\s*([^<]+?)\s*<', re.I)


def parse_seat_html(html):
    """Pure: TicketSeatMap HTML -> seats dict (same keys as SEAT_COUNT_JS)."""
    av = _SEAT_BTN_RE.findall(html or "")
    m = _TITLE_RE.search(html or "")
    return {"total": len(av), "available": av.count("True"), "unavailable": av.count("False"),
            "census": None, "title": unescape(m.group(1)) if m else ""}


# Cinemark serves exactly 70 seat maps per address, then answers every map
# with a 20-byte 404 (probe run 36313870231: 70 ok, then 40/40 404). So a
# runner spends its free 70 directly, and after a run of 404s switches to the
# residential proxy with a FRESH exit address per read (~46 KB/read incl.
# tunnel overhead), capped at CINEMARK_PROXY_MAX_MB per run. The proxy URL
# comes from CINEMARK_HTTP_PROXY_URL (the workflow maps the AMC proxy secret
# onto it) and is never printed. It is deliberately NOT AMC_SEAT_PROXY_URL:
# the browser lane reads that one, and browser pages through the proxy cost
# 6.3 MB/theatre (rejected 2026-09-12).
CINEMARK_PROXY_MAX_MB = float(os.environ.get("CINEMARK_PROXY_MAX_MB", "40"))
CINEMARK_PROXY_PACE_SEC = float(os.environ.get("CINEMARK_PROXY_PACE_SEC", "1"))
CINEMARK_CAP_404_STREAK = 3
PROXY_OVERHEAD_BYTES = 6 * 1024


class HttpSeatReader:
    """Paced plain-HTTP seat reader: direct until the per-address cap, then the
    residential proxy (fresh exit per read) within a byte budget."""

    def __init__(self, pace_sec=None, session=None, proxy_url=None, proxy_max_mb=None):
        self.pace = CINEMARK_HTTP_PACE_SEC if pace_sec is None else pace_sec
        self.session = session
        self.proxy_url = proxy_url if proxy_url is not None else (os.environ.get("CINEMARK_HTTP_PROXY_URL") or "")
        self.proxy_budget = (CINEMARK_PROXY_MAX_MB if proxy_max_mb is None else proxy_max_mb) * 1024 * 1024
        self.proxy_bytes = 0
        self.via_proxy = False
        self.streak_404 = 0
        self.proxy_session = None
        self.next_at = 0.0
        self.stats = {"http_ok": 0, "http_empty": 0, "http_throttled": 0, "http_error": 0,
                      "http_gone": 0, "proxy_ok": 0, "proxy_mb": 0.0}

    def _sess(self):
        if self.session is None:
            from curl_cffi import requests as cr
            self.session = cr.Session(impersonate="chrome")
        return self.session

    def _proxy_get(self, url):
        """One read through the proxy on a fresh tunnel (= fresh exit address)."""
        import seat_fetch_http
        if self.proxy_session is None:
            # NOT seat_fetch_http.make_session(): that one disables content
            # decoding (the AMC lane meters raw wire bytes and inflates by
            # hand), so every proxied map came back as 37 KB of undecoded gzip
            # with "no seats" (verify run 36314604906: proxy ok 0/185). Keep
            # its TLS curve pin (Azure->proxy tunnels hang on Chrome's
            # post-quantum key share) and let curl decode.
            from curl_cffi import requests as cr
            from curl_cffi.const import CurlOpt
            self.proxy_session = cr.Session(impersonate="chrome",
                                            curl_options={CurlOpt.SSL_EC_CURVES: seat_fetch_http.TLS_CURVES})
        try:
            r = self.proxy_session.get(url, timeout=30, proxies={"http": self.proxy_url, "https": self.proxy_url})
        finally:
            seat_fetch_http.drop_thread_connection(self.proxy_session)
        # decoded length overstates the wire bytes ~9x; bill the compressed
        # size when the server says it, else a conservative 1/8 of decoded
        wire = int(r.headers.get("content-length") or 0) or len(r.content or b"") // 8
        self.proxy_bytes += wire + PROXY_OVERHEAD_BYTES
        self.stats["proxy_mb"] = round(self.proxy_bytes / 1048576, 1)
        return r

    def proxy_available(self):
        return bool(self.proxy_url) and self.proxy_bytes < self.proxy_budget

    def read(self, href):
        url = href if href.startswith("http") else BASE + href
        for attempt in range(2):
            use_proxy = self.via_proxy and self.proxy_available()
            if self.via_proxy and not use_proxy:
                return None          # direct cap reached and the proxy budget is spent
            wait = self.next_at - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.next_at = time.monotonic() + (CINEMARK_PROXY_PACE_SEC if use_proxy else self.pace)
            try:
                r = self._proxy_get(url) if use_proxy else self._sess().get(url, timeout=30)
            except Exception:
                self.stats["http_error"] += 1
                return None
            if r.status_code == 404:
                # Direct: a run of 404s means this address hit Cinemark's
                # 70-map cap -> switch to the proxy and re-read this map there.
                # Through the proxy (fresh address) a 404 means the map is gone.
                self.stats["http_gone"] += 1
                if not use_proxy:
                    self.streak_404 += 1
                    if self.streak_404 >= CINEMARK_CAP_404_STREAK and self.proxy_available():
                        self.via_proxy = True
                        print(f"    direct address hit Cinemark's per-address cap after "
                              f"{self.stats['http_ok']} maps — switching to the residential proxy "
                              f"(budget {self.proxy_budget / 1048576:.0f} MB)", flush=True)
                        continue
                return None
            if r.status_code == 429 or "Just a moment" in r.text[:3000]:
                self.stats["http_throttled"] += 1
                self.next_at = time.monotonic() + 30 + self.pace      # let the bucket refill
                continue
            seats = parse_seat_html(r.text)
            if seats["total"]:
                self.stats["proxy_ok" if use_proxy else "http_ok"] += 1
                if not use_proxy:
                    self.streak_404 = 0
                return seats
            # Empty page: in production (run 36293422503) 171 of 249 reads came
            # back empty while stored links read 25/25 from a quiet address —
            # consistent with a soft throttle from the run's own browser
            # traffic. Back off and retry over HTTP instead of piling a browser
            # load on top. First few samples are logged for diagnosis.
            self.stats["http_empty"] += 1
            if use_proxy:
                return None          # fresh address per read — waiting does not help
            if self.stats["http_empty"] <= 3:
                import re as _re
                t = _re.search(r"<title>([^<]*)", r.text or "")
                print(f"    http empty sample: status={r.status_code} bytes={len(r.content)} "
                      f"title={(t.group(1).strip()[:50] if t else '')!r} "
                      f"wrong={'Something went wrong' in (r.text or '')}", flush=True)
            self.next_at = time.monotonic() + 20 + self.pace
        return None


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
                       "minutes_after": m_after,
                       "post_show": mode == "post",
                       "show_date": show_date, "day_of_week": dow,
                       "_prime": abs(hour - 19)})
    if mode == "post":
        # Most recently started first: minutes_until is 0 for every started
        # show, so it cannot order a post pass — minutes_after can.
        wanted.sort(key=lambda w: w["minutes_after"])
    else:
        wanted.sort(key=lambda w: (w["_prime"], w["show_date"]))
    counts = {}
    for w in wanted:
        key = (w["title"], w["show_date"])
        counts[key] = counts.get(key, 0) + 1
    for w in wanted:
        w["discovered"] = counts[(w["title"], w["show_date"])]
    if cap and cap > 0:
        # PER FILM: every tracked film gets censused at every theatre — a
        # global cap starved the non-prime film pool-wide (2026-09-03: BAM
        # 277 picks vs Onslaught 1). Two films = up to 2 seat loads/theatre;
        # the tarpit breaker + red-retry policy bound the extra load.
        taken = {}
        picks = []
        for w in wanted:
            if taken.get(w["title"], 0) < cap:
                taken[w["title"]] = taken.get(w["title"], 0) + 1
                picks.append(w)
        return picks
    return wanted


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
        # Store the ORIGINAL href absolutized, never a reconstruction: the
        # post-show census revisits this exact URL, and rebuilding it without
        # Showtime/CinemarkMovieId breaks the seat render (validation run
        # 33424701048: 10/10 incomplete).
        "amc_seat_map_url": (
            pick["href"] if str(pick.get("href", "")).startswith("http")
            else BASE + pick["href"] if pick.get("href")
            else f"{BASE}/TicketSeatMap/?TheaterId={pick['theater_id']}"
                 f"&ShowtimeId={pick['showtime_id']}"),
        "notes": f"cinemark-direct{'; post-show-census' if pick.get('post_show') else ''}; "
                 f"discovered_showtimes={pick['discovered']}; "
                 f"unavailable={seats.get('unavailable', '')}",
        "chain": "CNMK",
        "discovered_showtimes": str(pick["discovered"]),
        "unavailable_seats": str(seats.get("unavailable", "")),
        "row_kind": "post-show-census" if pick.get("post_show") else "cinemark-direct",
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

def spread_pick(items, k):
    """Pure: up to k items spread evenly across a time-sorted list."""
    items = list(items)
    if k <= 0 or len(items) <= k:
        return items
    if k == 1:
        return [items[len(items) // 2]]
    idx = sorted({round(i * (len(items) - 1) / (k - 1)) for i in range(k)})
    return [items[i] for i in idx]


def link_rows(theatre, entries, target_slugs, window_dates, weekend_of, now_utc):
    """Pure: every tracked, upcoming showing on a theatre page -> link rows."""
    picks = select_showtimes(entries or [], target_slugs, window_dates,
                             theatre.get("timezone", "America/Chicago"), now_utc, 0, mode="pre")
    return [{"weekend_of": weekend_of, "theatre_name": theatre.get("name", ""),
             "theatre_city": theatre.get("city", ""), "timezone": theatre.get("timezone", ""),
             "movie_title": pk["title"], "sdate": pk["sdate"], "show_date": pk["show_date"],
             "href": pk["href"] if str(pk["href"]).startswith("http") else BASE + pk["href"],
             "seen_at": now_utc.isoformat()} for pk in picks if pk.get("href")]


def append_links(rows, path=None):
    """Append link rows not already stored (dedupe on href). Returns count."""
    if not rows:
        return 0
    path = Path(path or CINEMARK_LINKS_CSV)
    have = set()
    if path.exists():
        with open(path, newline="") as f:
            have = {r.get("href", "") for r in csv.DictReader(f)}
    new = [r for r in rows if r["href"] not in have]
    seen, out = set(), []
    for r in new:
        if r["href"] in seen:
            continue
        seen.add(r["href"]); out.append(r)
    if not out:
        return 0
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LINK_FIELDS, extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerows(out)
    return len(out)


def post_candidates(sources, weekend_of, titles, now_utc, pool_names=None,
                    per_film=None, window_min=None):
    """Pure-ish: stored rows/links -> revisit list for the post-show census.

    sources: iterable of dicts with theatre_name/theatre_city/timezone/
    movie_title and either (sdate, href) [links] or (showtime_id,
    amc_seat_map_url) [stored rows]. Keeps shows that started 0..window
    minutes ago, at most per_film per (theatre, film, show date), spread
    across the day; restricted to pool_names when sharded."""
    from fandango_collect import showtime_timing
    per_film = CINEMARK_POST_PER_FILM if per_film is None else per_film
    window_min = CINEMARK_POST_SHOW_WINDOW_MIN if window_min is None else window_min
    groups, seen = {}, set()
    for r in sources:
        if (r.get("weekend_of") or "").strip() != weekend_of:
            continue
        if r.get("row_kind") == "post-show-census" or "post-show-census" in (r.get("notes") or ""):
            continue
        url = (r.get("href") or r.get("amc_seat_map_url") or "").strip()
        if "TheaterId=" in url:
            continue    # pre-2026-09-23 URL format: 404 since the redesign
        sdate = (r.get("sdate") or r.get("showtime_id") or "").strip()
        title = (r.get("movie_title") or "").strip()
        name = r.get("theatre_name", "")
        if not url or not sdate or url in seen or title not in titles:
            continue
        if pool_names is not None and name not in pool_names:
            continue
        tz = (r.get("timezone") or "America/Chicago").strip()
        m_after, m_until, show_date, dow = showtime_timing(sdate, tz, now_utc)
        if m_after is None or not (0 <= m_after <= window_min):
            continue
        seen.add(url)
        groups.setdefault((name, title, show_date), []).append({
            "theatre": {"name": name, "city": r.get("theatre_city", ""), "timezone": tz},
            "pick": {"title": title, "sdate": sdate, "show_date": show_date, "day_of_week": dow,
                     "minutes_until": m_until, "post_show": True, "discovered": 1,
                     "theater_id": "", "showtime_id": "", "href": url}})
    out = []
    for key in sorted(groups):
        out += spread_pick(sorted(groups[key], key=lambda x: x["pick"]["sdate"]), per_film)
    return out


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
    budget = proxy_egress.ByteBudget(CINEMARK_MAX_MB, label="cinemark lane")
    per_theatre_cap = CINEMARK_PER_THEATRE_CAP
    if proxy_egress.proxy_settings() and CINEMARK_PROXY_PER_THEATRE_CAP:
        # the interstitial that forced cap=1 is per-address; a rotating pool
        # spreads the load, so depth is affordable again
        per_theatre_cap = CINEMARK_PROXY_PER_THEATRE_CAP
    print(proxy_egress.egress_banner("cinemark lane", budget), flush=True)
    totals = {"visited": 0, "matched": 0, "captured": 0, "written": 0,
              "skipped": 0, "blocks": 0, "incomplete": 0,
              "date_nav_ok": 0, "date_nav_empty": 0, "date_nav_failed": 0,
              "links_stored": 0}
    rows = []

    print(f"Cinemark collect [{mode}] • weekend_of={weekend_of} • {len(pool)} theatres "
          f"• cap={per_theatre_cap}/theatre • deadline={CINEMARK_DEADLINE_SEC}s "
          f"• titles={list(target_slugs.values())}", flush=True)

    # Post-show census, stage 1: revisit seat-map URLs stored by earlier PRE
    # runs for shows that have since started (mirrors AMC: Phase 1 collects
    # links, the post-show pass revisits them). The showtimes page drops
    # started shows from its listing, so stored URLs are the reliable source;
    # page harvest below stays as a best-effort supplement.
    revisit = []
    if mode == "post":
        src_path = Path(os.environ.get("CINEMARK_POST_SOURCE") or CINEMARK_CSV)
        totals["weekend_rows_stored"] = 0
        sources = []
        if src_path.exists():
            with open(src_path, newline="") as f:
                for r in csv.DictReader(f):
                    # PRE rows only: counting census rows would make the
                    # dead-pre-lane red one-shot — Friday's post capture
                    # would disarm it for the rest of the weekend.
                    if ((r.get("weekend_of") or "").strip() == weekend_of
                            and (r.get("row_kind") or "") != "post-show-census"
                            and "post-show-census" not in (r.get("notes") or "")):
                        totals["weekend_rows_stored"] += 1
                    sources.append(r)
        if CINEMARK_LINKS_CSV.exists():
            with open(CINEMARK_LINKS_CSV, newline="") as f:
                sources += list(csv.DictReader(f))
        pool_names = {t.get("name", "") for t in pool} if CINEMARK_NUM_SHARDS > 1 else None
        revisit = post_candidates(sources, weekend_of, set(target_slugs.values()), now_utc,
                                  pool_names=pool_names)
        print(f"  post-show revisit candidates from stored rows: {len(revisit)}",
              flush=True)
        totals["revisit_candidates"] = len(revisit)

    # Per-theatre flush (the Fandango lane's lesson): rows already captured
    # must survive a mid-run death — one uncaught surprise at theatre 200
    # must not lose theatres 1-199.
    def _flush():
        w, d = append_rows(rows)
        totals["written"] = totals.get("written", 0) + w
        totals["deduped"] = totals.get("deduped", 0) + d
        totals["skipped"] += d
        rows.clear()

    http_reader = HttpSeatReader() if CINEMARK_SEAT_FETCH == "http" else None
    with sync_playwright() as p:
        browser = p.chromium.launch(**proxy_egress.launch_kwargs(
            {"headless": headless, "args": ["--disable-blink-features=AutomationControlled"]}))
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        proxy_egress.attach_meter(ctx, page, budget)
        proxy_egress.trim_page(page, budget)
        for item in revisit:
            if time.monotonic() > deadline or budget.exhausted():
                break
            seats = http_reader.read(item["pick"]["href"]) if http_reader else None
            if http_reader and not CINEMARK_BROWSER_FALLBACK and (
                    not seats or int(seats.get("total") or 0) < CINEMARK_MIN_SEATS):
                totals["incomplete"] += 1
                continue
            if not seats or int(seats.get("total") or 0) < CINEMARK_MIN_SEATS:
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
        _flush()
        # Tarpit breaker: after ~150 pages cinemark.com stops serving this
        # runner — every subsequent goto times out 30s apart (run
        # 33549713848 burned ~80 minutes on a dead tail). A streak of
        # consecutive page failures means the rest of the pool is lost too;
        # stop cleanly, keep what's captured, and let the next slot's fresh
        # runner IP take its shard.
        timeout_streak = 0
        for th in pool:
            if time.monotonic() > deadline or budget.exhausted():
                print("⏱  deadline reached; stopping cleanly", flush=True)
                break
            if timeout_streak >= 8:
                # The one observed 'tarpit' (run 33549713848) was an 11-page,
                # ~5.5-minute transient that self-cleared — a hard stop would
                # have abandoned the third of the pool that loaded fine after
                # it. Pause once and resume; stop only on a second streak.
                if (not totals.get("tarpit_pauses")
                        and time.monotonic() + 300 < deadline):
                    totals["tarpit_pauses"] = 1
                    print(f"⏸️  {timeout_streak} consecutive page failures — "
                          f"pausing 5 min for the throttle to clear "
                          f"(visited={totals['visited']})", flush=True)
                    time.sleep(300)
                    timeout_streak = 0
                else:
                    why = ("after a pause" if totals.get("tarpit_pauses")
                           else "too close to the deadline to pause")
                    print(f"🛑 {timeout_streak} consecutive page failures {why} — "
                          f"tarpitted; stopping the pool walk cleanly "
                          f"(visited={totals['visited']})", flush=True)
                    totals["tarpit_stop"] = 1
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
                    if time.monotonic() > deadline or budget.exhausted():
                        break
                    # The redesigned site (2026-09-23) honours ?showDate=:
                    # load the dated page directly; the click-the-carousel
                    # path stays as the fallback for the old layout.
                    how = None
                    try:
                        page.goto(f"{BASE}/theatres/{th['slug']}?showDate={want}",
                                  wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(2500)
                        if any((parse_seatmap_href(e.get("href", "")) or {})
                               .get("sdate", "")[:10] == want
                               for e in harvest_entries(page)):
                            how = "url:showDate"
                    except Exception:
                        how = None
                    if not how:
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
                timeout_streak += 1
                print(f"  {th.get('slug', '?')}: page ERROR {str(e)[:80]}",
                      flush=True)
                continue
            timeout_streak = 0
            picks = select_showtimes(entries or [], target_slugs, window_dates,
                                     th.get("timezone", "America/Chicago"),
                                     now_utc, per_theatre_cap, mode=mode)
            totals["matched"] += len(picks)
            if mode == "pre" and not os.environ.get("CINEMARK_OUTPUT"):
                try:
                    totals["links_stored"] += append_links(
                        link_rows(th, entries, target_slugs, window_dates, weekend_of, now_utc))
                except Exception as e:
                    print(f"  link store failed: {type(e).__name__}", flush=True)
            if mode == "post" and not picks:
                times = sorted((parse_seatmap_href(e.get("href", "")) or {})
                               .get("sdate", "")[11:] for e in (entries or []))[:8]
                print(f"  {th['slug']}: post-harvest empty — {len(entries or [])} "
                      f"listed showtimes, earliest {times[:4]} (page likely "
                      f"drops started shows)", flush=True)
            for pick in picks:
                if time.monotonic() > deadline or budget.exhausted():
                    break
                seats = http_reader.read(pick["href"]) if http_reader else None
                if seats and int(seats.get("total") or 0) >= CINEMARK_MIN_SEATS:
                    pass      # HTTP read the map; skip the browser load
                elif http_reader and not CINEMARK_BROWSER_FALLBACK:
                    totals["incomplete"] += 1
                    continue
                else:
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
                if not http_reader:
                    time.sleep(random.uniform(*CINEMARK_POLITE_SEC))   # the HTTP reader paces itself
            _flush()
        browser.close()

    _flush()
    if http_reader:
        totals.update(http_reader.stats)
    totals.setdefault("written", 0)
    print(budget.summary(), flush=True)
    print(budget.breakdown(), flush=True)
    print(f"\n=== Cinemark collect summary ===\n"
          f"  visited={totals['visited']} matched={totals['matched']} "
          f"captured={totals['captured']} written={totals['written']} "
          f"deduped={totals.get('deduped', 0)} "
          f"incomplete={totals['incomplete']} blocks={totals['blocks']} "
          f"challenges={totals.get('challenges', 0)} "
          f"date_nav ok/empty/failed={totals['date_nav_ok']}/"
          f"{totals['date_nav_empty']}/{totals['date_nav_failed']} "
          f"http ok/empty/throttled/error={totals.get('http_ok', 0)}/{totals.get('http_empty', 0)}/"
          f"{totals.get('http_throttled', 0)}/{totals.get('http_error', 0)} gone={totals.get('http_gone', 0)} "
          f"proxy ok={totals.get('proxy_ok', 0)} proxy_mb={totals.get('proxy_mb', 0)} links={totals.get('links_stored', 0)}\n"
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
    if not is_new:
        migrate_header(out_path, CINEMARK_FIELDS)      # old files gain the structured columns
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
    # Stored URL must be the ORIGINAL href absolutized — the post census
    # revisits it, and a param-stripped reconstruction breaks the render.
    assert row["amc_seat_map_url"] == BASE + picks[0]["href"], row["amc_seat_map_url"]

    # Post mode picks the most recently STARTED show first (minutes_until is
    # 0 for every started show and cannot order a post pass).
    post_entries = [
        {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=8&Showtime=2026-08-31T10:00:00",
         "movie_href": "/movies/toy-story-5"},          # started 5h ago (CT)
        {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=9&Showtime=2026-08-31T13:30:00",
         "movie_href": "/movies/toy-story-5"},          # started 1.5h ago
    ]
    post_picks = select_showtimes(post_entries, targets, {"2026-08-31"},
                                  "America/Chicago", now, cap=1, mode="post")
    assert [p["showtime_id"] for p in post_picks] == ["9"], post_picks

    # split-zone city overrides beat the state majority zone
    ep = theatre_from_url("https://www.cinemark.com/theatres/tx-el-paso/cinemark-west")
    assert ep and ep["timezone"] == "America/Denver", ep
    print("cinemark_collect selftest OK")


def tarpit_verdict(totals):
    """Exit policy for a tarpit-stopped run (pure, unit-tested).

    'red'  — tarpit fired with almost nothing captured: the whole shard-day
             is at stake and only a RED run gets the scheduler's fresh-IP
             retries.
    'warn' — tarpit fired after real captures: keep the green (a retry would
             mostly re-walk collected theatres) but say so loudly.
    'ok'   — no tarpit.
    """
    if not totals or not totals.get("tarpit_stop"):
        return "ok"
    return "red" if totals.get("captured", 0) < 20 else "warn"


def harvest_verdict(totals, mode="pre", min_visited=20):
    """'red' when a pre pass walked the pool and matched NOTHING (pure).

    2026-09-23..26: cinemark.com changed its seat-link format; every pre pass
    visited ~100 theatres, matched 0 showtimes, wrote 0 rows and exited GREEN
    for three days, so the scheduler never retried and nobody noticed. With
    tracked titles on sale, zero matches across a real walk is a layout or
    matcher break, never a quiet day."""
    if mode != "pre" or not totals:
        return "ok"
    if totals.get("visited", 0) >= min_visited and totals.get("matched", 0) == 0 \
            and not totals.get("tarpit_stop"):
        return "red"
    return "ok"


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
    verdict = tarpit_verdict(totals)
    if verdict == "red":
        print("❌ Tarpitted with almost nothing captured — the shard's day "
              "would be lost on a green exit (retries only re-dispatch RED "
              "runs, and a fresh runner IP is exactly the cure). Failing.")
        return 1
    if verdict == "warn":
        print("::warning::cinemark tarpit stopped the pool walk early — "
              f"captured={totals.get('captured', 0)} before the wall; the "
              "shard tail is lost until the next pass.")
    if harvest_verdict(totals, mode) == "red":
        print(f"❌ Pre pass visited {totals.get('visited', 0)} theatres and matched "
              "ZERO tracked showtimes — the site layout or link format changed "
              "(2026-09-23 precedent). Failing loudly.")
        return 1
    if totals and totals.get("written", 0) == 0 and totals.get("matched", 0) > 0:
        print("❌ Showtimes matched but zero rows written — failing loudly.")
        return 1
    # Revisit captures never increment `matched` (page-harvest picks do), so
    # an all-incomplete post census — e.g. seat-map render decay after start —
    # would otherwise exit green with zero rows.
    if (totals and mode == "post"
            and totals.get("revisit_candidates", 0) > 0
            and totals.get("captured", 0) == 0):
        print("❌ Post census: every stored-URL revisit came back incomplete "
              "— seat maps may no longer render post-start. Failing loudly.")
        return 1
    # The mirror hole (72h dry-run audit): with NO stored pre rows at all,
    # revisit_candidates is 0 and the guard above never arms — the showtimes
    # page drops started shows, so page harvest is near-empty too and a whole
    # census day would vanish on a green run. Scoped to the WEEKEND (round-3
    # audit): candidates can legitimately be 0 on a healthy lane — e.g.
    # Friday 06:20Z with zero Thursday previews at Cinemark, Fri-Sun rows all
    # still in the future — so the red arms only when the pre lane wrote
    # NOTHING for this weekend all week.
    if (totals and mode == "post"
            and totals.get("weekend_rows_stored", 0) == 0
            and totals.get("revisit_candidates", 0) == 0
            and totals.get("captured", 0) == 0):
        print("❌ Post census: the pre lane stored ZERO rows for this weekend, "
              "nothing to revisit, and page harvest captured nothing — census "
              "day lost. Failing loudly.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
