#!/usr/bin/env bash
# One command for the Reality Test: run every case (resumable), then build the HTML overview.
#   ./reality.sh "/path/to/HackatonChallendges/Delivery & Logistics"
set -euo pipefail
CASES="${1:?usage: ./reality.sh <cases folder>}"
OUT="${2:-ANSWERS}"
cd "$(dirname "$0")"
python3 run.py "$CASES" --out "$OUT" --workers "${DESK_WORKERS:-12}" --resume
python3 run.py "$CASES" --out "$OUT" --workers 4 --resume   # second pass retries anything that failed
python3 viewer.py "$OUT"
echo "Done. Results: $OUT/SUMMARY.md and $OUT/index.html"
