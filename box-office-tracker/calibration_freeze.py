"""Helpers for preserving pre-actual calibration state.

Calibration learns from reported box office actuals. These helpers snapshot the
calibration file before a weekend's actuals are recorded, so later replay runs
can answer "what would the model have said live?" without actual-result
contamination.
"""

from __future__ import annotations

import json
import os
from datetime import datetime


FREEZE_DIR_NAME = "calibration-freezes"


def calibration_has_weekend(calibration: dict, weekend_of: str) -> bool:
    """Return True if calibration history already contains this weekend."""
    if not weekend_of:
        return False
    return any(
        entry.get("weekend_of") == weekend_of
        for entry in calibration.get("history", []) or []
    )


def calibration_freeze_path(data_dir: str, weekend_of: str) -> str:
    return os.path.join(data_dir, FREEZE_DIR_NAME, f"{weekend_of}.json")


def save_calibration_freeze(
    data_dir: str,
    weekend_of: str,
    calibration: dict,
    *,
    source: str,
    movies: list[str] | None = None,
    overwrite: bool = False,
) -> str | None:
    """Persist a pre-actual calibration snapshot for one opening weekend.

    Existing snapshots are never overwritten by default. If calibration already
    contains a history entry for the same weekend, return None rather than
    saving a contaminated "pre-actual" freeze.
    """
    if not weekend_of:
        return None

    path = calibration_freeze_path(data_dir, weekend_of)
    if os.path.exists(path) and not overwrite:
        return path

    if not overwrite and calibration_has_weekend(calibration, weekend_of):
        return None

    freeze_dir = os.path.dirname(path)
    os.makedirs(freeze_dir, exist_ok=True)
    payload = {
        "schema": 1,
        "description": (
            "Pre-actual calibration snapshot for clean live-model replays. "
            "Use this instead of calibration.json when auditing what the model "
            "would have predicted before reported actuals were learned."
        ),
        "weekend_of": weekend_of,
        "frozen_at": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "movies": sorted(set(movies or [])),
        "calibration": json.loads(json.dumps(calibration)),
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return path


def load_calibration_freeze(data_dir: str, weekend_of: str) -> dict:
    """Load the calibration payload from a freeze file."""
    path = calibration_freeze_path(data_dir, weekend_of)
    with open(path, "r") as f:
        payload = json.load(f)
    return payload.get("calibration", payload)
