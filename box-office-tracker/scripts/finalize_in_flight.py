#!/usr/bin/env python3
"""Is a scrape run's finalize job writing to main right now?

The forecast job (phase=forecast) and finalize both append to the same derived
files (prediction-log.csv, ensemble-log.csv, ...). Finalize also carries the
merged scrape rows, and its push loop cannot resolve a conflict in those logs,
so the forecast job must never push under it. This asks GitHub.

Exit status 0: no finalize in flight (or GitHub could not be asked: a forecast
is never blocked by an API error). Exit status 1: one is running.

    GITHUB_TOKEN=... GITHUB_REPOSITORY=owner/repo python3 scripts/finalize_in_flight.py [--wait MINUTES]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
WORKFLOW = "box-office-pipeline.yml"
# Runs of these lanes have no finalize job: skip their job listings.
LANE_WORDS = ("fandango", "cinemark", "alamo", "harkins", "webedia", "regal", "collect-links",
              "calibrate", "forecast", "amc bridge", "probe")
POLL_SECONDS = 60


def _get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "box-office-tracker"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def candidate_runs(runs, own_run_id=""):
    """In-progress runs that could own a finalize job (the scrape phase)."""
    out = []
    for run in runs or []:
        title = (run.get("display_title") or run.get("name") or "").lower()
        if str(run.get("id")) == str(own_run_id) or any(word in title for word in LANE_WORDS):
            continue
        out.append(run)
    return out


def finalize_running(jobs):
    return any((job.get("name") or "").strip().lower() == "finalize" and job.get("status") == "in_progress"
               for job in jobs or [])


def in_flight(repo, token, own_run_id="", get=_get):
    runs = get(f"{API}/repos/{repo}/actions/workflows/{WORKFLOW}/runs?status=in_progress&per_page=50", token)
    for run in candidate_runs(runs.get("workflow_runs"), own_run_id):
        jobs = get(f"{API}/repos/{repo}/actions/runs/{run['id']}/jobs?per_page=50", token)
        if finalize_running(jobs.get("jobs")):
            return run.get("display_title") or str(run.get("id"))
    return None


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    wait_minutes = float(argv[argv.index("--wait") + 1]) if "--wait" in argv else 0.0
    repo = os.environ.get("GITHUB_REPOSITORY") or ""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not repo or not token:
        print("finalize check: no repository or token in the environment; assuming none in flight")
        return 0
    deadline = time.monotonic() + wait_minutes * 60
    while True:
        try:
            owner = in_flight(repo, token, os.environ.get("GITHUB_RUN_ID") or "")
        except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
            print(f"finalize check: GitHub not reachable ({type(exc).__name__}); assuming none in flight")
            return 0
        if not owner:
            print("finalize check: none in flight")
            return 0
        if time.monotonic() >= deadline:
            print(f"finalize check: '{owner}' is finalizing")
            return 1
        print(f"finalize check: '{owner}' is finalizing; waiting")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
