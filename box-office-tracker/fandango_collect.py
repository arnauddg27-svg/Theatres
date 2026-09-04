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
    phase1_weekend_anchor,
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
FANDANGO_PER_THEATRE_CAP = _env_int("FANDANGO_PER_THEATRE_CAP", 3)  # showtimes captured PER FILM per theatre
FANDANGO_MAX_THEATRES = _env_int("FANDANGO_MAX_THEATRES", 0)      # 0 = whole pool
# Hard seat-render budget per run (0 = unlimited). Scheduled runs set 30:
# on 2026-09-03, 18 hourly slots x 55 renders ran throttled nearly all day
# (338 captures of ~1,045 attempts; slots collapsing to 2-10) — every failed
# render burns budget AND triggers backoff/pauses. The pre-expansion cadence
# (~31 renders/hour) had 0 failures in 100+ runs. With the PER-FILM cap a
# 2-film weekend spends 30 as ~15 theatres x 2 films (both films censused at
# each theatre — the paired same-theatre read); 1-film as ~30 x 1. Breadth
# adapts, the budget never overruns.
FANDANGO_RENDER_BUDGET = _env_int("FANDANGO_RENDER_BUDGET", 0)

# Adaptive throttle handling. Fandango rate-limits its seat-availability backend
# per IP: under sustained load the seat page loads but the map never populates
# (stuck "Loading… 0 seats"). When such failures cluster we slow down, and if
# they persist we stop the run cleanly rather than burn the whole window on
# 18s-per-render timeouts. Rows already captured are kept (per-theatre flush).
FANDANGO_BACKOFF_AFTER = _env_int("FANDANGO_BACKOFF_AFTER", 4)        # consecutive seat-render fails → slow down
FANDANGO_STOP_AFTER = _env_int("FANDANGO_STOP_AFTER", 12)            # consecutive fails → stop the run
FANDANGO_BACKOFF_STEP_SEC = _env_int("FANDANGO_BACKOFF_STEP_SEC", 6)  # extra delay added per backoff step
FANDANGO_BACKOFF_MAX_SEC = _env_int("FANDANGO_BACKOFF_MAX_SEC", 30)   # cap on the added delay
# The throttle is transient (recovers in ~15 min), so on a sustained stall we
# PAUSE and resume rather than hard-stop — one nightly run can then bank several
# batches instead of one. Bounded by max-resumes and the run deadline.
FANDANGO_PAUSE_SEC = _env_int("FANDANGO_PAUSE_SEC", 720)      # wait this long for the limit to recover
FANDANGO_MAX_RESUMES = _env_int("FANDANGO_MAX_RESUMES", 2)    # pause/resume cycles before giving up
# Matrix fan-out: the seat rate limit is per-IP, so split the pool across N
# parallel GitHub jobs (one fresh IP each). A leg scrapes theatres[shard::N] —
# a deterministic, geographically-mixed, disjoint slice — staying under the
# per-IP budget; a merge step recombines the shard outputs.
FANDANGO_ORDER = os.environ.get("FANDANGO_ORDER", "prime")  # prime | nearest
FANDANGO_NUM_SHARDS = _env_int("FANDANGO_NUM_SHARDS", 0)      # 0/1 = no sharding (whole pool)
FANDANGO_SHARD = _env_int("FANDANGO_SHARD", 0)               # this leg's shard index


# ── Pure logic (offline-testable) ────────────────────────────────────────────

