#!/usr/bin/env python3
"""Decide whether a Phase 2 scrape leg should be skipped.

Commit-message markers are useful, but they are not sufficient on their own:
the 2026-05-03 failure committed ET/PT scrape markers without staging the
updated canonical seat-counts.csv. This guard only skips when the marker commit
also contains the canonical data file.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


SEAT_COUNTS_PATH = "box-office-tracker/data/seat-counts.csv"
SNAPSHOT_PATH = "box-office-tracker/data/pre-reservation-snapshots.csv"
_SNAPSHOT_SLOT = re.compile(r"^snapshot (\d{2}):(\d{2})Z$")


def slot_since(schedule_slot: str, now: datetime) -> str | None:
    """For a scheduled snapshot slot ("snapshot 22:30Z"), the ISO UTC time of
    its most recent occurrence at or before `now` — a retry at 01:10Z looks
    back to yesterday's 22:30Z. None for anything that is not such a slot."""
    m = _SNAPSHOT_SLOT.match((schedule_slot or "").strip())
    if not m:
        return None
    now = now.astimezone(timezone.utc)
    start = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
    if start > now:
        start -= timedelta(days=1)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def _write_output(path: str | None, skip: bool) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"skip={'true' if skip else 'false'}\n")


def _marker_commits(repo_root: Path, tz: str, since: str, pattern: str | None = None) -> list[str]:
    pattern = pattern or f"data: box office {tz} scrape"
    if len(since) <= 10:            # a bare date means "from midnight"
        since = f"{since} 00:00"
    result = _run(
        [
            "git",
            "log",
            f"--since={since}",
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
    return path in {line.strip() for line in result.stdout.splitlines() if line.strip()}


def should_skip(repo_root: Path, tz: str, force: bool, snapshots_only: bool, since: str,
                schedule_slot: str = "") -> bool:
    if force:
        print("Force-running — bypassing dedup guard")
        return False
    if snapshots_only:
        # A retried snapshot slot used to redo EVERY leg, including the ones
        # that had already committed (2026-09-15/16: ET re-read ~5,000 rows
        # three times per slot while the runner-unreachable CT/PT legs it was
        # retried for waited behind it). Skip a leg whose snapshot already
        # landed since this slot's scheduled time.
        slot_start = slot_since(schedule_slot or "", datetime.now(timezone.utc))
        if not slot_start:
            print("Snapshot-only run — bypassing normal scrape dedup guard")
            return False
        commits = _marker_commits(repo_root, tz, slot_start,
                                  pattern=f"data: box office {tz} pre-reservation snapshot")
        for commit in commits:
            if _commit_changed_path(repo_root, commit, SNAPSHOT_PATH):
                print(f"Skipping — {tz} snapshot for slot '{schedule_slot}' already "
                      f"committed in {commit[:12]} (since {slot_start})")
                return True
        print(f"No {tz} snapshot committed since {slot_start} for slot '{schedule_slot}'; running")
        return False

    commits = _marker_commits(repo_root, tz, since)
    if not commits:
        print(f"No {tz} scrape marker found since {since}; running")
        return False

    for commit in commits:
        if _commit_changed_path(repo_root, commit, SEAT_COUNTS_PATH):
            print(f"Skipping — {tz} scrape marker has canonical data in {commit[:12]}")
            return True

    print(
        f"Found {tz} scrape marker(s) since {since}, but none changed "
        f"{SEAT_COUNTS_PATH}; running to avoid marker-only data loss"
    )
    for commit in commits:
        print(f"marker_without_seat_counts={commit}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--tz", required=True)
    parser.add_argument("--force", default="false")
    parser.add_argument("--snapshots-only", default="false")
    parser.add_argument("--since", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--schedule-slot", default="")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    skip = should_skip(
        Path(args.repo_root).resolve(),
        args.tz,
        args.force == "true",
        args.snapshots_only == "true",
        args.since,
        schedule_slot=args.schedule_slot,
    )
    _write_output(args.github_output, skip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
