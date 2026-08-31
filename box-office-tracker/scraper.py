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
import time
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
import uuid

import requests
from playwright.async_api import async_playwright

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SEAT_CSV = DATA_DIR / "seat-counts.csv"
PRE_RESERVATION_CSV = DATA_DIR / "pre-reservation-snapshots.csv"
POLY_CSV = DATA_DIR / "polymarket-markets.csv"
RUN_LOG  = DATA_DIR / "run-log.md"
RUN_LOG_DIR = DATA_DIR / "run-logs"

THEATRES_JSON    = DATA_DIR / "theatres-all.json"
THEATRES_EXPANSION_JSON = DATA_DIR / "theatres-expansion.json"
LINKS_JSON       = DATA_DIR / "showtime-links.json"   # Phase 1 output / Phase 2 input
THEATRE_COUNTS_JSON = DATA_DIR / "theatre-counts.json"  # National theatre counts from BOM
MOVIE_METADATA_CSV = DATA_DIR / "movie-metadata.csv"  # Hand-maintained audience metadata


CORE_COHORT = "core"
EXPANSION_COHORT = "expansion"
DEFAULT_COLLECTION_COHORTS = (CORE_COHORT, EXPANSION_COHORT)
KNOWN_THEATRE_COHORTS = set(DEFAULT_COLLECTION_COHORTS)
REQUIRED_PHASE1_COHORTS = (CORE_COHORT,)


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default, minimum=None):
    raw = os.getenv(name)
    if raw is None:
        value = default
    else:
        try:
            value = int(raw)
        except ValueError:
            value = default
    if minimum is not None:
        value = max(minimum, value)
    return value


def _env_float(name, default, minimum=None):
    raw = os.getenv(name)
    if raw is None:
        value = default
    else:
        try:
            value = float(raw)
        except ValueError:
            value = default
    if minimum is not None:
        value = max(minimum, value)
    return value


def _parse_cohorts(value, default):
    raw = value if value is not None else ",".join(default)
    cohorts = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not cohorts or "all" in cohorts or "*" in cohorts:
        return set(default)
    selected = set(cohorts) & KNOWN_THEATRE_COHORTS
    return selected or set(default)


def _theatre_cohort(theatre):
    return (theatre.get("cohort") or CORE_COHORT).strip().lower()


def _copy_theatre(theatre, cohort):
    copied = dict(theatre)
    copied["cohort"] = (copied.get("cohort") or cohort).strip().lower()
    return copied


def is_amc_classic_theatre(theatre):
    name = str(theatre.get("name") or "").strip().lower()
    slug = str(theatre.get("slug") or "").strip().lower()
    return name.startswith("amc classic ") or slug.startswith("amc-classic-")


def _merge_theatre_group(target, group, theatres, default_cohort, allowed_cohorts):
    target.setdefault(group, [])
    existing_names = {
        t["name"]
        for group_theatres in target.values()
        for t in group_theatres
        if t.get("name")
    }
    for theatre in theatres:
        if not theatre.get("name") or not theatre.get("slug"):
            continue
        if is_amc_classic_theatre(theatre):
            continue
        copied = _copy_theatre(theatre, default_cohort)
        if _theatre_cohort(copied) not in allowed_cohorts:
            continue
        # Names are the durable key in showtime-links.json; never let an
        # expansion theatre shadow a core theatre with the same display name.
        if copied["name"] in existing_names:
            continue
        target[group].append(copied)
        existing_names.add(copied["name"])


def load_theatres(cohorts=None):
    """Load the theatre universe.

    The historical list is the core cohort. theatres-expansion.json is collected
    after core theatres so runtime pressure leaves the original sample intact;
    prediction normalizes the active sample back to its calibration reference.
    """
    allowed_cohorts = _parse_cohorts(
        cohorts if cohorts is not None else os.getenv("THEATRE_COLLECTION_COHORTS"),
        DEFAULT_COLLECTION_COHORTS,
    )

    if THEATRES_JSON.exists():
        with open(THEATRES_JSON, "r") as f:
            data = json.load(f)
        theatres = {}
        for group, group_theatres in data.items():
            if group.startswith("_"):
                continue
            theatres[group] = []
            _merge_theatre_group(
                theatres, group, group_theatres,
                default_cohort=CORE_COHORT,
                allowed_cohorts=allowed_cohorts,
            )
        if THEATRES_EXPANSION_JSON.exists():
            with open(THEATRES_EXPANSION_JSON, "r") as f:
                expansion = json.load(f)
            for group, group_theatres in expansion.items():
                if group.startswith("_"):
                    continue
                _merge_theatre_group(
                    theatres, group, group_theatres,
                    default_cohort=EXPANSION_COHORT,
                    allowed_cohorts=allowed_cohorts,
                )
        return theatres
    # Fallback: minimal set if JSON is missing
    return {
        "ET": [{"name": "AMC Empire 25", "slug": "amc-empire-25", "cohort": CORE_COHORT}],
        "CT": [{"name": "AMC River East 21", "slug": "amc-river-east-21", "cohort": CORE_COHORT}],
        "MT": [{"name": "AMC Westminster 24", "slug": "amc-westminster-24", "cohort": CORE_COHORT}],
        "PT": [{"name": "AMC The Grove 14", "slug": "amc-the-grove-14", "cohort": CORE_COHORT}],
    }


def _theatre_sort_key(theatre):
    # Core first. Expansion is best-effort and should be the first work dropped
    # if a Phase 1/2 deadline is approaching.
    return (
        1 if _theatre_cohort(theatre) == EXPANSION_COHORT else 0,
        theatre.get("dma", ""),
        theatre.get("name", ""),
    )


def _cohort_counts(theatres):
    counts = {}
    for theatre in theatres:
        cohort = _theatre_cohort(theatre)
        counts[cohort] = counts.get(cohort, 0) + 1
    return counts


def _parse_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def snapshot_theatre_signal_scores(seat_csv_path=SEAT_CSV):
    """Rank theatres by historical box-office signal in collected seat data.

    This is used only to shrink pre-reservation snapshot volume. The regular
    model-driving scrape still uses the full configured theatre universe.
    """
    scores = {}
    sample_keys = {}
    if not seat_csv_path.exists():
        return scores
    try:
        with open(seat_csv_path, newline="") as f:
            for row in csv.DictReader(f):
                theatre = (row.get("theatre_name") or "").strip()
                if not theatre:
                    continue
                seats_sold = _parse_float(row.get("seats_sold"), 0.0)
                total_seats = _parse_float(row.get("total_seats"), 0.0)
                if seats_sold < 0 or total_seats <= 0:
                    continue
                # Sold seats capture realized demand; capacity keeps large,
                # nationally useful venues from being over-penalized on quiet
                # titles. Distinct movie/day samples reward reliable theatres.
                scores[theatre] = scores.get(theatre, 0.0) + seats_sold + total_seats * 0.03
                sample_key = (
                    row.get("weekend_of", ""),
                    row.get("movie_title", ""),
                    row.get("date", "") or row.get("show_date", ""),
                )
                if any(sample_key):
                    sample_keys.setdefault(theatre, set()).add(sample_key)
    except OSError:
        return scores

    for theatre, keys in sample_keys.items():
        scores[theatre] = scores.get(theatre, 0.0) + len(keys) * 5.0
    return scores


def snapshot_demand_scores(pre_reservation_csv_path=None):
    """Per-theatre demand velocity from the latest pre-reservation readings.

    For the most recent weekend in the snapshots CSV, take each showtime's
    LATEST bucket reading and average occupancy per theatre. Theatres filling
    fastest carry the most information about demand censoring (sellouts), so
    the snapshot cap should prefer them. Returns {theatre_name: 0..1}.
    """
    path = pre_reservation_csv_path or PRE_RESERVATION_CSV
    if not Path(path).exists():
        return {}
    latest = {}
    max_weekend = ""
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                weekend = row.get("weekend_of", "") or ""
                if weekend > max_weekend:
                    max_weekend = weekend
                try:
                    total = float(row.get("total_seats") or 0)
                    reserved = float(row.get("reserved_seats") or 0)
                except (TypeError, ValueError):
                    continue
                if total <= 0:
                    continue
                key = (
                    weekend,
                    row.get("theatre_name", ""),
                    row.get("showtime_id", "") or row.get("showtime", ""),
                    row.get("show_date", ""),
                )
                bucket = str(row.get("snapshot_bucket", "") or "")
                prev = latest.get(key)
                if prev is None or bucket > prev[0]:
                    latest[key] = (bucket, reserved / total)
    except OSError:
        return {}
    sums = {}
    counts = {}
    for (weekend, theatre, _sid, _date), (_bucket, occ) in latest.items():
        if weekend != max_weekend or not theatre:
            continue
        sums[theatre] = sums.get(theatre, 0.0) + occ
        counts[theatre] = counts.get(theatre, 0) + 1
    return {t: sums[t] / counts[t] for t in sums if counts[t] > 0}


STRATEGIC_PHASE2_THEATRES = {
    "AMC Empire 25",
    "AMC Lincoln Square 13",
    "AMC Kips Bay 15",
    "AMC Magic Johnson Harlem 9",
    "AMC Newport Centre 11",
    "AMC DINE-IN Disney Springs 24",
    "AMC Altamonte Mall 18",
    "AMC Cherry Hill 24",
    "AMC DINE-IN Fashion District 8",
    "AMC Neshaminy 24",
    "AMC Plymouth Meeting Mall 12",
    "AMC Waterfront 22",
    "AMC Georgetown 14",
    "AMC Hoffman Center 22",
    "AMC Shirlington 7",
    "AMC Tysons Corner 16",
    "AMC Veterans 24",
    "AMC West Shore 14",
}


def regular_phase2_theatre_sort_key(theatre, signal_scores=None):
    signal_scores = signal_scores or {}
    name = theatre.get("name", "")
    return (
        1 if _theatre_cohort(theatre) == EXPANSION_COHORT else 0,
        -1 if name in STRATEGIC_PHASE2_THEATRES else 0,
        -signal_scores.get(name, 0.0),
        theatre.get("dma", ""),
        name,
    )


def _snapshot_cap_allocations(theatres_by_group, cap):
    groups = [group for group, rows in theatres_by_group.items() if rows]
    group_order = {group: index for index, group in enumerate(groups)}
    total = sum(len(theatres_by_group[group]) for group in groups)
    cap = max(0, min(int(cap or 0), total))
    if not groups or cap <= 0:
        return {group: 0 for group in theatres_by_group}
    if cap >= total:
        return {group: len(theatres_by_group.get(group, [])) for group in theatres_by_group}

    raw = {
        group: cap * (len(theatres_by_group[group]) / total)
        for group in groups
    }
    allocations = {
        group: min(len(theatres_by_group[group]), int(raw[group]))
        for group in groups
    }
    if cap >= len(groups):
        for group in groups:
            if allocations[group] == 0:
                allocations[group] = 1

    def allocated_total():
        return sum(allocations.values())

    while allocated_total() > cap:
        candidates = [
            group for group in groups
            if allocations[group] > (1 if cap >= len(groups) else 0)
        ]
        if not candidates:
            break
        group = min(candidates, key=lambda g: (raw[g] - int(raw[g]), allocations[g], g))
        allocations[group] -= 1

    while allocated_total() < cap:
        candidates = [
            group for group in groups
            if allocations[group] < len(theatres_by_group[group])
        ]
        if not candidates:
            break
        group = max(
            candidates,
            key=lambda g: (
                raw[g] - int(raw[g]),
                len(theatres_by_group[g]),
                -group_order.get(g, 0),
            ),
        )
        allocations[group] += 1

    return {group: allocations.get(group, 0) for group in theatres_by_group}


def _snapshot_link_availability(theatre, group, saved_links, requested_date_sets, movie_titles):
    if saved_links is None or requested_date_sets is None or not movie_titles:
        return 0
    entry = saved_links.get(theatre.get("name", ""))
    if not entry:
        return 0
    available_movie_dates = 0
    for date_str in requested_date_sets.get(group, []):
        movies = phase1_entry_movies(entry, date_str)
        available_movie_dates += sum(1 for title in movie_titles if movies.get(title))
    return available_movie_dates


def select_snapshot_theatre_names(theatres_map, groups=None, cap=None, signal_scores=None,
                                  saved_links=None, requested_date_sets=None,
                                  movie_titles=None):
    """Select a timezone-balanced top theatre set for snapshot-only probes."""
    cap = SNAPSHOT_TOP_THEATRE_CAP if cap is None else cap
    if cap <= 0:
        return set()
    groups = list(groups or [g for g in ("ET", "CT", "PT") if g in theatres_map])
    movie_titles = list(movie_titles or [])
    require_links = saved_links is not None and requested_date_sets is not None and movie_titles
    theatres_by_group = {}
    availability_by_name = {}
    dropped_by_group = {}
    for group in groups:
        rows = []
        dropped = 0
        for theatre in theatres_map.get(group, []):
            availability = _snapshot_link_availability(
                theatre,
                group,
                saved_links,
                requested_date_sets,
                movie_titles,
            )
            if require_links and availability <= 0:
                dropped += 1
                continue
            availability_by_name[theatre.get("name", "")] = availability
            rows.append(theatre)
        if dropped:
            dropped_by_group[group] = dropped
        if rows:
            theatres_by_group[group] = rows
    if require_links and dropped_by_group:
        # Surface silently-excluded theatres so a shrunken snapshot sample is
        # visible rather than masquerading as full coverage.
        summary = ", ".join(f"{g}:{n}" for g, n in sorted(dropped_by_group.items()))
        print(
            f"   ⚠️  Snapshot selection dropped {sum(dropped_by_group.values())} theatre(s) "
            f"with no current Phase 1 links ({summary})"
        )
        # DENOMINATOR-SHRINK GUARD (soft-fail audit finding 5): every later
        # coverage percentage is measured against the link-having pool, so a
        # links-starved weekend can read "48/50 = 96% coverage" while the
        # real fleet is 200+. When the drop halves the pool or worse, say so
        # loudly — the percentages that follow are honest fractions of a
        # dishonest base.
        total_dropped = sum(dropped_by_group.values())
        total_kept = sum(len(v) for v in theatres_by_group.values())
        if total_kept and total_dropped >= total_kept:
            print(f"::warning::snapshot theatre pool halved or worse by missing "
                  f"Phase 1 links ({total_dropped} dropped vs {total_kept} kept) — "
                  f"coverage percentages this run are fractions of the SHRUNKEN "
                  f"pool, not the fleet")
    if not theatres_by_group:
        return set()
    signal_scores = signal_scores if signal_scores is not None else snapshot_theatre_signal_scores()
    # Demand velocity from this weekend's latest snapshot readings: theatres
    # filling fastest carry the most sellout/demand-censoring information, so
    # they win the cap ahead of equally-available, equally-signalled peers.
    demand_scores = snapshot_demand_scores()
    allocations = _snapshot_cap_allocations(theatres_by_group, cap)
    selected = set()
    for group in groups:
        rows = theatres_by_group.get(group, [])
        limit = allocations.get(group, 0)
        ranked = sorted(
            rows,
            key=lambda theatre: (
                -availability_by_name.get(theatre.get("name", ""), 0),
                -round(demand_scores.get(theatre.get("name", ""), 0.0), 2),
                -signal_scores.get(theatre.get("name", ""), 0.0),
                _theatre_sort_key(theatre),
            ),
        )
        selected.update(theatre["name"] for theatre in ranked[:limit] if theatre.get("name"))
    return selected


def filter_theatres_map_by_names(theatres_map, theatre_names):
    names = set(theatre_names or [])
    if not names:
        return {group: [] for group in theatres_map}
    return {
        group: [theatre for theatre in theatres if theatre.get("name") in names]
        for group, theatres in theatres_map.items()
    }


def filter_saved_links_by_names(saved_links, theatre_names):
    names = set(theatre_names or [])
    if not names:
        return {}
    return {
        name: entry
        for name, entry in (saved_links or {}).items()
        if name in names
    }


def build_phase2_theatre_work(theatres_map, groups_to_check, collection_dates_by_group,
                              snapshots_only=False, snapshot_theatre_names=None):
    """Expand theatres into Phase 2 theatre/date work items."""
    selected_names = set(snapshot_theatre_names or [])
    all_theatres = []
    for group in groups_to_check:
        for date_str in collection_dates_by_group.get(group, [local_date_str(group)]):
            for theatre in theatres_map.get(group, []):
                if (
                    snapshots_only
                    and snapshot_theatre_names is not None
                    and theatre.get("name") not in selected_names
                ):
                    continue
                all_theatres.append({
                    **theatre,
                    "_tz": group,
                    "_date": date_str,
                    "_phase2_expected_date": date_str if snapshots_only else "",
                })
    return order_phase2_theatres_for_collection(
        all_theatres,
        snapshots_only=snapshots_only,
    )


def snapshot_global_selection_inputs(theatres_map):
    """Return the global TZ/date universe used to cap snapshot theatres.

    Snapshot jobs run as serialized ET/CT/PT matrix legs, but the theatre cap is
    a global capacity budget. Build the top-theatre set against all enabled
    timezone groups so a single leg cannot expand the cap to 100 theatres by
    itself.
    """
    groups = [group for group in ("ET", "CT", "PT") if group in (theatres_map or {})]
    return groups, phase2_collection_dates_by_group(groups, snapshots_only=True)


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
WEEKEND_FULL_DAY_START_HOUR = 10
DEFAULT_COLLECTION_START_HOUR = 17
COLLECTION_END_HOUR = 23
SHOWTIME_WINDOW_VERSION = "sat-sun-10-23-v1"
SHOWTIME_WINDOW_NOTE = f"showtime_window={SHOWTIME_WINDOW_VERSION}"

# Concurrency — 3 tabs on the 2GB VPS (Chromium base ~150MB + 3×75MB = ~375MB, well within limits).
MAX_CONCURRENT_TABS = 3
MAX_CONCURRENT_TABS_PHASE1 = 2
SNAPSHOT_MAX_CONCURRENT_TABS = 1


def add_showtime_window_note(note):
    """Tag scraped rows with the Phase 1 showtime-window contract used."""
    note = str(note or "").strip()
    if SHOWTIME_WINDOW_NOTE in note:
        return note
    return f"{note}; {SHOWTIME_WINDOW_NOTE}" if note else SHOWTIME_WINDOW_NOTE


def phase2_max_concurrent_tabs(snapshots_only=False):
    if snapshots_only:
        return _env_int(
            "SNAPSHOT_MAX_CONCURRENT_TABS",
            SNAPSHOT_MAX_CONCURRENT_TABS,
            minimum=1,
        )
    return _env_int("SCRAPER_MAX_CONCURRENT_TABS", MAX_CONCURRENT_TABS, minimum=1)

# Runtime guards. A single hung Playwright navigation (typically caused
# by AMC's Queue-It safety net redirecting the VPS IP) used to stall the whole
# scrape for hours. The per-theatre timeout caps each tab; the overall deadline
# stops launching new theatres early enough for in-flight work and artifact
# upload/finalize. Snapshot-only runs can raise PHASE2_DEADLINE_SEC from the
# workflow because they cover multiple weekend show dates; regular runs keep a
# short theatre cap so one slow location cannot consume the full-day budget.
PHASE1_THEATRE_TIMEOUT_SEC = 90
PHASE2_THEATRE_TIMEOUT_SEC = _env_int("PHASE2_THEATRE_TIMEOUT_SEC", 180, minimum=60)
try:
    PHASE1_DEADLINE_SEC = int(os.getenv("PHASE1_DEADLINE_SEC", str(45 * 60)))
except ValueError:
    PHASE1_DEADLINE_SEC = 45 * 60
