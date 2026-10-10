#!/usr/bin/env bash
# Render the mocked preview views with headless Chrome. Usage: preview/shoot.sh [out_dir]
set -euo pipefail
WEB="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/private/tmp/claude-501/-Users-matveidanisheuski-greatagent/915eac35-f09f-486c-842b-d8e84813985b/scratchpad/ui-shots}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT=3100
mkdir -p "$OUT"

cd "$WEB"
nohup npx vite --config preview/vite.config.ts --port "$PORT" --strictPort > "$OUT/preview-server.log" 2>&1 &
PID=$!
disown "$PID" 2>/dev/null || true
echo "$PID" > "$OUT/preview-server.pid"
trap 'kill "$PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  curl -sf "http://127.0.0.1:$PORT/" > /dev/null && break
  sleep 0.5
done

shot() { # view width height url
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 \
    --window-size="$2,$3" --screenshot="$OUT/$1-$2.png" "$4" > /dev/null 2>&1
  echo "$OUT/$1-$2.png"
}

for v in login ops ops-hold party; do shot "$v" 1440 1800 "http://127.0.0.1:$PORT/?view=$v"; done
# Phone width: headless Chrome clamps windows to ~500px, so render inside an exact 390px iframe (preview/frame.html).
for v in login party; do shot "$v" 390 3200 "http://127.0.0.1:$PORT/frame.html?view=$v&w=390&h=3200"; done
