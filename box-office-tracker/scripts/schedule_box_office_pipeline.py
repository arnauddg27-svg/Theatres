#!/usr/bin/env python3
"""Dispatch due Box Office Pipeline slots.

The same scheduler powers two layers:

* primary: GitHub Actions runs this every 30 minutes with github.token.
* watchdog: the VPS cron runs this every 30 minutes and only dispatches if the
  primary scheduler missed a slot past the fallback grace window.

Both layers use the same slot table and the same recent-run check, so they do
not drift into subtly different schedules.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Default location for the token-error marker (repo-relative: box-office-tracker/data/).
_DEFAULT_TOKEN_ERROR_MARKER = str(
    Path(__file__).resolve().parent.parent / "data" / "dispatch-token-error.marker"
)


def _write_token_error_marker(path: str, detail: str) -> None:
    """Record that dispatch is blocked by a bad GitHub token (visible signal)."""
    if not path:
        return
    try:
        marker = Path(path)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            f"{dt.datetime.now(dt.timezone.utc).isoformat()} {detail}\n"
        )
    except OSError:
        pass


def _clear_token_error_marker(path: str) -> None:
    """Clear the token-error marker once the token works again."""
    if not path:
        return
    try:
        Path(path).unlink()
    except (FileNotFoundError, OSError):
        pass


def _report_http_error(exc: urllib.error.HTTPError, marker_path: str) -> int:
    """Classify a GitHub API HTTPError, surface it loudly, and return exit code 1.

    A 401/403 means the token is expired/invalid — the operator's "token
    confusion" symptom, previously a SILENT `return 1`. Now it prints a distinct
    message and writes a marker file so the failure is visible.
    """
    code = getattr(exc, "code", None)
    if code in (401, 403):
        msg = (
            f"GitHub token expired or invalid (HTTP {code}); dispatch is disabled "
            "until the token is refreshed."
        )
        print(f"❌ {msg}", file=sys.stderr)
        _write_token_error_marker(marker_path, msg)
    else:
        reason = getattr(exc, "reason", "") or getattr(exc, "msg", "")
        print(f"GitHub API request failed: HTTP {code} {reason}", file=sys.stderr)
    return 1


# How many failures of the SAME slot to retry before giving up and alarming.
MAX_SLOT_RETRIES = 3

API = "https://api.github.com"
DEFAULT_WORKFLOW = "box-office-pipeline.yml"
DEFAULT_REF = "main"


def pipeline_inputs(
    phase: str,
    tz_group: str = "ALL",
    force: str = "false",
    snapshots: str = "false",
    snapshots_only: str = "false",
) -> dict[str, str]:
    return {
        "phase": phase,
        "tz_group": tz_group,
        "force": force,
        "test": "",
        "pre_reservation_snapshots": snapshots,
        "snapshots_only": snapshots_only,
    }


def cinemark_slot_inputs(mode: str = "") -> dict[str, str]:
    """Inputs for a Cinemark direct-lane slot (mode '' = pre, 'post' = census)."""
    inputs = pipeline_inputs("scrape-cinemark", "ALL", "false", "true", "true")
    if mode:
        inputs["cinemark_mode"] = mode
    return inputs


def fandango_slot_inputs(shard: int, num_shards: int,
                         order: str | None = None) -> dict[str, str]:
    """Inputs for one Fandango shard slot — phase + which 1/N slice of the pool."""
    inputs = pipeline_inputs("scrape-fandango", "ALL", "false", "true", "true")
    inputs["fandango_shard"] = str(shard)
    inputs["fandango_num_shards"] = str(num_shards)
    if order:
        inputs["fandango_order"] = order
    return inputs


@dataclass(frozen=True)
class Slot:
    name: str
    title: str
    cron_days: frozenset[int]
    hour: int
    minute: int
    inputs: dict[str, str]


# UTC weekday numbers match cron: Sunday=0, Monday=1, ... Saturday=6.
# Snapshot runs at 02:30 UTC, so UTC Sunday is Saturday night in U.S. time.
# Do not include UTC Monday in the 02:30Z snapshot: that would be Sunday night
# locally, just before the Monday 07:00 UTC post-Sunday regular scrape.
# Pre-reservation snapshots also run Monday-Wednesday (early-lead reads of the
# UPCOMING weekend's advance sales): the daytime 14:30Z/22:30Z slots run every
# UTC day, and 02:30Z adds UTC Tue/Wed (Monday/Tuesday night locally;
# Wednesday night was already covered via UTC Thursday). Monday collect-links
# slots exist so those early snapshots have fresh links; where a slice is
# missing the snapshot lane's targeted link repair rebuilds it.
# Collect-links runs Mon-Wed, but Polymarket sometimes lists a weekend's
# market later than that (One Night Only appeared after Wed 2026-08-05, so
# Phase 1 cleanly skipped, showtime-links stayed on the prior weekend, and
# every Friday snapshot lane hard-failed "run Phase 1 first" — the weekend's
# capture was lost). The early slot in each group also runs Thursday so a
# late-listed market still gets links before previews.
SLOTS: tuple[Slot, ...] = (
    Slot(
        "collect-links ET 13Z",
        "box office collect-links ET",
        frozenset({1, 2, 3, 4}),
        13,
        0,
        pipeline_inputs("collect-links", "ET"),
    ),
    Slot(
        "collect-links CT 15Z",
        "box office collect-links CT",
        frozenset({1, 2, 3, 4}),
        15,
        0,
        pipeline_inputs("collect-links", "CT"),
    ),
    Slot(
        "collect-links PT 17Z",
        "box office collect-links PT",
        frozenset({1, 2, 3, 4}),
        17,
        0,
        pipeline_inputs("collect-links", "PT"),
    ),
    Slot(
        "collect-links ET 19Z",
        "box office collect-links ET",
        frozenset({1, 2, 3}),
        19,
        0,
        pipeline_inputs("collect-links", "ET"),
    ),
    Slot(
        "collect-links CT 21Z",
        "box office collect-links CT",
        frozenset({1, 2, 3}),
        21,
        0,
        pipeline_inputs("collect-links", "CT"),
    ),
    Slot(
        "collect-links PT 23Z",
        "box office collect-links PT",
        frozenset({1, 2, 3}),
        23,
        0,
        pipeline_inputs("collect-links", "PT"),
    ),
    Slot(
        "snapshot 02:30Z",
        "box office scrape snapshot",
        frozenset({0, 2, 3, 4, 5, 6}),
        2,
        30,
        pipeline_inputs("scrape", "ALL", "true", "true", "true"),
    ),
    # AMC queue-wall resilience: on 2026-07-29 AMC put its whole site behind a
    # Queue-It waiting room (Spider-Man on-sale surge) and the two daily AMC
    # snapshot lanes read 0% coverage for days. The wall flaps on ~hour time-
    # scales — a Friday PT leg at 19:23Z passed clean minutes after the ET leg
    # was fully walled — so two extra daily attempts catch open windows. The
    # scraper still aborts politely on any queue redirect; snapshot-only runs
    # bypass the scrape dedup guard, and snapshot_bucket dedup makes extra
    # passes pure additional readings whenever AMC is healthy.
    Slot(
        "snapshot 14:30Z",
        "box office scrape snapshot",
        frozenset({0, 1, 2, 3, 4, 5, 6}),
        14,
        30,
        pipeline_inputs("scrape", "ALL", "true", "true", "true"),
    ),
    Slot(
        "snapshot 22:30Z",
        "box office scrape snapshot",
        frozenset({0, 1, 2, 3, 4, 5, 6}),
        22,
        30,
        pipeline_inputs("scrape", "ALL", "true", "true", "true"),
    ),
    # Fandango (Regal/Cinemark) pre-reservation snapshots — SHARDED across the
    # opening-weekend night. Fandango's seat limit is a per-Azure-range budget
    # that recovers in ~1 h, so fan-out can't beat it; instead 6 slots one hour
    # apart each scrape a different 1/6 of the pool (one fresh IP, alone), and
    # together cover all ~320 theatres in a single night. Same cron_days as the
    # AMC 02:30Z snapshot, including its Mon-Wed pre-opening nights (UTC
    # Tue/Wed/Thu): fandango_collect anchors those forward to the upcoming
    # Friday and renders date-parameterized theater pages. UTC Monday (Sunday
    # night) stays excluded. Isolated lane; gated out of the model until
    # Phase C.
    Slot("snapshot fandango 03Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 3, 0, fandango_slot_inputs(0, 6)),
    Slot("snapshot fandango 04Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 4, 0, fandango_slot_inputs(1, 6)),
    Slot("snapshot fandango 05Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 5, 0, fandango_slot_inputs(2, 6)),
    Slot("snapshot fandango 06Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 6, 0, fandango_slot_inputs(3, 6)),
    Slot("snapshot fandango 07Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 7, 0, fandango_slot_inputs(4, 6)),
    Slot("snapshot fandango 08Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 8, 0, fandango_slot_inputs(5, 6)),
    # SECOND nightly pass over the core ~160 theatres (shards 0-2 of the 6-way
    # split) at 09-11Z — gives those a second pre-reservation reading each night
    # (evening via 03-05Z + overnight here) so we capture how fast seats fill,
    # while the full 320 still gets one reading. Spaced ≥1 h from the evening
    # slots and from each other so Fandango's per-range limit stays recovered.
    Slot("snapshot fandango core 09Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 9, 0, fandango_slot_inputs(0, 6)),
    Slot("snapshot fandango core 10Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 10, 0, fandango_slot_inputs(1, 6)),
    Slot("snapshot fandango core 11Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 11, 0, fandango_slot_inputs(2, 6)),
    # SECOND-PASS SYMMETRY (2026-08-31, expanded 331-theatre Regal-only pool):
    # shards 3-5 historically got only their single overnight read while shards
    # 0-2 got velocity (09-11Z) and near-showtime (16-20Z) passes. With the
    # lane Regal-only and the budget per-slot unchanged (~55 renders at cap 1),
    # give shards 3-5 the same treatment: a 12-14Z velocity pass and a 21-23Z
    # near-showtime pass (17:00-19:00 ET — evening shows 1-4h out). All slots
    # stay >=1h apart, matching the budget's ~1h recovery.
    Slot("snapshot fandango core 12Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 12, 0, fandango_slot_inputs(3, 6)),
    Slot("snapshot fandango core 13Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 13, 0, fandango_slot_inputs(4, 6)),
    Slot("snapshot fandango core 14Z", "box office scrape-fandango ALL",
         frozenset({0, 2, 3, 4, 5, 6}), 14, 0, fandango_slot_inputs(5, 6)),
    Slot("snapshot fandango near 21Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 21, 0, fandango_slot_inputs(3, 6, order="nearest")),
    Slot("snapshot fandango near 22Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 22, 0, fandango_slot_inputs(4, 6, order="nearest")),
    Slot("snapshot fandango near 23Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 23, 0, fandango_slot_inputs(5, 6, order="nearest")),
    # NEAR-SHOWTIME afternoon pass over the core theatres, nearest-show-first:
    # the overnight slots capture at a median 13-16h lead (advance sales only),
    # which is why family-film occupancy reads near zero and the cross-chain
    # share stays family-gated. These read matinee/early-evening shows 1-4h out,
    # where advance-online occupancy best approximates final attendance —
    # accumulating the like-for-like data that eventually lifts the family gate.
    # Weekend-only by design: pre-opening days have no shows within hours, so a
    # near-showtime pass is meaningless there.
    Slot("snapshot fandango near 16Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 16, 0, fandango_slot_inputs(0, 6, order="nearest")),
    Slot("snapshot fandango near 18Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 18, 0, fandango_slot_inputs(1, 6, order="nearest")),
    Slot("snapshot fandango near 20Z", "box office scrape-fandango ALL",
         frozenset({0, 4, 5, 6}), 20, 0, fandango_slot_inputs(2, 6, order="nearest")),
    # Cinemark DIRECT lane (cinemark_collect.py; scale-validated 2026-08-31:
    # zero blocks over 35 sustained minutes from one IP, so no sharding —
    # one long job per pass). Read structure per design:
    #   pre passes EVERY day, covering today + all remaining/upcoming window
    #   days via the 15-day date carousel (Mon-Wed = upcoming weekend only);
    #   post census on show days only (UTC Fri/Sat/Sun/Mon early hours =
    #   Thu-Sun evenings locally): revisits seat-map URLs stored by the pre
    #   passes for shows that have since started (the page drops started
    #   shows, so day-of finals must come from stored links — AMC pattern).
    Slot("cinemark pre 09:20Z", "box office scrape-cinemark ALL",
         frozenset({0, 1, 2, 3, 4, 5, 6}), 9, 20, cinemark_slot_inputs()),
    Slot("cinemark pre 19:20Z", "box office scrape-cinemark ALL",
         frozenset({0, 1, 2, 3, 4, 5, 6}), 19, 20, cinemark_slot_inputs()),
    Slot("cinemark post 06:20Z", "box office scrape-cinemark ALL",
         frozenset({0, 1, 5, 6}), 6, 20, cinemark_slot_inputs("post")),
    Slot(
        "regular scrape 07Z",
        "box office scrape regular",
        frozenset({0, 1, 5, 6}),
        7,
        0,
        pipeline_inputs("scrape", "ALL", "false", "false", "false"),
    ),
    Slot(
        "calibrate Wednesday 12Z",
        "box office calibrate ALL",
        frozenset({3}),
        12,
        0,
        pipeline_inputs("calibrate", "ALL"),
    ),
)


def cron_dow(ts: dt.datetime) -> int:
    return (ts.weekday() + 1) % 7


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).replace(second=0, microsecond=0)


def candidate_due_slots(
    *,
    now: dt.datetime,
    lookback_minutes: int,
    mode: str,
    fallback_grace_minutes: int,
) -> list[tuple[dt.datetime, Slot]]:
    now = now.astimezone(dt.timezone.utc).replace(second=0, microsecond=0)
    window_start = now - dt.timedelta(minutes=lookback_minutes)
    window_end = now
    if mode == "watchdog":
        window_end = now - dt.timedelta(minutes=fallback_grace_minutes)
    if window_end < window_start:
        return []

    due: list[tuple[dt.datetime, Slot]] = []
    days_to_check = (lookback_minutes // 1440) + 2
    for slot in SLOTS:
        for days_back in range(days_to_check):
            candidate_date = (now - dt.timedelta(days=days_back)).date()
            scheduled_at = dt.datetime(
                candidate_date.year,
                candidate_date.month,
                candidate_date.day,
                slot.hour,
                slot.minute,
                tzinfo=dt.timezone.utc,
            )
            if cron_dow(scheduled_at) not in slot.cron_days:
                continue
            if window_start <= scheduled_at <= window_end:
                due.append((scheduled_at, slot))
    return sorted(due, key=lambda item: item[0])


class GitHubClient:
    def __init__(self, *, repo: str, token: str, api_url: str = API) -> None:
        self.repo = repo
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request_json(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.api_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"GitHub API {method} {path} failed: HTTP {exc.code} {detail}", file=sys.stderr)
            raise


def parse_github_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def recent_pipeline_run_exists(
    *,
    client: GitHubClient,
    workflow: str,
    titles: tuple[str, ...],
    scheduled_at: dt.datetime,
    now: dt.datetime,
) -> bool:
    runs = client.request_json(
        "GET",
        f"/repos/{client.repo}/actions/workflows/{workflow}/runs?event=workflow_dispatch&per_page=100",
    ).get("workflow_runs", [])
    lower_bound = scheduled_at - dt.timedelta(minutes=5)
    upper_bound = now + dt.timedelta(minutes=5)
    failed: list[dict] = []
    for run in runs:
        if run.get("display_title") not in titles:
            continue
        created_at = parse_github_time(run["created_at"])
        if not (lower_bound <= created_at <= upper_bound):
            continue
        # A run that FAILED did not service the slot. Counting it as serviced
        # (the old behaviour — this check looked only at display_title and
        # created_at) meant no failed slot was ever retried by either the
        # primary scheduler or the VPS watchdog: a leg that died in 30s on a
        # queue wall, a lock timeout or a stale-links abort silently consumed
        # the slot for the rest of the weekend. Treat only successful and
        # still-running runs as servicing it, so a failure gets re-dispatched
        # while the slot is still inside its lookback/grace window.
        if run.get("status") == "completed" and run.get("conclusion") not in (
            None, "success", "skipped", "neutral",
        ):
            failed.append(run)
            if len(failed) >= MAX_SLOT_RETRIES:
                # CIRCUIT BREAKER. Retrying is right for a transient fault, but
                # a PERSISTENT one then re-runs every slot forever: an
                # unresolvable seat-map collision failed the 22:30Z and 02:30Z
                # slots 8 times in a night, each run re-collecting ~2,000 rows
                # and discarding them at finalize. Stop re-dispatching and say
                # so loudly — a slot that failed this many times needs a human,
                # not another attempt.
                print(
                    f"::warning::{titles[0]} has failed {len(failed)} times in a "
                    f"row; NOT re-dispatching. Latest: {run.get('html_url')} "
                    f"({run.get('conclusion')}). This is a persistent fault — "
                    f"retrying cannot fix it."
                )
                return True
            print(
                f"Ignoring failed run for {titles[0]}: {run.get('display_title')} "
                f"{run.get('html_url')} concluded {run.get('conclusion')}; "
                f"slot is still due ({len(failed)}/{MAX_SLOT_RETRIES} attempts used)"
            )
            continue
        print(
            f"Skipping {titles[0]}: existing run {run.get('display_title')} "
            f"{run.get('html_url')} created at {run['created_at']}"
        )
        return True
    return False


def scheduled_display_title(slot: Slot) -> str:
    return f"box office scheduled {slot.name}"


def expected_slots_for_date(date: dt.date) -> list[tuple[dt.datetime, Slot]]:
    """Every slot whose cron fires on this UTC date, with its scheduled time."""
    out = []
    for slot in SLOTS:
        scheduled_at = dt.datetime(date.year, date.month, date.day,
                                   slot.hour, slot.minute, tzinfo=dt.timezone.utc)
        if cron_dow(scheduled_at) in slot.cron_days:
            out.append((scheduled_at, slot))
    return sorted(out, key=lambda item: item[0])


# A run created within this window of its scheduled time counts as the slot
# having been DISPATCHED (watchdog fallbacks land 30-75 min late; scheduler
# retries later still). The ledger asks "did any layer fire at all?", not
# "did it succeed?" — failures are the retry system's domain.
RECONCILE_GRACE_MINUTES = 180


def missing_slots(
    expected: list[tuple[dt.datetime, Slot]],
    runs: list[dict],
    grace_minutes: int = RECONCILE_GRACE_MINUTES,
) -> list[tuple[dt.datetime, Slot]]:
    """Expected slots with NO run (any conclusion) near their time."""
    missing = []
    for scheduled_at, slot in expected:
        titles = (scheduled_display_title(slot), slot.title)
        lower = scheduled_at - dt.timedelta(minutes=5)
        upper = scheduled_at + dt.timedelta(minutes=grace_minutes)
        for run in runs:
            if run.get("display_title") not in titles:
                continue
            created_at = parse_github_time(run["created_at"])
            if lower <= created_at <= upper:
                break
        else:
            missing.append((scheduled_at, slot))
    return missing


def reconcile_date(*, client: GitHubClient, workflow: str, date: dt.date) -> int:
    """After-the-fact slot ledger (audit 2026-08-23).

    Every monitor before this one watches RUNS — a slot that was never
    dispatched at all (GitHub cron gap >75 min while the VPS watchdog is
    down: both layers share the same 30-min shape) left zero trace anywhere.
    Recompute yesterday's expected slots from the same table the schedulers
    use and warn for any with no run whatsoever. Advisory: always exits 0.
    """
    expected = expected_slots_for_date(date)
    next_day = date + dt.timedelta(days=1)
    runs = client.request_json(
        "GET",
        f"/repos/{client.repo}/actions/workflows/{workflow}/runs"
        f"?event=workflow_dispatch&per_page=100&created={date}..{next_day}",
    ).get("workflow_runs", [])
    gone = missing_slots(expected, runs)
    print(f"slot ledger for {date}: {len(expected)} expected, "
          f"{len(expected) - len(gone)} dispatched, {len(gone)} missing")
    for scheduled_at, slot in gone:
        print(
            f"::warning::slot NEVER DISPATCHED — {slot.name} expected at "
            f"{scheduled_at.strftime('%H:%MZ')} on {date} has no run at all; "
            f"both dispatch layers (GitHub cron + VPS watchdog) missed it"
        )
    return 0


def dispatch_slot(
    *,
    client: GitHubClient,
    workflow: str,
    ref: str,
    slot: Slot,
    mode: str,
    dry_run: bool,
) -> None:
    workflow_inputs = dict(slot.inputs)
    workflow_inputs["schedule_slot"] = slot.name
    workflow_inputs["schedule_mode"] = mode
    body = {"ref": ref, "inputs": workflow_inputs}
    if dry_run:
        print(f"DRY RUN dispatch {scheduled_display_title(slot)}: {json.dumps(body, sort_keys=True)}")
        return
    client.request_json(
        "POST",
        f"/repos/{client.repo}/actions/workflows/{workflow}/dispatches",
        body,
    )
    print(f"Dispatched {scheduled_display_title(slot)}: {json.dumps(workflow_inputs, sort_keys=True)}")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from None
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"{value!r} must be positive")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("primary", "watchdog"), default=os.environ.get("SCHEDULER_MODE", "primary"))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or os.environ.get("GH_REPO"))
    parser.add_argument("--workflow", default=os.environ.get("TARGET_WORKFLOW", DEFAULT_WORKFLOW))
    parser.add_argument("--ref", default=os.environ.get("TARGET_REF", DEFAULT_REF))
    parser.add_argument("--lookback-minutes", type=positive_int, default=positive_int(os.environ.get("LOOKBACK_MINUTES", "75")))
    parser.add_argument(
        "--fallback-grace-minutes",
        type=positive_int,
        default=positive_int(os.environ.get("FALLBACK_GRACE_MINUTES", "30")),
        help="watchdog mode waits this long after a slot before dispatching it",
    )
    parser.add_argument("--now", help="override current UTC time for tests, e.g. 2026-05-24T04:00:00Z")
    parser.add_argument("--dry-run", action="store_true", default=os.environ.get("DRY_RUN", "false").lower() == "true")
    parser.add_argument(
        "--token-env",
        default=os.environ.get("TOKEN_ENV", "GITHUB_TOKEN"),
        help="environment variable containing the GitHub token",
    )
    parser.add_argument(
        "--token-error-marker",
        default=_DEFAULT_TOKEN_ERROR_MARKER,
        help="file written when the GitHub token is rejected (401/403); cleared on success",
    )
    parser.add_argument(
        "--reconcile",
        default=None,
        metavar="DATE",
        help="slot-ledger mode: report expected slots on DATE (YYYY-MM-DD or "
             "'yesterday', UTC) that no run ever serviced; dispatches nothing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.repo:
        print("repo is required via --repo, GITHUB_REPOSITORY, or GH_REPO", file=sys.stderr)
        return 2
    if args.lookback_minutes > 1440:
        print("--lookback-minutes must be 1440 or less", file=sys.stderr)
        return 2
    if args.mode == "primary" and args.lookback_minutes > 240:
        print("--lookback-minutes must be 240 or less in primary mode", file=sys.stderr)
        return 2

    now = parse_utc(args.now) if args.now else dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)

    if args.reconcile:
        token = os.environ.get(args.token_env) or os.environ.get("GH_TOKEN")
        if not token:
            print(f"{args.token_env} or GH_TOKEN is required for --reconcile", file=sys.stderr)
            return 1
        if args.reconcile == "yesterday":
            target = (now - dt.timedelta(days=1)).date()
        else:
            target = dt.date.fromisoformat(args.reconcile)
        return reconcile_date(
            client=GitHubClient(repo=args.repo, token=token),
            workflow=args.workflow,
            date=target,
        )

    due = candidate_due_slots(
        now=now,
        lookback_minutes=args.lookback_minutes,
        mode=args.mode,
        fallback_grace_minutes=args.fallback_grace_minutes,
    )
    window_start = now - dt.timedelta(minutes=args.lookback_minutes)
    window_end = now if args.mode == "primary" else now - dt.timedelta(minutes=args.fallback_grace_minutes)
    if not due:
        if window_end < window_start:
            print(
                f"No due slots for {args.mode}: lookback window is shorter than "
                f"the {args.fallback_grace_minutes} minute fallback grace."
            )
            return 0
        print(f"No due slots for {args.mode} between {window_start.isoformat()} and {window_end.isoformat()}")
        return 0

    token = os.environ.get(args.token_env) or os.environ.get("GH_TOKEN")
    if not token:
        print(f"{args.token_env} or GH_TOKEN is required to inspect and dispatch GitHub workflow runs", file=sys.stderr)
        return 1
    client = GitHubClient(repo=args.repo, token=token)

    try:
        for scheduled_at, slot in due:
            print(f"Due slot {slot.name} at {scheduled_at.isoformat()} -> {scheduled_display_title(slot)}")
            if recent_pipeline_run_exists(
                client=client,
                workflow=args.workflow,
                titles=(scheduled_display_title(slot), slot.title),
                scheduled_at=scheduled_at,
                now=now,
            ):
                continue
            dispatch_slot(
                client=client,
                workflow=args.workflow,
                ref=args.ref,
                slot=slot,
                mode=args.mode,
                dry_run=args.dry_run,
            )
    except urllib.error.HTTPError as exc:
        try:
            return _report_http_error(exc, args.token_error_marker)
        finally:
            exc.close()
    except urllib.error.URLError as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        return 1
    # The token successfully inspected/dispatched runs — clear any prior alert.
    _clear_token_error_marker(args.token_error_marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