PHASE2_DEADLINE_SEC = _env_int("PHASE2_DEADLINE_SEC", 60 * 60, minimum=60)
REGULAR_PHASE2_MIN_DEADLINE_SEC = _env_int("REGULAR_PHASE2_MIN_DEADLINE_SEC", 9000, minimum=60)
REGULAR_PHASE2_MAX_DEADLINE_SEC = _env_int(
    "REGULAR_PHASE2_MAX_DEADLINE_SEC",
    10800,
    minimum=REGULAR_PHASE2_MIN_DEADLINE_SEC,
)
REGULAR_PHASE2_BASE_DEADLINE_SEC = _env_int("REGULAR_PHASE2_BASE_DEADLINE_SEC", 1800, minimum=60)
REGULAR_PHASE2_PER_THEATRE_SEC = _env_float("REGULAR_PHASE2_PER_THEATRE_SEC", 9.0, minimum=0.0)
REGULAR_PHASE2_PER_SHOWTIME_SEC = _env_float("REGULAR_PHASE2_PER_SHOWTIME_SEC", 10.0, minimum=0.0)
REGULAR_PHASE2_MIN_COVERAGE_RATIO = _env_float("REGULAR_PHASE2_MIN_COVERAGE_RATIO", 0.90, minimum=0.0)
# Below this fresh-link ratio a partial Phase 1 cache is too sparse to trust
# for a regular scrape (a Queue-It wall profile, not a thin night); between
# this floor and PHASE1_MIN_FRESH_LINK_RATIO the leg proceeds LOUDLY on the
# smaller panel — post-showtime seat reads are unrecoverable, so an ~88%%
# panel beats the 0%% a hard fail used to leave.
REGULAR_PHASE2_PARTIAL_LINK_FLOOR = _env_float("REGULAR_PHASE2_PARTIAL_LINK_FLOOR", 0.50, minimum=0.0)
try:
    PHASE1_MIN_FRESH_LINK_RATIO = float(os.getenv("PHASE1_MIN_FRESH_LINK_RATIO", "0.80"))
except ValueError:
    PHASE1_MIN_FRESH_LINK_RATIO = 0.80
PHASE1_MIN_MOVIE_LINK_THEATRES = _env_int("PHASE1_MIN_MOVIE_LINK_THEATRES", 1, minimum=1)
try:
    SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO = float(os.getenv("SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO", "0.80"))
except ValueError:
    SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO = 0.80
# Below the MIN ratio (0.80) we still commit a partial snapshot with a warning so
# the model can weight it by coverage. Below this FATAL floor the capture is so
# sparse (e.g. a handful of theatres) that recording it as real data would be
# misleading, so the snapshot fails instead. The default (0.25) only catches
# truly-degenerate captures and preserves the established "partial-but-real"
# commit behaviour; raise it via the env var to be stricter.
try:
    SNAPSHOT_FATAL_COVERAGE_RATIO = float(os.getenv("SNAPSHOT_FATAL_COVERAGE_RATIO", "0.25"))
except ValueError:
    SNAPSHOT_FATAL_COVERAGE_RATIO = 0.25
PHASE1_FULL_WEEKEND_LINKS = _env_bool("PHASE1_FULL_WEEKEND_LINKS", True)
try:
    PHASE1_MAX_THEATRE_DATE_VISITS = int(os.getenv("PHASE1_MAX_THEATRE_DATE_VISITS", "2000"))
except ValueError:
    PHASE1_MAX_THEATRE_DATE_VISITS = 2000
try:
    PRE_RESERVATION_BUCKET_MINUTES = int(os.getenv("PRE_RESERVATION_BUCKET_MINUTES", "60"))
except ValueError:
    PRE_RESERVATION_BUCKET_MINUTES = 60
ENABLE_PRERESERVATION_SNAPSHOTS = _env_bool("ENABLE_PRERESERVATION_SNAPSHOTS", False)
SNAPSHOT_REPAIR_LINKS = _env_bool("SNAPSHOT_REPAIR_LINKS", False)
# 200 theatres ≈ 2x the sellout/demand-velocity sample at ~1.6s/row measured
# throughput; per-TZ legs stay within the (raised) snapshot deadline, and the
# demand-first ordering degrades gracefully if a heavy Wednesday probe runs long.
SNAPSHOT_TOP_THEATRE_CAP = _env_int("SNAPSHOT_TOP_THEATRE_CAP", 200, minimum=1)
SNAPSHOT_SAME_DAY_CUTOFF_HOUR = _env_int("SNAPSHOT_SAME_DAY_CUTOFF_HOUR", 6, minimum=0)

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


def phase2_expected_dates(groups, snapshots_only=False):
    """Return the Phase 1 show dates required by this Phase 2 mode."""
    if snapshots_only:
        expected = {}
        for group in groups:
            dates = phase2_snapshot_collection_dates(local_now(group))
            if dates:
                expected[group] = dates[0]
        return expected
    return {group: phase1_expected_date(group) for group in groups}


def phase2_snapshot_collection_dates(local):
    """Return show dates a snapshot-only Phase 2 should probe.

    Snapshot probes cover the remaining opening weekend. Runtime is controlled
    by selecting only the top historical-signal theatres rather than truncating
    the future-day window.
    """
    if local.weekday() in (0, 1, 2):  # Mon-Wed pre-opening (early-lead reads)
        weekend = phase1_weekend_anchor(local, full_weekend=True)
        start = local + timedelta(days=1)
    else:  # Thu-Sun opening weekend
        weekend = opening_weekend_friday(local)
        # A delayed 02:30Z snapshot can cross midnight in ET while the full
        # show day is still ahead. Keep that current local show date until the
        # early-morning cutoff instead of silently losing the Friday/Sunday read.
        start = local if local.hour < SNAPSHOT_SAME_DAY_CUTOFF_HOUR else local + timedelta(days=1)

    start_date = start.strftime("%Y-%m-%d")
    end_date = opening_weekend_show_dates(weekend)[-1]
    dates = [
        date_str
        for date_str in opening_weekend_show_dates(weekend)
        if start_date <= date_str <= end_date
    ]
    if dates:
        return dates
    return []


def phase2_collection_dates_by_group(groups, snapshots_only=False):
    """Return all show dates Phase 2 should visit for each timezone group."""
    if snapshots_only:
        return {
            group: phase2_snapshot_collection_dates(local_now(group))
            for group in groups
        }
    return {group: [phase1_expected_date(group)] for group in groups}


def order_phase2_theatres_for_collection(theatres, snapshots_only=False, signal_scores=None):
    """Order Phase 2 work so deadline pressure leaves representative coverage."""
    if not snapshots_only:
        if signal_scores is None:
            signal_scores = snapshot_theatre_signal_scores()
        return sorted(theatres, key=lambda theatre: regular_phase2_theatre_sort_key(
            theatre,
            signal_scores=signal_scores,
        ))

    ordered = []
    cohort_order = {CORE_COHORT: 0, EXPANSION_COHORT: 1}
    grouped = {}
    for theatre in theatres:
        key = (
            cohort_order.get(_theatre_cohort(theatre), 99),
            _theatre_cohort(theatre),
            theatre.get("_tz", ""),
        )
        grouped.setdefault(key, []).append(theatre)

    for key in sorted(grouped):
        rows = grouped[key]
        dates = sorted({row.get("_date", "") for row in rows if row.get("_date")})
        if not dates:
            ordered.extend(sorted(rows, key=_theatre_sort_key))
            continue

        by_date = {}
        for index, date_str in enumerate(dates):
            date_rows = sorted(
                [row for row in rows if row.get("_date") == date_str],
                key=_theatre_sort_key,
            )
            if date_rows:
                offset = index % len(date_rows)
                date_rows = date_rows[offset:] + date_rows[:offset]
            by_date[date_str] = date_rows

        max_len = max((len(date_rows) for date_rows in by_date.values()), default=0)
        for row_index in range(max_len):
            for date_str in dates:
                date_rows = by_date[date_str]
                if row_index < len(date_rows):
                    ordered.append(date_rows[row_index])

    return ordered


def snapshot_theatre_coverage(expected_theatres, snapshot_rows):
    """Measure snapshot breadth by show-date/timezone theatre coverage.

    Snapshot rows are showtime-level, so row count alone can be misleading: a
    few busy theatres can produce more rows than a broad but sparse sample. The
    coverage contract for snapshot-only runs is theatre-date breadth.
    """
    expected_by_slice = {}
    for theatre in expected_theatres:
        date_str = theatre.get("_date", "")
        tz = theatre.get("_tz", "")
        name = theatre.get("name", "")
        if not date_str or not tz or not name:
            continue
        expected_by_slice.setdefault((date_str, tz), set()).add(name)

    observed_by_slice = {key: set() for key in expected_by_slice}
    for row in snapshot_rows:
        date_str = str(row.get("show_date", "") or "")
        tz = str(row.get("timezone", "") or "")
        name = str(row.get("theatre_name", "") or "")
        key = (date_str, tz)
        if key in observed_by_slice and name:
            observed_by_slice[key].add(name)

    expected_total = sum(len(names) for names in expected_by_slice.values())
    observed_total = sum(
        len(observed_by_slice.get(key, set()) & expected)
        for key, expected in expected_by_slice.items()
    )
    ratio = (observed_total / expected_total) if expected_total else 1.0
    by_slice = {}
    for key in sorted(expected_by_slice):
        expected = expected_by_slice[key]
        observed = observed_by_slice.get(key, set()) & expected
        slice_ratio = (len(observed) / len(expected)) if expected else 1.0
        by_slice[key] = {
            "expected": len(expected),
            "observed": len(observed),
            "ratio": slice_ratio,
        }
    return {
        "expected_total": expected_total,
        "observed_total": observed_total,
        "ratio": ratio,
        "by_slice": by_slice,
    }


def snapshot_coverage_failures(report, min_ratio=SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO):
    failures = []
    if report["expected_total"] and report["ratio"] < min_ratio:
        failures.append(
            f"overall {report['observed_total']}/{report['expected_total']} "
            f"theatre-date slices ({report['ratio']:.1%})"
        )
    for (date_str, tz), details in report.get("by_slice", {}).items():
        if details["expected"] and details["ratio"] < min_ratio:
            failures.append(
                f"{date_str} {tz} {details['observed']}/{details['expected']} "
                f"theatres ({details['ratio']:.1%})"
            )
    return failures


def snapshot_coverage_failure_is_fatal(report, snapshot_rows_written,
                                       fatal_ratio=SNAPSHOT_FATAL_COVERAGE_RATIO):
    """Decide whether thin snapshot coverage should fail the run.

    Fatal when either (a) no rows were captured at all, or (b) the overall
    theatre-date coverage is below the FATAL floor — in which case the data is
    too sparse to record honestly, so we fail rather than commit a misleadingly
    partial snapshot. Coverage between the fatal floor and the MIN warning
    threshold still commits (with a warning) so the model can weight it.
    """
    if not report.get("expected_total"):
        return False
    if snapshot_rows_written <= 0 and report.get("observed_total", 0) <= 0:
        return True
    ratio = report.get("ratio")
    if ratio is not None and ratio < fatal_ratio:
        return True
    return False


def regular_phase2_theatre_coverage(expected_theatres, results, movie_titles,
                                    saved_links=None, expected_dates=None):
    expected_by_movie = {title: set() for title in (movie_titles or [])}
    if saved_links is not None and expected_dates is not None:
        for theatre in expected_theatres:
            name = theatre.get("name")
            entry = saved_links.get(name)
            if not name or not entry:
                continue
            expected_date = phase2_theatre_expected_date(theatre, entry, expected_dates)
            movies = phase1_entry_movies(entry, expected_date)
            for title in movie_titles or []:
                if movies.get(title):
                    expected_by_movie[title].add(name)
    else:
        expected_names = {
            theatre.get("name")
            for theatre in expected_theatres
            if theatre.get("name")
        }
        expected_by_movie = {title: set(expected_names) for title in (movie_titles or [])}

    expected_names = set().union(*expected_by_movie.values()) if expected_by_movie else set()
    observed_by_movie = {title: set() for title in (movie_titles or [])}
    for result in results:
        movie = result.get("movie")
        theatre = result.get("theatre")
        if movie in observed_by_movie and theatre in expected_by_movie.get(movie, set()):
            observed_by_movie[movie].add(theatre)

    by_movie = {}
    for title in movie_titles or []:
        expected_total = len(expected_by_movie.get(title, set()))
        observed = len(observed_by_movie.get(title, set()))
        ratio = (observed / expected_total) if expected_total else 1.0
        by_movie[title] = {
            "expected": expected_total,
            "observed": observed,
            "ratio": ratio,
        }
    return {
        "expected_total": len(expected_names),
        "by_movie": by_movie,
        "expected_theatres_by_movie": {
            title: sorted(names)
            for title, names in expected_by_movie.items()
        },
    }


def regular_phase2_coverage_failures(report, min_ratio=REGULAR_PHASE2_MIN_COVERAGE_RATIO):
    failures = []
    for title, details in report.get("by_movie", {}).items():
        if details["expected"] and details["ratio"] < min_ratio:
            failures.append(
                f"{title} {details['observed']}/{details['expected']} "
                f"theatres ({details['ratio']:.1%})"
            )
    return failures


def snapshot_phase1_coverage_failure_is_fatal(report):
    """Snapshot preflight should only fail when no selected links are usable."""
    return bool(report.get("expected_total") and not report.get("fresh_count"))


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


def opening_weekend_show_dates(weekend_of):
    """Return Thu/Fri/Sat/Sun dates for an opening-weekend Friday key."""
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    return [
        (friday + timedelta(days=offset)).strftime("%Y-%m-%d")
        for offset in (-1, 0, 1, 2)
    ]


