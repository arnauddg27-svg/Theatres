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
from typing import Any


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


@dataclass(frozen=True)
class Slot:
    name: str
    title: str
    cron_days: frozenset[int]
    hour: int
    minute: int
    inputs: dict[str, str]


# UTC weekday numbers match cron: Sunday=0, Monday=1, ... Saturday=6.
SLOTS: tuple[Slot, ...] = (
    Slot(
        "collect-links ET 13Z",
        "box office collect-links ET",
        frozenset({2, 3}),
        13,
        0,
        pipeline_inputs("collect-links", "ET"),
    ),
    Slot(
        "collect-links CT 15Z",
        "box office collect-links CT",
        frozenset({2, 3}),
        15,
        0,
        pipeline_inputs("collect-links", "CT"),
    ),
    Slot(
        "collect-links PT 17Z",
        "box office collect-links PT",
        frozenset({2, 3}),
        17,
        0,
        pipeline_inputs("collect-links", "PT"),
    ),
    Slot(
        "collect-links ET 19Z",
        "box office collect-links ET",
        frozenset({2, 3}),
        19,
        0,
        pipeline_inputs("collect-links", "ET"),
    ),
    Slot(
        "collect-links CT 21Z",
        "box office collect-links CT",
        frozenset({2, 3}),
        21,
        0,
        pipeline_inputs("collect-links", "CT"),
    ),
    Slot(
        "collect-links PT 23Z",
        "box office collect-links PT",
        frozenset({2, 3}),
        23,
        0,
        pipeline_inputs("collect-links", "PT"),
    ),
    Slot(
        "snapshot 02:30Z",
        "box office scrape snapshot",
        frozenset({0, 1, 4, 5, 6}),
        2,
        30,
        pipeline_inputs("scrape", "ALL", "true", "true", "true"),
    ),
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
    for run in runs:
        if run.get("display_title") not in titles:
            continue
        created_at = parse_github_time(run["created_at"])
        if lower_bound <= created_at <= upper_bound:
            print(
                f"Skipping {titles[0]}: existing run {run.get('display_title')} "
                f"{run.get('html_url')} created at {run['created_at']}"
            )
            return True
    return False


def scheduled_display_title(slot: Slot) -> str:
    return f"box office scheduled {slot.name}"


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
        default=positive_int(os.environ.get("FALLBACK_GRACE_MINUTES", "90")),
        help="watchdog mode waits this long after a slot before dispatching it",
    )
    parser.add_argument("--now", help="override current UTC time for tests, e.g. 2026-05-24T04:00:00Z")
    parser.add_argument("--dry-run", action="store_true", default=os.environ.get("DRY_RUN", "false").lower() == "true")
    parser.add_argument(
        "--token-env",
        default=os.environ.get("TOKEN_ENV", "GITHUB_TOKEN"),
        help="environment variable containing the GitHub token",
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
        exc.close()
        return 1
    except urllib.error.URLError as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
