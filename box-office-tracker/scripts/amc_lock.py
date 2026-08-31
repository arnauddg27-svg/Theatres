#!/usr/bin/env python3
"""Acquire or release the global AMC capacity lock for GitHub Actions.

The lock is represented by a dedicated remote branch. Creating a missing remote
ref is atomic on GitHub: when two jobs try to push the lock branch at the same
time, one succeeds and the other is rejected. That gives us a real cross-run
mutex without relying on GitHub Actions concurrency groups, which only keep one
pending run per group.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCK_BRANCH = "box-office-amc-lock"
LOCK_FILE = "amc-lock.json"

# Distinct from None: the GitHub run-status probe could not reach the API at all
# (rate limit / outage), so we genuinely do not know whether the lock holder is
# still running. This must NOT be treated as "holder is dead" — see _lock_is_stale.
RUN_STATE_UNKNOWN = "unknown"

# When the run-status probe is UNKNOWN, only break the lock after this multiple of
# the normal TTL. A briefly-stuck lock is visible and self-heals at the hard
# ceiling; breaking a still-active lock silently double-runs AMC (data corruption).
AMC_LOCK_HARD_TTL_MULTIPLIER = float(os.environ.get("AMC_LOCK_HARD_TTL_MULTIPLIER", "3.0"))
# Retry budget for the run-status probe before declaring UNKNOWN.
AMC_LOCK_PROBE_ATTEMPTS = int(os.environ.get("AMC_LOCK_PROBE_ATTEMPTS", "3"))
AMC_LOCK_PROBE_BACKOFF_SEC = float(os.environ.get("AMC_LOCK_PROBE_BACKOFF_SEC", "2.0"))


def _run(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = False,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=capture,
        check=check,
    )


def _git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return _run(["git", *args], cwd=cwd, check=check)


def _remote_url(repo_root: Path) -> str:
    result = _git(repo_root, "remote", "get-url", "origin", check=True)
    return result.stdout.strip()


def _copy_auth_config(source_repo: Path, target_repo: Path) -> None:
    """Copy checkout-provided GitHub auth headers into the temp lock repo."""
    result = _git(source_repo, "config", "--get-regexp", r"^http\..*\.extraheader$")
    if result.returncode != 0:
        return
    for line in result.stdout.splitlines():
        if not line.strip() or " " not in line:
            continue
        key, value = line.split(" ", 1)
        _git(target_repo, "config", "--local", key, value, check=True)


def _lock_ref(branch: str) -> str:
    return f"refs/heads/{branch}"


def _current_lock_sha(repo_root: Path, branch: str) -> str | None:
    result = _git(repo_root, "ls-remote", "--heads", "origin", _lock_ref(branch))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-remote failed")
    line = result.stdout.strip()
    if not line:
        return None
    return line.split()[0]


def _read_lock_metadata(repo_root: Path, branch: str) -> tuple[str, dict[str, Any]] | None:
    sha = _current_lock_sha(repo_root, branch)
    if not sha:
        return None
    result = _git(repo_root, "show", f"{sha}:{LOCK_FILE}")
    if result.returncode != 0:
        # The lock branch is never fetched by actions/checkout (fetch-depth 50
        # of main only), so the lock commit is usually NOT in the local object
        # store and `git show` fails. The old code returned (sha, {}) here; an
        # empty payload has no created_at/run_id, which _lock_is_stale reads as
        # an over-TTL orphan — so every lane instantly broke every other lane's
        # LIVE lock and the "global" lock serialized nothing. Fetch the ref,
        # then retry the read.
        _git(repo_root, "fetch", "--depth", "1", "origin", _lock_ref(branch))
        result = _git(repo_root, "show", f"{sha}:{LOCK_FILE}")
    if result.returncode != 0:
        # Still unreadable (branch advanced between ls-remote and fetch, or the
        # fetch failed). Unreadable must mean "assume HELD", never "breakable":
        # the sentinel below makes _lock_is_stale return False, and the next
        # poll re-resolves the sha and tries again.
        return sha, {"payload_unreadable": True}
    try:
        return sha, json.loads(result.stdout)
    except json.JSONDecodeError:
        return sha, {"payload_unreadable": True}


def _github_run_is_active(run_id: str | None) -> bool | None | str:
    """Tri-state run-status probe.

    Returns:
      True  — the run is confirmed active (queued/in_progress/...).
      False — the run is confirmed NOT active (completed/cancelled/...).
      None  — no run id recorded (the lock is genuinely orphaned).
      RUN_STATE_UNKNOWN — the GitHub API could not be reached after retries, so
        the holder's liveness is unknown. Callers must NOT treat this as "dead".

    The distinction matters: the old code returned None for BOTH "no run id" and
    "API failed", so a transient API outage on an over-TTL lock would break a
    still-active lock and double-run AMC.
    """
    if not run_id:
        return None
    cmd = ["gh", "run", "view", str(run_id), "--json", "status,conclusion"]
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        cmd.extend(["--repo", repo])
    for attempt in range(max(1, AMC_LOCK_PROBE_ATTEMPTS)):
        result = _run(cmd, capture=True)
        if result.returncode == 0:
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                payload = None
            if payload is not None:
                status = str(payload.get("status") or "")
                return status in {"queued", "in_progress", "waiting", "requested", "pending"}
        # API call failed or returned unparseable output — retry, then give up.
        if attempt < AMC_LOCK_PROBE_ATTEMPTS - 1:
            time.sleep(AMC_LOCK_PROBE_BACKOFF_SEC * (attempt + 1))
    return RUN_STATE_UNKNOWN


def _lock_is_stale(metadata: dict[str, Any], ttl_seconds: int,
                   hard_ttl_seconds: float | None = None,
                   current_run_id: str | None = None) -> bool:
    if hard_ttl_seconds is None:
        hard_ttl_seconds = ttl_seconds * AMC_LOCK_HARD_TTL_MULTIPLIER
    if metadata.get("payload_unreadable"):
        # We could not read the lock payload at all, so we know nothing about
        # its age or holder. Never break what we cannot read — a waiter that
        # eventually times out is a visible red run; a wrongly broken live lock
        # is a silent AMC double-run.
        return False
    created_at = metadata.get("created_at_epoch")
    try:
        age = time.time() - float(created_at)
    except (TypeError, ValueError):
        age = ttl_seconds + 1
    if age < ttl_seconds:
        return False

    # A lock held by MY OWN workflow run was leaked by an earlier leg of this
    # run: the scrape matrix is max-parallel: 1, so no sibling leg can be
    # holding it while I am the one executing. The liveness probe cannot see
    # this — it asks GitHub about the WORKFLOW run id, which is shared by every
    # leg, so it reports "in_progress" (that's me) and the lock looked alive
    # forever. The remaining legs then burned their full wait budget and failed,
    # and the lock only became breakable after the whole run ended.
    if current_run_id and str(metadata.get("run_id") or "") == str(current_run_id):
        print(
            f"AMC lock: holder run {current_run_id} is THIS run — an earlier "
            f"leg leaked it (legs are sequential), breaking after {age:.0f}s"
        )
        return True

    active = _github_run_is_active(str(metadata.get("run_id") or ""))
    if active is True:
        return False                      # holder confirmed alive — never break
    if active is False:
        return True                       # holder confirmed dead — safe to break
    if active is None:
        return True                       # no run id => orphaned; age already >= ttl
    # active == RUN_STATE_UNKNOWN: API unreachable, holder liveness unknown.
    # Prefer a stuck lock (visible, hard-ceiling-bounded) over a double-run race;
    # only break as a last resort once the hard ceiling is exceeded.
    return age >= hard_ttl_seconds


def _delete_lock(repo_root: Path, branch: str, expected_sha: str) -> bool:
    result = _git(
        repo_root,
        "push",
        f"--force-with-lease={_lock_ref(branch)}:{expected_sha}",
        "origin",
        f":{_lock_ref(branch)}",
    )
    return result.returncode == 0


def _create_lock_commit(repo_root: Path, branch: str, metadata: dict[str, Any]) -> tuple[bool, str]:
    remote = _remote_url(repo_root)
    with tempfile.TemporaryDirectory(prefix="amc-lock-") as tmp:
        tmp_path = Path(tmp)
        _git(tmp_path, "init", check=True)
        _git(tmp_path, "config", "user.name", "github-actions[bot]", check=True)
        _git(
            tmp_path,
            "config",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
            check=True,
        )
        _git(tmp_path, "remote", "add", "origin", remote, check=True)
        _copy_auth_config(repo_root, tmp_path)
        (tmp_path / LOCK_FILE).write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        _git(tmp_path, "add", LOCK_FILE, check=True)
        _git(tmp_path, "commit", "-m", "lock: box office AMC capacity", check=True)
        sha = _git(tmp_path, "rev-parse", "HEAD", check=True).stdout.strip()
        result = _git(tmp_path, "push", "origin", f"HEAD:{_lock_ref(branch)}")
        if result.returncode == 0:
            return True, sha
        return False, result.stderr.strip() or result.stdout.strip()


def _write_github_output(path: str | None, values: dict[str, str]) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        for key, value in values.items():
            f.write(f"{key}={value}\n")


def acquire(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    deadline = time.monotonic() + args.wait_seconds
    run_id = args.run_id or os.environ.get("GITHUB_RUN_ID", "")
    run_attempt = args.run_attempt or os.environ.get("GITHUB_RUN_ATTEMPT", "")

    while True:
        existing = _read_lock_metadata(repo_root, args.lock_branch)
        if existing:
            sha, metadata = existing
            owner = metadata.get("run_id", "unknown")
            mode = metadata.get("mode", "unknown")
            if metadata.get("payload_unreadable"):
                # Distinct from "held by run unknown": we could not READ the
                # payload (fetch failed, or the branch advanced mid-read), so
                # we are deliberately treating the lock as held. Name the
                # condition so a stuck-unreadable lock is diagnosable from logs.
                print(f"AMC lock: payload for {sha[:12]} unreadable this poll "
                      f"(fetch failed or lock moved) — assuming held")
            if _lock_is_stale(metadata, args.ttl_minutes * 60,
                              current_run_id=run_id):
                print(f"AMC lock: breaking stale lock {sha[:12]} from run {owner} ({mode})")
                if _delete_lock(repo_root, args.lock_branch, sha):
                    continue
                print("AMC lock: stale lock changed before deletion; retrying")
            else:
                remaining = max(0, int(deadline - time.monotonic()))
                if remaining <= 0:
                    print(f"AMC lock: timed out waiting for run {owner} ({mode})")
                    return 1
                print(
                    f"AMC lock: held by run {owner} ({mode}); "
                    f"waiting {min(args.poll_seconds, remaining)}s"
                )
                time.sleep(min(args.poll_seconds, remaining))
            continue

        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_at_epoch": time.time(),
            "mode": args.mode,
            "run_id": run_id,
            "run_attempt": run_attempt,
            "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "job": os.environ.get("GITHUB_JOB", ""),
            "actor": os.environ.get("GITHUB_ACTOR", ""),
        }
        ok, detail = _create_lock_commit(repo_root, args.lock_branch, metadata)
        if ok:
            print(f"AMC lock: acquired {detail[:12]} for {args.mode}")
            _write_github_output(
                args.github_output or os.environ.get("GITHUB_OUTPUT"),
                {"acquired": "true", "lock_sha": detail},
            )
            return 0

        print(f"AMC lock: acquire race lost ({detail}); retrying")
        if time.monotonic() >= deadline:
            print("AMC lock: timed out during acquire races")
            return 1
        time.sleep(args.poll_seconds)


def release(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    expected_sha = args.lock_sha or os.environ.get("AMC_LOCK_SHA", "")
    if not expected_sha:
        print("AMC lock: no lock sha supplied; nothing to release")
        return 0

    existing = _read_lock_metadata(repo_root, args.lock_branch)
    if not existing:
        print("AMC lock: branch already absent")
        return 0
    current_sha, metadata = existing
    if current_sha != expected_sha:
        print(
            "AMC lock: current lock is not ours "
            f"({current_sha[:12]} != {expected_sha[:12]}); leaving it in place"
        )
        return 0

    if _delete_lock(repo_root, args.lock_branch, current_sha):
        print(f"AMC lock: released {current_sha[:12]} from run {metadata.get('run_id', 'unknown')}")
        return 0
    print("AMC lock: release failed")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    acquire_parser = subparsers.add_parser("acquire")
    acquire_parser.add_argument("--repo-root", default=".")
    acquire_parser.add_argument("--lock-branch", default=LOCK_BRANCH)
    acquire_parser.add_argument("--mode", required=True)
    acquire_parser.add_argument("--run-id", default="")
    acquire_parser.add_argument("--run-attempt", default="")
    acquire_parser.add_argument("--wait-seconds", type=int, default=6 * 60 * 60)
    acquire_parser.add_argument("--poll-seconds", type=int, default=60)
    acquire_parser.add_argument("--ttl-minutes", type=int, default=360)
    acquire_parser.add_argument("--github-output", default="")
    acquire_parser.set_defaults(func=acquire)

    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("--repo-root", default=".")
    release_parser.add_argument("--lock-branch", default=LOCK_BRANCH)
    release_parser.add_argument("--lock-sha", default="")
    release_parser.set_defaults(func=release)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"AMC lock: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
