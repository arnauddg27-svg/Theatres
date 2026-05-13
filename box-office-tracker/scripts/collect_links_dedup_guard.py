#!/usr/bin/env python3
"""Decide whether a Phase 1 collect-links job should be skipped.

Commit-message markers are only safe when the same commit also changed the
canonical showtime link cache. Marker-only commits must not block future link
collection, because that leaves snapshot and scrape jobs running on stale or
partial link data.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


SHOWTIME_LINKS_PATH = "box-office-tracker/data/showtime-links.json"


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


def should_skip(repo_root: Path, tz: str, force: bool, since: str) -> bool:
    if force:
        print("Force-running — bypassing collect-links dedup guard")
        return False

    commits = _marker_commits(repo_root, tz, since)
    if not commits:
        print(f"No {tz} collect-links marker found since {since}; running")
        return False

    for commit in commits:
        if _commit_changed_path(repo_root, commit, SHOWTIME_LINKS_PATH):
            print(f"Skipping — {tz} collect-links marker has canonical links in {commit[:12]}")
            return True

    print(
        f"Found {tz} collect-links marker(s) since {since}, but none changed "
        f"{SHOWTIME_LINKS_PATH}; running to avoid marker-only link loss"
    )
    for commit in commits:
        print(f"marker_without_showtime_links={commit}")
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
