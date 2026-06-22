#!/usr/bin/env python3
"""Phase B — production Fandango (Regal/Cinemark) pre-reservation collector.

ISOLATION CONTRACT: this module writes ONLY to
``data/fandango-pre-reservation-snapshots.csv`` — a NEW, separate file. It never
touches the AMC ``seat-counts.csv`` / ``pre-reservation-snapshots.csv``. The
Fandango file's schema is a strict SUPERSET of the AMC pre-reservation schema
(``PRE_RESERVATION_FIELDS`` imported from scraper, no drift) plus a trailing
``chain`` column (REGL/CNMK), so Phase C can merge the two trivially (AMC rows
→ chain="AMC"). Until then Fandango data accumulates here, gated OUT of the
model. See memory: fandango-stored-in-its-own-file-not-amc-schema.

Discovery (proven live 2026-06-22):
  1. requests GET ``{zip}_movietimes`` (SSR) → theater-page slugs, chain from
     the slug prefix (regal-* / cinemark-*).
  2. render ``/{slug}/theater-page`` (Playwright) → every ``a[href*=jump.aspx]``
     showtime button maps to its film via the nearest ancestor containing an
     ``a[href*=movie-overview]`` link (e.g. /toy-story-5-2026-243393/...);
     ``sdate`` is already in the jump href.
  3. keep only showtimes whose movie matches a tracked title and whose date is
     in the opening-weekend window and is still pre-show.
  4. follow the jump href → seatselection page → SEAT_COUNT_JS; record only if
     ``assess_completeness`` passes (the Fandango partial-render guard).

Run:  python3 fandango_collect.py                 # current weekend, tracked titles
      python3 fandango_collect.py --titles "Toy Story 5"
      python3 fandango_collect.py --selftest      # offline logic checks, no network
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# Proven primitives from the Phase A probe (chain filter, seat counting, block
# sentinel, completeness gate). Re-validated end to end before this module.
from fandango_probe import (
    UA,
    CHROMIUM_ARGS,
    WANTED_CHAINS,
    SEAT_COUNT_JS,
    theater_page_links,
    is_wanted_chain,
    seat_url_params,
    assess_completeness,
    looks_blocked,
)

# Single source of truth for the row schema + weekend/target wiring. Importing
# (not copying) the AMC schema guarantees the Fandango file stays a superset.
from scraper import (
    PRE_RESERVATION_FIELDS,
    PRE_RESERVATION_DEDUPE_FIELDS,
    opening_weekend_friday,
    opening_weekend_show_dates,
    tracked_movie_titles_from_state,
    snapshot_bucket,
    should_record_pre_reservation_snapshot,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
FANDANGO_CSV = DATA_DIR / "fandango-pre-reservation-snapshots.csv"
THEATRES_JSON = DATA_DIR / "theatres-fandango.json"

# Schema = AMC pre-reservation schema + chain (superset; trivially mergeable).
FANDANGO_PRE_RESERVATION_FIELDS = list(PRE_RESERVATION_FIELDS) + ["chain"]
# chain is in the dedupe key too: a Regal `mid` must never dedupe against a
# Cinemark `mid` that happens to collide (and keeps AMC-merge safe in Phase C).
FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS = tuple(PRE_RESERVATION_DEDUPE_FIELDS) + ("chain",)

_DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except (TypeError, ValueError):
        return default


# Run-shape knobs. The theatre pool is national (~hundreds); each run samples a
# rotating subset within the deadline using N parallel browsers. Defaults are
# tuned so a ~320-theatre pool completes inside the GH job budget on a 2-core
# runner; the workflow can override via env.
FANDANGO_CONCURRENCY = _env_int("FANDANGO_CONCURRENCY", 3)        # parallel browsers
FANDANGO_DEADLINE_SEC = _env_int("FANDANGO_DEADLINE_SEC", 4200)   # stop launching new theatres after this
FANDANGO_PER_THEATRE_CAP = _env_int("FANDANGO_PER_THEATRE_CAP", 3)  # showtimes captured per theatre
FANDANGO_MAX_THEATRES = _env_int("FANDANGO_MAX_THEATRES", 0)      # 0 = whole pool

# Adaptive throttle handling. Fandango rate-limits its seat-availability backend
# per IP: under sustained load the seat page loads but the map never populates
# (stuck "Loading… 0 seats"). When such failures cluster we slow down, and if
# they persist we stop the run cleanly rather than burn the whole window on
# 18s-per-render timeouts. Rows already captured are kept (per-theatre flush).
FANDANGO_BACKOFF_AFTER = _env_int("FANDANGO_BACKOFF_AFTER", 4)        # consecutive seat-render fails → slow down
FANDANGO_STOP_AFTER = _env_int("FANDANGO_STOP_AFTER", 12)            # consecutive fails → stop the run
FANDANGO_BACKOFF_STEP_SEC = _env_int("FANDANGO_BACKOFF_STEP_SEC", 6)  # extra delay added per backoff step
FANDANGO_BACKOFF_MAX_SEC = _env_int("FANDANGO_BACKOFF_MAX_SEC", 30)   # cap on the added delay


# ── Pure logic (offline-testable) ────────────────────────────────────────────

def slugify_title(title):
    """'Toy Story 5' -> 'toy-story-5' (matches Fandango's movie-overview slug)."""
    s = re.sub(r"[^a-z0-9]+", "-", str(title or "").lower()).strip("-")
    return s


def overview_core_slug(href):
    """'/toy-story-5-2026-243393/movie-overview' -> 'toy-story-5'.

    Fandango movie-overview slugs are ``{title-slug}-{year}-{fandangoId}``; strip
    the trailing ``-YYYY-NNNN`` so we compare against the bare title slug.
    """
    if not href:
        return ""
    path = urlparse(href).path or href
    m = re.search(r"/([a-z0-9\-]+)/movie-overview", path)
    core = m.group(1) if m else ""
    return re.sub(r"-\d{4}-\d+$", "", core)


def match_target_title(overview_href, target_slugs):
    """Return the canonical tracked title for a movie-overview link, or None.

    ``target_slugs`` maps slugified-title -> canonical title. Exact core-slug
    match only — so 'Toy Story' (toy-story) never swallows 'Toy Story 5'
    (toy-story-5).
    """
    core = overview_core_slug(overview_href)
    return target_slugs.get(core)


def sdate_from_jump_href(href):
    """Extract the local showtime datetime from a jump.aspx href.

    Fandango encodes it as ``sdate=2026-06-22+19%3A55`` -> '2026-06-22 19:55'.
    """
    q = parse_qs(urlparse(href).query)
    raw = unquote((q.get("sdate") or [""])[0]).replace("+", " ").strip()
    return raw


def parse_show_datetime(sdate):
    """'2026-06-22 19:55' -> naive datetime, or None."""
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(sdate, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _local_to_utc(show_dt, tz_name):
    """Best-effort local-showtime -> aware UTC. Falls back to UTC if tz absent."""
    if show_dt is None:
        return None
    try:
        from zoneinfo import ZoneInfo
        return show_dt.replace(tzinfo=ZoneInfo(tz_name)).astimezone(timezone.utc)
    except Exception:
        return show_dt.replace(tzinfo=timezone.utc)


def showtime_timing(sdate, tz_name, now_utc):
    """Return (minutes_after_showtime, minutes_until_showtime, show_date, dow).

    ``minutes_after_showtime`` < 0 means the show is still in the future (the
    pre-reservation window), matching scraper's convention.
    """
    show_dt = parse_show_datetime(sdate)
    if show_dt is None:
        return None, "", "", ""
    show_utc = _local_to_utc(show_dt, tz_name)
    minutes_after = int((now_utc - show_utc).total_seconds() // 60)
    minutes_until = max(0, -minutes_after)
    show_date = show_dt.strftime("%Y-%m-%d")
    dow = _DOW[show_dt.weekday()]
    return minutes_after, minutes_until, show_date, dow


def select_wanted_showtimes(entries, target_slugs, window_dates, tz_name,
                            now_utc, cap):
    """From a theatre's showtime buttons, pick the tracked-title showtimes worth
    capturing: in-window date, still pre-show, prime-time first (the strongest
    reservation signal), capped. Pure — unit-tested offline.
    """
    wanted = []
    for e in entries:
        title = match_target_title(e.get("movieOverview", ""), target_slugs)
        if not title:
            continue
        sdate = sdate_from_jump_href(e.get("href", ""))
        m_after, m_until, show_date, dow = showtime_timing(sdate, tz_name, now_utc)
        if m_after is None or show_date not in window_dates:
            continue
        if not should_record_pre_reservation_snapshot(m_after):
            continue
        show_dt = parse_show_datetime(sdate)
        hour = show_dt.hour if show_dt else 12
        wanted.append({
            "title": title, "sdate": sdate, "href": e.get("href", ""),
            "minutes_until": m_until, "show_date": show_date, "day_of_week": dow,
            "_prime": abs(hour - 19),  # distance from 7pm
        })
    # Prime-time evening shows first (highest occupancy signal), then by date.
    wanted.sort(key=lambda w: (w["_prime"], w["show_date"]))
    if cap and cap > 0:
        wanted = wanted[:cap]
    return wanted


def build_fandango_row(theatre, movie_title, sdate, seat_url, params, seats,
                       weekend_of, run_id, check_time, minutes_until, show_date,
                       day_of_week, note=""):
    """Build one pre-reservation snapshot row (schema = AMC superset + chain)."""
    total = int(seats.get("total", 0) or 0)
    reserved = int(seats.get("reserved", 0) or 0)
    available = int(seats.get("available", max(0, total - reserved)) or 0)
    occ = round(reserved / total * 100, 1) if total else 0.0
    tz_name = theatre.get("timezone", "")
    # Show time label from the local sdate (e.g. '19:55').
    show_dt = parse_show_datetime(sdate)
    showtime_label = show_dt.strftime("%H:%M") if show_dt else sdate
    return {
        "weekend_of": weekend_of,
        "run_id": run_id,
        "snapshot_time": check_time,
        "snapshot_bucket": snapshot_bucket(check_time),
        "show_date": show_date,
        "day_of_week": day_of_week,
        "theatre_name": theatre.get("name", ""),
        "theatre_city": theatre.get("city", theatre.get("dma", "")),
        "timezone": tz_name,
        "movie_title": movie_title,
        "showtime": showtime_label,
        # Fandango's `mid` query param is the MOVIE id (constant across a film's
        # showtimes), NOT a per-showtime id — so the showtime is identified by its
        # datetime. Using it here keeps distinct showtimes as distinct rows and
        # anchors the reservation-delta to the correct prior reading.
        "showtime_id": sdate,
        "minutes_until_showtime": str(minutes_until),
        "auditorium_name": "",
        "auditorium_type": "Standard",
        "total_seats": str(total),
        "reserved_seats": str(reserved),
        "available_seats": str(available),
        "occupancy_pct": str(occ),
        "delta_reserved_since_previous": "",
        "amc_seat_map_url": seat_url,   # legacy-named column: holds the seat-map URL
        "notes": note,
        "chain": params.get("chain", theatre.get("chain", "")),
    }


def fandango_row_key(row):
    return tuple(str(row.get(f, "") or "") for f in FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS)


_IDENTITY_FIELDS = ("weekend_of", "show_date", "theatre_name", "movie_title",
                    "showtime_id", "auditorium_type", "chain")


def _identity(row):
    return tuple(str(row.get(f, "") or "") for f in _IDENTITY_FIELDS)


# ── CSV I/O (isolated file only) ─────────────────────────────────────────────

def ensure_fandango_header(csv_path=None):
    csv_path = csv_path or FANDANGO_CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        with open(csv_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FANDANGO_PRE_RESERVATION_FIELDS).writeheader()


def append_unique_fandango_rows(rows, csv_path=None):
    """Append snapshots to the isolated Fandango file, deduped by the chain-aware
    key, computing delta_reserved vs the prior bucket for the same showtime."""
    if not rows:
        return 0, 0
    csv_path = csv_path or FANDANGO_CSV
    ensure_fandango_header(csv_path)

    existing_keys = set()
    reserved_index = {}
    if csv_path.exists():
        with open(csv_path, "r", newline="") as f:
            for ex in csv.DictReader(f):
                existing_keys.add(tuple(
                    str(ex.get(fld, "") or "")
                    for fld in FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS
                ))
                bucket = str(ex.get("snapshot_bucket", "") or "")
                try:
                    reserved = int(float(ex.get("reserved_seats", 0) or 0))
                except (TypeError, ValueError):
                    continue
                reserved_index.setdefault(_identity(ex), []).append((bucket, reserved))

    pending, seen, skipped = [], set(existing_keys), 0
    for row in rows:
        normalized = {fld: str(row.get(fld, "") or "")
                      for fld in FANDANGO_PRE_RESERVATION_FIELDS}
        if not normalized.get("delta_reserved_since_previous"):
            prior = [
                r for b, r in reserved_index.get(_identity(normalized), ())
                if b < str(normalized.get("snapshot_bucket", "") or "")
            ]
            if prior:
                try:
                    normalized["delta_reserved_since_previous"] = str(
                        int(float(normalized.get("reserved_seats", 0) or 0)) - max(prior)
                    )
                except (TypeError, ValueError):
                    pass
        key = tuple(str(normalized.get(fld, "") or "")
                    for fld in FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS)
        if key in seen:
            skipped += 1
            continue
        pending.append(normalized)
        seen.add(key)

    if pending:
        with open(csv_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=FANDANGO_PRE_RESERVATION_FIELDS).writerows(pending)
    return len(pending), skipped


def load_fandango_theatres(zips=None):
    """Load Regal/Cinemark theatres from theatres-fandango.json (chain-filtered)."""
    if not THEATRES_JSON.exists():
        return []
    with open(THEATRES_JSON) as f:
        data = json.load(f)
    out = []
    for th in data.get("theatres", []):
        if th.get("chain", "").upper() not in WANTED_CHAINS:
            continue
        if zips and str(th.get("zip", "")) not in {str(z) for z in zips}:
            continue
        out.append(th)
    return out


# ── Browser discovery + capture ──────────────────────────────────────────────

# For each hydrated showtime button, walk ancestors to the movie container and
# read its movie-overview href (the film identity). Validated live 2026-06-22.
SHOWTIME_ENTRIES_JS = r"""() => {
  const out = [];
  document.querySelectorAll('a[href*="jump.aspx"]').forEach(a => {
    let n = a, slug = '';
    for (let d = 0; d < 12 && n; d++, n = n.parentElement) {
      const mo = n.querySelector && n.querySelector('a[href*="movie-overview"]');
      if (mo) { slug = mo.getAttribute('href') || ''; break; }
    }
    out.push({ time: (a.textContent || '').trim(), href: a.href, movieOverview: slug });
  });
  return out;
}"""


def _note_seat_failure(shared):
    """Record a seat-map render failure (throttle/block signal) shared across all
    workers — they hit one IP-level limit. Returns True if the run should stop."""
    with shared["lock"]:
        shared["consec_fail"] += 1
        n = shared["consec_fail"]
        if n >= shared["stop_after"]:
            if not shared["stop"].is_set():
                shared["stop"].set()
                print(f"   ⛔ {n} consecutive seat-render failures — likely IP-throttled; "
                      "stopping the run (rows already captured are kept).")
            return True
        if n >= shared["backoff_after"]:
            shared["backoff_extra"] = min(
                shared["backoff_extra"] + shared["backoff_step"], shared["backoff_max"])
            print(f"   🐢 {n} consecutive seat-render failures — backing off "
                  f"(+{shared['backoff_extra']:.0f}s/render).")
        return False


def _note_seat_success(shared):
    """A seat map rendered — reset the throttle counter and any backoff."""
    with shared["lock"]:
        shared["consec_fail"] = 0
        shared["backoff_extra"] = 0.0


def _capture_theatre(page, th, shared):
    """Render one theatre, capture its tracked-title seat maps. Returns
    (rows, stats). Feeds the shared throttle state so the run backs off / stops
    when the seat-availability backend starts rate-limiting."""
    slug = th.get("slug", "")
    tz_name = th.get("timezone", "")
    stats = {"matched": 0, "renders": 0, "incompletes": 0, "blocks": 0, "seat_fails": 0}
    try:
        page.goto(f"https://www.fandango.com/{slug}/theater-page",
                  wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        if looks_blocked(page):
            stats["blocks"] += 1
            print(f"  {slug}: BLOCKED on theater-page")
            return [], stats
        entries = page.evaluate(SHOWTIME_ENTRIES_JS)
    except Exception as e:
        print(f"  {slug}: theater-page ERROR {str(e)[:80]}")
        return [], stats

    wanted = select_wanted_showtimes(entries, shared["target_slugs"],
                                     shared["window_dates"], tz_name,
                                     shared["now_utc"], shared["per_theatre_cap"])
    stats["matched"] = len(wanted)
    rows = []
    for w in wanted:
        if shared["stop"].is_set():
            break
        with shared["lock"]:
            extra = shared["backoff_extra"]
        time.sleep(random.uniform(*shared["polite"]) + extra)
        stats["renders"] += 1
        seats = None
        try:
            page.goto(w["href"], wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(1200)
            if looks_blocked(page):
                stats["blocks"] += 1
                stats["seat_fails"] += 1
                if _note_seat_failure(shared):
                    break
                continue
            params = seat_url_params(page.url)
            if not params["is_seat_page"] or not is_wanted_chain(params["chain"]):
                continue   # routing miss, not a throttle signal
            try:
                page.wait_for_selector(".seat-map__seat", timeout=8000)
            except Exception:
                # one reload-retry — the seat map occasionally hydrates slowly
                page.reload(wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector(".seat-map__seat", timeout=10000)
            seats = page.evaluate(SEAT_COUNT_JS)
        except Exception:
            # seat page loaded but the map never populated ("Loading… 0 seats") —
            # the signature of the seat-availability throttle.
            stats["seat_fails"] += 1
            if _note_seat_failure(shared):
                break
            continue
        if not seats or seats.get("total", 0) <= 0:
            stats["seat_fails"] += 1
            if _note_seat_failure(shared):
                break
            continue
        _note_seat_success(shared)
        if not assess_completeness(seats.get("total", 0),
                                   seats.get("rowFirst", ""),
                                   seats.get("containerFits")):
            stats["incompletes"] += 1
            continue
        rows.append(build_fandango_row(
            th, w["title"], w["sdate"], page.url, params, seats,
            shared["weekend_of"], shared["run_id"], shared["check_time"],
            w["minutes_until"], w["show_date"], w["day_of_week"],
        ))
    return rows, stats


def _worker(slice_theatres, shared):
    """One browser processing a slice of theatres until the shared deadline.
    Each worker owns its own Playwright instance (the sync API is per-thread)."""
    from playwright.sync_api import sync_playwright

    agg = {"matched": 0, "renders": 0, "incompletes": 0, "blocks": 0,
           "seat_fails": 0, "written": 0, "skipped": 0, "captured": 0, "visited": 0}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=shared["headless"], args=CHROMIUM_ARGS)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 1600})
        page = ctx.new_page()
        for th in slice_theatres:
            if shared["stop"].is_set() or time.monotonic() >= shared["deadline"]:
                break
            agg["visited"] += 1
            rows, stats = _capture_theatre(page, th, shared)
            for k in stats:
                agg[k] += stats[k]
            # Flush per theatre (under a lock — the file is the shared writer)
            # so a deadline/crash keeps earlier theatres' rows durable.
            if rows:
                with shared["lock"]:
                    w, sk = append_unique_fandango_rows(rows)
                agg["written"] += w
                agg["skipped"] += sk
                agg["captured"] += len(rows)
        browser.close()
    return agg


def collect(weekend_of=None, titles=None, zips=None, theatres=None,
            per_theatre_cap=None, max_theatres=None, headless=True, run_id=None,
            polite=(1.0, 2.5), concurrency=None, deadline_sec=None):
    """Capture tracked-title Regal/Cinemark seat maps across the national pool
    using N parallel browsers, bounded by a deadline, appending to the isolated
    Fandango file. Returns a totals dict."""
    weekend_of = weekend_of or opening_weekend_friday()
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return {}
    target_slugs = {slugify_title(t): t for t in titles}
    window_dates = set(opening_weekend_show_dates(weekend_of))
    theatres = theatres if theatres is not None else load_fandango_theatres(zips)
    if not theatres:
        print("⚠️  No Fandango theatres configured (data/theatres-fandango.json).")
        return {}

    per_theatre_cap = per_theatre_cap if per_theatre_cap is not None else FANDANGO_PER_THEATRE_CAP
    concurrency = concurrency if concurrency is not None else FANDANGO_CONCURRENCY
    deadline_sec = deadline_sec if deadline_sec is not None else FANDANGO_DEADLINE_SEC
    max_theatres = max_theatres if max_theatres is not None else FANDANGO_MAX_THEATRES

    # Shuffle so a deadline-bounded (partial) run still samples the pool broadly,
    # and coverage rotates across nights rather than always starting in the same
    # cities.
    theatres = list(theatres)
    random.shuffle(theatres)
    if max_theatres and max_theatres > 0:
        theatres = theatres[:max_theatres]

    now_utc = datetime.now(timezone.utc)
    check_time = now_utc.isoformat()
    run_id = run_id or f"fandango-{snapshot_bucket(check_time)}"
    concurrency = max(1, min(concurrency, len(theatres)))

    print(f"Fandango collect • weekend_of={weekend_of} • {len(theatres)} theatres "
          f"• {concurrency} workers • cap={per_theatre_cap}/theatre "
          f"• deadline={deadline_sec}s • titles={list(target_slugs.values())}")

    shared = {
        "target_slugs": target_slugs, "window_dates": window_dates,
        "now_utc": now_utc, "weekend_of": weekend_of, "run_id": run_id,
        "check_time": check_time, "per_theatre_cap": per_theatre_cap,
        "polite": polite, "headless": headless,
        "deadline": time.monotonic() + deadline_sec, "lock": threading.Lock(),
        # adaptive throttle state, shared across workers (one IP-level limit)
        "stop": threading.Event(), "consec_fail": 0, "backoff_extra": 0.0,
        "backoff_after": FANDANGO_BACKOFF_AFTER, "stop_after": FANDANGO_STOP_AFTER,
        "backoff_step": float(FANDANGO_BACKOFF_STEP_SEC),
        "backoff_max": float(FANDANGO_BACKOFF_MAX_SEC),
    }

    # Round-robin slices so each worker's slice is geographically mixed.
    slices = [theatres[i::concurrency] for i in range(concurrency)]
    totals = {"matched": 0, "renders": 0, "incompletes": 0, "blocks": 0,
              "seat_fails": 0, "written": 0, "skipped": 0, "captured": 0, "visited": 0}
    if concurrency == 1:
        aggs = [_worker(slices[0], shared)]
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            aggs = list(ex.map(lambda s: _worker(s, shared), slices))
    for agg in aggs:
        for k in totals:
            totals[k] += agg.get(k, 0)
    totals["throttled_stop"] = shared["stop"].is_set()

    print("\n=== Fandango collect summary ===")
    print(f"  pool={len(theatres)} visited={totals['visited']}"
          f"{' (STOPPED EARLY — throttled)' if totals['throttled_stop'] else ''} "
          f"matched_showtimes={totals['matched']} renders={totals['renders']}")
    print(f"  captured={totals['captured']} written={totals['written']} "
          f"deduped={totals['skipped']} incomplete_dropped={totals['incompletes']} "
          f"seat_fails={totals['seat_fails']} blocks={totals['blocks']}")
    print(f"  -> {FANDANGO_CSV}")
    return totals


# ── Offline self-test ────────────────────────────────────────────────────────

def _selftest():
    assert slugify_title("Toy Story 5") == "toy-story-5"
    assert slugify_title("Star Wars: The Mandalorian & Grogu") == "star-wars-the-mandalorian-grogu"

    assert overview_core_slug("/toy-story-5-2026-243393/movie-overview") == "toy-story-5"
    assert overview_core_slug("https://www.fandango.com/backrooms-2026-244954/movie-overview") == "backrooms"

    targets = {slugify_title(t): t for t in ["Toy Story 5", "Backrooms"]}
    assert match_target_title("/toy-story-5-2026-243393/movie-overview", targets) == "Toy Story 5"
    assert match_target_title("/backrooms-2026-244954/movie-overview", targets) == "Backrooms"
    # 'Toy Story' must NOT match 'Toy Story 5'
    assert match_target_title("/toy-story-1995-1234/movie-overview", targets) is None
    assert match_target_title("/some-other-film-2026-999/movie-overview", targets) is None

    href = ("https://tickets.fandango.com/transaction/ticketing/mobile/jump.aspx"
            "?row_count=1&sdate=2026-06-20+19%3A55&mid=244348")
    assert sdate_from_jump_href(href) == "2026-06-20 19:55", sdate_from_jump_href(href)
    assert parse_show_datetime("2026-06-20 19:55") == datetime(2026, 6, 20, 19, 55)

    # timing: a future show (now well before showtime) is pre-show
    now = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)
    m_after, m_until, sd, dow = showtime_timing("2026-06-20 19:55", "UTC", now)
    assert m_after < 0 and m_until > 0 and sd == "2026-06-20" and dow == "Saturday", (m_after, m_until, sd, dow)
    assert should_record_pre_reservation_snapshot(m_after)
    # a past show is not recorded
    m_after2, _, _, _ = showtime_timing("2026-06-20 08:00", "UTC", now)
    assert not should_record_pre_reservation_snapshot(m_after2)

    # row schema completeness + chain present + seat-map URL stored
    theatre = {"name": "Regal Test", "city": "Dallas", "timezone": "America/Chicago", "chain": "REGL"}
    params = {"chain": "REGL", "tid": "AACAW", "mid": "244348", "sdate": "2026-06-20 19:55", "is_seat_page": True}
    seats = {"total": 200, "reserved": 50, "available": 150, "rowFirst": "A", "containerFits": True}
    seat_url = "https://tickets.fandango.com/mobileexpress/seatselection?chainCode=REGL&tid=AACAW&mid=244348"
    row = build_fandango_row(theatre, "Toy Story 5", "2026-06-20 19:55", seat_url, params, seats,
                             "2026-06-19", "run-x", now.isoformat(), 475, "2026-06-20", "Saturday")
    assert set(row) == set(FANDANGO_PRE_RESERVATION_FIELDS), set(FANDANGO_PRE_RESERVATION_FIELDS) ^ set(row)
    # showtime_id is the showtime datetime (Fandango's mid is the movie id, not per-showtime)
    assert row["chain"] == "REGL" and row["showtime_id"] == "2026-06-20 19:55"
    assert row["amc_seat_map_url"] == seat_url and row["occupancy_pct"] == "25.0"

    # dedupe key includes chain (so REGL/CNMK never collapse)
    r2 = dict(row); r2["chain"] = "CNMK"
    assert fandango_row_key(row) != fandango_row_key(r2)

    # schema is a strict superset of the AMC pre-reservation schema
    assert FANDANGO_PRE_RESERVATION_FIELDS[:-1] == list(PRE_RESERVATION_FIELDS)
    assert FANDANGO_PRE_RESERVATION_FIELDS[-1] == "chain"

    print("fandango_collect selftest OK")


def main():
    ap = argparse.ArgumentParser(description="Fandango Regal/Cinemark pre-reservation collector")
    ap.add_argument("--selftest", action="store_true", help="offline logic checks, no network")
    ap.add_argument("--weekend", help="weekend_of (YYYY-MM-DD); default = current")
    ap.add_argument("--titles", nargs="*", help="override tracked titles")
    ap.add_argument("--zips", nargs="*", help="restrict to theatres in these zips")
    ap.add_argument("--max-theatres", type=int, default=FANDANGO_MAX_THEATRES,
                    help="cap theatres visited this run (0 = whole pool)")
    ap.add_argument("--per-theatre-cap", type=int, default=FANDANGO_PER_THEATRE_CAP,
                    help="showtimes captured per theatre (prime-time first)")
    ap.add_argument("--concurrency", type=int, default=FANDANGO_CONCURRENCY,
                    help="parallel browsers")
    ap.add_argument("--deadline-sec", type=int, default=FANDANGO_DEADLINE_SEC,
                    help="stop launching new theatres after this many seconds")
    ap.add_argument("--no-headless", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    collect(weekend_of=args.weekend, titles=args.titles, zips=args.zips,
            per_theatre_cap=args.per_theatre_cap, max_theatres=args.max_theatres,
            concurrency=args.concurrency, deadline_sec=args.deadline_sec,
            headless=not args.no_headless)


if __name__ == "__main__":
    main()