def slugify_title(title):
    """'Toy Story 5' -> 'toy-story-5' (matches Fandango's movie-overview slug).

    Fandango spells symbols out in its slugs — '&' becomes 'and'
    ('Minions & Monsters' -> 'minions-and-monsters') — so normalize those before
    stripping to alphanumerics, or the whole film is silently dropped from the
    lane on an exact core-slug match.

    A trailing parenthesized year in the TRACKED title ('Moana (2026)') is
    stripped: overview_core_slug already removes Fandango's own '-YYYY-NNNN'
    suffix, so keeping the year here can never match ('moana-2026' vs 'moana' —
    live miss 2026-07-10: Moana got zero Fandango rows all weekend).
    """
    s = str(title or "").lower().replace("&", " and ")
    s = re.sub(r"\s*\((?:19|20)\d{2}\)\s*$", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def overview_core_slug(href):
    """'/toy-story-5-2026-243393/movie-overview' -> 'toy-story-5'.

    Fandango movie-overview slugs come in two shapes:
    ``{title-slug}-{year}-{fandangoId}`` (e.g. ``toy-story-5-2026-243393``) and
    ``{title-slug}-{fandangoId}`` with NO year (e.g. ``coyote-vs-acme-246329``).
    Strip a trailing ``-YYYY-NNNN`` (id of any length, matching the original
    behavior) OR a bare ``-NNNN`` id of 4+ digits, so we compare against the
    bare title slug. Requiring 4+ digits for the bare form leaves a real sequel
    number (``toy-story-5``) untouched. Missing the bare-id form cost
    'Coyote vs. Acme' its entire 2026-08-28 Fandango capture.
    """
    if not href:
        return ""
    path = urlparse(href).path or href
    m = re.search(r"/([a-z0-9\-]+)/movie-overview", path)
    core = m.group(1) if m else ""
    return re.sub(r"-(?:\d{4}-\d+|\d{4,})$", "", core)


# Roman numerals / number words normalize to digits so 'mortal-kombat-ii'
# matches a tracked 'Mortal Kombat 2' (and vice versa).
_NUMERAL_TOKENS = {
    "ii": "2", "iii": "3", "iv": "4", "vi": "6", "vii": "7", "viii": "8",
    "ix": "9", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}
_NEAR_MISS_LOGGED = set()


def _slug_tokens(slug):
    return frozenset(_NUMERAL_TOKENS.get(t, t) for t in (slug or "").split("-") if t)


def match_target_title(overview_href, target_slugs):
    """Return the canonical tracked title for a movie-overview link, or None.

    ``target_slugs`` maps slugified-title -> canonical title. Exact core-slug
    match first — so 'Toy Story' (toy-story) never swallows 'Toy Story 5'
    (toy-story-5). Falls back to normalized TOKEN-SET equality (word order,
    roman-numeral/number-word variants). Anything close-but-unmatched is logged
    LOUDLY: two whole films were silently dropped by slug variants already
    ('Minions & Monsters' via '&', 'Moana (2026)' via the year suffix) — the
    next variant must show up in run logs, not in a zero-row post-mortem.
    """
    core = overview_core_slug(overview_href)
    hit = target_slugs.get(core)
    if hit or not core:
        return hit
    # Second candidate: strip only a bare trailing id (5+ digits) from the RAW
    # slug. The primary strip above can over-consume when a title itself ends
    # in a 4-digit number ('blade-runner-2049-246329' -> 'blade-runner'); this
    # candidate yields 'blade-runner-2049'. Fandango ids are 5-6 digits, so
    # \d{5,} never eats a real sequel/year in the title.
    path = urlparse(overview_href).path or overview_href or ""
    m = re.search(r"/([a-z0-9\-]+)/movie-overview", path)
    raw = m.group(1) if m else ""
    alt = re.sub(r"-\d{5,}$", "", raw)
    if alt != core:
        hit = target_slugs.get(alt)
        if hit:
            return hit
    core_tokens = _slug_tokens(core)
    alt_tokens = _slug_tokens(alt) if alt != core else core_tokens
    for slug, title in target_slugs.items():
        if _slug_tokens(slug) in (core_tokens, alt_tokens):
            return title
    for slug, title in target_slugs.items():
        slug_tokens = _slug_tokens(slug)
        overlap = len(core_tokens & slug_tokens)
        union = len(core_tokens | slug_tokens) or 1
        if overlap / union >= 0.5 and core not in _NEAR_MISS_LOGGED:
            _NEAR_MISS_LOGGED.add(core)
            print(f"⚠️  NEAR-MISS: overview slug '{core}' did not match tracked "
                  f"'{title}' (slug '{slug}') — possible new slug-variant bug")
    return None


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


def page_visit_dates(window_dates, show_dates, ref_dt):
    """Which theater-page dates to render for one theatre. Pure — unit-tested.

    The default (dateless) theater-page serves only the CURRENT local day —
    verified from 306 production runs whose captures never exceed a ~43h lead —
    so it can never see the opening weekend from Monday-Wednesday. On those
    pre-opening days (and for explicit ad-hoc show_dates) each window date is
    rendered via ``theater-page?date=YYYY-MM-DD``. Thu-Sun keeps the proven
    dateless visit: same-day shows plus the overnight roll to the next day.
    ``None`` in the result means "render the default page".
    """
    if show_dates:
        return sorted(set(show_dates))
    if ref_dt.weekday() in (0, 1, 2):  # Mon-Wed pre-opening (early-lead reads)
        return sorted(window_dates)
    if ref_dt.weekday() == 3 and ref_dt.hour < 9:
        # UTC Thursday 03-08Z is still WEDNESDAY EVENING at every US theatre
        # (03Z = 23:00 ET / 20:00 PT), so the dateless page serves Wednesday's
        # shows — never in the Thu-Sun window. This made the Wednesday-night
        # overnight slots structurally near-zero (17 rows total across ~10
        # weekends vs 218-323 for Fri/Sat/Sun at the same hour). Render the
        # window dates instead; from 09Z the local pages have rolled to
        # Thursday and the proven dateless visit works.
        return sorted(window_dates)
    return [None]


def select_wanted_showtimes(entries, target_slugs, window_dates, tz_name,
                            now_utc, cap, order="prime"):
    """From a theatre's showtime buttons, pick the tracked-title showtimes worth
    capturing: in-window date, still pre-show, capped. Pure — unit-tested offline.

    order="prime"   : prime-time evening shows first (strongest reservation signal;
                      the overnight slots' default).
    order="nearest" : soonest showtime first — the afternoon "near" slots use this
                      to read occupancy 1-4h before showtime, where advance-online
                      reservations best approximate final attendance (the
                      like-for-like data the family walk-up confound needs).
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
    # Attach the PRE-CAP discovered showtime count per (title, show_date): the
    # per-chain showings allocation is the volume signal the occupancy-only
    # cross-chain share is missing (a chain giving a film few showings reads as
    # high occupancy — the Young Washington confound). Recorded in row notes.
    counts = {}
    for w in wanted:
        key = (w["title"], w["show_date"])
        counts[key] = counts.get(key, 0) + 1
    for w in wanted:
        w["discovered"] = counts[(w["title"], w["show_date"])]
    if order == "nearest":
        wanted.sort(key=lambda w: (w["minutes_until"], w["_prime"]))
    else:
        # Prime-time evening shows first (highest occupancy signal), then by date.
        wanted.sort(key=lambda w: (w["_prime"], w["show_date"]))
    if cap and cap > 0:
        # PER FILM: a multi-film weekend must census every tracked film at
        # every theatre — a global cap let the 7pm-slot owner win the only
        # pick pool-wide (2026-09-03: BAM 277 picks vs Onslaught 1). Twice
        # the films = twice the picks; the RENDER budget (not this cap)
        # bounds total load, trading theatre breadth for film completeness.
        taken = {}
        picks = []
        for w in wanted:
            if taken.get(w["title"], 0) < cap:
                taken[w["title"]] = taken.get(w["title"], 0) + 1
                picks.append(w)
        wanted = picks
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
            cur_bucket = str(normalized.get("snapshot_bucket", "") or "")
            prior = [
                (b, r) for b, r in reserved_index.get(_identity(normalized), ())
                if b < cur_bucket
            ]
            if prior:
                try:
                    # delta vs the LATEST prior bucket's reserved count (max by
                    # bucket string == chronological), not the max reserved —
                    # matches scraper._previous_reserved_count semantics.
                    prev_reserved = max(prior)[1]
                    normalized["delta_reserved_since_previous"] = str(
                        int(float(normalized.get("reserved_seats", 0) or 0)) - prev_reserved
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


# Which chains this lane COLLECTS (comma-sep env override). Default REGL-only
# since 2026-08-31: Cinemark moved to its own direct lane (cinemark_collect.py,
# independent rate budget, all 306 theatres), so every Fandango seat render
# spent on a CNMK theatre wastes the per-Azure-range budget that is this
# lane's binding constraint. Regal-only roughly doubles Regal depth per slot.
# CNMK theatres stay in theatres-fandango.json and remain collectable via
# FANDANGO_CHAINS=REGL,CNMK for comparisons. NOTE: from this change on, the
# Fandango CSV gains only REGL rows; predict's cross-chain rc side becomes
# Regal-only (Regal already supplied the majority of rows, e.g. 487/782 on
# weekend 2026-08-28, so CROSS_CHAIN_MIN_RC_ROWS stays satisfied).
FANDANGO_CHAINS = frozenset(
    c.strip().upper()
    for c in (os.environ.get("FANDANGO_CHAINS") or "REGL").split(",")
    if c.strip()
)


def load_fandango_theatres(zips=None):
    """Load this lane's chain-filtered theatres from theatres-fandango.json."""
    if not THEATRES_JSON.exists():
        return []
    with open(THEATRES_JSON) as f:
        data = json.load(f)
    out = []
    for th in data.get("theatres", []):
        if th.get("chain", "").upper() not in FANDANGO_CHAINS:
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


def _log_seat_failure(shared, slug, kind, url):
    """Print the first few seat-render failures per run WITH their class.

    2026-09-03: 19 slots, ~700 seat_fails, and not one line saying WHY —
    the counters were silent, so throttle vs block vs selector drift was
    indistinguishable from logs. Capped so a throttled run stays readable."""
    with shared["lock"]:
        n = shared.get("fail_logged", 0)
        if n >= 8:
            return
        shared["fail_logged"] = n + 1
    print(f"   seat-fail[{kind}] {slug} {str(url)[:100]}", flush=True)


def _note_seat_failure(shared):
    """Record a seat-map render failure (throttle/block signal) shared across all
    workers — they hit one IP-level limit. On a sustained stall, open a pause
    window (resume after the limit recovers) rather than hard-stop; only stop
    once the resume budget or the deadline is exhausted. Returns True to stop."""
    with shared["lock"]:
        shared["consec_fail"] += 1
        n = shared["consec_fail"]
        if n >= shared["stop_after"]:
            now = time.monotonic()
            if now < shared["paused_until"]:
                # another worker already opened a pause window — just reset
                shared["consec_fail"] = 0
                return False
            if (shared["resume_count"] < shared["max_resumes"]
                    and now + shared["pause_sec"] < shared["deadline"]):
                shared["paused_until"] = now + shared["pause_sec"]
                shared["resume_count"] += 1
                shared["consec_fail"] = 0
                shared["backoff_extra"] = 0.0
                print(f"   ⏸️  {n} consecutive seat-render failures — throttled; pausing "
                      f"{shared['pause_sec'] / 60:.0f} min then resuming "
                      f"(resume {shared['resume_count']}/{shared['max_resumes']}).")
                return False
            if not shared["stop"].is_set():
                shared["stop"].set()
                print(f"   ⛔ throttled and out of resume budget "
                      f"({shared['resume_count']}/{shared['max_resumes']}) — "
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


def _wait_if_paused(shared):
    """Cooperatively wait out a throttle pause window, then resume. Bounded by the
    run deadline and the stop flag so a pause never overruns the budget."""
    while not shared["stop"].is_set():
        with shared["lock"]:
            paused_until = shared["paused_until"]
        now = time.monotonic()
        if now >= paused_until or now >= shared["deadline"]:
            return
        time.sleep(min(5.0, paused_until - now))


def _capture_theatre(page, th, shared):
    """Render one theatre, capture its tracked-title seat maps. Returns
    (rows, stats). Feeds the shared throttle state so the run backs off / stops
    when the seat-availability backend starts rate-limiting."""
    slug = th.get("slug", "")
    tz_name = th.get("timezone", "")
    stats = {"matched": 0, "renders": 0, "incompletes": 0, "blocks": 0, "seat_fails": 0}
    entries = []
    seen_hrefs = set()
    for page_date in shared.get("page_dates", [None]):
        url = f"https://www.fandango.com/{slug}/theater-page"
        if page_date:
            url += f"?date={page_date}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)
            if looks_blocked(page):
                stats["blocks"] += 1
                print(f"  {slug}: BLOCKED on theater-page"
                      f"{f' date={page_date}' if page_date else ''}")
                return [], stats
            # Merge across dated renders; sdate in each jump href keeps the
            # showtime's own date, so a date param Fandango ignored simply
            # yields entries the window filter drops (loudly zero, not wrong).
            for e in page.evaluate(SHOWTIME_ENTRIES_JS):
                href = e.get("href", "")
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                entries.append(e)
        except Exception as e:
            print(f"  {slug}: theater-page ERROR {str(e)[:80]}")
            if not entries:
                return [], stats
            break

    wanted = select_wanted_showtimes(entries, shared["target_slugs"],
                                     shared["window_dates"], tz_name,
                                     shared["now_utc"], shared["per_theatre_cap"],
                                     order=shared.get("order", "prime"))
    stats["matched"] = len(wanted)
    rows = []
    for w in wanted:
        if shared["stop"].is_set():
            break
        # Hard render budget (shared across workers): spend it and stop
        # cleanly — breadth adapts to film count, the budget never overruns.
        budget = shared.get("render_budget_left")
        if budget is not None:
            with shared["lock"]:
                if shared["render_budget_left"] <= 0:
                    shared["budget_done"].set()
                    break
                shared["render_budget_left"] -= 1
        _wait_if_paused(shared)   # ride out a throttle pause window before resuming
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
                _log_seat_failure(shared, slug, "blocked-page", page.url)
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
        except Exception as exc:
            # seat page loaded but the map never populated ("Loading… 0 seats") —
            # the signature of the seat-availability throttle.
            stats["seat_fails"] += 1
            _log_seat_failure(shared, slug, f"map-never-populated ({type(exc).__name__})",
                              page.url)
            if _note_seat_failure(shared):
                break
            continue
        if not seats or seats.get("total", 0) <= 0:
            stats["seat_fails"] += 1
            _log_seat_failure(shared, slug, "zero-seats", page.url)
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
            note=f"discovered_showtimes={w.get('discovered', '')}",
        ))
    return rows, stats


