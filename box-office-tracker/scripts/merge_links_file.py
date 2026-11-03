#!/usr/bin/env python3
"""Resolve a rebase conflict on data/showtime-links.json.

    python3 scripts/merge_links_file.py TARGET SOURCE

TARGET is main's copy (``git checkout --ours`` during a rebase), SOURCE the
copy this job wrote before pulling. Two lanes rewrite the whole JSON file —
collect-links and, since 2026-11-01, finalize (it unions the links the scrape
legs repaired) — so git cannot merge them: the 2026-11-03 17Z PT collect-links
push conflicted three times with the 17:31Z snapshot finalize and ended red
("data not committed"). Resolution: a file for a newer weekend wins whole
(weekend rollover is collect-links' job); the same weekend is unioned
theatre-date by theatre-date with the finalize merge rule, so neither side's
links are lost.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from merge_scrape_artifacts import _merge_showtime_links  # noqa: E402


def weekend_of(path):
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return data.get("weekend_of") or data.get("date") or ""


def resolve(target, source):
    """Leave the resolved file at TARGET; return a one-line description."""
    ours, theirs = weekend_of(source), weekend_of(target)
    if ours is None:
        return f"kept main's copy ({theirs or 'no weekend'}): ours is unreadable"
    if theirs is None or ours > theirs:
        shutil.copyfile(source, target)
        return f"took ours: weekend {ours} is newer than main's {theirs or 'unreadable'}"
    if ours < theirs:
        return f"kept main's copy: weekend {theirs} is newer than ours ({ours})"
    updated = _merge_showtime_links(Path(target), [Path(source)])
    return f"unioned {updated} theatre-date(s) of ours into main's weekend {theirs}"


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(__doc__)
        return 2
    print(f"showtime-links conflict: {resolve(*args)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
