#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <timeout_seconds> <command...>"
  exit 1
fi

TIMEOUT="$1"
shift

"$@" &
PID=$!
START=$SECONDS

echo "[TIMEOUT] Started PID=$PID timeout=${TIMEOUT}s"

while kill -0 "$PID" 2>/dev/null; do
  ELAPSED=$((SECONDS - START))
  if [[ "$ELAPSED" -ge "$TIMEOUT" ]]; then
    echo "[TIMEOUT] Sending TERM to PID=$PID"
    kill -TERM "$PID" 2>/dev/null || true
    sleep 5
    echo "[TIMEOUT] Sending KILL to PID=$PID"
    kill -KILL "$PID" 2>/dev/null || true
    exit 124
  fi
  sleep 1
done

wait "$PID"
