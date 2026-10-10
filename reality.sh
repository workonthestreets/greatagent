#!/usr/bin/env bash
# One command for the Reality Test: run every case (resumable), then build the HTML overview.
#   ./reality.sh "/path/to/HackatonChallendges/Delivery & Logistics"
set -euo pipefail
CASES="${1:?usage: ./reality.sh <cases folder>}"
OUT="${2:-ANSWERS}"
cd "$(dirname "$0")"
# Preflight: one tiny API call, so a missing key or empty credit balance shows up now, not mid-run.
python3 - <<'EOF' || { echo "API preflight failed: fix ANTHROPIC_API_KEY / account credit, then re-run this script."; exit 1; }
import os
from deskagent.llm import load_dotenv, model_list
load_dotenv()
import anthropic
client, last = anthropic.Anthropic(), None
for m in model_list(os.environ.get("DESK_MODEL")):
    try:
        client.messages.create(model=m, max_tokens=5, messages=[{"role": "user", "content": "ping"}])
        print(f"API preflight ok ({m})")
        break
    except (anthropic.NotFoundError, anthropic.PermissionDeniedError) as exc:
        last = exc
else:
    raise SystemExit(f"no model available: {last}")
EOF
python3 run.py "$CASES" --out "$OUT" --workers "${DESK_WORKERS:-12}" --resume
python3 run.py "$CASES" --out "$OUT" --workers 4 --resume   # second pass retries anything that failed
python3 viewer.py "$OUT"
echo "Done. Results: $OUT/SUMMARY.md and $OUT/index.html"
