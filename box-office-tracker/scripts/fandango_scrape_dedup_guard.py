#!/usr/bin/env python3
"""Decide whether a Fandango snapshot lane should be skipped.

Mirror of scrape_dedup_guard.py for the isolated Fandango lane: only skip when a
"data: box office fandango snapshot" marker commit from today also actually
changed the canonical Fandango file. A marker-only commit (message but no data)
must NOT cause a skip, or we'd silently drop a day of multi-chain coverage.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


FANDANGO_PATH = "box-office-tracker/data/fandango-pre-reservation-snapshots.csv"
MARKER = "data: box office fandango snapshot"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def _write_output(path: str | None, skip: bool) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"skip={'true' if skip else 'false'}\n")


def _marker_commits(repo_root: Path, since: str) -> list[str]:
    result = _run(
        ["git", "log", f"--since={since} 00:00", "--format=%H", f"--grep={MARKER}"],
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


def should_skip(repo_root: Path, force: bool, since: str) -> bool:
    if force:
        print("Force-running — bypassing Fandango dedup guard")
        return False

    commits = _marker_commits(repo_root, since)
    if not commits:
        print(f"No Fandango snapshot marker found since {since}; running")
        return False

    for commit in commits:
        if _commit_changed_path(repo_root, commit, FANDANGO_PATH):
            print(f"Skipping — Fandango snapshot marker has canonical data in {commit[:12]}")
            return True

    print(
        f"Found Fandango snapshot marker(s) since {since}, but none changed "
        f"{FANDANGO_PATH}; running to avoid marker-only data loss"
    )
    for commit in commits:
        print(f"marker_without_fandango_data={commit}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--force", default="false")
    parser.add_argument("--since", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    skip = should_skip(Path(args.repo_root).resolve(), args.force == "true", args.since)
    _write_output(args.github_output, skip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
