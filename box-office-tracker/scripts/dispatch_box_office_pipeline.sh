#!/usr/bin/env bash
# VPS cron wrapper for the Box Office Pipeline workflow.
#
# Usage:
#   dispatch_box_office_pipeline.sh collect-links ET
#   dispatch_box_office_pipeline.sh scrape
#   dispatch_box_office_pipeline.sh snapshot
#   dispatch_box_office_pipeline.sh calibrate
#
# Environment overrides:
#   GH_REPO=owner/repo            GitHub repo passed to `gh workflow run`
#   WORKFLOW_FILE=box-office-pipeline.yml
#   FORCE=true                   Pass force=true to the workflow
#   TEST=5                       Pass test=N to the workflow
#   GH_TOKEN_FILE=/path/.env      Optional env file containing GH_TOKEN
#   GH_REF=main                   Git ref passed to `gh workflow run --ref`
#   SKIP_GITHUB_AUTH_PROBE=true   Only for tests/emergencies; skips preflight
#   DISPATCH_STATE_DIR=/var/tmp/box-office-dispatch
#   DISPATCH_DEDUP_WINDOW_SEC=900

set -euo pipefail

WORKFLOW_FILE="${WORKFLOW_FILE:-box-office-pipeline.yml}"
GH_REPO="${GH_REPO:-}"
GH_REF="${GH_REF:-main}"
FORCE="${FORCE:-false}"
TEST="${TEST:-}"
GH_TOKEN_FILE="${GH_TOKEN_FILE:-}"
DISPATCH_STATE_DIR="${DISPATCH_STATE_DIR:-/var/tmp/box-office-dispatch}"
DISPATCH_DEDUP_WINDOW_SEC="${DISPATCH_DEDUP_WINDOW_SEC:-900}"
SKIP_GITHUB_AUTH_PROBE="${SKIP_GITHUB_AUTH_PROBE:-false}"

if [[ -n "$GH_TOKEN_FILE" ]]; then
  if [[ ! -f "$GH_TOKEN_FILE" ]]; then
    echo "GH_TOKEN_FILE does not exist: $GH_TOKEN_FILE" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$GH_TOKEN_FILE"
  if [[ -n "${GH_TOKEN:-}" ]]; then
    export GH_TOKEN
  fi
fi

usage() {
  echo "Usage: $0 collect-links ET|CT|PT|ALL | scrape | snapshot | calibrate" >&2
  exit 2
}

validate_github_auth() {
  if [[ -z "$GH_REPO" ]]; then
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: GH_REPO is required" >&2
    return 1
  fi
  if [[ -z "${GH_TOKEN:-}" ]]; then
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: GH_TOKEN is missing; set it in GH_TOKEN_FILE=$GH_TOKEN_FILE" >&2
    return 1
  fi

  if [[ "$SKIP_GITHUB_AUTH_PROBE" == "true" ]]; then
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: skipping GitHub auth preflight because SKIP_GITHUB_AUTH_PROBE=true"
    return 0
  fi

  local auth_probe
  if ! auth_probe="$(gh api "repos/${GH_REPO}" --jq .default_branch 2>&1)"; then
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: GitHub auth failed for ${GH_REPO}; refresh GH_TOKEN_FILE=$GH_TOKEN_FILE" >&2
    echo "Create a fine-grained GitHub token with Actions: read/write and Contents: read/write for ${GH_REPO}, then store it as GH_TOKEN in that env file." >&2
    echo "$auth_probe" >&2
    return 1
  fi
}

run_workflow() {
  validate_github_auth

  local -a cmd=(gh workflow run "$WORKFLOW_FILE" --ref "$GH_REF")
  if [[ -n "$GH_REPO" ]]; then
    cmd+=(--repo "$GH_REPO")
  fi
  cmd+=("$@")
  echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: ${cmd[*]}"
  "${cmd[@]}"
}

slot_key_for() {
  local mode="$1"
  local tz="${2:-ALL}"
  local repo="${GH_REPO:-default-repo}"
  printf '%s' "${repo}_${WORKFLOW_FILE}_${mode}_${tz}" \
    | tr -c 'A-Za-z0-9._=-' '_'
}

path_age_seconds() {
  python3 -c 'import os, sys, time; p=sys.argv[1]; print(int(time.time() - os.path.getmtime(p)) if os.path.exists(p) else 0)' "$1"
}

run_once_per_slot() {
  local mode="$1"
  local tz="${2:-ALL}"
  shift 2 || true

  mkdir -p "$DISPATCH_STATE_DIR"

  local slot_key lock_dir stamp_file now last age lock_age
  slot_key="$(slot_key_for "$mode" "$tz")"
  lock_dir="$DISPATCH_STATE_DIR/${slot_key}.lockdir"
  stamp_file="$DISPATCH_STATE_DIR/${slot_key}.stamp"
  now="$(date -u '+%s')"

  if ! mkdir "$lock_dir" 2>/dev/null; then
    lock_age="$(path_age_seconds "$lock_dir")"
    if [[ "$lock_age" =~ ^[0-9]+$ ]] && (( lock_age > DISPATCH_DEDUP_WINDOW_SEC )); then
      echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: removing stale slot lock (${mode} ${tz}, age ${lock_age}s)"
      rmdir "$lock_dir" 2>/dev/null || true
      if ! mkdir "$lock_dir" 2>/dev/null; then
        echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: duplicate slot already active (${mode} ${tz}); skipping"
        return 0
      fi
    else
      echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: duplicate slot already active (${mode} ${tz}); skipping"
      return 0
    fi
  fi
  trap "rmdir $(printf '%q' "$lock_dir") 2>/dev/null || true" EXIT

  if [[ -f "$stamp_file" ]]; then
    last="$(head -n 1 "$stamp_file" 2>/dev/null || true)"
    if [[ "$last" =~ ^[0-9]+$ ]]; then
      age=$((now - last))
      if (( age >= 0 && age < DISPATCH_DEDUP_WINDOW_SEC )); then
        echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: recent dispatch already sent for ${mode} ${tz} ${slot_key}; skipping"
        return 0
      fi
    fi
  fi

  run_workflow "$@"
  {
    echo "$now"
    echo "mode=$mode"
    echo "tz=$tz"
    echo "workflow=$WORKFLOW_FILE"
    echo "repo=$GH_REPO"
  } > "$stamp_file"
}

mode="${1:-}"
case "$mode" in
  collect-links)
    tz="${2:-}"
    case "$tz" in
      ET|CT|PT|ALL) ;;
      *) usage ;;
    esac
    run_once_per_slot "$mode" "$tz" \
      -f phase=collect-links \
      -f tz_group="$tz" \
      -f force="$FORCE"
    ;;
  scrape)
    run_once_per_slot "$mode" "ALL" \
      -f phase=scrape \
      -f tz_group=ALL \
      -f force="$FORCE" \
      -f test="$TEST" \
      -f pre_reservation_snapshots=false \
      -f snapshots_only=false
    ;;
  snapshot)
    run_once_per_slot "$mode" "ALL" \
      -f phase=scrape \
      -f tz_group=ALL \
      -f force=true \
      -f test="$TEST" \
      -f pre_reservation_snapshots=true \
      -f snapshots_only=true
    ;;
  calibrate)
    run_once_per_slot "$mode" "ALL" \
      -f phase=calibrate \
      -f tz_group=ALL \
      -f force=false
    ;;
  *)
    usage
    ;;
esac
