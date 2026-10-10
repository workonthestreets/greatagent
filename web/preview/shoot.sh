#!/usr/bin/env bash
# Render the mocked preview views with headless Chrome. Usage: preview/shoot.sh [out_dir]
set -euo pipefail
WEB="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/private/tmp/claude-501/-Users-matveidanisheuski-greatagent/915eac35-f09f-486c-842b-d8e84813985b/scratchpad/ui-shots-2}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT="${PORT:-3100}"  # override when another preview server holds 3100
mkdir -p "$OUT"

cd "$WEB"
nohup npx vite --config preview/vite.config.ts --port "$PORT" --strictPort > "$OUT/preview-server.log" 2>&1 &
PID=$!
disown "$PID" 2>/dev/null || true
echo "$PID" > "$OUT/preview-server.pid"
trap 'kill "$PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  kill -0 "$PID" 2>/dev/null || { echo "preview server failed, see $OUT/preview-server.log" >&2; exit 1; }
  curl -sf "http://127.0.0.1:$PORT/" > /dev/null && break
  sleep 0.5
done

shot() { # view width height url
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 \
    --window-size="$2,$3" --screenshot="$OUT/$1-$2.png" "$4" > /dev/null 2>&1
  echo "$OUT/$1-$2.png"
}

for v in login ops ops-hold ops-drag ops-medal party driver depot merchant; do shot "$v" 1440 1800 "http://127.0.0.1:$PORT/?view=$v"; done
shot rewards 1440 2600 "http://127.0.0.1:$PORT/?view=rewards"
# Phone width: headless Chrome clamps windows to ~500px, so render inside an exact 390px iframe (preview/frame.html).
for v in login party driver ops; do shot "$v" 390 3200 "http://127.0.0.1:$PORT/frame.html?view=$v&w=390&h=3200"; done
