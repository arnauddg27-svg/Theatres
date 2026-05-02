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

set -euo pipefail

WORKFLOW_FILE="${WORKFLOW_FILE:-box-office-pipeline.yml}"
GH_REPO="${GH_REPO:-}"
FORCE="${FORCE:-false}"
TEST="${TEST:-}"

usage() {
  echo "Usage: $0 collect-links ET|CT|PT|ALL | scrape | snapshot | calibrate" >&2
  exit 2
}

run_workflow() {
  local -a cmd=(gh workflow run "$WORKFLOW_FILE")
  if [[ -n "$GH_REPO" ]]; then
    cmd+=(--repo "$GH_REPO")
  fi
  cmd+=("$@")
  echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') dispatch: ${cmd[*]}"
  "${cmd[@]}"
}

mode="${1:-}"
case "$mode" in
  collect-links)
    tz="${2:-}"
    case "$tz" in
      ET|CT|PT|ALL) ;;
      *) usage ;;
    esac
    run_workflow \
      -f phase=collect-links \
      -f tz_group="$tz" \
      -f force="$FORCE"
    ;;
  scrape)
    run_workflow \
      -f phase=scrape \
      -f tz_group=ALL \
      -f force="$FORCE" \
      -f test="$TEST" \
      -f pre_reservation_snapshots=false \
      -f snapshots_only=false
    ;;
  snapshot)
    run_workflow \
      -f phase=scrape \
      -f tz_group=ALL \
      -f force=true \
      -f test="$TEST" \
      -f pre_reservation_snapshots=true \
      -f snapshots_only=true
    ;;
  calibrate)
    run_workflow \
      -f phase=calibrate \
      -f tz_group=ALL \
      -f force=false
    ;;
  *)
    usage
    ;;
esac
