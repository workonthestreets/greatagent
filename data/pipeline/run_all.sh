#!/usr/bin/env bash
# Regenerates every normalized artefact under data/delivery/. Usage: bash data/pipeline/run_all.sh [/path/to/HackatonPublicCases]
# Layout written: data/delivery/{inputs,agent,human,catalogue,database}/ (see data/README.md).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$(dirname "$HERE")"
ROOT="$(dirname "$DATA")"
D="$DATA/delivery"
SRC="${1:-$HOME/HackatonPublicCases}"
PY="python3 -I"   # isolated mode: the case files are untrusted downloaded data
mkdir -p "$D/inputs" "$D/agent" "$D/human" "$D/catalogue" "$D/database"

# 1. Public Delivery & Logistics cases: parse, then normalize with the gold labels
$PY "$HERE/parse_cases.py" "$SRC/Delivery & Logistics" "$D/inputs/raw_cases.jsonl" \
    --attachments-text "$D/inputs/attachments_text" --case-prefix DEL
$PY "$HERE/normalize_delivery.py" "$D/inputs/raw_cases.jsonl" "$HERE/gold_labels_delivery.csv" "$D"

# 2. Other tracks: structural parse only, into the git-ignored dump-research/ folder (this repo ships the Delivery agent only)
DUMP="$ROOT/dump-research/data"
mkdir -p "$DUMP/banking" "$DUMP/insurance" "$DUMP/property"
$PY "$HERE/parse_cases.py" "$SRC/Banking & Financial Services" "$DUMP/banking/raw_cases.jsonl" --case-prefix BNK
$PY "$HERE/parse_cases.py" "$SRC/Insurance Claims Processing" "$DUMP/insurance/raw_cases.jsonl" --case-prefix INS
$PY "$HERE/parse_cases.py" "$SRC/Property Management" "$DUMP/property/raw_cases.jsonl" --case-prefix PRM

# 3. Stress cases from this repo (same format, no labels), when present
if [ -d "$ROOT/stress_cases" ]; then
  $PY "$HERE/parse_cases.py" "$ROOT/stress_cases" "$D/inputs/stress_raw.jsonl" --attachments-text "$D/inputs/attachments_text" --case-prefix STR
fi

# 4. Database on Andrey's system model, its DDL and the reconciliation document
STRESS_ARG=""; [ -f "$D/inputs/stress_raw.jsonl" ] && STRESS_ARG="--stress $D/inputs/stress_raw.jsonl"
$PY "$HERE/build_db.py" --cases "$D/agent/cases.jsonl" --facts "$HERE/facts_delivery.py" --out "$D/database/delivery.sqlite" \
    --schema-out "$D/database/schema.sql" --recon-out "$D/human/RECONCILIATION.md" $STRESS_ARG

echo "done: $(wc -l < "$D/agent/cases.jsonl") delivery cases, $(wc -l < "$D/agent/events.jsonl") events, database at $D/database/delivery.sqlite"