def _worker(slice_theatres, shared):
    """One browser processing a slice of theatres until the shared deadline.
    Each worker owns its own Playwright instance (the sync API is per-thread)."""
    from playwright.sync_api import sync_playwright

    agg = {"matched": 0, "renders": 0, "incompletes": 0, "blocks": 0,
           "seat_fails": 0, "written": 0, "skipped": 0, "captured": 0, "visited": 0}
    # A worker must never raise: ThreadPoolExecutor.map re-raises on iteration,
    # which would discard the OTHER workers' results and crash collect(). Any
    # browser/launch failure just ends this worker with its partial agg (rows
    # already flushed per-theatre stay safe on disk).
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=shared["headless"], args=CHROMIUM_ARGS)
            ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 1600})
            page = ctx.new_page()
            for th in slice_theatres:
                if (shared["stop"].is_set() or shared["budget_done"].is_set()
                        or time.monotonic() >= shared["deadline"]):
                    break
                _wait_if_paused(shared)   # ride out a throttle pause before the next theatre
                if shared["stop"].is_set() or shared["budget_done"].is_set():
                    break
                if time.monotonic() >= shared["deadline"]:
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
    except Exception as e:
        print(f"  ⚠️  worker aborted ({str(e)[:100]}) — keeping its captured rows")
    return agg


