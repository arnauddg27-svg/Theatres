#!/usr/bin/env bash
# Commit one lane's snapshot CSV onto the latest main: save ours, reset to
# origin/main, re-apply our rows by key (union), rotate settled weekends into
# the lane archive, commit, push; retry on a lost push race.
#
#   commit_lane.sh <lane> <csv path from repo root> <commit message> [extra file]
#
# Shared by the lane commit steps AND by long-running loop jobs, which call it
# after every pass: on 2026-10-02 the Alamo 02:40Z walk-in loop was killed by a
# runner shutdown 2 h in and lost every pass's rows because it committed only
# at the end. Idempotent: re-running with nothing new is a no-op.
set -uo pipefail
lane=$1; csv=$2; msg=$3; extra=${4:-}
KEY=weekend_of,snapshot_bucket,show_date,theatre_name,movie_title,showtime_id,auditorium_type,chain,row_kind
archive=box-office-tracker/data/$lane-archive
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
if [ -n "$extra" ] && [ -f "$extra" ]; then cp "$extra" "/tmp/$lane-extra"; fi
if [ ! -f "$csv" ]; then echo "No $lane data."; exit 0; fi
cp "$csv" "/tmp/$lane-ours.csv"
for i in 1 2 3 4 5; do
  git fetch -q origin main
  git reset -q --hard origin/main
  if [ -f "$csv" ]; then
    added=$(python3 box-office-tracker/scripts/union_csv_rows.py "/tmp/$lane-ours.csv" "$csv" --key "$KEY" --archived-dir "$archive")
  else
    cp "/tmp/$lane-ours.csv" "$csv"; added=all
  fi
  echo "$lane rows added on top of main: $added"
  python3 box-office-tracker/scripts/rotate_lane_csv.py "$csv" --archive-dir "$archive"
  if [ -d "$archive" ]; then git add "$archive"; fi
  if [ -n "$extra" ] && [ -f "/tmp/$lane-extra" ]; then cp "/tmp/$lane-extra" "$extra"; git add "$extra"; fi
  git add "$csv"
  if git diff --staged --quiet; then echo "Nothing new relative to main."; exit 0; fi
  git commit -q -m "$msg"
  if git push -q origin HEAD:main; then exit 0; fi
  echo "Push attempt $i lost a race, re-applying on the new main..."
  sleep $((i * 7))
done
exit 1
