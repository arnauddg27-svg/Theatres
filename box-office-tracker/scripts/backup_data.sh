#!/usr/bin/env bash
# Verified backup of the irreplaceable box-office data.
#
# WHY: seat maps and pre-reservation states are EPHEMERAL observations — a
# moment's reservation count can never be re-observed. Losing a row is not a
# rebuild-from-source situation, it is permanent. This session alone saw rows
# destroyed three ways (a rebase strategy that discarded commits, a cleaner
# that aborted a merge, an archive path nothing staged), so a second copy that
# does not depend on the repo being healthy is worth the 15MB.
#
# WHAT: canonical CSVs + rotated gzip archives + calibration and its freezes +
# metadata. Excludes data/run-logs (~86MB of diagnostics, low value, in git).
#
# USAGE:  bash scripts/backup_data.sh [dest-dir]
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../data" && pwd)"
REPO="$(cd "$SRC/../.." && pwd)"
DEST="${1:-$HOME/Documents/box-office-backups}"
mkdir -p "$DEST"

STAMP="$(cd "$REPO" && git log -1 --format=%cd --date=format:%Y%m%d-%H%M%S)"
SHA="$(cd "$REPO" && git rev-parse --short HEAD)"
OUT="$DEST/box-office-data-$STAMP-$SHA.tar.gz"

PATHS=(
  seat-counts.csv pre-reservation-snapshots.csv
  fandango-pre-reservation-snapshots.csv
  seat-archive pre-reservation-archive
  calibration.json calibration-freezes
  movie-metadata.csv reviews.csv social-signals.csv polymarket-markets.csv
  daily-actual-overrides.csv historical-comps.csv theatre-counts.json
  theatres-all.json theatres-expansion.json showtime-links.json
)

cd "$SRC"
tar --exclude='__pycache__' --exclude='.*cache*.json' -czf "$OUT" "${PATHS[@]}"

# A backup you have not restored is not a backup: extract and byte-compare.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
tar -xzf "$OUT" -C "$TMP"
python3 - "$SRC" "$TMP" "$OUT" <<'PY'
import csv, gzip, hashlib, sys
from pathlib import Path
src, restored, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    op = gzip.open if p.suffix == ".gz" else open
    with op(p, "rt", newline="", errors="replace") as f:
        return sum(1 for _ in csv.reader(f)) - 1
lines, total, bad = [], 0, 0
for b in sorted(restored.rglob("*")):
    if not b.is_file():
        continue
    rel = b.relative_to(restored)
    original = src / rel
    same = original.exists() and sha(original) == sha(b)
    bad += 0 if same else 1
    n = rows(b) if b.suffix in {".csv", ".gz"} else ""
    total += n if isinstance(n, int) else 0
    lines.append(f"{'OK ' if same else 'BAD'}  {str(n):>8}  {rel}")
manifest = out.with_suffix(".manifest.txt")
manifest.write_text(
    f"box-office data backup\narchive: {out.name}\nrows: {total}\n"
    f"files: {len(lines)}  mismatched: {bad}\n\nstatus  rows      path\n"
    + "\n".join(lines) + "\n")
print(f"  files: {len(lines)}   rows: {total:,}   mismatched: {bad}")
print(f"  manifest: {manifest}")
if bad:
    raise SystemExit("BACKUP VERIFY FAILED — do not trust this archive")
PY
echo "✅ verified backup: $OUT"
