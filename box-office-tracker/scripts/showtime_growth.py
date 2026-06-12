#!/usr/bin/env python3
"""Schedule-growth demand signal from showtime-links.json git history.

AMC ADDS showtimes when a title surges — capacity added is demand the seat
counts cannot censor (sold-out shows hide demand; extra scheduled shows reveal
it). Phase 1 commits showtime-links.json several times per weekend (Tue/Wed
warm cache, repairs, refreshes), so the per-(movie, date) show-count growth is
fully recoverable from git history with zero extra scraping.

Diagnostic only — not consumed by the prediction model. Adopting growth as a
model feature must pass the leave-one-movie-out bake-off first.

Usage:
    python3 scripts/showtime_growth.py                 # last 3 weekends
    python3 scripts/showtime_growth.py --weekends 6
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Both `git log -- <path>` and `git show <sha>:<path>` resolve the path
# relative to the git cwd, so run everything from the repo root.
_REPO_ROOT = Path(subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=ROOT, capture_output=True, text=True, check=True,
).stdout.strip())
LINKS_REL = (ROOT / "data" / "showtime-links.json").relative_to(_REPO_ROOT).as_posix()


def _git(*args):
    return subprocess.run(
        ["git", *args], cwd=_REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def _show_counts(blob):
    """{(movie, date): showtime count} from one showtime-links.json payload."""
    counts = defaultdict(int)
    weekend = blob.get("weekend_of", "")
    for theatre in (blob.get("theatres") or {}).values():
        for date_str, date_entry in (theatre.get("dates") or {}).items():
            for movie, shows in (date_entry.get("movies") or {}).items():
                counts[(movie, date_str)] += len(shows or [])
    return weekend, counts


def main(argv):
    n_weekends = 3
    if "--weekends" in argv:
        n_weekends = int(argv[argv.index("--weekends") + 1])

    commits = _git(
        "log", "--format=%H %cI", "--", LINKS_REL
    ).strip().splitlines()
    # oldest -> newest
    commits = [line.split() for line in reversed(commits)]

    by_weekend = defaultdict(list)  # weekend -> [(commit_time, counts)]
    for sha, ctime in commits:
        try:
            blob = json.loads(_git("show", f"{sha}:{LINKS_REL}"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        weekend, counts = _show_counts(blob)
        if weekend and counts:
            by_weekend[weekend].append((ctime, counts))

    weekends = sorted(by_weekend)[-n_weekends:]
    for weekend in weekends:
        versions = by_weekend[weekend]
        if len(versions) < 2:
            continue
        first_time, first = versions[0]
        last_time, last = versions[-1]
        print(f"\n=== weekend {weekend}: {len(versions)} schedule versions "
              f"({first_time[:16]} -> {last_time[:16]}) ===")
        movies = sorted({m for m, _ in list(first) + list(last)})
        print(f"{'movie':<42}{'date':<12}{'first':>6}{'last':>6}{'growth':>8}")
        for movie in movies:
            dates = sorted({d for m, d in list(first) + list(last) if m == movie})
            for date_str in dates:
                a = first.get((movie, date_str), 0)
                b = last.get((movie, date_str), 0)
                if a == 0 and b == 0:
                    continue
                growth = (b - a) / a * 100 if a else float("inf")
                marker = "  <-- demand surge" if a and growth >= 15 else ""
                growth_s = f"{growth:+.0f}%" if a else "new"
                print(f"{movie[:41]:<42}{date_str:<12}{a:>6}{b:>6}{growth_s:>8}{marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
