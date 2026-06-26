#!/usr/bin/env python3
"""Safely stage finalize outputs after merging scrape artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


OUTPUT_FILES = [
    "box-office-tracker/data/seat-counts.csv",
    "box-office-tracker/data/pre-reservation-snapshots.csv",
    "box-office-tracker/data/polymarket-markets.csv",
    "box-office-tracker/data/calibration.json",
    "box-office-tracker/data/seat-counts.xlsx",
    "box-office-tracker/data/reviews.csv",
]
RUN_LOG_DIR = "box-office-tracker/data/run-logs"
CALIBRATION_FREEZE_DIR = "box-office-tracker/data/calibration-freezes"


def _run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)


def _git(repo_root: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return _run(["git", *args], repo_root, check=check)


def _load_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"merge summary not found: {path}")
    return json.loads(path.read_text())


def _stage_if_exists(repo_root: Path, rel_path: str) -> bool:
    path = repo_root / rel_path
    if not path.exists():
        print(f"Finalize staging: optional path absent, skipped: {rel_path}")
        return False
    _git(repo_root, "add", "--", rel_path, check=True)
    print(f"Finalize staging: staged {rel_path}")
    return True


def _is_staged(repo_root: Path, rel_path: str) -> bool:
    result = _git(repo_root, "diff", "--cached", "--quiet", "--", rel_path)
    return result.returncode == 1


def _has_unstaged_change(repo_root: Path, rel_path: str) -> bool:
    result = _git(repo_root, "diff", "--quiet", "--", rel_path)
    return result.returncode == 1


def _has_any_staged_change(repo_root: Path) -> bool:
    result = _git(repo_root, "diff", "--cached", "--quiet")
    return result.returncode == 1


def _fail_if_expected_change_not_staged(
    repo_root: Path,
    summary: dict[str, Any],
    count_key: str,
    rel_path: str,
) -> None:
    expected = int(summary.get(count_key, 0) or 0)
    if expected > 0 and not _is_staged(repo_root, rel_path):
        if not _has_unstaged_change(repo_root, rel_path):
            print(
                f"Finalize staging: {count_key}={expected}, but {rel_path} "
                "has no net diff after cleanup."
            )
            return
        raise RuntimeError(
            f"merge summary says {count_key}={expected}, but {rel_path} is not staged"
        )


def _marker_file_has_scrape_markers(marker_file: Path) -> bool:
    if not marker_file.exists():
        return False
    return any(
        line.strip().startswith("data: box office ")
        and line.strip().endswith(" scrape")
        for line in marker_file.read_text().splitlines()
    )


def _strip_scrape_markers(marker_file: Path) -> None:
    if not marker_file.exists():
        return
    kept = [
        line
        for line in marker_file.read_text().splitlines()
        if not (
            line.strip().startswith("data: box office ")
            and line.strip().endswith(" scrape")
        )
    ]
    marker_file.write_text("\n".join(kept) + ("\n" if kept else ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--marker-file", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = _load_summary(Path(args.summary_file))
    marker_file = Path(args.marker_file)

    try:
        for rel_path in OUTPUT_FILES:
            _stage_if_exists(repo_root, rel_path)
        _stage_if_exists(repo_root, CALIBRATION_FREEZE_DIR)
        _stage_if_exists(repo_root, RUN_LOG_DIR)

        _fail_if_expected_change_not_staged(
            repo_root,
            summary,
            "seat_added",
            "box-office-tracker/data/seat-counts.csv",
        )
        _fail_if_expected_change_not_staged(
            repo_root,
            summary,
            "seat_metadata_updated",
            "box-office-tracker/data/seat-counts.csv",
        )
        _fail_if_expected_change_not_staged(
            repo_root,
            summary,
            "pre_reservation_added",
            "box-office-tracker/data/pre-reservation-snapshots.csv",
        )
        _fail_if_expected_change_not_staged(
            repo_root,
            summary,
            "polymarket_added",
            "box-office-tracker/data/polymarket-markets.csv",
        )

        if _marker_file_has_scrape_markers(marker_file) and not _is_staged(
            repo_root, "box-office-tracker/data/seat-counts.csv"
        ):
            if not _has_unstaged_change(repo_root, "box-office-tracker/data/seat-counts.csv"):
                _strip_scrape_markers(marker_file)
                print(
                    "Finalize staging: stripped normal scrape markers because "
                    "seat-counts.csv has no net staged data change."
                )
                if not _has_any_staged_change(repo_root):
                    seat_added = int(summary.get("seat_added", 0) or 0)
                    raise RuntimeError(
                        f"scrape markers exist with seat_added={seat_added}, "
                        "but no canonical data is staged; "
                        "refusing to create marker-only commit"
                    )
                return 0
            raise RuntimeError(
                "scrape markers exist, but seat-counts.csv is not staged; "
                "refusing to create marker-only commit"
            )
    except Exception as exc:
        print(f"Finalize staging failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
