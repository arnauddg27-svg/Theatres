#!/usr/bin/env python3
"""Decide whether a Phase 1 collect-links job should be skipped.

Commit-message markers are only safe when the same commit also changed the
canonical showtime link cache. Marker-only commits must not block future link
collection, because that leaves snapshot and scrape jobs running on stale or
partial link data.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


SHOWTIME_LINKS_PATH = "box-office-tracker/data/showtime-links.json"
POLYMARKET_MARKETS_PATH = "box-office-tracker/data/polymarket-markets.csv"
THEATRES_ALL_PATH = "box-office-tracker/data/theatres-all.json"
THEATRE_COUNTS_PATH = "box-office-tracker/data/theatre-counts.json"
MOVIE_METADATA_PATH = "box-office-tracker/data/movie-metadata.csv"

TZ_TO_ZONE = {
    "ET": "America/New_York",
    "CT": "America/Chicago",
    "PT": "America/Los_Angeles",
}
WEEKEND_FULL_DAY_START_HOUR = 10
DEFAULT_COLLECTION_START_HOUR = 17
DEFAULT_MIN_FRESH_LINK_RATIO = 0.80


def default_since_date(now: datetime | None = None) -> str:
    """Look back to Tuesday when Wednesday is acting as the warm-cache fallback."""
    now = now or datetime.now(timezone.utc)
    if now.weekday() == 2:  # Wednesday UTC fallback should respect Tuesday successes.
        now = now - timedelta(days=1)
    return now.strftime("%Y-%m-%d")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def _write_output(path: str | None, skip: bool) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"skip={'true' if skip else 'false'}\n")


def _marker_commits(repo_root: Path, tz: str, since: str) -> list[str]:
    pattern = f"data: box office {tz} collect-links"
    result = _run(
        [
            "git",
            "log",
            f"--since={since} 00:00",
            "--format=%H",
            f"--grep={pattern}",
        ],
        repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _commit_changed_path(repo_root: Path, commit: str, path: str) -> bool:
    result = _run(["git", "show", "--name-only", "--format=", commit], repo_root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git show failed")
    changed_paths = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return path in changed_paths


def _print_commit_list(label: str, commits: list[str], limit: int = 10) -> None:
    for commit in commits[:limit]:
        print(f"{label}={commit}")
    if len(commits) > limit:
        print(f"{label}_omitted={len(commits) - limit}")


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def _unique_titles(values: list[str]) -> list[str]:
    seen: set[str] = set()
    titles: list[str] = []
    for value in values:
        cleaned = (value or "").strip()
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        titles.append(cleaned)
    return titles


def _parse_iso_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _opening_weekend_friday(dt: datetime) -> str:
    weekday = dt.weekday()  # Mon=0 ... Sun=6
    if weekday == 3:  # Thursday -> next Friday
        friday = dt + timedelta(days=1)
    elif weekday == 4:
        friday = dt
    elif weekday == 5:
        friday = dt - timedelta(days=1)
    elif weekday == 6:
        friday = dt - timedelta(days=2)
    elif weekday == 0:
        friday = dt - timedelta(days=3)
    elif weekday == 1:
        friday = dt - timedelta(days=4)
    else:
        friday = dt - timedelta(days=5)
    return friday.strftime("%Y-%m-%d")


def _opening_weekend_show_dates(weekend_of: str) -> list[str]:
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    return [
        (friday + timedelta(days=offset)).strftime("%Y-%m-%d")
        for offset in (-1, 0, 1, 2)
    ]


def _phase1_weekend_anchor(ref_dt: datetime, full_weekend: bool = True) -> str:
    if full_weekend and ref_dt.weekday() == 1:  # Tuesday warm-cache links.
        return (ref_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    if full_weekend and ref_dt.weekday() == 2:  # Wednesday fallback links.
        return (ref_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    return _opening_weekend_friday(ref_dt)


def _collection_window_start_hour(date_str: str) -> int:
    parsed = _parse_date(date_str)
    if parsed and parsed.weekday() in (5, 6):  # Saturday/Sunday.
        return WEEKEND_FULL_DAY_START_HOUR
    return DEFAULT_COLLECTION_START_HOUR


def _local_now(tz: str, now: datetime | None = None) -> datetime:
    zone = TZ_TO_ZONE.get(tz, "UTC")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(ZoneInfo(zone))


def _phase1_expected_dates(tz: str, now: datetime | None = None) -> list[str]:
    local = _local_now(tz, now)
    current_date = local.strftime("%Y-%m-%d")
    weekend_dates = _opening_weekend_show_dates(
        _phase1_weekend_anchor(local, full_weekend=True)
    )
    if local.weekday() in (1, 2):
        return weekend_dates
    if local.weekday() in (3, 4, 5):
        current_start = _collection_window_start_hour(current_date)
        if local.hour >= current_start:
            future_dates = [date_str for date_str in weekend_dates if date_str > current_date]
            if future_dates:
                return future_dates
        return [date_str for date_str in weekend_dates if date_str >= current_date]
    return [current_date]


def _movie_metadata_weekends(repo_root: Path) -> dict[str, str]:
    path = repo_root / MOVIE_METADATA_PATH
    if not path.exists():
        return {}
    weekends: dict[str, str] = {}
    try:
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                title = (row.get("movie") or row.get("movie_title") or "").strip()
                weekend = (row.get("weekend_of") or "").strip()
                if title and _parse_date(weekend):
                    weekends[title.lower()] = weekend
    except OSError as exc:
        print(f"Could not read {MOVIE_METADATA_PATH}: {exc}; ignoring metadata filter")
    return weekends


def _tracked_titles_from_showtime_links(saved_links: dict, expected_weekend: str) -> list[str]:
    if (saved_links.get("weekend_of") or saved_links.get("date")) != expected_weekend:
        return []
    titles: list[str] = []
    theatres = saved_links.get("theatres") or {}
    if not isinstance(theatres, dict):
        return []
    for entry in theatres.values():
        if not isinstance(entry, dict):
            continue
        movies = entry.get("movies") or {}
        if isinstance(movies, dict):
            titles.extend(movies.keys())
        dates = entry.get("dates") or {}
        if not isinstance(dates, dict):
            continue
        for date_entry in dates.values():
            date_movies = (date_entry or {}).get("movies") if isinstance(date_entry, dict) else {}
            if isinstance(date_movies, dict):
                titles.extend(date_movies.keys())
    return _unique_titles(titles)


def _tracked_titles_from_theatre_counts(repo_root: Path, expected_weekend: str) -> list[str]:
    path = repo_root / THEATRE_COUNTS_PATH
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {THEATRE_COUNTS_PATH}: {exc}; ignoring requested-movie state")
        return []
    if not isinstance(payload, dict):
        return []
    updated_dt = _parse_iso_datetime(str(payload.get("_updated") or ""))
    if not updated_dt or _opening_weekend_friday(updated_dt) != expected_weekend:
        return []
    requested = payload.get("_requested_movies") or []
    if not isinstance(requested, list):
        return []
    return _unique_titles([str(title) for title in requested])


def _csv_market_titles(repo_root: Path, expected_weekend: str, market_since: str) -> list[str]:
    path = repo_root / POLYMARKET_MARKETS_PATH
    if not path.exists():
        print(f"{POLYMARKET_MARKETS_PATH} not found; no CSV active-market fallback")
        return []

    since_dt = _parse_date(market_since)
    metadata_weekends = _movie_metadata_weekends(repo_root)
    titles: list[str] = []
    ignored_metadata_titles: list[str] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = (row.get("movie_title") or "").strip()
            row_dt = _parse_date((row.get("date") or "").strip())
            if not title or row_dt is None:
                continue
            if since_dt and row_dt < since_dt:
                continue
            metadata_weekend = metadata_weekends.get(title.lower())
            if metadata_weekend:
                if metadata_weekend == expected_weekend:
                    titles.append(title)
                else:
                    ignored_metadata_titles.append(title)
                continue
            if _opening_weekend_friday(row_dt) == expected_weekend:
                titles.append(title)
                continue
            # Pre-opening rows are stamped with the observation date, not the
            # movie's weekend. If no metadata disqualifies the title, keep it as
            # a conservative active-slate candidate rather than letting a stale
            # marker hide a newly added Polymarket movie.
            titles.append(title)

    if not titles:
        print(f"No usable movie rows in {POLYMARKET_MARKETS_PATH} since {market_since}")
        return []

    if ignored_metadata_titles:
        print(
            f"Ignoring {len(set(ignored_metadata_titles))} metadata-known "
            f"out-of-weekend market title(s)"
        )
    return _unique_titles(titles)


def _active_movie_titles(repo_root: Path, expected_weekend: str, market_since: str) -> list[str]:
    saved_links = _load_showtime_links(repo_root)
    titles: list[str] = []
    titles.extend(_tracked_titles_from_showtime_links(saved_links, expected_weekend))
    titles.extend(_tracked_titles_from_theatre_counts(repo_root, expected_weekend))
    titles.extend(_csv_market_titles(repo_root, expected_weekend, market_since))
    active = _unique_titles(titles)
    if not active:
        print(f"No active movie state found for weekend {expected_weekend}; running")
    return active


def _active_market_since(expected_dates: list[str]) -> str:
    if not expected_dates:
        return default_since_date()
    weekend = _opening_weekend_friday(datetime.strptime(expected_dates[0], "%Y-%m-%d"))
    return (datetime.strptime(weekend, "%Y-%m-%d") - timedelta(days=3)).strftime("%Y-%m-%d")


def _expected_weekend(expected_dates: list[str]) -> str:
    if not expected_dates:
        return _opening_weekend_friday(datetime.now(timezone.utc))
    return _opening_weekend_friday(datetime.strptime(expected_dates[0], "%Y-%m-%d"))


def _load_showtime_links(repo_root: Path) -> dict:
    path = repo_root / SHOWTIME_LINKS_PATH
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {SHOWTIME_LINKS_PATH}: {exc}; running")
        return {}
    return payload if isinstance(payload, dict) else {}


def _movie_link_counts(
    saved_links: dict,
    tz: str,
    expected_dates: list[str],
    movie_titles: list[str],
) -> dict[str, dict[str, int]]:
    title_set = set(movie_titles)
    counts = {
        date_str: {title: 0 for title in movie_titles}
        for date_str in expected_dates
    }
    theatres = saved_links.get("theatres") or {}
    if not isinstance(theatres, dict):
        return counts

    for entry in theatres.values():
        if not isinstance(entry, dict):
            continue
        if (entry.get("tz") or "").upper() != tz:
            continue
        dates = entry.get("dates") or {}
        if not isinstance(dates, dict):
            continue
        for date_str in expected_dates:
            movies = (dates.get(date_str) or {}).get("movies") or {}
            if not isinstance(movies, dict):
                continue
            for title in title_set.intersection(movies.keys()):
                if movies.get(title):
                    counts[date_str][title] += 1
    return counts


def _active_movie_link_coverage_ok(
    repo_root: Path,
    tz: str,
    expected_dates: list[str],
    movie_titles: list[str],
    min_theatres_per_movie_date: int,
) -> bool:
    if not movie_titles:
        return False
    if not expected_dates:
        print(f"No expected Phase 1 dates for {tz}; running")
        return False

    saved_links = _load_showtime_links(repo_root)
    if not saved_links:
        print(f"{SHOWTIME_LINKS_PATH} missing or unreadable; running")
        return False

    expected_weekend = _opening_weekend_friday(
        datetime.strptime(expected_dates[0], "%Y-%m-%d")
    )
    links_weekend = saved_links.get("weekend_of") or saved_links.get("date")
    if links_weekend and links_weekend != expected_weekend:
        print(
            f"{SHOWTIME_LINKS_PATH} is for weekend {links_weekend}, "
            f"expected {expected_weekend}; running"
        )
        return False

    counts = _movie_link_counts(saved_links, tz, expected_dates, movie_titles)
    missing: list[str] = []
    for date_str, title_counts in counts.items():
        for title, count in title_counts.items():
            if count < min_theatres_per_movie_date:
                missing.append(f"{date_str} {title} ({count})")

    if missing:
        print(
            f"{tz} link cache is missing active movie coverage "
            f"(need >= {min_theatres_per_movie_date} theatre/date/title):"
        )
        for item in missing[:25]:
            print(f"  missing_or_thin={item}")
        if len(missing) > 25:
            print(f"  ... {len(missing) - 25} more gaps")
        return False

    print(
        f"{tz} link cache covers {len(movie_titles)} active movie(s) across "
        f"{len(expected_dates)} Phase 1 date(s): {', '.join(expected_dates)}"
    )
    return True


def _min_fresh_link_ratio() -> float:
    try:
        return float(os.getenv("PHASE1_MIN_FRESH_LINK_RATIO", DEFAULT_MIN_FRESH_LINK_RATIO))
    except ValueError:
        return DEFAULT_MIN_FRESH_LINK_RATIO


def _is_amc_classic_theatre(name: str) -> bool:
    return "AMC CLASSIC" in name.upper()


def _expected_theatre_names(repo_root: Path, tz: str) -> list[str]:
    path = repo_root / THEATRES_ALL_PATH
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {THEATRES_ALL_PATH}: {exc}; skipping theatre ratio check")
        return []
    theatres = payload.get(tz) if isinstance(payload, dict) else None
    if not isinstance(theatres, list):
        return []
    names: list[str] = []
    seen_names: set[str] = set()
    for theatre in theatres:
        if not isinstance(theatre, dict):
            continue
        name = (theatre.get("name") or "").strip()
        slug = (theatre.get("slug") or "").strip()
        if not name or not slug or _is_amc_classic_theatre(name):
            continue
        if name in seen_names:
            continue
        names.append(name)
        seen_names.add(name)
    return names


def _phase1_date_entry(entry: dict, expected_date: str) -> bool:
    dates = entry.get("dates")
    if isinstance(dates, dict) and isinstance(dates.get(expected_date), dict):
        return True
    return entry.get("show_date") == expected_date


def _fresh_theatre_link_coverage_ok(
    repo_root: Path,
    tz: str,
    expected_dates: list[str],
    min_ratio: float,
) -> bool:
    theatre_names = _expected_theatre_names(repo_root, tz)
    if not theatre_names:
        print(f"No {THEATRES_ALL_PATH} theatre universe for {tz}; skipping theatre ratio check")
        return True

    saved_links = _load_showtime_links(repo_root)
    theatres = saved_links.get("theatres") or {}
    if not isinstance(theatres, dict):
        theatres = {}

    expected_total = len(theatre_names) * len(expected_dates)
    fresh_total = 0
    by_date: dict[str, tuple[int, int]] = {}
    for date_str in expected_dates:
        fresh_for_date = 0
        for name in theatre_names:
            entry = theatres.get(name)
            if not isinstance(entry, dict):
                continue
            entry_tz = (entry.get("tz") or tz).upper()
            if entry_tz != tz:
                continue
            if _phase1_date_entry(entry, date_str):
                fresh_for_date += 1
        by_date[date_str] = (fresh_for_date, len(theatre_names))
        fresh_total += fresh_for_date

    ratio = (fresh_total / expected_total) if expected_total else 1.0
    if ratio >= min_ratio:
        print(
            f"{tz} link cache theatre coverage is {fresh_total}/{expected_total} "
            f"({ratio:.1%}); minimum {min_ratio:.0%}"
        )
        return True

    print(
        f"{tz} link cache theatre coverage is too low: {fresh_total}/{expected_total} "
        f"({ratio:.1%}); minimum {min_ratio:.0%}"
    )
    for date_str, (fresh, expected) in by_date.items():
        date_ratio = (fresh / expected) if expected else 1.0
        print(f"  theatre_coverage={date_str} {fresh}/{expected} ({date_ratio:.1%})")
    return False


def should_skip(
    repo_root: Path,
    tz: str,
    force: bool,
    since: str,
    now: datetime | None = None,
    min_theatres_per_movie_date: int = 1,
    min_fresh_link_ratio: float | None = None,
) -> bool:
    if force:
        print("Force-running — bypassing collect-links dedup guard")
        return False

    commits = _marker_commits(repo_root, tz, since)
    if not commits:
        print(f"No {tz} collect-links marker found since {since}; running")
        return False

    link_commits = [
        commit
        for commit in commits
        if _commit_changed_path(repo_root, commit, SHOWTIME_LINKS_PATH)
    ]
    if link_commits:
        expected_dates = _phase1_expected_dates(tz, now)
        expected_weekend = _expected_weekend(expected_dates)
        market_since = _active_market_since(expected_dates)
        active_titles = _active_movie_titles(repo_root, expected_weekend, market_since)
        print(
            f"Dedup active-slate check for {tz}: "
            f"{len(active_titles)} movie(s), weekend={expected_weekend}, market_since={market_since}, "
            f"dates={','.join(expected_dates)}"
        )
        if _active_movie_link_coverage_ok(
            repo_root,
            tz,
            expected_dates,
            active_titles,
            min_theatres_per_movie_date,
        ) and _fresh_theatre_link_coverage_ok(
            repo_root,
            tz,
            expected_dates,
            _min_fresh_link_ratio() if min_fresh_link_ratio is None else min_fresh_link_ratio,
        ):
            print(
                f"Skipping — {tz} collect-links marker has canonical links in "
                f"{link_commits[0][:12]} and current active-movie coverage is present"
            )
            return True

        print(
            f"Found {tz} collect-links marker(s) with {SHOWTIME_LINKS_PATH}, "
            "but current active-movie or theatre coverage is incomplete; running"
        )
        _print_commit_list("marker_with_incomplete_active_links", link_commits)
        return False

    print(
        f"Found {tz} collect-links marker(s) since {since}, but none changed "
        f"{SHOWTIME_LINKS_PATH}; running to avoid marker-only link loss"
    )
    _print_commit_list("marker_without_showtime_links", commits)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--tz", required=True)
    parser.add_argument("--force", default="false")
    parser.add_argument("--since", default="")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    skip = should_skip(
        Path(args.repo_root).resolve(),
        args.tz,
        args.force == "true",
        args.since or default_since_date(),
    )
    _write_output(args.github_output, skip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