def phase1_weekend_anchor(ref_dt, full_weekend=False):
    """Weekend key Phase 1 should collect links for."""
    if full_weekend and ref_dt.weekday() == 0:  # Monday early-lead links
        return (ref_dt + timedelta(days=4)).strftime("%Y-%m-%d")
    if full_weekend and ref_dt.weekday() == 1:  # Tuesday warm-cache links
        return (ref_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    if full_weekend and ref_dt.weekday() == 2:  # Wednesday pre-opening links
        return (ref_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    return opening_weekend_friday(ref_dt)


def phase1_collection_dates(tz_group, target_date=None, ref_dt=None,
                            full_weekend=False):
    """Dates Phase 1 should visit for one timezone.

    Full-weekend expansion starts with a Monday early-lead pass, then
    Tuesday/Wednesday/Thursday/Friday fill gaps and refresh late schedule
    changes.

    A same-day full-weekend run ALWAYS keeps the current local day in its
    collection set, even in the evening. AMC serves the whole day's listing
    until local midnight; the evening schedule is the most complete (it has
    absorbed any late showtime additions); ``merge_showtime_entries`` unions
    rows, so a late capture can never shrink an earlier same-day one; and
    Phase 1 coverage is measured per theatre — an evening run still has
    in-window showtimes, so theatres stay covered.

    Dropping today here used to strand any timezone whose only successful
    collection landed after the local window start. When an AMC block delayed
    the Tue/Wed warm cache (2026-06-12), the CT/PT catch-up runs fired ~18:00
    local and, under the old rule, collected only Sat/Sun — losing the
    just-opened Friday show date that the Saturday post-show Phase 2 scrape
    needs. By the time Phase 2 ran, Friday had rolled off AMC and was
    unrecoverable, so CT/PT lost the whole opening-Friday seat capture while
    ET (which collected that morning) kept it.
    """
    if target_date:
        base_dt = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        base_dt = ref_dt or local_now(tz_group)

    current_date = target_date or base_dt.strftime("%Y-%m-%d")
    if full_weekend:
        weekend_dates = opening_weekend_show_dates(
            phase1_weekend_anchor(base_dt, full_weekend=True)
        )
        if base_dt.weekday() in (0, 1, 2):
            return weekend_dates
        if base_dt.weekday() in (3, 4, 5):
            return [date_str for date_str in weekend_dates if date_str >= current_date]
    return [current_date]


# A cinema "business day" runs past midnight — the last shows of 2026-08-07
# start at 22:00-23:00 and AMC keeps listing them into the small hours. The
# repair window follows that day, not the calendar date.
PHASE1_REPAIR_THEATRE_DAY_HOURS = 6


def phase1_target_date_is_repairable(tz_group, target_date):
    """True when AMC can still plausibly expose showtime links for target_date."""
    try:
        target_day = datetime.strptime(target_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return False
    return target_day >= local_now(tz_group).date()


def phase1_target_date_is_within_theatre_day(tz_group, target_date):
    """Looser window for a LAST-RESORT repair when no cached links exist.

    A cinema business day runs past midnight: the last shows of a date start at
    22:00-23:00 and AMC keeps listing them into the small hours. The strict
    calendar check above is right for deciding whether to spend the repair
    budget when usable cached links exist — but it also made the 07:00 UTC
    regular scrape structurally UNREPAIRABLE (that slot runs 00:00-03:00 local,
    so phase1_expected_date, now - 12h, is always the previous calendar day).
    With no cached links the only other branch is fail_phase, so that timezone
    lost every seat read for the weekend. When there is nothing to fall back
    on, trying is strictly better than failing.
    """
    try:
        target_day = datetime.strptime(target_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return False
    theatre_day = (
        local_now(tz_group) - timedelta(hours=PHASE1_REPAIR_THEATRE_DAY_HOURS)
    ).date()
    return target_day >= theatre_day


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


def _is_active_polymarket_event(event):
    """Return True for live events that can still drive collection."""
    return (
        bool(event.get("active", True))
        and not bool(event.get("closed", False))
        and not bool(event.get("archived", False))
    )


def _event_to_box_office_market(event):
    title = event.get("title", "")
    title_lower = title.lower()

    # Same filter as trade.py: must have BOTH keywords. Non-opening markets
    # need a separate model path before they can safely drive collection.
    if "opening weekend" not in title_lower or "box office" not in title_lower:
        return None
    if is_comparison_box_office_market(title):
        print(f"    ↷ Skipping comparison market: {title}")
        return None

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

    return {
        "movie_title": movie_name,
        "market_url": event_url,
        "question": title,
        "current_odds": "N/A",
        "volume": total_volume or float(event.get("volume", 0) or event.get("volume24hr", 0) or 0),
        "market_id": str(event.get("id", "")),
        "end_date": (
            event.get("endDate")
            or event.get("end_date")
            or event.get("end_date_iso")
            or event.get("endDateIso")
        ),
        "bracket_markets": bracket_markets,
    }


def _fetch_polymarket_events_feed():
    url = "https://gamma-api.polymarket.com/events"
    params = {
        "active": "true",
        "closed": "false",
        "limit": 500,
        "order": "volume24hr",
        "ascending": "false",
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _fetch_polymarket_public_search_events():
    url = "https://gamma-api.polymarket.com/public-search"
    params = {
        "q": "box office",
        "limit": 50,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    if isinstance(payload, dict):
        return payload.get("events", [])
    if isinstance(payload, list):
        return payload
    return []


# Set by fetch_polymarket_box_office: True when at least one Polymarket feed
# answered (even with zero markets), False when every feed errored. Lets the
# no-markets exits distinguish "quiet release weekend, nothing to track" (clean
# skip, exit 0 — e.g. 2026-07-24 had no box office market and every lane
# alarm-failed for two days) from "market discovery is broken" (real failure).
POLYMARKET_LAST_FETCH_OK = None
# True only when at least one box-office-shaped event was successfully PARSED.
# "The socket answered" is not enough evidence for a clean skip: if Polymarket
# renames a field or changes its title wording so _event_to_box_office_market
# returns None for everything, the feed still returns 200 and we would exit 0
# with zero rows — a parser regression taking the pipeline dark for a weekend
# with every signal green, which is the exact failure class these guards exist
# to prevent.
POLYMARKET_LAST_PARSE_OK = None


def fetch_polymarket_box_office():
    """
    Find active opening-weekend box office bracket events on Polymarket.

    Uses the same logic as trade.py: searches the Gamma events API for
    events with "opening weekend" AND "box office" in the title, then
    extracts the quoted movie name. This ensures scraper.py collects
    seat data for exactly the movies trade.py will try to trade.

    Returns list of dicts with movie info.
    """
    global POLYMARKET_LAST_FETCH_OK, POLYMARKET_LAST_PARSE_OK
    print("\n📊 Checking Polymarket for active box office markets...")

    feed_ok = False
    events = []
    try:
        events.extend(_fetch_polymarket_events_feed())
        feed_ok = True
    except Exception as e:
        print(f"  ⚠️  Polymarket events API error: {e}")

    try:
        search_events = _fetch_polymarket_public_search_events()
        feed_ok = True
        if search_events:
            print(f"  🔎 Public search returned {len(search_events)} box-office candidate event(s)")
            seen_ids = {str(e.get("id", "")) for e in events}
            for event in search_events:
                event_id = str(event.get("id", ""))
                if event_id and event_id in seen_ids:
                    continue
                events.append(event)
    except Exception as e:
        print(f"  ⚠️  Polymarket public-search fallback error: {e}")

    candidates_by_movie = {}
    parsed_any = False
    parse_near_misses = []

    for event in events:
        if not _is_active_polymarket_event(event):
            continue
        market = _event_to_box_office_market(event)
        if market is None:
            # An ACTIVE event that looks box-office-shaped but failed to
            # convert is a parser/schema regression candidate, not a quiet
            # weekend. The old global parsed_any let ONE parseable event
            # anywhere (e.g. a holdover market) vouch for the whole feed, so a
            # misparse of this weekend's only opening market clean-skipped the
            # entire weekend green (soft-fail audit finding 4).
            title = str(event.get("title") or "")
            tl = title.lower()
            # Mirror the matcher's own precondition exactly: only an event
            # with BOTH keywords is in this lane's target class. Holdover
            # markets ("4th weekend box office") and comparison markets fail
            # conversion BY DESIGN and must not veto quiet-weekend skips.
            if ("opening weekend" in tl and "box office" in tl
                    and not is_comparison_box_office_market(title)):
                parse_near_misses.append(title[:80])
            continue
        parsed_any = True
        candidates_by_movie.setdefault(market["movie_title"], []).append(market)

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

    POLYMARKET_LAST_FETCH_OK = feed_ok
    # A clean skip is only safe when nothing box-office-shaped failed to
    # parse: near-misses veto it so the run fails loud instead of green.
    POLYMARKET_LAST_PARSE_OK = parsed_any and not parse_near_misses
    if parse_near_misses:
        print(f"  \u26a0\ufe0f  {len(parse_near_misses)} box-office-shaped event(s) "
              f"FAILED to parse — refusing to treat this as a quiet weekend:")
        for t in parse_near_misses[:5]:
            print(f"      - {t}")
    if feed_ok and not parsed_any and events:
        print(f"  ⚠️  {len(events)} event(s) returned but NONE parsed as a box "
              f"office market — possible parser/schema regression, not a quiet "
              f"weekend.")
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
            stamped = ""
            notes = row.get("notes", "") or ""
            if notes.startswith("weekend_of="):
                stamped = notes.split("=", 1)[1].strip()
            if stamped:
                row_weekend = stamped
            else:
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
                    for date_entry in (entry.get("dates") or {}).values():
                        titles.extend((date_entry.get("movies") or {}).keys())
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


def movie_titles_missing_metadata(movie_titles, metadata_csv=None):
    """Tracked titles with no movie-metadata.csv row or no audience_type.

    The audience classification drives the broad_family cross-chain gate and
    the audience-aware Friday multiplier; a missing row silently disables both
    (PAW Patrol 2026-08-14 recorded -36% that way, and both 2026-08-28 films
    ran unprotected). The file is hand-maintained, so surface the gap LOUDLY
    at collect-links time — days before the first snapshot slot — instead of
    as a buried print in the prediction output once the weekend is running.
    """
    path = Path(metadata_csv) if metadata_csv else MOVIE_METADATA_CSV
    have = {}
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                name = str(row.get("movie", "") or "").strip().lower()
                if not name:
                    continue
                audience = str(row.get("audience_type", "") or "").strip()
                have[name] = bool(audience) or have.get(name, False)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  ⚠️  Could not read movie metadata ({e}); treating all titles as unmetadata'd")
    return [
        title for title in movie_titles
        if not have.get(str(title or "").strip().lower())
    ]


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


def market_end_datetime(market):
    raw = (
        market.get("end_date")
        or market.get("endDate")
        or market.get("end_date_iso")
        or market.get("endDateIso")
    )
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def market_matches_collection_weekend(market, weekend):
    """True when a live Polymarket event resolves inside this opening weekend window."""
    end_dt = market_end_datetime(market)
    if end_dt is None:
        # Do not drop markets if the API shape changes and omits an end date;
        # later Phase 1 link filtering still prevents impossible AMC work.
        return True
    weekend_date = datetime.strptime(weekend, "%Y-%m-%d").date()
    end_date = end_dt.astimezone(timezone.utc).date()
    return weekend_date <= end_date <= weekend_date + timedelta(days=6)


def filter_live_markets_for_weekend(live_markets, weekend, phase_label):
    kept = [
        market for market in live_markets
        if market_matches_collection_weekend(market, weekend)
    ]
    dropped = [
        market for market in live_markets
        if not market_matches_collection_weekend(market, weekend)
    ]
    if dropped:
        print(
            f"  ↷ {phase_label}: ignoring {len(dropped)} live market(s) outside "
            f"collection weekend {weekend}: "
            + ", ".join(m.get("movie_title", "unknown") for m in dropped[:5])
        )
    return kept


def select_collection_markets(live_markets, ref_dt, phase_label,
                              weekend_override=None,
                              prefer_live_markets=False):
    """Choose which movie markets drive the data-collection run."""
    live_markets = live_markets or []
    weekend = weekend_override or opening_weekend_friday(ref_dt)
    live_markets = filter_live_markets_for_weekend(live_markets, weekend, phase_label)
    tracked_titles = tracked_movie_titles_from_state(weekend)

    if prefer_live_markets and live_markets:
        if tracked_titles:
            live_titles = unique_preserving_order(m.get("movie_title", "") for m in live_markets)
            print(
                f"  🔜 {phase_label}: pre-opening collection for weekend {weekend}; "
                f"using live market(s): {', '.join(live_titles)}"
            )
        return live_markets

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


def save_polymarket_data(markets, weekend_of=None):
    """Save Polymarket bracket markets to CSV — one row per bracket question.

    weekend_of stamps the COLLECTION weekend into the notes column
    ("weekend_of=YYYY-MM-DD"). Without it, readers must infer the weekend from
    the observation date via opening_weekend_friday — and rows observed Mon-Wed
    for the UPCOMING weekend map to the PRIOR Friday, bleeding next weekend's
    market into the closing weekend's collection and poly data (dependency
    audit finding D6). The notes column is reused so the append-only CSV needs
    no schema migration; readers prefer the stamp and fall back to the legacy
    date mapping for old rows.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    note = f"weekend_of={weekend_of}" if weekend_of else ""

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
                    bkt["volume"], bkt["market_id"], note,
                ])
                new_count += 1

    print(f"  Saved {new_count} new bracket market entries to CSV")


# ─── Box Office Mojo — National Theatre Counts ──────────────────────────────

def _parse_bom_chart_theatre_counts(html):
    """Parse a Box Office Mojo weekend/daily chart into {title_lower: theatres}.

    Stdlib HTML table parse (no external deps): read the table, locate the
    'Release' and 'Theaters' columns by header NAME, and pull each row's pair.
    Robust to BOM's column reordering, unlike the old positional regex (which
    silently matched nothing and left theatre-counts.json empty).
    """
    class _ChartTable(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_cell = False
            self.is_header_row = False
            self.cur = []
            self.rows = []
            self.buf = ""

        def handle_starttag(self, tag, attrs):
            if tag == "tr":
                self.cur = []
                self.is_header_row = False
            elif tag in ("td", "th"):
                self.in_cell = True
                self.buf = ""
                if tag == "th":
                    self.is_header_row = True

        def handle_endtag(self, tag):
            if tag in ("td", "th") and self.in_cell:
                self.cur.append(self.buf.strip())
                self.in_cell = False
            elif tag == "tr" and self.cur:
                self.rows.append((self.is_header_row, self.cur))

        def handle_data(self, data):
            if self.in_cell:
                self.buf += data

    parser = _ChartTable()
    try:
        parser.feed(html)
    except Exception:
        return {}
    header = next((cells for is_h, cells in parser.rows if is_h), None)
    if not header or "Release" not in header or "Theaters" not in header:
        return {}
    ri, ti = header.index("Release"), header.index("Theaters")
    counts = {}
    for is_h, cells in parser.rows:
        if is_h or len(cells) <= max(ri, ti):
            continue
        title = cells[ri].strip()
        raw = cells[ti].replace(",", "").strip()
        if title and raw.isdigit():
            count = int(raw)
            if 10 <= count <= 12000:  # plausible theatre-count range
                # Keep the widest count seen for a title (opening footprint).
                counts[title.lower()] = max(count, counts.get(title.lower(), 0))
    return counts


def fetch_bom_theatre_counts(movie_titles):
    """
    Scrape Box Office Mojo for national theatre counts of the requested movies.
    Reads the most recent weekend chart plus the last few daily charts (the
    weekend chart only lists COMPLETED weekends, so a film opening this weekend
    is found via the daily chart once previews/opening day post). Note: BOM only
    publishes a film's theatre count after it opens — pre-opening titles won't
    be found here and rely on movie-metadata / a manual override instead.
    Saves results to theatre-counts.json. Returns {movie_title: theatre_count}.
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
    # Weekend chart = most recent COMPLETED weekend (movies mid-run). Daily
    # charts for the last few days catch brand-new openings (Thu previews /
    # opening day) not yet on the weekend chart. Merge, keeping widest count.
    chart_urls = ["https://www.boxofficemojo.com/weekend/chart/"]
    today = datetime.now().date()
    for back in range(0, 3):
        day = today - timedelta(days=back)
        chart_urls.append(f"https://www.boxofficemojo.com/date/{day.isoformat()}/")

    parsed = {}
    for url in chart_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            for title, count in _parse_bom_chart_theatre_counts(resp.text).items():
                if count > parsed.get(title, 0):
                    parsed[title] = count
        except Exception as e:
            print(f"  ⚠️  BOM chart fetch failed ({url}): {e}")

    if parsed:
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
                print(f"  ⚠️  {movie}: no BOM match found (may not have opened yet)")
    else:
        print("  ⚠️  No BOM chart rows parsed — leaving prior counts untouched.")

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


def collection_window_start_hour(date_str):
    """Return the first local showtime hour to collect for a show date."""
    try:
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    except (TypeError, ValueError):
        return DEFAULT_COLLECTION_START_HOUR
    if day_name in {"Saturday", "Sunday"}:
        return WEEKEND_FULL_DAY_START_HOUR
    return DEFAULT_COLLECTION_START_HOUR


def showtime_in_collection_window(time_str, date_str):
    """True when a showtime belongs to the Phase 1/2 collection window."""
    hour = parse_showtime_hour(time_str)
    if hour is None:
        return False
    return collection_window_start_hour(date_str) <= hour <= COLLECTION_END_HOUR


def filter_showtime_entries_for_collection_window(entries, date_str):
    """Keep saved/loaded showtime entries that match the intended date window."""
    return [
        entry for entry in entries
        if showtime_in_collection_window(entry.get("showtime", ""), date_str)
    ]


def _showtime_entry_key(entry):
    showtime_id = str(entry.get("showtime_id", "") or "").strip()
    if showtime_id:
        return ("id", showtime_id)
    showtime = str(entry.get("showtime", "") or "").strip().lower()
    fmt = str(entry.get("format", entry.get("auditorium_type", "")) or "").strip().lower()
    return ("time-format", showtime, fmt)


def merge_showtime_entries(*entry_lists):
    """Merge showtime link rows without losing older same-date seat-map IDs."""
    merged = []
    by_key = {}
    for entries in entry_lists:
        for raw in entries or []:
            if not raw:
                continue
            entry = dict(raw)
            if not entry.get("format") and entry.get("auditorium_type"):
                entry["format"] = entry.get("auditorium_type")
            key = _showtime_entry_key(entry)
            if key in by_key:
                existing = by_key[key]
                if "source" not in entry and existing.get("source"):
                    existing.pop("source", None)
                for field, value in entry.items():
                    if field == "source" and not existing.get("source"):
                        continue
                    if value not in (None, ""):
                        existing[field] = value
                continue
            by_key[key] = entry
            merged.append(entry)

    def sort_key(entry):
        hour = parse_showtime_hour(entry.get("showtime", ""))
        return (
            hour if hour is not None else 99,
            str(entry.get("format", "") or ""),
            str(entry.get("showtime_id", "") or ""),
        )

    return sorted(merged, key=sort_key)


def merge_saved_movie_maps(*movie_maps):
    """Merge {movie: [showtime entries]} maps movie-by-movie."""
    merged = {}
    for movie_map in movie_maps:
        for movie, entries in (movie_map or {}).items():
            merged[movie] = merge_showtime_entries(merged.get(movie, []), entries)
    return merged


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

PRE_RESERVATION_FIELDS = [
    "weekend_of", "run_id",
    "snapshot_time", "snapshot_bucket",
    "show_date", "day_of_week", "theatre_name", "theatre_city",
    "timezone", "movie_title", "showtime", "showtime_id",
    "minutes_until_showtime", "auditorium_name", "auditorium_type",
    "total_seats", "reserved_seats", "available_seats",
    "occupancy_pct", "delta_reserved_since_previous",
    "amc_seat_map_url", "notes",
]

PRE_RESERVATION_DEDUPE_FIELDS = (
    "weekend_of",
    "snapshot_bucket",
    "show_date",
    "theatre_name",
    "movie_title",
    "showtime_id",
    "auditorium_type",
)


def _csv_lineterminator(path):
    """Keep large tracked CSVs in their existing line-ending style."""
    try:
        candidate = Path(path)
        if candidate.exists():
            with candidate.open("rb") as f:
                if b"\r\n" in f.read(8192):
                    return "\r\n"
    except OSError:
        pass
    return "\n"


def ensure_csv_header():
    """Create seat-counts.csv with header if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SEAT_CSV.exists():
        with open(SEAT_CSV, "w", newline="") as f:
            writer = csv.writer(f, lineterminator=_csv_lineterminator(SEAT_CSV))
            writer.writerow(SEAT_FIELDS)


def ensure_pre_reservation_header():
    """Create pre-reservation-snapshots.csv with header if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PRE_RESERVATION_CSV.exists():
        with open(PRE_RESERVATION_CSV, "w", newline="") as f:
            writer = csv.writer(f, lineterminator=_csv_lineterminator(PRE_RESERVATION_CSV))
            writer.writerow(PRE_RESERVATION_FIELDS)


def _seat_row_dict(row_data):
    return dict(zip(SEAT_FIELDS, row_data))


def _parse_seat_count(value):
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _format_seat_number(value):
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}".rstrip("0").rstrip(".")


def _normalize_seat_count_fields(row):
    total = _parse_seat_count(row.get("total_seats"))
    sold = _parse_seat_count(row.get("seats_sold"))
    available = _parse_seat_count(row.get("seats_available"))
    if total is None or total < 0:
        return row

    if sold is None and available is not None:
        sold = max(total - available, 0)
    if available is None and sold is not None:
        available = max(total - sold, 0)

    if sold is not None:
        row["seats_sold"] = str(sold)
    if available is not None:
        row["seats_available"] = str(available)
    if sold is not None and total > 0:
        row["occupancy_pct"] = _format_seat_number(round(sold / total * 100, 1))
    elif total == 0:
        row["occupancy_pct"] = "0"

    return row


def _normalize_seat_row(row):
    if isinstance(row, list):
        row = _seat_row_dict(row)
    normalized = {field: str(row.get(field, "") or "") for field in SEAT_FIELDS}
    return _normalize_seat_count_fields(normalized)


def _seat_row_key(row):
    if isinstance(row, list):
        row = _seat_row_dict(row)
    return tuple(str(row.get(field, "") or "") for field in SEAT_DEDUPE_FIELDS)


def _merge_seat_row_metadata(existing, incoming):
    """Update metadata-only fields when a duplicate row carries newer context."""
    existing_note = str(existing.get("notes", "") or "")
    incoming_note = str(incoming.get("notes", "") or "")
    changed = False

    for part in (piece.strip() for piece in incoming_note.split(";")):
        if not part.startswith("showtime_window="):
            continue
        if part and part not in existing_note:
            existing["notes"] = f"{existing_note}; {part}" if existing_note else part
            existing_note = existing["notes"]
            changed = True

    return changed


def _pre_reservation_row_key(row):
    return tuple(str(row.get(field, "") or "") for field in PRE_RESERVATION_DEDUPE_FIELDS)


def snapshot_bucket(check_time, minutes=PRE_RESERVATION_BUCKET_MINUTES):
    """Round snapshot timestamps down to a stable time bucket."""
    try:
        dt = datetime.fromisoformat(str(check_time).replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    bucket_minutes = max(1, int(minutes or 60))
    floored_minute = (dt.minute // bucket_minutes) * bucket_minutes
    bucketed = dt.replace(minute=floored_minute, second=0, microsecond=0)
    return bucketed.strftime("%Y-%m-%dT%H:%MZ")


_PRE_RESERVATION_IDENTITY_FIELDS = (
    "weekend_of", "show_date", "theatre_name", "movie_title",
    "showtime_id", "auditorium_type",
)


def _pre_reservation_identity(row):
    return tuple(
        str(row.get(field, "") or "") for field in _PRE_RESERVATION_IDENTITY_FIELDS
    )


def _previous_reserved_count(row, reserved_index=None):
    """Latest prior reserved count for this showtime identity.

    `reserved_index` ({identity: sorted-insertable list of (bucket, reserved)})
    is built once per append batch by `append_unique_pre_reservation_rows`; the
    old implementation re-read the entire snapshots CSV for EVERY appended row
    (O(rows_in_file x rows_appended) — minutes of wasted CPU per probe, growing
    weekly). Passing no index falls back to a one-off single-file scan.
    """
    if reserved_index is None:
        reserved_index = _build_reserved_index()
        if reserved_index is None:
            return None
    identity = _pre_reservation_identity(row)
    current_bucket = str(row.get("snapshot_bucket", "") or "")
    previous = [
        (bucket, reserved)
        for bucket, reserved in reserved_index.get(identity, ())
        if bucket < current_bucket
    ]
    if not previous:
        return None
    return max(previous)[1]


def _build_reserved_index():
    """One pass over the snapshots CSV -> {identity: [(bucket, reserved), ...]}."""
    if not PRE_RESERVATION_CSV.exists():
        return None
    index = {}
    try:
        with open(PRE_RESERVATION_CSV, "r", newline="") as f:
            for existing in csv.DictReader(f):
                bucket = str(existing.get("snapshot_bucket", "") or "")
                try:
                    reserved = int(float(existing.get("reserved_seats", 0) or 0))
                except (TypeError, ValueError):
                    continue
                index.setdefault(_pre_reservation_identity(existing), []).append(
                    (bucket, reserved)
                )
    except OSError:
        return None
    return index


def append_unique_pre_reservation_rows(rows):
    """Append pre-reservation snapshots without double-counting a time bucket."""
    if not rows:
        return 0, 0

    ensure_pre_reservation_header()
    existing_keys = set()
    reserved_index = {}
    capacity_by_showtime = {}
    with open(PRE_RESERVATION_CSV, "r", newline="") as f:
        for row in csv.DictReader(f):
            existing_keys.add(_pre_reservation_row_key(row))
            _is_partial_render(row, capacity_by_showtime)  # build capacity index
            bucket = str(row.get("snapshot_bucket", "") or "")
            try:
                reserved = int(float(row.get("reserved_seats", 0) or 0))
            except (TypeError, ValueError):
                continue
            reserved_index.setdefault(_pre_reservation_identity(row), []).append(
                (bucket, reserved)
            )

    pending = []
    seen_keys = set(existing_keys)
    skipped = 0
    partial_renders = 0
    for row in rows:
        normalized = {field: str(row.get(field, "") or "") for field in PRE_RESERVATION_FIELDS}
        if _is_partial_render(normalized, capacity_by_showtime):
            partial_renders += 1
            skipped += 1
            continue
        if not normalized.get("delta_reserved_since_previous"):
            previous = _previous_reserved_count(normalized, reserved_index)
            if previous is not None:
                try:
                    normalized["delta_reserved_since_previous"] = str(
                        int(float(normalized.get("reserved_seats", 0) or 0)) - previous
                    )
                except (TypeError, ValueError):
                    normalized["delta_reserved_since_previous"] = ""
        key = _pre_reservation_row_key(normalized)
        if key in seen_keys:
            skipped += 1
            continue
        pending.append(normalized)
        seen_keys.add(key)

    if partial_renders:
        print(
            f"   ⚠️  Dropped {partial_renders} snapshot row(s) whose total_seats "
            f"collapsed below {SEAT_CAPACITY_PARTIAL_RENDER_RATIO:.0%} of the known "
            "capacity for the same showtime (partial seat-map render)"
        )

    if pending:
        with open(PRE_RESERVATION_CSV, "a", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=PRE_RESERVATION_FIELDS,
                lineterminator=_csv_lineterminator(PRE_RESERVATION_CSV),
            )
            writer.writerows(pending)

    return len(pending), skipped


# A showtime's auditorium capacity cannot shrink between readings. An incoming
# total_seats below this fraction of the best prior reading for the SAME
# showtime means the seat map only partially rendered — recording it would
# silently undercount sold seats (the number every dollar derives from).
SEAT_CAPACITY_PARTIAL_RENDER_RATIO = _env_float(
    "SEAT_CAPACITY_PARTIAL_RENDER_RATIO", 0.80, minimum=0.0
)


def _showtime_capacity_key(row):
    """Stable per-showtime identity for capacity comparison (URL carries the id)."""
    url = str(row.get("amc_seat_map_url", "") or "")
    if url:
        return url
    showtime_id = str(row.get("showtime_id", "") or "")
    return showtime_id or None


def _is_partial_render(row, capacity_by_showtime,
                       ratio=SEAT_CAPACITY_PARTIAL_RENDER_RATIO):
    """True when this reading's total_seats collapsed vs the known capacity."""
    key = _showtime_capacity_key(row)
    if not key:
        return False
    try:
        total = float(row.get("total_seats") or 0)
    except (TypeError, ValueError):
        return False
    if total <= 0:
        return False
    known = capacity_by_showtime.get(key, 0.0)
    if total > known:
        capacity_by_showtime[key] = total
        return False
    return known > 0 and total < known * ratio


def append_unique_seat_rows(rows):
    """Append only rows we haven't already logged for this showtime snapshot."""
    if not rows:
        return 0, 0

    ensure_csv_header()
    existing_rows = []
    existing_by_key = {}
    capacity_by_showtime = {}
    if SEAT_CSV.exists():
        with open(SEAT_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                normalized = _normalize_seat_row(row)
                existing_rows.append(normalized)
                existing_by_key.setdefault(_seat_row_key(normalized), normalized)
                _is_partial_render(normalized, capacity_by_showtime)  # build index

    pending = []
    seen_keys = set(existing_by_key)
    skipped = 0
    partial_renders = 0
    metadata_updated = 0
    for row in rows:
        normalized = _normalize_seat_row(row)
        key = _seat_row_key(normalized)
        if key in seen_keys:
            skipped += 1
            existing_row = existing_by_key.get(key)
            if existing_row and _merge_seat_row_metadata(existing_row, normalized):
                metadata_updated += 1
            continue
        if _is_partial_render(normalized, capacity_by_showtime):
            partial_renders += 1
            skipped += 1
            continue
        pending.append(normalized)
        seen_keys.add(key)
        existing_by_key[key] = normalized

    if partial_renders:
        print(
            f"   ⚠️  Dropped {partial_renders} seat row(s) whose total_seats collapsed "
            f"below {SEAT_CAPACITY_PARTIAL_RENDER_RATIO:.0%} of the known capacity for "
            "the same showtime (partial seat-map render)"
        )

    if metadata_updated:
        with open(SEAT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=SEAT_FIELDS,
                lineterminator=_csv_lineterminator(SEAT_CSV),
            )
            writer.writeheader()
            writer.writerows(existing_rows + pending)
    elif pending:
        with open(SEAT_CSV, "a", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=SEAT_FIELDS,
                lineterminator=_csv_lineterminator(SEAT_CSV),
            )
            writer.writerows(pending)

    return len(pending), skipped


def build_pre_reservation_row(theatre, tz, movie_title, show, seat_data,
                              weekend_of, run_id, show_date, day_of_week,
                              check_time, delta_minutes, market_url="", note=""):
    showtime_id = show.get("showtime_id", "")
    amc_url = f"https://www.amctheatres.com/showtimes/{showtime_id}/seats" if showtime_id else ""
    return {
        "weekend_of": weekend_of,
        "run_id": run_id,
        "snapshot_time": check_time,
        "snapshot_bucket": snapshot_bucket(check_time),
        "show_date": show_date,
        "day_of_week": day_of_week,
        "theatre_name": theatre["name"],
        "theatre_city": theatre.get("city", theatre.get("dma", "")),
        "timezone": tz,
        "movie_title": movie_title,
        "showtime": show.get("showtime", ""),
        "showtime_id": showtime_id,
        "minutes_until_showtime": str(max(0, -int(delta_minutes))),
        "auditorium_name": "",
        "auditorium_type": show.get("format", "Standard"),
        "total_seats": str(seat_data["total_seats"]),
        "reserved_seats": str(seat_data["seats_sold"]),
        "available_seats": str(seat_data["seats_available"]),
        "occupancy_pct": str(seat_data["occupancy_pct"]),
        "delta_reserved_since_previous": "",
        "amc_seat_map_url": amc_url,
        "notes": note,
    }


def should_record_pre_reservation_snapshot(delta_minutes):
    """True when the seat map is still a pre-show reservation snapshot."""
    try:
        return int(delta_minutes) <= 0
    except (TypeError, ValueError):
        return False


def _log_slug(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value or "")).strip("-") or "run"


def run_log_file_path(tz_group, run_id=None, now=None):
    now = now or datetime.now()
    run_part = _log_slug(run_id or uuid.uuid4().hex[:8])
    tz_part = _log_slug(tz_group)
    return (
        RUN_LOG_DIR
        / now.strftime("%Y-%m-%d")
        / f"{now.strftime('%Y%m%d-%H%M%S')}-{run_part}-{tz_part}.md"
    )


def log_run(tz_group, movies, results, issues, run_id=None, now=None):
    """Write a stable per-run log file.

    Phase 2 runs ET/CT/PT in parallel. A single append-only Markdown file is
    hard to merge cleanly across matrix pushes, so each leg writes an immutable
    log file and the workflow commits the directory.
    """
    now = now or datetime.now()
    log_path = run_log_file_path(tz_group, run_id=run_id, now=now)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "w") as f:
        f.write(f"# {now.strftime('%Y-%m-%d %H:%M')} - {tz_group} Group\n\n")
        f.write(f"- **Run ID:** {run_id or 'unknown'}\n")
        f.write(f"- **Polymarket movies tracked:** {', '.join(movies) if movies else 'None found'}\n")
        f.write(f"- **Rows:** {len(results)}\n")
        f.write(f"- **Issues:** {len(issues)}\n\n")

        if results:
            f.write("## Seat Rows\n\n")
            f.write("| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |\n")
            f.write("|---------|-------|--------|----------|-----------|-------------|\n")
            for r in results:
                f.write(f"| {r['theatre']} | {r['movie']} | {r['format']} | "
                        f"{r['showtime']} | {r['occupancy']}% | {r['delta']} min |\n")
            f.write("\n")

        if issues:
            f.write("## Issues\n\n")
            for issue in issues:
                f.write(f"- {issue}\n")
            f.write("\n")

        f.write("---\n")

    return log_path


def fail_phase(message, exit_code=1):
    """Abort the phase with a non-zero exit so Actions can retry or fail."""
    print(message)
    raise SystemExit(exit_code)


def phase1_groups(tz_group):
    return [tz_group] if tz_group != "ALL" else ["ET", "CT", "MT", "PT"]


def phase1_date_entry(entry, expected_date):
    """Return the link payload for expected_date from old or multi-date schema."""
    if not entry:
        return None
    dates = entry.get("dates") or {}
    if expected_date and isinstance(dates, dict):
        date_entry = dates.get(expected_date)
        if date_entry and date_entry.get("movies"):
            return date_entry
    if expected_date and entry.get("show_date") != expected_date:
        return None
    if entry.get("movies"):
        return entry
    return None


def phase1_entry_movies(entry, expected_date):
    date_entry = phase1_date_entry(entry, expected_date)
    movies = (date_entry or {}).get("movies") or {}
    return {
        movie: filter_showtime_entries_for_collection_window(shows, expected_date)
        for movie, shows in movies.items()
    }


def phase2_theatre_expected_date(theatre, entry, expected_dates):
    """Return the show date Phase 2 should use for a theatre/link entry."""
    if theatre.get("_phase2_expected_date"):
        return theatre["_phase2_expected_date"]
    ref_tz = theatre.get("_tz") or entry.get("tz") or "ET"
    return expected_dates.get(ref_tz) or phase1_expected_date(ref_tz)


def phase2_saved_showtime_count(theatres, saved_links, movie_titles, expected_dates):
    """Count the linked showtimes Phase 2 is about to attempt."""
    movie_titles = set(movie_titles or [])
    count = 0
    for theatre in theatres:
        entry = saved_links.get(theatre.get("name"))
        if not entry:
            continue
        expected_date = phase2_theatre_expected_date(theatre, entry, expected_dates)
        movies = phase1_entry_movies(entry, expected_date)
        for title in movie_titles:
            count += len(movies.get(title) or [])
    return count


def phase2_runtime_deadline_sec(theatres, saved_links, movie_titles, expected_dates,
                                snapshots_only=False, max_concurrent_tabs=None,
                                configured_deadline_sec=None):
    """Return an internal Phase 2 deadline sized to the linked workload.

    GitHub's step timeout is an outer guard. This deadline decides when the
    scraper stops launching new AMC theatres. Regular weekend full-day windows
    can be several times larger than preview/evening windows, so the regular
    budget must scale with linked showtime volume. Snapshot runs keep their
    explicit workflow deadline because their theatre cap is already fixed.
    """
    configured = PHASE2_DEADLINE_SEC if configured_deadline_sec is None else configured_deadline_sec
    if snapshots_only:
        return int(configured)

    theatre_count = len({theatre.get("name") for theatre in theatres if theatre.get("name")})
    showtime_count = phase2_saved_showtime_count(
        theatres,
        saved_links,
        movie_titles,
        expected_dates,
    )
    tabs = max(1, int(max_concurrent_tabs or phase2_max_concurrent_tabs(False)))
    scaled_work = (
        theatre_count * REGULAR_PHASE2_PER_THEATRE_SEC
        + showtime_count * REGULAR_PHASE2_PER_SHOWTIME_SEC
    ) / tabs
    dynamic_deadline = int(REGULAR_PHASE2_BASE_DEADLINE_SEC + scaled_work)
    deadline = max(int(configured), REGULAR_PHASE2_MIN_DEADLINE_SEC, dynamic_deadline)
    return min(REGULAR_PHASE2_MAX_DEADLINE_SEC, deadline)


def filter_fresh_phase2_theatres(all_theatres, saved_links, expected_dates):
    """Keep theatres whose Phase 1 entry matches the Phase 2 target show date."""
    fresh_theatres = []
    stale_skipped = []
    for theatre in all_theatres:
        entry = saved_links[theatre["name"]]
        expected_date = phase2_theatre_expected_date(theatre, entry, expected_dates)
        if not phase1_date_entry(entry, expected_date):
            entry_date = entry.get("show_date")
            stale_skipped.append(
                f"{theatre['name']} ({theatre.get('_tz','?')}: "
                f"show_date={entry_date}, expected={expected_date})"
            )
            continue
        fresh_theatres.append(theatre)
    return fresh_theatres, stale_skipped


def _phase1_entry_has_any_movies(entry):
    if entry.get("movies"):
        return True
    for date_entry in (entry.get("dates") or {}).values():
        if date_entry.get("movies"):
            return True
    return False


def _phase1_date_entry_from_top_level(entry):
    if not entry or not entry.get("show_date") or not entry.get("movies"):
        return None
    return {
        "collected_at": entry.get("collected_at"),
        "showtime_window_version": entry.get(
            "showtime_window_version",
            SHOWTIME_WINDOW_VERSION,
        ),
        "movies": entry.get("movies", {}),
    }


def merge_phase1_date_entries(old_date_entry, new_date_entry):
    """Merge one show_date payload while preserving rolled-off same-day links."""
    if not old_date_entry:
        return dict(new_date_entry or {})
    if not new_date_entry:
        return dict(old_date_entry or {})
    merged = dict(old_date_entry)
    movies = merge_saved_movie_maps(
        old_date_entry.get("movies") or {},
        new_date_entry.get("movies") or {},
    )
    merged.update({k: v for k, v in new_date_entry.items() if k != "movies"})
    merged["movies"] = movies
    merged["showtime_window_version"] = new_date_entry.get(
        "showtime_window_version",
        old_date_entry.get("showtime_window_version", SHOWTIME_WINDOW_VERSION),
    )
    return merged


def merge_phase1_entries(old_entry, new_entry):
    """Merge multi-date Phase 1 entries without dropping unrefreshed dates."""
    if not new_entry:
        return old_entry
    if not old_entry:
        return new_entry
    merged = dict(old_entry)
    if new_entry.get("tz"):
        merged["tz"] = new_entry["tz"]
    if new_entry.get("cohort"):
        merged["cohort"] = new_entry["cohort"]
    merged_dates = dict(old_entry.get("dates") or {})
    old_top_level = _phase1_date_entry_from_top_level(old_entry)
    if old_top_level:
        old_show_date = old_entry.get("show_date")
        merged_dates[old_show_date] = merge_phase1_date_entries(
            merged_dates.get(old_show_date),
            old_top_level,
        )
    for date_str, date_entry in (new_entry.get("dates") or {}).items():
        merged_dates[date_str] = merge_phase1_date_entries(
            merged_dates.get(date_str),
            date_entry,
        )
    new_top_level = _phase1_date_entry_from_top_level(new_entry)
    if new_top_level:
        new_show_date = new_entry.get("show_date")
        merged_dates[new_show_date] = merge_phase1_date_entries(
            merged_dates.get(new_show_date),
            new_top_level,
        )
    if merged_dates:
        merged["dates"] = merged_dates
    if new_entry.get("show_date"):
        merged["show_date"] = new_entry["show_date"]
        merged["movies"] = (merged_dates.get(new_entry["show_date"]) or {}).get("movies", {})
    elif old_entry.get("show_date") in merged_dates:
        merged["movies"] = (merged_dates.get(old_entry["show_date"]) or {}).get("movies", {})
    merged["showtime_window_version"] = new_entry.get(
        "showtime_window_version",
        merged.get("showtime_window_version", SHOWTIME_WINDOW_VERSION),
    )
    return merged


def _cohort_from_snapshot_note(note):
    note = str(note or "").lower()
    if "cohort=expansion" in note:
        return EXPANSION_COHORT
    if "cohort=core" in note:
        return CORE_COHORT
    return ""


def load_pre_reservation_showtime_links(weekend_of, movie_titles=None,
                                        theatre_metadata_by_name=None):
    """Return Phase1-like links preserved by prior snapshot rows."""
    if not PRE_RESERVATION_CSV.exists():
        return {}
    theatre_metadata_by_name = theatre_metadata_by_name or {}
    requested = {
        str(title or "").strip().lower(): str(title or "").strip()
        for title in (movie_titles or [])
        if str(title or "").strip()
    }
    links = {}
    try:
        with open(PRE_RESERVATION_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                if weekend_of and str(row.get("weekend_of", "") or "") != weekend_of:
                    continue
                show_date = str(row.get("show_date", "") or "").strip()
                theatre_name = str(row.get("theatre_name", "") or "").strip()
                movie_title = str(row.get("movie_title", "") or "").strip()
                showtime = str(row.get("showtime", "") or "").strip()
                showtime_id = str(row.get("showtime_id", "") or "").strip()
                if not theatre_name or not show_date or not movie_title or not showtime_id:
                    continue
                movie_key = movie_title.lower()
                if requested and movie_key not in requested:
                    continue
                if requested:
                    movie_title = requested[movie_key]
                if not showtime_in_collection_window(showtime, show_date):
                    continue
                fmt = (
                    str(row.get("auditorium_type", "") or "").strip()
                    or str(row.get("auditorium_name", "") or "").strip()
                    or "Standard"
                )
                theatre_metadata = theatre_metadata_by_name.get(theatre_name) or {}
                cohort = (
                    theatre_metadata.get("cohort")
                    or _cohort_from_snapshot_note(row.get("notes", ""))
                    or ""
                )
                snapshot_entry = {
                    "tz": str(row.get("timezone", "") or "").strip(),
                    "cohort": cohort,
                    "showtime_window_version": SHOWTIME_WINDOW_VERSION,
                    "dates": {
                        show_date: {
                            "showtime_window_version": SHOWTIME_WINDOW_VERSION,
                            "movies": {
                                movie_title: [
                                    {
                                        "showtime": showtime,
                                        "showtime_id": showtime_id,
                                        "format": fmt,
                                        "source": "snapshot-preserved link",
                                    }
                                ]
                            },
                        }
                    },
                }
                links[theatre_name] = merge_phase1_entries(
                    links.get(theatre_name),
                    snapshot_entry,
                )
    except Exception as exc:
        print(f"  ⚠️  Could not load snapshot-preserved showtime links: {exc}")
        return {}
    return links


def merge_snapshot_links_into_phase1_saved_links(saved_links, snapshot_links):
    """Augment regular Phase 2 links with showtime IDs captured by snapshots."""
    merged = dict(saved_links or {})
    for theatre_name, snapshot_entry in (snapshot_links or {}).items():
        if not snapshot_entry:
            continue
        merged[theatre_name] = merge_phase1_entries(
            merged.get(theatre_name),
            snapshot_entry,
        )
    return merged


def count_phase1_showtime_links(saved_links):
    count = 0
    for entry in (saved_links or {}).values():
        for date_entry in (entry.get("dates") or {}).values():
            for entries in (date_entry.get("movies") or {}).values():
                count += len(entries or [])
        for entries in (entry.get("movies") or {}).values():
            count += len(entries or [])
    return count


def phase1_cache_is_mergeable(existing, current_weekend):
    """True when an existing Phase 1 cache can safely merge with new links."""
    if not existing:
        return False
    existing_weekend = existing.get("weekend_of") or existing.get("date", "")
    if existing_weekend and existing_weekend != current_weekend:
        return False
    return existing.get("showtime_window_version") == SHOWTIME_WINDOW_VERSION


def sanitize_phase1_links_for_current_window(saved_links):
    """Drop per-date Phase 1 entries collected under an older showtime window."""
    sanitized = {}
    for name, entry in (saved_links or {}).items():
        kept = dict(entry)
        kept_dates = {}
        for date_str, date_entry in (entry.get("dates") or {}).items():
            if date_entry.get("showtime_window_version") == SHOWTIME_WINDOW_VERSION:
                kept_dates[date_str] = date_entry

        if kept_dates:
            kept["dates"] = kept_dates
        else:
            kept.pop("dates", None)

        top_level_is_current = (
            entry.get("showtime_window_version") == SHOWTIME_WINDOW_VERSION
            and entry.get("show_date")
            and entry.get("movies")
        )
        if not top_level_is_current:
            kept.pop("show_date", None)
            kept.pop("movies", None)

        if kept.get("dates") or kept.get("movies"):
            sanitized[name] = kept
    return sanitized


def merge_collected_phase1_links_with_existing_cache(collected_links, existing, current_weekend):
    """Merge a partial Phase 1 refresh with preserved current-weekend links.

    AMC can queue or hide subsets of showtimes on a refresh. A failed partial
    refresh should not fail the run when the already committed current-window
    cache still covers those missing theatre/date slices.
    """
    merged = dict(collected_links or {})
    existing_theatres = {}
    existing_is_mergeable = phase1_cache_is_mergeable(existing or {}, current_weekend)
    if existing_is_mergeable:
        existing_theatres = sanitize_phase1_links_for_current_window(
            (existing or {}).get("theatres", {})
        )

    merged_theatres = dict(existing_theatres)
    for name, new_entry in ((collected_links or {}).get("theatres") or {}).items():
        merged_theatres[name] = merge_phase1_entries(merged_theatres.get(name), new_entry)

    merged["theatres"] = merged_theatres
    if existing_is_mergeable and (existing or {}).get("weekend_of"):
        merged["weekend_of"] = existing["weekend_of"]
    if existing_is_mergeable and (existing or {}).get("date"):
        merged["date"] = existing["date"]
    merged["showtime_window_version"] = SHOWTIME_WINDOW_VERSION
    return merged


def phase1_link_coverage(saved_links, theatres_map, groups, expected_dates,
                         required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Count fresh Phase 1 theatre entries against the configured theatre universe."""
    required_cohorts = set(required_cohorts or [])
    expected_total = 0
    fresh_names = []
    stale_entries = []
    missing_entries = []

    for group in groups:
        expected_date = expected_dates.get(group)
        for theatre in theatres_map.get(group, []):
            if required_cohorts and _theatre_cohort(theatre) not in required_cohorts:
                continue
            expected_total += 1
            name = theatre["name"]
            entry = saved_links.get(name)
            if not entry:
                missing_entries.append(f"{name} ({group}: missing)")
                continue
            entry_date = entry.get("show_date")
            if phase1_date_entry(entry, expected_date):
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


def phase1_link_coverage_for_date_sets(saved_links, theatres_map, groups, expected_date_sets,
                                        required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Count fresh Phase 1 entries across every required show date."""
    required_cohorts = set(required_cohorts or [])
    expected_total = 0
    fresh_names = []
    stale_entries = []
    missing_entries = []
    by_date = {}

    for group in groups:
        for expected_date in expected_date_sets.get(group, []):
            by_date.setdefault(expected_date, {"expected": 0, "fresh": 0})
            for theatre in theatres_map.get(group, []):
                if required_cohorts and _theatre_cohort(theatre) not in required_cohorts:
                    continue
                expected_total += 1
                by_date[expected_date]["expected"] += 1
                name = theatre["name"]
                entry = saved_links.get(name)
                label = f"{name} ({group}: expected={expected_date})"
                if not entry:
                    missing_entries.append(f"{label}, missing")
                    continue
                entry_date = entry.get("show_date")
                if phase1_date_entry(entry, expected_date):
                    fresh_names.append(f"{name}|{group}|{expected_date}")
                    by_date[expected_date]["fresh"] += 1
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
        "by_date": dict(sorted(by_date.items())),
    }


def phase1_required_link_coverage(saved_links, theatres_map, groups, expected_dates,
                                  collection_dates_by_group,
                                  required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Coverage report for the exact Phase 1 contract the later scraper needs."""
    if any(len(dates) > 1 for dates in collection_dates_by_group.values()):
        return phase1_link_coverage_for_date_sets(
            saved_links,
            theatres_map,
            groups,
            collection_dates_by_group,
            required_cohorts=required_cohorts,
        )
    return phase1_link_coverage(
        saved_links,
        theatres_map,
        groups,
        expected_dates,
        required_cohorts=required_cohorts,
    )


def print_phase1_coverage(report, label, min_ratio=PHASE1_MIN_FRESH_LINK_RATIO):
    expected = report["expected_total"]
    fresh = report["fresh_count"]
    ratio = report["ratio"]
    print(f"\n🧯 {label}: {fresh}/{expected} fresh theatres ({ratio:.1%}); minimum {min_ratio:.0%}")
    if report.get("by_date"):
        for date_str, date_report in report["by_date"].items():
            date_expected = date_report["expected"]
            date_fresh = date_report["fresh"]
            date_ratio = (date_fresh / date_expected) if date_expected else 1.0
            print(f"   {date_str}: {date_fresh}/{date_expected} fresh ({date_ratio:.1%})")
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
    for date_str, date_report in (report.get("by_date") or {}).items():
        expected = date_report["expected"]
        if not expected:
            continue
        ratio = date_report["fresh"] / expected
        if ratio < min_ratio:
            fail_phase(
                f"❌ {label} below reliability threshold for {date_str}: "
                f"{date_report['fresh']}/{expected} fresh theatres "
                f"({ratio:.1%}, need {min_ratio:.0%})."
            )


def phase1_forward_cache_is_usable(saved_links, theatres_map, groups,
                                   expected_dates,
                                   min_ratio=PHASE1_MIN_FRESH_LINK_RATIO):
    """True when an older full-weekend link file still covers the target date."""
    report = phase1_link_coverage(
        saved_links,
        theatres_map,
        groups,
        expected_dates,
    )
    return bool(report["expected_total"] and report["ratio"] >= min_ratio)


def phase1_forward_cache_is_usable_for_date_sets(saved_links, theatres_map, groups,
                                                  expected_date_sets,
                                                  min_ratio=PHASE1_MIN_FRESH_LINK_RATIO):
    """True when an older full-weekend link file covers every required show date."""
    report = phase1_link_coverage_for_date_sets(
        saved_links,
        theatres_map,
        groups,
        expected_date_sets,
    )
    if not report["expected_total"] or report["ratio"] < min_ratio:
        return False
    for date_report in report.get("by_date", {}).values():
        expected = date_report["expected"]
        if expected and date_report["fresh"] / expected < min_ratio:
            return False
    return True


def phase1_movie_link_counts(saved_links, groups=None, expected_dates=None,
                             required_cohorts=REQUIRED_PHASE1_COHORTS):
    counts = {}
    required_cohorts = set(required_cohorts or [])
    for entry in saved_links.values():
        if required_cohorts:
            cohort = (entry.get("cohort") or CORE_COHORT).strip().lower()
            if cohort not in required_cohorts:
                continue
        tz = entry.get("tz")
        if groups is not None and tz not in groups:
            continue
        if expected_dates is not None:
            expected_date = expected_dates.get(tz)
            if expected_date and not phase1_date_entry(entry, expected_date):
                continue
        expected_date = expected_dates.get(tz) if expected_dates is not None else None
        movies = phase1_entry_movies(entry, expected_date) if expected_date else (
            entry.get("movies") or {}
        )
        if not movies and expected_dates is None:
            for date_entry in (entry.get("dates") or {}).values():
                for movie, shows in (date_entry.get("movies") or {}).items():
                    if shows:
                        counts[movie] = counts.get(movie, 0) + 1
            continue
        for movie, shows in movies.items():
            if shows:
                counts[movie] = counts.get(movie, 0) + 1
    return counts


def _unique_market_titles(poly_markets):
    titles = []
    seen = set()
    for market in poly_markets or []:
        title = (market.get("movie_title") or "").strip()
        if title and title not in seen:
            titles.append(title)
            seen.add(title)
    return titles


def phase1_movie_link_counts_by_slice(saved_links, groups, expected_date_sets,
                                      required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Count movie links by timezone/show-date so new-market gaps cannot hide."""
    counts = {}
    required_cohorts = set(required_cohorts or [])
    groups = set(groups or [])
    for entry in saved_links.values():
        if required_cohorts:
            cohort = (entry.get("cohort") or CORE_COHORT).strip().lower()
            if cohort not in required_cohorts:
                continue
        tz = entry.get("tz")
        if groups and tz not in groups:
            continue
        for expected_date in expected_date_sets.get(tz, []):
            movies = phase1_entry_movies(entry, expected_date)
            for movie, shows in movies.items():
                if shows:
                    key = (tz, expected_date, movie)
                    counts[key] = counts.get(key, 0) + 1
    return counts


def active_market_phase1_link_gaps(poly_markets, saved_links, groups, expected_date_sets,
                                   min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                                   required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Return active movie/timezone/date slices with no usable Phase 1 links."""
    counts = phase1_movie_link_counts_by_slice(
        saved_links,
        groups,
        expected_date_sets,
        required_cohorts=required_cohorts,
    )
    gaps = []
    for title in _unique_market_titles(poly_markets):
        for group in groups:
            for expected_date in expected_date_sets.get(group, []):
                fresh = counts.get((group, expected_date, title), 0)
                if fresh < min_theatres:
                    gaps.append({
                        "movie_title": title,
                        "timezone": group,
                        "show_date": expected_date,
                        "fresh_theatres": fresh,
                        "required_theatres": min_theatres,
                    })
    return gaps


def require_active_market_phase1_links(poly_markets, saved_links, groups, expected_date_sets,
                                       label,
                                       min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                                       required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Fail loudly when a live market would be silently skipped for a TZ/date."""
    gaps = active_market_phase1_link_gaps(
        poly_markets,
        saved_links,
        groups,
        expected_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    if not gaps:
        return

    print(f"\n❌ {label}: active market(s) missing Phase 1 movie links")
    for gap in gaps[:20]:
        print(
            "    - "
            f"{gap['movie_title']} {gap['show_date']} {gap['timezone']}: "
            f"{gap['fresh_theatres']}/{gap['required_theatres']} theatres"
        )
    if len(gaps) > 20:
        print(f"    ... and {len(gaps) - 20} more")
    fail_phase(
        f"❌ {label} has active Polymarket movie(s) with zero current AMC links. "
        "Run Phase 1 collect-links for the missing timezone/date before scraping."
    )


def warn_active_market_phase1_link_gaps(poly_markets, saved_links, groups, expected_date_sets,
                                        label,
                                        min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                                        required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Log active movie link gaps without blocking partial regular seat data."""
    gaps = active_market_phase1_link_gaps(
        poly_markets,
        saved_links,
        groups,
        expected_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    if not gaps:
        return []

    print(f"\n⚠️  {label}: active movie Phase 1 link gap(s); continuing with linked movies")
    for gap in gaps[:20]:
        print(
            "    - "
            f"{gap['movie_title']} {gap['show_date']} {gap['timezone']}: "
            f"{gap['fresh_theatres']}/{gap['required_theatres']} theatres"
        )
    if len(gaps) > 20:
        print(f"    ... and {len(gaps) - 20} more")
    return gaps


def snapshot_preserved_phase1_fallback_gaps(poly_markets, fresh_links, merged_links,
                                            groups, expected_date_sets,
                                            min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                                            required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Fresh Phase 1 gaps that only pass because snapshot-preserved links exist."""
    fresh_gaps = active_market_phase1_link_gaps(
        poly_markets,
        fresh_links,
        groups,
        expected_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    if not fresh_gaps:
        return []
    merged_gaps = active_market_phase1_link_gaps(
        poly_markets,
        merged_links,
        groups,
        expected_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    still_missing = {
        (gap["movie_title"], gap["timezone"], gap["show_date"])
        for gap in merged_gaps
    }
    return [
        gap for gap in fresh_gaps
        if (gap["movie_title"], gap["timezone"], gap["show_date"]) not in still_missing
    ]


def repairable_phase1_gaps(gaps):
    return [
        gap for gap in gaps
        if phase1_target_date_is_repairable(gap["timezone"], gap["show_date"])
    ]


def remove_snapshot_links_for_gaps(snapshot_links, gaps):
    """Drop preserved snapshot links for repairable active-movie gaps."""
    if not gaps:
        return snapshot_links or {}
    gap_keys = {
        (gap["timezone"], gap["show_date"], gap["movie_title"])
        for gap in gaps
    }
    filtered = {}
    for theatre_name, entry in (snapshot_links or {}).items():
        if not entry:
            continue
        entry_tz = entry.get("tz") or entry.get("timezone") or ""
        kept_entry = dict(entry)
        kept_dates = {}
        for date_str, date_entry in (entry.get("dates") or {}).items():
            kept_date = dict(date_entry)
            kept_movies = {}
            for movie, shows in (date_entry.get("movies") or {}).items():
                key = (entry_tz, date_str, movie)
                if key in gap_keys:
                    continue
                if shows:
                    kept_movies[movie] = shows
            if kept_movies:
                kept_date["movies"] = kept_movies
                kept_dates[date_str] = kept_date
        if kept_dates:
            kept_entry["dates"] = kept_dates
        else:
            kept_entry.pop("dates", None)

        top_level_movies = {}
        for movie, shows in (entry.get("movies") or {}).items():
            key = (entry_tz, entry.get("show_date", ""), movie)
            if key in gap_keys:
                continue
            if shows:
                top_level_movies[movie] = shows
        if top_level_movies:
            kept_entry["movies"] = top_level_movies
        else:
            kept_entry.pop("movies", None)

        if kept_entry.get("dates") or kept_entry.get("movies"):
            filtered[theatre_name] = kept_entry
    return filtered


async def repair_regular_snapshot_preserved_fallbacks_async(
        poly_markets, saved_links, snapshot_preserved_links,
        groups, expected_date_sets):
    """Repair fresh Phase 1 gaps before preserved snapshot links can mask them.

    Preserved snapshot links are useful when AMC has already rolled a show date
    off the public listing. For current/future show dates, though, they should
    never be the first successful source for an active movie slice: rebuild
    Phase 1 first when possible, then drop the preserved active-movie slice
    if fresh links are still missing. That keeps regular data partial but clean.
    """
    if not snapshot_preserved_links:
        return saved_links, {}, []

    merged_links = merge_snapshot_links_into_phase1_saved_links(
        saved_links,
        snapshot_preserved_links,
    )
    fallback_gaps = snapshot_preserved_phase1_fallback_gaps(
        poly_markets,
        saved_links,
        merged_links,
        groups,
        expected_date_sets,
    )
    repairable_gaps = repairable_phase1_gaps(fallback_gaps)
    remaining_gaps = fallback_gaps
    if repairable_gaps:
        repair_slices = sorted({
            (gap["timezone"], gap["show_date"]) for gap in repairable_gaps
        })
        print(
            "\n🔧 Regular Phase 2 fresh-link repair: snapshot-preserved links "
            "would mask active movie gap(s)."
        )
        for group, date_str in repair_slices:
            missing = sorted({
                gap["movie_title"]
                for gap in repairable_gaps
                if gap["timezone"] == group and gap["show_date"] == date_str
            })
            print(f"    - repairing {group} {date_str}: {', '.join(missing)}")
            try:
                await run_collect_links_async(group, target_date=date_str, full_weekend=False)
            except SystemExit as e:
                print(
                    f"      ⚠️  fresh-link repair did not complete "
                    f"(exit {getattr(e, 'code', 1)}) — continuing with the "
                    "partial link cache"
                )
            except Exception as e:
                print(
                    f"      ⚠️  fresh-link repair errored ({e}) — continuing "
                    "with the partial link cache"
                )

        try:
            with open(LINKS_JSON) as f:
                reloaded = json.load(f).get("theatres", {})
            saved_links = sanitize_phase1_links_for_current_window(reloaded)
        except Exception as e:
            fail_phase(f"❌ Could not reload repaired Phase 1 links: {e}")

        merged_links = merge_snapshot_links_into_phase1_saved_links(
            saved_links,
            snapshot_preserved_links,
        )
        remaining_gaps = snapshot_preserved_phase1_fallback_gaps(
            poly_markets,
            saved_links,
            merged_links,
            groups,
            expected_date_sets,
        )

    if remaining_gaps:
        print(
            "\n⚠️  Fresh Phase 1 links are missing for active movie slices; "
            "dropping snapshot-preserved links for those slices and continuing "
            "with clean partial data."
        )
        issues = []
        for gap in remaining_gaps[:20]:
            issue = (
                "Fresh Phase 1 link gap: "
                f"{gap['movie_title']} {gap['show_date']} {gap['timezone']} "
                f"had {gap['fresh_theatres']}/{gap['required_theatres']} "
                "fresh theatres; preserved links were not used"
            )
            issues.append(issue)
            print(f"    - {issue}")
        if len(remaining_gaps) > 20:
            print(f"    ... and {len(remaining_gaps) - 20} more")
        filtered_snapshot_links = remove_snapshot_links_for_gaps(
            snapshot_preserved_links,
            remaining_gaps,
        )
        return saved_links, filtered_snapshot_links, issues

    return saved_links, snapshot_preserved_links, []


def snapshot_usable_date_sets(poly_markets, saved_links, groups, requested_date_sets,
                              min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                              required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Keep snapshot dates with at least one active movie Phase 1 link.

    Snapshot probes are a future-demand layer. A missing remaining-weekend movie
    slice should not throw away snapshot data for the whole timezone, and a
    missing lower-volume movie should not block another active movie with links.
    """
    usable = {}
    skipped = []
    titles = _unique_market_titles(poly_markets)
    counts = phase1_movie_link_counts_by_slice(
        saved_links,
        groups,
        requested_date_sets,
        required_cohorts=required_cohorts,
    )
    for group in groups:
        for date_str in requested_date_sets.get(group, []):
            gaps = []
            present_titles = []
            for title in titles:
                fresh = counts.get((group, date_str, title), 0)
                if fresh >= min_theatres:
                    present_titles.append(title)
                    continue
                gaps.append({
                    "movie_title": title,
                    "timezone": group,
                    "show_date": date_str,
                    "fresh_theatres": fresh,
                    "required_theatres": min_theatres,
                })
            if present_titles:
                usable.setdefault(group, []).append(date_str)
            if gaps:
                skipped.append({
                    "timezone": group,
                    "show_date": date_str,
                    "missing_movies": sorted({gap["movie_title"] for gap in gaps}),
                    "gaps": gaps,
                    "date_skipped": not present_titles,
                })
    return usable, skipped


async def repair_snapshot_phase1_links_async(poly_markets, saved_links, groups, requested_date_sets,
                                             min_theatres=PHASE1_MIN_MOVIE_LINK_THEATRES,
                                             required_cohorts=REQUIRED_PHASE1_COHORTS,
                                             link_filter_names=None):
    """Try to fill missing snapshot link slices, then return usable partial coverage.

    Snapshot data is better partial than absent. This repair is deliberately
    targeted to the missing timezone/date slices and does not convert snapshot
    runs into a broad Phase 1 rebuild.
    """
    validation_links = (
        filter_saved_links_by_names(saved_links, link_filter_names)
        if link_filter_names is not None else saved_links
    )
    usable, skipped = snapshot_usable_date_sets(
        poly_markets,
        validation_links,
        groups,
        requested_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    if not skipped:
        return saved_links, usable, skipped

    repairs = sorted({
        (item["timezone"], item["show_date"])
        for item in skipped
    })
    print("\n🔧 Snapshot link repair: missing active movie links detected")
    for group, date_str in repairs:
        missing_movies = sorted({
            movie
            for item in skipped
            if item["timezone"] == group and item["show_date"] == date_str
            for movie in item["missing_movies"]
        })
        print(
            f"    - repairing {group} {date_str}: "
            f"{', '.join(missing_movies)}"
        )
        try:
            await run_collect_links_async(group, target_date=date_str, full_weekend=False)
        except SystemExit as e:
            print(
                f"      ⚠️  targeted Phase 1 repair did not complete "
                f"(exit {getattr(e, 'code', 1)}) — keeping partial snapshot data"
            )
        except Exception as e:
            print(
                f"      ⚠️  targeted Phase 1 repair errored ({e}) — "
                "keeping partial snapshot data"
            )

    repaired_links = saved_links
    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                repaired_links = sanitize_phase1_links_for_current_window(
                    json.load(f).get("theatres", {})
                )
        except Exception as e:
            print(f"      ⚠️  Could not reload repaired Phase 1 links: {e}")

    usable, skipped = snapshot_usable_date_sets(
        poly_markets,
        (
            filter_saved_links_by_names(repaired_links, link_filter_names)
            if link_filter_names is not None else repaired_links
        ),
        groups,
        requested_date_sets,
        min_theatres=min_theatres,
        required_cohorts=required_cohorts,
    )
    return repaired_links, usable, skipped


def filter_markets_with_phase1_links(poly_markets, saved_links, min_theatres=1,
                                     groups=None, expected_dates=None,
                                     required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Drop Polymarket markets that have no fresh AMC Phase 1 links."""
    if not poly_markets:
        return []

    linked_counts = phase1_movie_link_counts(
        saved_links,
        groups=groups,
        expected_dates=expected_dates,
        required_cohorts=required_cohorts,
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


def filter_markets_with_phase1_links_for_date_sets(poly_markets, saved_links,
                                                   min_theatres=1,
                                                   groups=None,
                                                   expected_date_sets=None,
                                                   required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Keep markets with links in at least one requested timezone/date slice."""
    if not poly_markets:
        return []
    groups = list(groups or [])
    expected_date_sets = expected_date_sets or {}
    linked_counts = phase1_movie_link_counts_by_slice(
        saved_links,
        groups,
        expected_date_sets,
        required_cohorts=required_cohorts,
    )
    filtered = []
    skipped = []
    for market in poly_markets:
        title = market.get("movie_title", "")
        has_links = any(
            linked_counts.get((group, date_str, title), 0) >= min_theatres
            for group in groups
            for date_str in expected_date_sets.get(group, [])
        )
        if has_links:
            filtered.append(market)
        else:
            skipped.append(title or market.get("question", "unknown market"))

    if skipped:
        print("\n↷ Skipping Polymarket market(s) with no requested AMC Phase 1 links:")
        for title in skipped:
            print(f"    - {title}")
    return filtered


def linked_markets_for_phase1_saved_links(poly_markets, saved_links, groups,
                                          expected_date_sets,
                                          min_theatres=1,
                                          required_cohorts=REQUIRED_PHASE1_COHORTS):
    """Return markets with at least one usable link in the requested TZ/date scope."""
    expected_date_sets = expected_date_sets or {}
    if any(len(dates or []) > 1 for dates in expected_date_sets.values()):
        return filter_markets_with_phase1_links_for_date_sets(
            poly_markets,
            saved_links,
            min_theatres=min_theatres,
            groups=groups,
            expected_date_sets=expected_date_sets,
            required_cohorts=required_cohorts,
        )
    expected_dates = {
        group: dates[0]
        for group, dates in expected_date_sets.items()
        if dates
    }
    return filter_markets_with_phase1_links(
        poly_markets,
        saved_links,
        min_theatres=min_theatres,
        groups=groups,
        expected_dates=expected_dates,
        required_cohorts=required_cohorts,
    )


# ─── Main Orchestrator ───────────────────────────────────────────────────────

async def _scrape_theatre(browser, theatre, date_str, movie_titles, market_urls,
                          weekend_of="", run_id="", saved_movies=None, test_mode=False,
                          capture_pre_reservations=False):
    """
    Scrape one theatre's seat maps using pre-collected Phase 1 showtime IDs.

    saved_movies: required — {movie_title: [{showtime, showtime_id, format}]}
                  collected during Phase 1 (collect-links run).
                  If None the theatre is skipped (Phase 1 must run first).

    Returns (results_list, issues_list, csv_rows_list, pre_reservation_rows_list).
    """
    if saved_movies is None:
        return [], [f"{theatre['name']}: no Phase 1 links — skipped"], [], []

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
    pre_reservation_rows = []
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

        # Build showtime work from saved Phase 1 links.
        # Phase 1 already selected the right local-time window — use those links
        # regardless of what time Phase 2 runs (avoids cross-midnight filter failures).
        # Only use titles from the current discovery/fallback list. The saved
        # links file is merged across runs, so stale bad titles should not be
        # re-scraped just because they are still present in showtime-links.json.
        movie_shows_map = {}
        for movie_title in movie_titles:
            entries = filter_showtime_entries_for_collection_window(
                saved_movies.get(movie_title, []),
                date_str,
            )
            if not entries:
                continue
            started = entries
            seen = set()
            shows = []
            for e in sorted(started,
                            key=lambda x: -(parse_showtime_hour(x.get("showtime", "")) or 0)):
                showtime_id = str(e.get("showtime_id", "") or "").strip()
                key = showtime_id or (e.get("format", "Standard"), e.get("showtime", "?"))
                if key in seen:
                    continue
                seen.add(key)
                source = e.get("source") or "saved link"
                shows.append((
                    {"showtime": e["showtime"], "showtime_id": e["showtime_id"],
                     "format": e.get("format", "Standard"), "flags": "", "source": source},
                    f"{e.get('format','Standard')} @ {e['showtime']} ({source})",
                ))
            shows.sort(key=lambda x: -get_format_priority(x[0].get("format", "")))
            # In test mode, only try the single highest-priority show per movie
            if test_mode:
                shows = shows[:1]
            movie_shows_map[movie_title] = shows

        queue_blocked = False
        for movie_title, showtime_work in movie_shows_map.items():
            if queue_blocked:
                break
            if not showtime_work:
                continue

            for show, reason in showtime_work:
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
                    note = f"{flags}. {reason}" if flags else reason
                    note = add_showtime_window_note(note)
                    if _theatre_cohort(theatre) == EXPANSION_COHORT:
                        note = f"{note}; cohort=expansion"
                    if (
                        capture_pre_reservations
                        and should_record_pre_reservation_snapshot(delta_minutes)
                    ):
                        pre_reservation_rows.append(
                            build_pre_reservation_row(
                                theatre, tz, movie_title, show, seat_data,
                                weekend_of, run_id, today, day_of_week,
                                check_time, delta_minutes,
                                market_url=market_urls.get(movie_title, ""),
                                note=note,
                            )
                        )
                    csv_rows.append([
                        weekend_of, run_id,
                        today, day_of_week, theatre["name"], theatre.get("city", theatre.get("dma", "")),
                        tz, movie_title, market_urls.get(movie_title, ""),
                        st, check_time, delta_minutes,
                        "", fmt,
                        seat_data["total_seats"], seat_data["seats_sold"],
                        seat_data["seats_available"], occ,
                        amc_url, note,
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

    return results, issues, csv_rows, pre_reservation_rows


async def _collect_links_theatre(browser, theatre, date_str, movie_titles):
    """
    Phase 1: Visit a theatre's showtime page and save target-window showtime IDs.
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
            collection_window = filter_showtime_entries_for_collection_window(
                matching,
                date_str,
            )
            if collection_window:
                collected[movie_title] = [
                    {"showtime": s.get("showtime"), "showtime_id": s.get("showtime_id"),
                     "format": s.get("format", "Standard")}
                    for s in collection_window
                ]
    except Exception as e:
        print(f"  ⚠️  {theatre['name']}: {e}")
    finally:
        try:
            await asyncio.wait_for(context.close(), timeout=10)
        except Exception:
            pass
    return collected


def _cap_phase1_visits(all_theatres, expected_dates, max_visits):
    """Keep Phase 1 inside a predictable browser-work budget."""
    total = len(all_theatres)
    if not max_visits or total <= max_visits:
        return all_theatres, []

    required = [
        theatre for theatre in all_theatres
        if theatre.get("_date") == expected_dates.get(theatre.get("_tz"))
    ]
    optional = [
        theatre for theatre in all_theatres
        if theatre.get("_date") != expected_dates.get(theatre.get("_tz"))
    ]
    if len(required) > max_visits:
        fail_phase(
            f"❌ Phase 1 capacity cap {max_visits} is below required same-day "
            f"theatre visits ({len(required)}). Increase PHASE1_MAX_THEATRE_DATE_VISITS."
        )
    kept_optional = optional[:max(0, max_visits - len(required))]
    skipped = optional[len(kept_optional):]
    return required + kept_optional, skipped


def phase1_collection_batches(all_theatres, expected_dates):
    """Order Phase 1 work so today's showtime links cannot starve behind future cache work."""
    buckets = [
        ("core current-day pass", []),
        ("expansion current-day pass", []),
        ("core forward-cache pass", []),
        ("expansion forward-cache pass", []),
    ]
    by_label = dict(buckets)

    for theatre in all_theatres:
        is_current_day = theatre.get("_date") == expected_dates.get(theatre.get("_tz"))
        is_expansion = _theatre_cohort(theatre) == EXPANSION_COHORT
        if is_current_day and is_expansion:
            by_label["expansion current-day pass"].append(theatre)
        elif is_current_day:
            by_label["core current-day pass"].append(theatre)
        elif is_expansion:
            by_label["expansion forward-cache pass"].append(theatre)
        else:
            by_label["core forward-cache pass"].append(theatre)

    return [(label, rows) for label, rows in buckets if rows]


async def run_collect_links_async(tz_group="ALL", target_date=None,
                                  full_weekend=None):
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
    if full_weekend is None:
        full_weekend = PHASE1_FULL_WEEKEND_LINKS
    if target_date:
        try:
            target_ref_dt = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            fail_phase(f"❌ Invalid Phase 1 target date: {target_date}")
    else:
        target_ref_dt = ref_local
    live_markets = fetch_polymarket_box_office()
    preopening_full_weekend = bool(full_weekend and target_ref_dt.weekday() in (0, 1, 2))
    current_weekend = phase1_weekend_anchor(target_ref_dt, full_weekend=full_weekend)
    poly_markets = select_collection_markets(
        live_markets,
        target_ref_dt,
        "Phase 1",
        weekend_override=current_weekend,
        prefer_live_markets=preopening_full_weekend,
    )

    if not poly_markets:
        if POLYMARKET_LAST_FETCH_OK and POLYMARKET_LAST_PARSE_OK:
            print("↷ Polymarket answered and parsed fine but lists no box "
                  "office market for this weekend — nothing to collect "
                  "(clean skip).")
            return
        fail_phase("❌ No active Polymarket box office markets and no saved CSV fallback.")

    movie_titles = [m["movie_title"] for m in poly_markets]
    missing_metadata = movie_titles_missing_metadata(movie_titles)
    if missing_metadata:
        names = ", ".join(missing_metadata)
        print(f"⚠️  No movie-metadata.csv row (or empty audience_type) for: {names}")
        print(f"::warning::tracked film(s) missing audience metadata: {names} — "
              f"the broad_family cross-chain gate and audience-aware Friday "
              f"multiplier will be OFF for their predictions; add a row to "
              f"box-office-tracker/data/movie-metadata.csv before Thursday previews")
    today = target_date or ref_local.strftime("%Y-%m-%d")
    groups = phase1_groups(tz_group)
    collection_dates_by_group = {
        group: phase1_collection_dates(
            group,
            target_date=target_date,
            ref_dt=target_ref_dt if target_date else local_now(group),
            full_weekend=full_weekend,
        )
        for group in groups
    }
    expected_dates = {group: dates[0] for group, dates in collection_dates_by_group.items()}
    all_theatres = []
    for group in groups:
        for date_str in collection_dates_by_group[group]:
            for t in theatres_map.get(group, []):
                all_theatres.append({**t, "_tz": group, "_date": date_str})
    all_theatres.sort(key=_theatre_sort_key)
    all_theatres, capacity_skipped = _cap_phase1_visits(
        all_theatres,
        expected_dates,
        PHASE1_MAX_THEATRE_DATE_VISITS,
    )

    print(f"\n🏛️  Visiting {len(all_theatres)} theatres to collect links...")
    print(f"   Cohorts: {_cohort_counts(all_theatres)}")
    total_requested_visits = len(all_theatres) + len(capacity_skipped)
    print(f"   Theatre-date visits: {len(all_theatres)}/{total_requested_visits} "
          f"planned; cap {PHASE1_MAX_THEATRE_DATE_VISITS}")
    if any(len(v) > 1 for v in collection_dates_by_group.values()):
        print("   Full-weekend link cache enabled for Wednesday/Thursday run")
    if capacity_skipped:
        print(f"   ⚠️  Capacity cap skipped {len(capacity_skipped)} optional future-date theatre visits")

    # Store the opening-weekend Friday anchor, not the calendar day. Thursday
    # Phase 1 runs collect links for Friday's opening weekend and must merge
    # with later TZ-group runs and pass Phase 2 validation that same night.
    links = {
        "date": current_weekend,
        "weekend_of": current_weekend,
        "collected_local_date": today,
        "collected_at": datetime.now().isoformat(),
        "showtime_window_version": SHOWTIME_WINDOW_VERSION,
        "showtime_windows": {
            "default": f"{DEFAULT_COLLECTION_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
            "Saturday": f"{WEEKEND_FULL_DAY_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
            "Sunday": f"{WEEKEND_FULL_DAY_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
        },
        "theatres": {},
    }
    sem = asyncio.Semaphore(MAX_CONCURRENT_TABS_PHASE1)
    deadline_at = time.monotonic() + PHASE1_DEADLINE_SEC

    def theatre_key(theatre):
        return (
            theatre["name"],
            theatre.get("_tz", ""),
            theatre.get("_date", today),
        )

    theatre_by_key = {theatre_key(t): t for t in all_theatres}

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

        async def collect_with_deadline(theatres, label, budget_sec):
            if not theatres or budget_sec <= 0:
                return []

            tasks = [asyncio.create_task(bounded(t)) for t in theatres]
            done, pending = await asyncio.wait(tasks, timeout=budget_sec)
            if pending:
                elapsed = PHASE1_DEADLINE_SEC - max(0, int(deadline_at - time.monotonic()))
                print(
                    f"\n⏱️  Phase 1 {label} deadline after {elapsed}s — "
                    f"cancelling {len(pending)} pending theatres"
                )
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

            results = []
            for task in done:
                try:
                    results.append(task.result())
                except Exception as e:
                    results.append(e)
            return results

        outcome_by_key = {}

        def merge_outcomes(batch_outcomes):
            for outcome in batch_outcomes:
                if isinstance(outcome, Exception):
                    continue
                name, tz, show_date, _ = outcome
                outcome_by_key[(name, tz, show_date)] = outcome

        async def collect_and_merge(theatres, label):
            if not theatres:
                return
            budget = max(0, int(deadline_at - time.monotonic()))
            if budget <= 0:
                print(f"\n⏱️  Skipping Phase 1 {label} — deadline is exhausted")
                return
            merge_outcomes(await collect_with_deadline(theatres, label, budget))

        async def collect_batch_with_retry(theatres, label):
            await collect_and_merge(theatres, label)

            # Retry theatres that returned 0 showtimes — likely hit rate-limit on first pass.
            failed = [
                theatre
                for theatre in theatres
                if theatre_key(theatre) in outcome_by_key and not outcome_by_key[theatre_key(theatre)][3]
            ]
            if not failed:
                return
            retry_budget = max(0, int(deadline_at - time.monotonic()))
            min_retry_budget = 60 if "forward-cache" in label else 30
            if retry_budget > min_retry_budget:
                print(f"\n🔄 Retrying {len(failed)} {label} theatres that returned 0 showtimes (5s delay)...")
                await asyncio.sleep(5)
                merge_outcomes(
                    await collect_with_deadline(
                        failed,
                        f"{label} retry",
                        max(0, int(deadline_at - time.monotonic())),
                    )
                )
            else:
                print(f"\n⏱️  Skipping retry for {len(failed)} {label} theatres — Phase 1 deadline is near")

        for label, batch_theatres in phase1_collection_batches(all_theatres, expected_dates):
            await collect_batch_with_retry(batch_theatres, label)

        skipped = len(theatre_by_key) - len(outcome_by_key)
        if skipped > 0:
            print(f"  ⏱️  Phase 1 skipped {skipped} theatres before coverage validation")
        outcomes = list(outcome_by_key.values())

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
            theatre = theatre_by_key.get((name, tz, show_date), {})
            entry = links["theatres"].setdefault(name, {
                "tz": tz,
                "cohort": _theatre_cohort(theatre),
                "dates": {},
            })
            entry["tz"] = tz
            entry["cohort"] = _theatre_cohort(theatre)
            entry["showtime_window_version"] = SHOWTIME_WINDOW_VERSION
            entry.setdefault("dates", {})[show_date] = {
                "movies": collected,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "showtime_window_version": SHOWTIME_WINDOW_VERSION,
            }
            if show_date == expected_dates.get(tz) or not entry.get("movies"):
                entry["show_date"] = show_date
                entry["movies"] = collected
            total_links += sum(len(v) for v in collected.values())

    existing = {}
    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                existing = json.load(f)
            existing_weekend = existing.get("weekend_of") or existing.get("date", "")
            if existing_weekend and existing_weekend != current_weekend:
                existing = {}
            elif existing and not phase1_cache_is_mergeable(existing, current_weekend):
                print(
                    "  ⚠️  Existing Phase 1 cache uses an older showtime window "
                    f"({existing.get('showtime_window_version') or 'none'}); starting fresh"
                )
                existing = {}
        except Exception as e:
            print(f"  ⚠️  Could not load existing showtime-links.json ({e}) — starting fresh")
            existing = {}

    # Validate the canonical cache we are about to write, not only the newest
    # refresh batch. This lets preserved same-weekend links cover theatre/date
    # slices that AMC temporarily queued or hid during the refresh.
    links = merge_collected_phase1_links_with_existing_cache(
        links,
        existing,
        current_weekend,
    )

    fresh_report = phase1_required_link_coverage(
        links["theatres"],
        theatres_map,
        groups,
        expected_dates,
        collection_dates_by_group,
    )
    coverage_label = f"Phase 1 collected links for {tz_group}"
    if any(len(dates) > 1 for dates in collection_dates_by_group.values()):
        coverage_label = f"Phase 1 full-weekend links for {tz_group}"

    # SAVE BEFORE THE GATE (audit 2026-08-23): the all-or-nothing coverage
    # fail_phase below used to discard the entire merged link cache — every
    # 100%%-covered date included — over one 85%% date. The merge with the
    # existing cache is a monotonic union, so writing first can only add
    # links; the gate still fails the job red so retry slots keep firing.
    # Atomic write: the commit step may now run after a failure/cancel, and
    # must never see a torn file.
    DATA_DIR.mkdir(exist_ok=True)
    links["showtime_window_version"] = SHOWTIME_WINDOW_VERSION
    links["showtime_windows"] = {
        "default": f"{DEFAULT_COLLECTION_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
        "Saturday": f"{WEEKEND_FULL_DAY_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
        "Sunday": f"{WEEKEND_FULL_DAY_START_HOUR}:00-{COLLECTION_END_HOUR}:00",
    }
    # Use the latest successful Phase 1 refresh time. Weekend Phase 2 runs for
    # MT/PT happen more than 12h after the ET/noon collection window, so keeping
    # the earliest timestamp would incorrectly mark fresh same-day links as stale.
    links["collected_at"] = datetime.now(timezone.utc).isoformat()
    _date_ratios = [
        (dr["fresh"] / dr["expected"])
        for dr in (fresh_report.get("by_date") or {}).values() if dr["expected"]
    ]
    _degraded = bool(fresh_report["expected_total"]) and (
        fresh_report["ratio"] < PHASE1_MIN_FRESH_LINK_RATIO
        or any(r < PHASE1_MIN_FRESH_LINK_RATIO for r in _date_ratios)
    )
    links["link_coverage"] = {
        "ratio": round(fresh_report["ratio"], 4),
        "fresh": fresh_report["fresh_count"],
        "expected": fresh_report["expected_total"],
        "min_ratio": PHASE1_MIN_FRESH_LINK_RATIO,
        "degraded": _degraded,
    }
    _tmp_links = LINKS_JSON.with_suffix(".json.tmp")
    with open(_tmp_links, "w") as f:
        json.dump(links, f, indent=2)
    os.replace(_tmp_links, LINKS_JSON)
    print(f"\n✅ Saved {total_links} showtime links from {len(links['theatres'])} theatres total → {LINKS_JSON}"
          + ("  [DEGRADED — below coverage threshold; retry slots will re-collect]" if _degraded else ""))

    require_phase1_coverage(fresh_report, coverage_label)
    active_link_gaps = warn_active_market_phase1_link_gaps(
        poly_markets,
        links["theatres"],
        groups,
        collection_dates_by_group,
        coverage_label,
    )
    linked_markets = linked_markets_for_phase1_saved_links(
        poly_markets,
        links["theatres"],
        groups,
        collection_dates_by_group,
    )
    if not linked_markets:
        fail_phase(
            f"❌ {coverage_label} has no active Polymarket movie links. "
            "Run Phase 1 collect-links again before scraping."
        )
    if active_link_gaps:
        print(
            f"\n⚠️  {coverage_label}: preserving full active market list "
            "while committing partial timezone links"
        )
    expansion_report = phase1_link_coverage(
        links["theatres"], theatres_map, groups, expected_dates,
        required_cohorts=(EXPANSION_COHORT,),
    )
    if expansion_report["expected_total"]:
        print_phase1_coverage(
            expansion_report,
            f"Phase 1 expansion links for {tz_group}",
            min_ratio=0.0,
        )
    movie_titles = [m["movie_title"] for m in poly_markets]
    fetch_bom_theatre_counts(movie_titles)
    save_polymarket_data(poly_markets, weekend_of=current_weekend)


async def ensure_phase1_links_async(tz_group="ALL"):
    """Self-heal Phase 1 links before regular Phase 2 scraping.

    Theatre coverage alone is not enough: if a new Polymarket movie appears
    after one timezone's Phase 1 run, that timezone can have fresh theatre
    links for older movies while having zero links for the new active title.
    """
    if tz_group == "ALL":
        for group in phase1_groups(tz_group):
            await ensure_phase1_links_async(group)
        return

    theatres_map = load_theatres()
    target_date = phase1_expected_date(tz_group)
    expected_dates = {tz_group: target_date}
    expected_date_sets = {tz_group: [target_date]}
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_weekend = opening_weekend_friday(target_dt)
    saved_links = {}

    if LINKS_JSON.exists():
        try:
            with open(LINKS_JSON) as f:
                links_data = json.load(f)
            links_weekend = links_data.get("weekend_of") or links_data.get("date", "")
            if links_weekend == target_weekend:
                if links_data.get("showtime_window_version") == SHOWTIME_WINDOW_VERSION:
                    saved_links = sanitize_phase1_links_for_current_window(
                        links_data.get("theatres", {})
                    )
                else:
                    print(
                        "\n⚠️  Phase 1 links use an older showtime window; "
                        f"rebuilding {tz_group} links before scraping."
                    )
            elif links_weekend:
                print(
                    f"\n⚠️  Phase 1 links are from weekend {links_weekend}, "
                    f"but {tz_group} needs {target_weekend}."
                )
        except Exception as e:
            print(f"\n⚠️  Could not inspect Phase 1 links before scrape: {e}")

    live_markets = fetch_polymarket_box_office()
    poly_markets = select_collection_markets(
        live_markets,
        target_dt,
        "Phase 1 repair",
        weekend_override=target_weekend,
    )
    report = phase1_link_coverage(saved_links, theatres_map, [tz_group], expected_dates)
    movie_gaps = active_market_phase1_link_gaps(
        poly_markets,
        saved_links,
        [tz_group],
        expected_date_sets,
    )
    if (
        (not report["expected_total"] or report["ratio"] >= PHASE1_MIN_FRESH_LINK_RATIO)
        and not movie_gaps
    ):
        print_phase1_coverage(report, f"Phase 1 preflight for {tz_group}")
        return

    print_phase1_coverage(report, f"Phase 1 preflight for {tz_group}")
    if movie_gaps:
        print(f"\n🔧 Phase 1 preflight for {tz_group}: active movie link gap(s) detected:")
        for gap in movie_gaps[:20]:
            print(
                "    - "
                f"{gap['movie_title']} {gap['show_date']} {gap['timezone']}: "
                f"{gap['fresh_theatres']}/{gap['required_theatres']} theatres"
            )
        if len(movie_gaps) > 20:
            print(f"    ... and {len(movie_gaps) - 20} more")
    if not phase1_target_date_is_repairable(tz_group, target_date):
        if report["fresh_count"]:
            print(
                f"\n↷ Skipping Phase 1 repair for {tz_group} {target_date}: "
                "the show date has already rolled off AMC. Regular Phase 2 "
                "will use cached links and filter any unlinked active movie."
            )
            return
        if not phase1_target_date_is_within_theatre_day(tz_group, target_date):
            fail_phase(
                f"❌ Phase 1 links for {tz_group} {target_date} are missing or stale, "
                "and the show date has already rolled off AMC, so an automatic "
                "repair cannot rebuild them."
            )
        print(
            f"\n⚠️  Phase 1 links for {tz_group} {target_date} are missing and the "
            f"calendar date has rolled over, but the theatre day has not and "
            f"there are no usable cached links — attempting a last-resort repair "
            f"instead of failing the whole timezone."
        )
    print(f"\n🔧 Rebuilding Phase 1 links for {tz_group} show date {target_date} before scraping.")
    rebuild_incomplete = False
    try:
        await run_collect_links_async(tz_group, target_date=target_date, full_weekend=False)
    except SystemExit as e:
        # The rebuild saves the merged cache BEFORE its coverage gate, so a
        # below-threshold rebuild leaves a usable partial file. Letting the
        # SystemExit propagate here killed the entire regular leg — trading
        # an ~88%% panel for 0%% of an unrecoverable night.
        rebuild_incomplete = True
        print(
            f"\n⚠️  Phase 1 rebuild for {tz_group} {target_date} did not meet "
            f"its coverage gate (exit {getattr(e, 'code', 1)}) — evaluating "
            "the partial link cache instead of failing the leg."
        )
    except Exception as e:
        rebuild_incomplete = True
        print(
            f"\n⚠️  Phase 1 rebuild for {tz_group} {target_date} errored ({e}) "
            "— evaluating whatever link cache is on disk instead of failing "
            "the leg."
        )

    try:
        with open(LINKS_JSON) as f:
            repaired_links = json.load(f).get("theatres", {})
    except Exception as e:
        fail_phase(f"❌ Could not reload Phase 1 links after rebuild for {tz_group}: {e}")
    repaired_report = phase1_link_coverage(repaired_links, theatres_map, [tz_group], expected_dates)
    repaired_label = f"Phase 1 repaired links for {tz_group}"
    if not rebuild_incomplete:
        require_phase1_coverage(repaired_report, repaired_label)
    else:
        print_phase1_coverage(repaired_report, repaired_label,
                              min_ratio=PHASE1_MIN_FRESH_LINK_RATIO)
        partial_ratio = (repaired_report["ratio"]
                         if repaired_report["expected_total"] else 1.0)
        if partial_ratio < REGULAR_PHASE2_PARTIAL_LINK_FLOOR:
            fail_phase(
                f"❌ {repaired_label}: {partial_ratio:.1%} fresh theatre "
                f"coverage is below the partial-links floor "
                f"({REGULAR_PHASE2_PARTIAL_LINK_FLOOR:.0%}) — a wall profile, "
                "too sparse to trust for a regular scrape."
            )
        print(
            f"::warning::{repaired_label}: proceeding with PARTIAL fresh links "
            f"({partial_ratio:.1%} < {PHASE1_MIN_FRESH_LINK_RATIO:.0%}); "
            "tonight's panel is smaller and coverage percentages this run are "
            "fractions of the shrunken panel"
        )
    require_active_market_phase1_links(
        poly_markets,
        repaired_links,
        [tz_group],
        expected_date_sets,
        f"Phase 1 repaired links for {tz_group}",
    )


async def run_async(tz_group="ALL", force=False, test_max=None,
                    capture_pre_reservations=False, snapshots_only=False,
                    repair_snapshot_links=False):
    """
    Main entry point (async).
    Parallelizes browser tabs using a semaphore. Snapshot-only probes default
    lower so they can coexist with the model-driving scrape without stampeding
    AMC seat-map requests.
    """
    max_concurrent_tabs = phase2_max_concurrent_tabs(snapshots_only=snapshots_only)
    print(f"{'='*60}")
    print(f"🎬 Box Office Tracker (Playwright) — {tz_group} Group")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Concurrency: {max_concurrent_tabs} tabs")
    if snapshots_only:
        print("   Snapshot-only: on (seat-counts.csv will not be appended)")
        if repair_snapshot_links:
            print("   Snapshot link repair: on (targeted missing date slices only)")
    print(f"{'='*60}")

    ensure_csv_header()
    if capture_pre_reservations:
        ensure_pre_reservation_header()

    # Use tz-adjusted local date (server clock is UTC; runs after midnight UTC
    # would otherwise stamp tomorrow's date on tonight's data).
    groups_to_check = phase1_groups(tz_group)
    # For mixed-TZ runs use ET as the reference (most conservative, first to tick over)
    ref_tz = tz_group if tz_group != "ALL" else "ET"
    local = local_now(ref_tz)
    today = local.strftime("%Y-%m-%d")
    local_dow = local.strftime("%A")


    theatres_map = load_theatres()
    snapshot_theatre_names = None
    coverage_theatres_map = theatres_map
    snapshot_selection_groups, snapshot_selection_date_sets = snapshot_global_selection_inputs(
        theatres_map
    )
    if snapshots_only:
        snapshot_theatre_names = select_snapshot_theatre_names(
            theatres_map,
            groups=snapshot_selection_groups,
        )
        coverage_theatres_map = filter_theatres_map_by_names(
            theatres_map,
            snapshot_theatre_names,
        )
        selected_by_group = {
            group: sum(
                1
                for theatre in theatres_map.get(group, [])
                if theatre.get("name") in snapshot_theatre_names
            )
            for group in groups_to_check
        }
        print(
            "   Snapshot theatre cap candidates: "
            f"{sum(selected_by_group.values())}/{SNAPSHOT_TOP_THEATRE_CAP} "
            f"selected for this run ({selected_by_group})"
        )

    # Step 1: Get Polymarket movies
    # Step 2: Build flat list of theatres to scrape
    snapshot_preopening = bool(snapshots_only and local.weekday() in (0, 1, 2))
    weekend = (
        phase1_weekend_anchor(local, full_weekend=True)
        if snapshot_preopening
        else opening_weekend_friday(local)
    )
    live_markets = fetch_polymarket_box_office()
    poly_markets = select_collection_markets(
        live_markets,
        local,
        "Phase 2",
        weekend_override=weekend,
        prefer_live_markets=snapshot_preopening,
    )

    if not poly_markets:
        if POLYMARKET_LAST_FETCH_OK and POLYMARKET_LAST_PARSE_OK:
            issue = ("No box office market listed on Polymarket for this "
                     "weekend — nothing to scrape (clean skip)")
            print(f"\n↷ {issue}")
            log_run(tz_group, [], [], [issue])
            return
        log_run(tz_group, [], [], ["No active Polymarket box office markets found"])
        fail_phase("\n❌ No active box office markets on Polymarket and no saved CSV fallback.")

    run_id = local.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    collection_dates_by_group = phase2_collection_dates_by_group(
        groups_to_check,
        snapshots_only=snapshots_only,
    )
    if snapshots_only:
        groups_to_check = [
            group for group in groups_to_check
            if collection_dates_by_group.get(group)
        ]
        collection_dates_by_group = {
            group: collection_dates_by_group[group]
            for group in groups_to_check
        }
        if not groups_to_check:
            issue = (
                "No future snapshot show dates remain; same-day actuals are "
                "collected by the regular Phase 2 scrape."
            )
            print(f"\n↷ {issue}")
            log_run(tz_group, [m["movie_title"] for m in poly_markets], [], [issue], run_id=run_id)
            return
    expected_dates = (
        {
            group: dates[0]
            for group, dates in collection_dates_by_group.items()
            if dates
        }
        if snapshots_only
        else phase2_expected_dates(groups_to_check, snapshots_only=False)
    )
    coverage_dates_by_group = (
        collection_dates_by_group
        if snapshots_only
        else {group: [expected_dates[group]] for group in groups_to_check}
    )
    if snapshots_only:
        print("   Snapshot show dates: " + ", ".join(
            f"{group}={','.join(dates)}"
            for group, dates in collection_dates_by_group.items()
        ))

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
                if links_data.get("showtime_window_version") != SHOWTIME_WINDOW_VERSION:
                    message = (
                        "\n⚠️  showtime-links.json was generated with an older showtime "
                        "window; Saturday/Sunday need 10am-11pm links."
                    )
                    if snapshots_only and repair_snapshot_links:
                        print(message + " Snapshot repair will rebuild the requested slices.")
                        saved_links = {}
                        collected_at_str = ""
                    else:
                        fail_phase(message + " Run Phase 1 collect-links first.")
                else:
                    saved_links = sanitize_phase1_links_for_current_window(
                        links_data.get("theatres", {})
                    )
                age_str = ""
                if collected_at_str:
                    collected_at = datetime.fromisoformat(collected_at_str.replace("Z", "+00:00"))
                    if collected_at.tzinfo is None:
                        collected_at = collected_at.replace(tzinfo=timezone.utc)
                    age_hours = (datetime.now(timezone.utc) - collected_at).total_seconds() / 3600
                    age_str = f" from {age_hours:.1f}h ago"
                    if age_hours > 12:
                        has_forward_cache = phase1_forward_cache_is_usable_for_date_sets(
                            saved_links,
                            coverage_theatres_map,
                            groups_to_check,
                            coverage_dates_by_group,
                        )
                        if not force and not has_forward_cache:
                            fail_phase(f"\n❌ showtime-links.json is stale ({age_hours:.1f}h old) — run Phase 1 first.")
                        reason = "--force was set" if force else "forward-cache links cover this show date"
                        print(f"\n⚠️  showtime-links.json is stale ({age_hours:.1f}h old) — proceeding because {reason}.")
                print(f"\n📂 Phase 1 links{age_str} ({len(saved_links)} theatres)")
            elif links_weekend and snapshots_only and repair_snapshot_links:
                # Self-heal instead of stranding the weekend. Phase 1 runs
                # Tue-Thu; if it skipped (Polymarket listed the market later)
                # or failed, this file still points at the PRIOR weekend and
                # every snapshot slot — 3/day x 4 days, the whole pre-
                # reservation dataset — used to hard-fail here with "run
                # Phase 1 first" and no scheduled slot left to fix it. That
                # is what cost the 2026-08-07 weekend. The repair path below
                # already rebuilds exactly the slices this run needs; it was
                # simply unreachable for the most common stale state.
                print(f"\n⚠️  showtime-links.json is from weekend {links_weekend} "
                      f"(current: {current_weekend}) — rebuilding the snapshot "
                      f"slices for this weekend instead of aborting.")
                saved_links = {}
                collected_at_str = ""
            elif links_weekend:
                fail_phase(f"\n❌ showtime-links.json is from weekend {links_weekend} (current: {current_weekend}) — run Phase 1 first.")
            elif snapshots_only and repair_snapshot_links:
                # Same self-heal as the wrong-weekend branch: a legacy-schema
                # file (no weekend metadata) used to hard-fail every snapshot
                # slot with nothing scheduled to fix it — the 2026-08-07
                # stranding through a different door (dependency audit D4).
                print("\n⚠️  showtime-links.json has no weekend metadata — "
                      "rebuilding the snapshot slices instead of aborting.")
                saved_links = {}
                collected_at_str = ""
            else:
                fail_phase(
                    "\n❌ showtime-links.json uses the legacy schema without "
                    "weekend/window metadata — run Phase 1 collect-links first."
                )
        except SystemExit:
            raise
        except Exception as e:
            if snapshots_only and repair_snapshot_links:
                print(f"\n⚠️  Could not load showtime-links.json ({e}) — "
                      f"rebuilding the snapshot slices instead of aborting.")
                saved_links = {}
                links_meta = {}
                collected_at_str = ""
            else:
                fail_phase(f"\n❌ Could not load showtime-links.json: {e} — run Phase 1 first.")
    elif snapshots_only and repair_snapshot_links:
        print("\n⚠️  showtime-links.json not found — rebuilding the snapshot "
              "slices instead of aborting.")
        saved_links = {}
        links_meta = {}
        collected_at_str = ""
    else:
        fail_phase("\n❌ showtime-links.json not found — run Phase 1 first.")

    regular_snapshot_fallback_issues = []
    if not snapshots_only:
        fresh_phase1_links = saved_links
        theatre_metadata_by_name = {
            theatre.get("name"): theatre
            for group_theatres in theatres_map.values()
            for theatre in group_theatres
            if theatre.get("name")
        }
        snapshot_preserved_links = load_pre_reservation_showtime_links(
            weekend,
            movie_titles=_unique_market_titles(poly_markets),
            theatre_metadata_by_name=theatre_metadata_by_name,
        )
        if snapshot_preserved_links:
            if not test_max:
                (
                    saved_links,
                    snapshot_preserved_links,
                    repair_issues,
                ) = await repair_regular_snapshot_preserved_fallbacks_async(
                    poly_markets,
                    saved_links,
                    snapshot_preserved_links,
                    groups_to_check,
                    coverage_dates_by_group,
                )
                regular_snapshot_fallback_issues.extend(repair_issues)
                fresh_phase1_links = saved_links
            snapshot_link_count = count_phase1_showtime_links(snapshot_preserved_links)
            merged_links = merge_snapshot_links_into_phase1_saved_links(
                saved_links,
                snapshot_preserved_links,
            )
            fallback_gaps = snapshot_preserved_phase1_fallback_gaps(
                poly_markets,
                fresh_phase1_links,
                merged_links,
                groups_to_check,
                coverage_dates_by_group,
            )
            if fallback_gaps:
                print(
                    "\n⚠️  Snapshot-preserved links are covering fresh Phase 1 "
                    "active-movie gap(s):"
                )
                for gap in fallback_gaps[:20]:
                    issue = (
                        "Snapshot-preserved Phase 1 fallback: "
                        f"{gap['movie_title']} {gap['show_date']} {gap['timezone']} "
                        f"had {gap['fresh_theatres']}/{gap['required_theatres']} "
                        "fresh theatres"
                    )
                    regular_snapshot_fallback_issues.append(issue)
                    print(f"    - {issue}")
                if len(fallback_gaps) > 20:
                    print(f"    ... and {len(fallback_gaps) - 20} more")
            saved_links = merged_links
            print(
                "\n📎 Added "
                f"{snapshot_link_count} snapshot-preserved showtime links "
                "to regular Phase 2 input."
            )

    snapshot_skipped_slice_issues = []
    phase1_validation_links = (
        filter_saved_links_by_names(saved_links, snapshot_theatre_names)
        if snapshots_only else saved_links
    )
    if snapshots_only:
        linked_snapshot_theatre_names = select_snapshot_theatre_names(
            theatres_map,
            groups=snapshot_selection_groups,
            saved_links=saved_links,
            requested_date_sets=snapshot_selection_date_sets,
            movie_titles=_unique_market_titles(poly_markets),
        )
        if linked_snapshot_theatre_names:
            snapshot_theatre_names = linked_snapshot_theatre_names
            coverage_theatres_map = filter_theatres_map_by_names(
                theatres_map,
                snapshot_theatre_names,
            )
            phase1_validation_links = filter_saved_links_by_names(
                saved_links,
                snapshot_theatre_names,
            )
        if repair_snapshot_links and not test_max:
            saved_links, usable_date_sets, skipped_date_slices = (
                await repair_snapshot_phase1_links_async(
                    poly_markets,
                    saved_links,
                    groups_to_check,
                    coverage_dates_by_group,
                    link_filter_names=snapshot_theatre_names,
                )
            )
            phase1_validation_links = filter_saved_links_by_names(
                saved_links,
                snapshot_theatre_names,
            )
            linked_snapshot_theatre_names = select_snapshot_theatre_names(
                theatres_map,
                groups=snapshot_selection_groups,
                saved_links=saved_links,
                requested_date_sets=snapshot_selection_date_sets,
                movie_titles=_unique_market_titles(poly_markets),
            )
            if linked_snapshot_theatre_names:
                snapshot_theatre_names = linked_snapshot_theatre_names
                coverage_theatres_map = filter_theatres_map_by_names(
                    theatres_map,
                    snapshot_theatre_names,
                )
                phase1_validation_links = filter_saved_links_by_names(
                    saved_links,
                    snapshot_theatre_names,
                )
                usable_date_sets, skipped_date_slices = snapshot_usable_date_sets(
                    poly_markets,
                    phase1_validation_links,
                    groups_to_check,
                    coverage_dates_by_group,
                )
        else:
            usable_date_sets, skipped_date_slices = snapshot_usable_date_sets(
                poly_markets,
                phase1_validation_links,
                groups_to_check,
                coverage_dates_by_group,
            )
        if skipped_date_slices:
            print("\n↷ Snapshot active-movie link gaps:")
            for skipped in skipped_date_slices:
                if skipped.get("date_skipped"):
                    issue = (
                        f"Snapshot skipped {skipped['timezone']} {skipped['show_date']} "
                        f"missing links for {', '.join(skipped['missing_movies'])}"
                    )
                else:
                    issue = (
                        f"Snapshot partial {skipped['timezone']} {skipped['show_date']} "
                        f"missing links for {', '.join(skipped['missing_movies'])}"
                    )
                snapshot_skipped_slice_issues.append(issue)
                print(f"    - {issue}")

        groups_to_check = [
            group for group in groups_to_check
            if usable_date_sets.get(group)
        ]
        if not groups_to_check:
            fail_phase(
                "\n❌ Snapshot-only run has no timezone/date slices with complete "
                "active movie Phase 1 links."
            )
        collection_dates_by_group = {
            group: usable_date_sets[group]
            for group in groups_to_check
        }
        coverage_dates_by_group = collection_dates_by_group
        expected_dates = {
            group: dates[0]
            for group, dates in collection_dates_by_group.items()
            if dates
        }
        print("   Snapshot usable show dates: " + ", ".join(
            f"{group}={','.join(dates)}"
            for group, dates in collection_dates_by_group.items()
        ))
        selected_by_group = {
            group: sum(
                1
                for theatre in theatres_map.get(group, [])
                if theatre.get("name") in snapshot_theatre_names
            )
            for group in groups_to_check
        }
        print(f"   Snapshot final selected theatres: {selected_by_group}")

    if snapshots_only:
        active_link_gaps = active_market_phase1_link_gaps(
            poly_markets,
            phase1_validation_links,
            groups_to_check,
            coverage_dates_by_group,
        )
        if active_link_gaps:
            print(f"\n⚠️  Phase 1 scrape preflight for {tz_group}: partial active movie links")
            for gap in active_link_gaps[:20]:
                print(
                    "    - "
                    f"{gap['movie_title']} {gap['show_date']} {gap['timezone']}: "
                    f"{gap['fresh_theatres']}/{gap['required_theatres']} theatres"
                )
            if len(active_link_gaps) > 20:
                print(f"    ... and {len(active_link_gaps) - 20} more")
    else:
        warn_active_market_phase1_link_gaps(
            poly_markets,
            phase1_validation_links,
            groups_to_check,
            coverage_dates_by_group,
            f"Phase 1 scrape preflight for {tz_group}",
        )

    if snapshots_only:
        poly_markets = filter_markets_with_phase1_links_for_date_sets(
            poly_markets,
            phase1_validation_links,
            groups=groups_to_check,
            expected_date_sets=coverage_dates_by_group,
        )
    else:
        poly_markets = filter_markets_with_phase1_links(
            poly_markets,
            phase1_validation_links,
            groups=groups_to_check,
            expected_dates=expected_dates,
        )
    if not poly_markets:
        log_run(tz_group, [], [], ["No active Polymarket markets have current Phase 1 links"])
        fail_phase("\n❌ No active box office markets have current AMC Phase 1 links.")
    save_polymarket_data(poly_markets, weekend_of=weekend)

    movie_titles = [m["movie_title"] for m in poly_markets]
    market_urls = {m["movie_title"]: m["market_url"] for m in poly_markets}

    all_theatres = build_phase2_theatre_work(
        theatres_map,
        groups_to_check,
        collection_dates_by_group,
        snapshots_only=snapshots_only,
        snapshot_theatre_names=snapshot_theatre_names,
    )

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
    # Regular post-show scrapes use `local_now(tz) - 12h` because at the
    # standard 04:00 UTC Phase 2 schedule, ET has already rolled past local
    # midnight while CT/PT have not. Snapshot-only probes run before show day
    # rolls over, so they use the current local date instead.
    fresh_theatres, stale_skipped = filter_fresh_phase2_theatres(
        all_theatres,
        saved_links,
        expected_dates,
    )
    if stale_skipped:
        print(f"\n⚠️  Skipping {len(stale_skipped)} theatres with stale Phase 1 entries "
              f"(Phase 1 didn't refresh this TZ today):")
        for s in stale_skipped[:5]:
            print(f"    {s}")
        if len(stale_skipped) > 5:
            print(f"    ... and {len(stale_skipped)-5} more")
    all_theatres = fresh_theatres

    coverage_report = phase1_link_coverage_for_date_sets(
        saved_links,
        coverage_theatres_map,
        groups_to_check,
        coverage_dates_by_group,
    )
    if not test_max:
        if snapshots_only:
            print_phase1_coverage(coverage_report, f"Phase 1 scrape preflight for {tz_group}")
            if snapshot_phase1_coverage_failure_is_fatal(coverage_report):
                fail_phase(
                    f"❌ Phase 1 scrape preflight for {tz_group} has zero usable "
                    "selected snapshot links."
                )
            if coverage_report["expected_total"] and coverage_report["ratio"] < PHASE1_MIN_FRESH_LINK_RATIO:
                print(
                    "\n⚠️  Snapshot Phase 1 coverage is partial; continuing so "
                    "available pre-reservation rows can be committed and weighted."
                )
        else:
            require_phase1_coverage(coverage_report, f"Phase 1 scrape preflight for {tz_group}")
        expansion_report = phase1_link_coverage_for_date_sets(
            saved_links, coverage_theatres_map, groups_to_check, coverage_dates_by_group,
            required_cohorts=(EXPANSION_COHORT,),
        )
        if expansion_report["expected_total"]:
            print_phase1_coverage(
                expansion_report,
                f"Phase 1 expansion preflight for {tz_group}",
                min_ratio=0.0,
            )

    # Test mode: cap to N theatres
    if test_max:
        all_theatres = all_theatres[:test_max]
        print(f"\n🧪 TEST MODE — limiting to {test_max} theatres, time filter bypassed")

    print(f"\n🏛️  Scraping {len(all_theatres)} theatres with saved links "
          f"(across {len(groups_to_check)} timezone(s))...")
    print(f"   Cohorts: {_cohort_counts(all_theatres)}")
    print(f"   Weekend: {weekend}  Run: {run_id}")

    if not all_theatres:
        fail_phase("❌ No theatres found in saved links for this timezone group.")

    linked_showtime_count = phase2_saved_showtime_count(
        all_theatres,
        saved_links,
        movie_titles,
        expected_dates,
    )
    phase2_deadline_sec = phase2_runtime_deadline_sec(
        all_theatres,
        saved_links,
        movie_titles,
        expected_dates,
        snapshots_only=snapshots_only,
        max_concurrent_tabs=max_concurrent_tabs,
    )
    theatre_timeout_sec = PHASE2_THEATRE_TIMEOUT_SEC
    print(
        "   Runtime budget: "
        f"{phase2_deadline_sec}s internal deadline, "
        f"{theatre_timeout_sec}s per theatre, "
        f"{max_concurrent_tabs} tab(s), {linked_showtime_count} linked showtime(s)"
    )

    # Step 3: Parallel scrape with semaphore — flush each theatre to CSV immediately
    all_results = []
    all_issues = []
    all_issues.extend(snapshot_skipped_slice_issues)
    all_issues.extend(regular_snapshot_fallback_issues)
    sem = asyncio.Semaphore(max_concurrent_tabs)
    write_lock = asyncio.Lock()
    snapshot_write_lock = asyncio.Lock()
    written_rows = 0
    skipped_rows = 0
    snapshot_rows_written = 0
    snapshot_rows_skipped = 0
    all_snapshot_rows = []

    # Per-theatre and overall deadlines. We stop accepting new work early enough
    # for in-flight theatres and artifact upload/finalize to finish before the
    # workflow step timeout. Per-theatre wait_for prevents one hung tab (usually
    # from AMC's queue-it redirect) from stalling the whole run.
    overall_deadline = asyncio.get_event_loop().time() + phase2_deadline_sec

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=_CHROMIUM_ARGS)

        async def bounded_scrape(theatre):
            nonlocal written_rows, skipped_rows, snapshot_rows_written, snapshot_rows_skipped
            name = theatre["name"]
            if asyncio.get_event_loop().time() >= overall_deadline:
                all_issues.append(f"{name}: overall deadline reached — skipped")
                return
            async with sem:
                if asyncio.get_event_loop().time() >= overall_deadline:
                    all_issues.append(f"{name}: overall deadline reached — skipped")
                    return
                saved_entry = saved_links[name]
                expected_show_date = phase2_theatre_expected_date(
                    theatre,
                    saved_entry,
                    expected_dates,
                )
                t_date = (
                    expected_show_date
                    if phase1_date_entry(saved_entry, expected_show_date)
                    else (
                        saved_entry.get("show_date")
                        or links_meta.get("collected_local_date")
                        or theatre.get("_date", today)
                    )
                )
                theatre_saved = phase1_entry_movies(saved_entry, t_date)
                try:
                    outcome = await asyncio.wait_for(
                        _scrape_theatre(
                            browser, theatre, t_date, movie_titles, market_urls,
                            weekend_of=weekend, run_id=run_id,
                            saved_movies=theatre_saved,
                            test_mode=bool(test_max),
                            capture_pre_reservations=capture_pre_reservations,
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
            results, issues, csv_rows, snapshot_rows = outcome
            all_results.extend(results)
            all_issues.extend(issues)
            if snapshot_rows:
                all_snapshot_rows.extend(snapshot_rows)
                async with snapshot_write_lock:
                    w, s = append_unique_pre_reservation_rows(snapshot_rows)
                    snapshot_rows_written += w
                    snapshot_rows_skipped += s
            # Flush to disk immediately so data survives a mid-run kill
            if csv_rows and not snapshots_only:
                async with write_lock:
                    w, s = append_unique_seat_rows(csv_rows)
                    written_rows += w
                    skipped_rows += s

        async def run_scrape_batch(theatres, label):
            if not theatres:
                return
            if asyncio.get_event_loop().time() >= overall_deadline:
                all_issues.extend(
                    f"{t['name']}: overall deadline reached before {label} batch — skipped"
                    for t in theatres
                )
                return
            print(f"\n▶ {label} cohort batch: {len(theatres)} theatre(s)")
            tasks = [bounded_scrape(t) for t in theatres]
            await asyncio.gather(*tasks, return_exceptions=True)

        core_theatres = [
            t for t in all_theatres
            if _theatre_cohort(t) != EXPANSION_COHORT
        ]
        expansion_theatres = [
            t for t in all_theatres
            if _theatre_cohort(t) == EXPANSION_COHORT
        ]
        await run_scrape_batch(core_theatres, CORE_COHORT)
        await run_scrape_batch(expansion_theatres, EXPANSION_COHORT)

        try:
            await asyncio.wait_for(browser.close(), timeout=15)
        except Exception:
            pass
    if skipped_rows:
        print(f"↺ Skipped {skipped_rows} duplicate seat row(s)")
    if snapshot_rows_skipped:
        print(f"↺ Skipped {snapshot_rows_skipped} duplicate pre-reservation snapshot row(s)")

    snapshot_failures = []
    fatal_snapshot_failure = False
    if snapshots_only and not test_max:
        snapshot_report = snapshot_theatre_coverage(all_theatres, all_snapshot_rows)
        print(
            "\n🧯 Snapshot theatre coverage: "
            f"{snapshot_report['observed_total']}/{snapshot_report['expected_total']} "
            f"theatre-date slices ({snapshot_report['ratio']:.1%}); "
            f"minimum {SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO:.0%}"
        )
        for (date_str, tz), details in snapshot_report["by_slice"].items():
            print(
                f"   {date_str} {tz}: "
                f"{details['observed']}/{details['expected']} "
                f"({details['ratio']:.1%})"
            )
        snapshot_failures = snapshot_coverage_failures(snapshot_report)
        if snapshot_failures:
            all_issues.append(
                "Snapshot coverage below minimum: "
                + "; ".join(snapshot_failures[:8])
            )
            fatal_snapshot_failure = snapshot_coverage_failure_is_fatal(
                snapshot_report,
                snapshot_rows_written,
            )
            if fatal_snapshot_failure:
                print(
                    f"\n❌ Snapshot coverage {snapshot_report['ratio']:.1%} is below the "
                    f"fatal floor {SNAPSHOT_FATAL_COVERAGE_RATIO:.0%}; refusing to commit "
                    "misleadingly sparse snapshot data."
                )
                # Make the refusal REAL. The leg exits 1, but its artifact
                # still carries the local CSV, and the merge filter keeps
                # snapshot-only sources regardless of job status — so the
                # "refused" sparse rows merged into canonical anyway
                # (soft-fail audit 2026-08-23, verified). This marker travels
                # with the artifact; merge drops the leg's snapshot source
                # when it is present.
                try:
                    marker_dir = os.path.join(DATA_DIR, "scrape-manifest")
                    os.makedirs(marker_dir, exist_ok=True)
                    with open(os.path.join(
                            marker_dir, f"{tz_group}-snapshot-fatal.marker"), "w") as mf:
                        mf.write(
                            f"coverage={snapshot_report['ratio']:.4f} "
                            f"floor={SNAPSHOT_FATAL_COVERAGE_RATIO}\n")
                except OSError as e:
                    print(f"  ⚠️  could not write fatal-floor marker: {e}")
            else:
                print(
                    "\n⚠️  Snapshot coverage is partial, but rows were captured; "
                    "committing partial snapshot data for the model to weight by coverage."
                )
    elif not test_max:
        regular_report = regular_phase2_theatre_coverage(
            all_theatres,
            all_results,
            movie_titles,
            saved_links=saved_links,
            expected_dates=expected_dates,
        )
        regular_failures = regular_phase2_coverage_failures(regular_report)
        print(
            "\n🧯 Regular theatre coverage: "
            f"minimum {REGULAR_PHASE2_MIN_COVERAGE_RATIO:.0%}"
        )
        for title, details in regular_report.get("by_movie", {}).items():
            print(
                f"   {title}: "
                f"{details['observed']}/{details['expected']} "
                f"theatres ({details['ratio']:.1%})"
            )
        if regular_failures:
            all_issues.append(
                "Regular coverage below minimum: "
                + "; ".join(regular_failures[:8])
            )

    # Step 5: Log and summarize
    log_run(tz_group, movie_titles, all_results, all_issues, run_id=run_id)

    if fatal_snapshot_failure:
        fail_phase(
            "\n❌ Snapshot-only run captured no usable theatre coverage. "
            + "; ".join(snapshot_failures[:8])
        )

    # Use local time for the day check — PT phase 2 runs at 7am UTC which is
    # already "Sunday" UTC, but still "Saturday" PT local time.
    ref_tz_for_day = tz_group if tz_group != "ALL" else "PT"
    local_day = local_now(ref_tz_for_day).strftime("%A")
    if local_day in ("Saturday", "Sunday") and tz_group in ("PT", "ALL"):
        generate_weekend_summary()

    print(f"\n{'='*60}")
    snapshot_msg = (
        f", {snapshot_rows_written} pre-reservation snapshots"
        if capture_pre_reservations else ""
    )
    print(f"✅ Run complete — {written_rows} seat counts logged{snapshot_msg}, {len(all_issues)} issues")
    print(f"{'='*60}")
    # OUTPUT FLOOR (soft-fail audit 2026-08-23). The snapshot lane gained a
    # fatal coverage floor after the Queue-It wall, but the REGULAR lane — the
    # one that writes the model's ground-truth seat counts — could log
    # "✅ Run complete — 0 seat counts" and exit 0 (fleet-wide wall, seat-map
    # DOM drift, deadline exhaustion all reach here). Zero rows on a run that
    # had movies to scrape means nothing was captured and nothing is lost by
    # failing: red gets the scheduler retry + circuit breaker instead of a
    # green run and a finalize that quietly freezes predictions. Partial
    # capture (>0 rows) stays green — partial post-show data is real revenue
    # and must commit; the completeness watchdog grades its volume.
    if not snapshots_only and poly_markets and written_rows == 0:
        fail_phase("❌ Regular scrape wrote ZERO seat rows for tracked titles "
                   "— failing loudly instead of green-zero.")


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

async def run_with_preflight_async(tz_group="ALL", force=False, test_max=None,
                                   ensure_links=False,
                                   capture_pre_reservations=False,
                                   snapshots_only=False,
                                   repair_snapshot_links=False):
    if ensure_links and not test_max:
        await ensure_phase1_links_async(tz_group)
    await run_async(
        tz_group,
        force=force,
        test_max=test_max,
        capture_pre_reservations=capture_pre_reservations,
        snapshots_only=snapshots_only,
        repair_snapshot_links=repair_snapshot_links,
    )


def run(tz_group="ALL", force=False, test_max=None, ensure_links=False,
        capture_pre_reservations=False, snapshots_only=False,
        repair_snapshot_links=False):
    """Sync wrapper for the async pipeline."""
    asyncio.run(run_with_preflight_async(
        tz_group,
        force=force,
        test_max=test_max,
        ensure_links=ensure_links,
        capture_pre_reservations=capture_pre_reservations,
        snapshots_only=snapshots_only,
        repair_snapshot_links=repair_snapshot_links,
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
    full_weekend_links_mode = "--full-weekend-links" in args
    pre_reservation_mode = (
        "--pre-reservation-snapshots" in args
        or ENABLE_PRERESERVATION_SNAPSHOTS
    )
    snapshots_only_mode = "--snapshots-only" in args
    repair_snapshot_links_mode = (
        "--repair-snapshot-links" in args
        or SNAPSHOT_REPAIR_LINKS
    )
    if snapshots_only_mode:
        pre_reservation_mode = True

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

    args = [
        a for a in args
        if a not in (
            "--collect-links", "--force", "--ensure-links",
            "--full-weekend-links", "--pre-reservation-snapshots",
            "--snapshots-only", "--repair-snapshot-links",
        )
    ]

    tz = args[0].upper() if args else "ALL"

    if tz not in ("ET", "CT", "MT", "PT", "ALL"):
        print(f"Usage: python scraper.py [--collect-links] [--full-weekend-links] [--ensure-links] [--force] [--test N] [--pre-reservation-snapshots] [--snapshots-only] [--repair-snapshot-links] [ET|CT|MT|PT|ALL]")
        print(f"  --collect-links  Phase 1: save showtime IDs to showtime-links.json")
        print(f"  --full-weekend-links  Phase 1: on Thursday, collect Thu-Sun showtime links")
        print(f"  --ensure-links   Phase 2: repair missing/stale Phase 1 links for this TZ before scraping")
        print(f"  --force          Force re-scrape even if showtime-links.json is stale")
        print(f"  --test N         Phase 2 test: run N theatres only, skip time filter")
        print(f"  --pre-reservation-snapshots  Also write time-bucketed reserved-seat snapshots")
        print(f"  --snapshots-only Write rolling remaining-weekend snapshots without appending prediction seat-count rows")
        print(f"  --repair-snapshot-links  In snapshot mode, attempt targeted Phase 1 repair before keeping partial data")
        print(f"  ET               Eastern theatres only")
        print(f"  CT               Central theatres only")
        print(f"  MT               Mountain theatres only")
        print(f"  PT               Pacific theatres only")
        print(f"  ALL              All theatres (default)")
        sys.exit(1)

    if collect_links_mode:
        asyncio.run(run_collect_links_async(tz, full_weekend=full_weekend_links_mode or PHASE1_FULL_WEEKEND_LINKS))
    else:
        run(
            tz,
            force=force_mode,
            test_max=test_max,
            ensure_links=ensure_links_mode,
            capture_pre_reservations=pre_reservation_mode,
            snapshots_only=snapshots_only_mode,
            repair_snapshot_links=repair_snapshot_links_mode,
        )
