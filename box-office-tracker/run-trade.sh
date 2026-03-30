#!/bin/bash
# Run on EU VPS via cron. Pulls latest data from GitHub, then trades.
#
# Cron schedule (add to VPS crontab):
#   # Thu-Sun, 30 min after each GH Actions run to allow data commit
#   30 0 * * 4,5,6,0  /path/to/box-office-tracker/run-trade.sh  # after ET run
#   30 2 * * 4,5,6,0  /path/to/box-office-tracker/run-trade.sh  # after CT run
#   30 4 * * 4,5,6,0  /path/to/box-office-tracker/run-trade.sh  # after PT run
#
# Setup:
#   1. Clone repo: git clone https://github.com/arnauddg27-svg/Theatres.git
#   2. pip install requests python-dotenv httpx py-clob-client
#   3. Create .env with POLYMARKET_PRIVATE_KEY and POLYMARKET_FUNDER_ADDRESS
#   4. Set DRY_RUN=false in .env when ready to go live

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "$(date) — Pulling latest data..."
git pull --quiet

echo "$(date) — Running trade.py..."
python3 trade.py

echo "$(date) — Done."
