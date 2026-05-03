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
        return sha, {}
    try:
        return sha, json.loads(result.stdout)
    except json.JSONDecodeError:
        return sha, {}


def _github_run_is_active(run_id: str | None) -> bool | None:
    if not run_id:
        return None
    cmd = ["gh", "run", "view", str(run_id), "--json", "status,conclusion"]
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        cmd.extend(["--repo", repo])
    result = _run(
        cmd,
        capture=True,
    )
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    status = str(payload.get("status") or "")
    return status in {"queued", "in_progress", "waiting", "requested", "pending"}


def _lock_is_stale(metadata: dict[str, Any], ttl_seconds: int) -> bool:
    created_at = metadata.get("created_at_epoch")
    try:
        age = time.time() - float(created_at)
    except (TypeError, ValueError):
        age = ttl_seconds + 1
    if age < ttl_seconds:
        return False

    active = _github_run_is_active(str(metadata.get("run_id") or ""))
    if active is None:
        return age >= ttl_seconds
    return not active


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
            if _lock_is_stale(metadata, args.ttl_minutes * 60):
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