def _egress_ip():
    """Best-effort outbound IP — lets us tell whether parallel GitHub jobs get
    distinct IPs (per-IP rate limit → fan-out works) vs share one (range limit)."""
    try:
        import urllib.request
        return urllib.request.urlopen("https://api.ipify.org", timeout=10).read().decode().strip()
    except Exception:
        return "?"


def shard_theatres(theatres, shard, num_shards):
    """Deterministic, disjoint, geographically-mixed slice for one matrix leg."""
    if not num_shards or num_shards <= 1:
        return theatres
    return list(theatres)[shard % num_shards::num_shards]


def collect(weekend_of=None, titles=None, zips=None, theatres=None,
            per_theatre_cap=None, max_theatres=None, headless=True, run_id=None,
            polite=(1.0, 2.5), concurrency=None, deadline_sec=None, show_dates=None,
            shard=None, num_shards=None):
    """Capture tracked-title Regal/Cinemark seat maps across the national pool
    using N parallel browsers, bounded by a deadline, appending to the isolated
    Fandango file. Returns a totals dict.

    show_dates overrides the opening-weekend window (used for ad-hoc test runs
    that capture an arbitrary date, e.g. validating GitHub seat capture today)."""
    # Mon-Wed anchor FORWARD to the upcoming Friday (early-lead pre-opening
    # reads, mirroring the AMC snapshot lane); Thu-Sun this is
    # opening_weekend_friday. Runner-local time is UTC on GitHub-hosted jobs,
    # matching the UTC slot table.
    ref_now = datetime.now()
    weekend_of = weekend_of or phase1_weekend_anchor(ref_now, full_weekend=True)
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    if not titles:
        # State (showtime-links.json / theatre-counts) only refreshes when
        # Phase 1 runs (Tue-Thu). When a weekend's Polymarket market is listed
        # late — One Night Only 2026-08-07, then Insidious/Mutiny 2026-08-21 —
        # those passes cleanly skip, state stays on the PRIOR weekend, and this
        # lane silently captured nothing on Thursday and Friday (green runs,
        # zero rows), losing the preview-day volume q that the cross-chain
        # share and the family early-window policy depend on. This collector
        # never needed links — it discovers showtimes on Fandango BY TITLE —
        # so fall back to live Polymarket discovery before giving up.
        try:
            from scraper import (fetch_polymarket_box_office,
                                 select_collection_markets, local_now)
            live = select_collection_markets(
                fetch_polymarket_box_office(),
                local_now("ET"),
                "Fandango title fallback",
                weekend_override=weekend_of,
            )
            titles = [m["movie_title"] for m in (live or [])]
            if titles:
                print(f"↷ State had no titles for weekend_of={weekend_of}; "
                      f"live Polymarket discovery found: {', '.join(titles)}")
        except Exception as e:
            print(f"⚠️  Live Polymarket title fallback failed: {e}")
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return {}
    target_slugs = {slugify_title(t): t for t in titles}
    window_dates = set(show_dates) if show_dates else set(opening_weekend_show_dates(weekend_of))
    theatres = theatres if theatres is not None else load_fandango_theatres(zips)
    if not theatres:
        print("⚠️  No Fandango theatres configured (data/theatres-fandango.json).")
        return {}

    num_shards = num_shards if num_shards is not None else FANDANGO_NUM_SHARDS
    shard = shard if shard is not None else FANDANGO_SHARD
    if num_shards and num_shards > 1:
        theatres = shard_theatres(theatres, shard, num_shards)
        print(f"  shard {shard % num_shards}/{num_shards}: {len(theatres)} theatres of the pool")

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

    page_dates = page_visit_dates(window_dates, show_dates, ref_now)
    print(f"Fandango collect • egress_ip={_egress_ip()} • weekend_of={weekend_of} "
          f"• {len(theatres)} theatres • {concurrency} workers "
          f"• cap={per_theatre_cap}/theatre • deadline={deadline_sec}s "
          f"• titles={list(target_slugs.values())}"
          + (f" • dated theater-page visits: {page_dates}"
             if page_dates != [None] else ""))

    shared = {
        "target_slugs": target_slugs, "window_dates": window_dates,
        "page_dates": page_dates,
        "order": FANDANGO_ORDER,
        "now_utc": now_utc, "weekend_of": weekend_of, "run_id": run_id,
        "check_time": check_time, "per_theatre_cap": per_theatre_cap,
        "polite": polite, "headless": headless,
        "deadline": time.monotonic() + deadline_sec, "lock": threading.Lock(),
        "render_budget_left": FANDANGO_RENDER_BUDGET or None,
        "budget_done": threading.Event(),
        # adaptive throttle state, shared across workers (one IP-level limit)
        "stop": threading.Event(), "consec_fail": 0, "backoff_extra": 0.0,
        "backoff_after": FANDANGO_BACKOFF_AFTER, "stop_after": FANDANGO_STOP_AFTER,
        "backoff_step": float(FANDANGO_BACKOFF_STEP_SEC),
        "backoff_max": float(FANDANGO_BACKOFF_MAX_SEC),
        # pause/resume: ride out the transient throttle instead of hard-stopping
        "paused_until": 0.0, "resume_count": 0,
        "max_resumes": FANDANGO_MAX_RESUMES, "pause_sec": float(FANDANGO_PAUSE_SEC),
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
    totals["pauses"] = shared["resume_count"]
    totals["dated_visits"] = page_dates != [None]

    print("\n=== Fandango collect summary ===")
    print(f"  pool={len(theatres)} visited={totals['visited']}"
          f"{' (STOPPED EARLY — throttled)' if totals['throttled_stop'] else ''} "
          f"matched_showtimes={totals['matched']} renders={totals['renders']}")
    print(f"  captured={totals['captured']} written={totals['written']} "
          f"deduped={totals['skipped']} incomplete_dropped={totals['incompletes']} "
          f"seat_fails={totals['seat_fails']} blocks={totals['blocks']} "
          f"throttle_pauses={totals['pauses']}")
    print(f"  -> {FANDANGO_CSV}")
    return totals


# ── Offline self-test ────────────────────────────────────────────────────────

def _selftest():
    assert slugify_title("Toy Story 5") == "toy-story-5"
    # '&' must become 'and' to match Fandango's slug (regression: 2026-07-03,
    # 'Minions & Monsters' was silently dropped when '&' was stripped instead)
    assert slugify_title("Star Wars: The Mandalorian & Grogu") == "star-wars-the-mandalorian-and-grogu"
    assert slugify_title("Minions & Monsters") == "minions-and-monsters"
    assert match_target_title(
        "/minions-and-monsters-2026-241234/movie-overview",
        {slugify_title("Minions & Monsters"): "Minions & Monsters"},
    ) == "Minions & Monsters"

    assert overview_core_slug("/toy-story-5-2026-243393/movie-overview") == "toy-story-5"
    assert overview_core_slug("https://www.fandango.com/backrooms-2026-244954/movie-overview") == "backrooms"
    # Bare-id slug (no year segment) — the shape that dropped 'Coyote vs. Acme'.
    assert overview_core_slug("/coyote-vs-acme-246329/movie-overview") == "coyote-vs-acme"
    assert match_target_title(
        "/coyote-vs-acme-246329/movie-overview",
        {slugify_title("Coyote vs. Acme"): "Coyote vs. Acme"},
    ) == "Coyote vs. Acme"
    # Title ending in a 4-digit number + bare id: primary strip over-consumes
    # ('blade-runner'), the bare-id candidate must still land the exact match.
    assert match_target_title(
        "/blade-runner-2049-246329/movie-overview",
        {slugify_title("Blade Runner 2049"): "Blade Runner 2049"},
    ) == "Blade Runner 2049"
    # Year-form slugs must keep matching exactly as before.
    assert match_target_title(
        "/coyote-vs-acme-2026-246329/movie-overview",
        {slugify_title("Coyote vs. Acme"): "Coyote vs. Acme"},
    ) == "Coyote vs. Acme"

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

    # page_visit_dates: explicit show_dates always render dated pages; Mon-Wed
    # pre-opening renders every window date; Thu-Sun keeps the dateless visit.
    window = {"2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06"}
    assert page_visit_dates(window, ["2026-08-30"], datetime(2026, 8, 28)) == ["2026-08-30"]
    for day in (8, 31), (9, 1), (9, 2):  # Mon/Tue/Wed
        got = page_visit_dates(window, None, datetime(2026, *day))
        assert got == sorted(window), (day, got)
    # UTC Thursday before 09Z is Wednesday evening at every US theatre — the
    # overnight 03-08Z slots must render dated pages or they read ~nothing.
    for hour in (3, 8):
        got = page_visit_dates(window, None, datetime(2026, 9, 3, hour))
        assert got == sorted(window), (hour, got)
    # From 09Z Thursday the local pages have rolled to Thursday: dateless.
    for args in ((2026, 9, 3, 9), (2026, 9, 3, 16), (2026, 9, 4, 3),
                 (2026, 9, 5, 3), (2026, 9, 6, 12)):  # Thu 09Z+, Fri-Sun
        assert page_visit_dates(window, None, datetime(*args)) == [None], args

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
    ap.add_argument("--titles", nargs="*", help="override tracked titles (or env FANDANGO_TITLES, comma-sep)")
    ap.add_argument("--show-dates", nargs="*",
                    help="override the opening-weekend window with these YYYY-MM-DD dates "
                         "(or env FANDANGO_SHOW_DATES, comma-sep) — for ad-hoc test runs")
    ap.add_argument("--zips", nargs="*", help="restrict to theatres in these zips")
    ap.add_argument("--max-theatres", type=int, default=FANDANGO_MAX_THEATRES,
                    help="cap theatres visited this run (0 = whole pool)")
    ap.add_argument("--per-theatre-cap", type=int, default=FANDANGO_PER_THEATRE_CAP,
                    help="showtimes captured per theatre (prime-time first)")
    ap.add_argument("--concurrency", type=int, default=FANDANGO_CONCURRENCY,
                    help="parallel browsers")
    ap.add_argument("--deadline-sec", type=int, default=FANDANGO_DEADLINE_SEC,
                    help="stop launching new theatres after this many seconds")
    ap.add_argument("--shard", type=int, default=FANDANGO_SHARD, help="this leg's shard index")
    ap.add_argument("--num-shards", type=int, default=FANDANGO_NUM_SHARDS,
                    help="total shards (0/1 = whole pool)")
    ap.add_argument("--no-headless", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return

    # Env fallbacks let the workflow pass overrides without building a CLI string.
    def _csv_env(name):
        raw = (os.environ.get(name) or "").strip()
        return [p.strip() for p in raw.split(",") if p.strip()] or None

    titles = args.titles or _csv_env("FANDANGO_TITLES")
    show_dates = args.show_dates or _csv_env("FANDANGO_SHOW_DATES")
    zips = args.zips or _csv_env("FANDANGO_ZIPS")
    # FANDANGO_OUTPUT redirects writes to a throwaway path so an ad-hoc test run
    # never pollutes the canonical data/fandango-pre-reservation-snapshots.csv.
    out_override = (os.environ.get("FANDANGO_OUTPUT") or "").strip()
    if out_override:
        global FANDANGO_CSV
        FANDANGO_CSV = Path(out_override)

    totals = collect(weekend_of=args.weekend, titles=titles, zips=zips,
                     per_theatre_cap=args.per_theatre_cap, max_theatres=args.max_theatres,
                     concurrency=args.concurrency, deadline_sec=args.deadline_sec,
                     show_dates=show_dates, shard=args.shard, num_shards=args.num_shards,
                     headless=not args.no_headless)
    # OUTPUT FLOOR (soft-fail audit 2026-08-23). main() used to discard the
    # totals, so a run that resolved titles and then wrote NOTHING — throttle
    # hard-stop, all theatres blocked, seat-map DOM drift — exited 0 and was
    # indistinguishable from success; the 2026-08-21 lane went green-zero for
    # two days that way. A GENUINELY quiet weekend (no titles from state or
    # live discovery) stays a green skip: collect() returns {} then, and
    # exiting red on quiet weekends would re-create the failed-slot alarm
    # noise the clean-skip work removed. Titles present + zero rows = red, so
    # the scheduler retries and the circuit breaker escalates.
    if totals and totals.get("written", 0) == 0:
        # Pre-opening exception: on dated early-lead visits (Mon-Wed and the
        # Wednesday-night 03-08Z slots), zero MATCHED showtimes with zero
        # blocks means the chains simply have not posted the weekend schedule
        # yet — there is nothing to capture, and now that the workflow step
        # propagates this exit code (PIPESTATUS fix), exiting red here would
        # burn the slot's 3 retries and trip the circuit breaker every early
        # week. matched > 0 with zero rows written, or any block, is still a
        # real failure and stays red.
        if (totals.get("dated_visits")
                and totals.get("matched", 0) == 0
                and totals.get("blocks", 0) == 0):
            print("\u21b7 Pre-opening dated visits found no matching showtimes "
                  "yet (schedule not posted) — nothing to capture (clean skip).")
            return
        print("\u274c Titles were tracked but zero Fandango rows were written "
              "— failing loudly instead of green-zero.")
        sys.exit(1)


if __name__ == "__main__":
    main()
