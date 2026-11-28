#!/usr/bin/env bash
# Forecast, log and commit WITHOUT the AMC scrape (pipeline phase=forecast).
#
# Until 2026-11-28 the forecast ran only as the last job of an AMC scrape run.
# With AMC unreadable those runs spend one to five hours failing their legs
# before finalize starts, so the forecast's clock followed the one source that
# is dead. The model now rests on reported grosses and the other chains'
# counted seats (chain_forecast.py), which change at known times: the seat
# counts of a day are complete at 10:00 UTC the next morning, and The Numbers
# posts the day's gross through the following afternoon. The scheduler runs
# this at those times.
#
# Same steps and order as finalize's forecast half, minus everything that
# belongs to the AMC merge. Derived files only (stage_finalize_outputs.py
# --forecast). If main moves under those files while this runs, the forecast
# is made again on the new main; it never pushes while a scrape run's finalize
# is writing (scripts/finalize_in_flight.py).
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
T=box-office-tracker
SLOT="${SCHEDULE_SLOT:-manual}"

forecast() {
  (
    cd "$T" || exit 1
    python3 holdover.py --refresh || echo "::warning::holdover market refresh crashed — registry unchanged"
    python3 scripts/fetch_daily_actuals.py || echo "::warning::daily actuals fetch failed — forecasting on the grosses on file"
    python3 scripts/fill_movie_metadata.py --tracked --write || echo "::warning::movie metadata fill failed — predictions run on defaults for unfilled films"
    python3 scripts/refresh_theatre_counts.py || echo "::warning::theatre-count refresh failed — sync uses the last fetched chart"
    python3 scripts/sync_opening_theatre_counts.py --write || echo "::warning::opening theatre-count sync failed — metadata keeps the pre-release count"
    if [ "${HAS_PROXY:-false}" = "true" ]; then export SNAPSHOT_TOP_THEATRE_CAP=1000; else export SNAPSHOT_TOP_THEATRE_CAP=120; fi
    python3 predict.py || exit 1          # the forecast itself: a crash fails the job, the scheduler retries the slot
    python3 holdover_forecast.py || echo "::warning::holdover forecast crashed — no holdover rows this run"
    python3 holdover_forecast.py --grade || echo "::warning::holdover grading crashed — data/holdover-grades.csv not refreshed"
    python3 scripts/log_polymarket_odds.py || echo "::warning::Polymarket odds not logged this run"
    python3 scripts/fetch_trade_forecasts.py || echo "::warning::trade forecast fetch crashed — the combined forecast uses what is on file"
    python3 scripts/ensemble_forecast.py || echo "::warning::combined forecast crashed — data/ensemble-log.csv not refreshed"
    python3 scripts/paper_trade.py || echo "::warning::paper trading crashed — no bets placed or settled this run"
  )
}

# 0 pushed or nothing to push; 2 main moved under the forecast's own files; 1 gave up.
commit_and_push() {
  git config user.name "github-actions[bot]"
  git config user.email "github-actions[bot]@users.noreply.github.com"
  python3 "$T/scripts/stage_finalize_outputs.py" --forecast || return 1
  if git diff --staged --quiet; then echo "Forecast changed no derived file."; return 0; fi
  git commit -q -m "data: box office forecast ($SLOT)"
  for i in 1 2 3 4 5; do
    if ! python3 "$T/scripts/finalize_in_flight.py"; then
      echo "A scrape run is finalizing and will forecast on the same data: this forecast is not pushed."
      return 0
    fi
    if ! git pull -q --rebase --autostash origin main; then
      git rebase --abort 2>/dev/null || true
      return 2
    fi
    if git push -q origin HEAD:main; then echo "Forecast pushed."; return 0; fi
    echo "Push attempt $i lost a race, retrying..."
    sleep $((i * 5))
  done
  return 1
}

python3 "$T/scripts/finalize_in_flight.py" --wait 12 || echo "Finalize still running after 12 min; forecasting anyway (checked again before the push)."
for attempt in 1 2 3; do
  git fetch -q origin main
  git reset -q --hard origin/main
  forecast || { echo "::error::predict.py failed"; exit 1; }
  commit_and_push
  rc=$?
  if [ "$rc" = "0" ]; then exit 0; fi
  if [ "$rc" = "2" ]; then echo "main moved under the forecast's own files (attempt $attempt); forecasting again on the new main."; continue; fi
  echo "::error::forecast not pushed"; exit 1
done
echo "::error::main kept moving under the forecast; not pushed"
exit 1
