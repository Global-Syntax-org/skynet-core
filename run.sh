#!/usr/bin/env bash
set -euo pipefail

# run.sh - safe one-shot launcher for Skynet Core web app
# - kills existing listener on port 5000 (if any)
# - starts the app with system python3 (prefer .venv if present)
# - writes logs to /tmp/skynet_web.log and pid to /tmp/skynet_web.pid

LOG=/tmp/skynet_web.log
PIDFILE=/tmp/skynet_web.pid

echo "[run.sh] checking for listener on port 5000..."
oldpid=$(lsof -t -iTCP:5000 -sTCP:LISTEN 2>/dev/null || true)
if [ -n "$oldpid" ]; then
  echo "[run.sh] found listener PID=$oldpid — sending TERM"
  kill "$oldpid" 2>/dev/null || true
  for i in {1..5}; do
    if ! ps -p "$oldpid" > /dev/null 2>&1; then
      echo "[run.sh] process $oldpid exited"
      break
    fi
    sleep 1
  done
  if ps -p "$oldpid" > /dev/null 2>&1; then
    echo "[run.sh] process $oldpid still alive — sending SIGKILL"
    kill -9 "$oldpid" 2>/dev/null || true
    sleep 1
  fi
  if ps -p "$oldpid" > /dev/null 2>&1; then
    echo "[run.sh] failed to kill process $oldpid" >&2
    ps -p "$oldpid" -o pid,cmd
    exit 1
  fi
else
  echo "[run.sh] no existing listener on port 5000"
fi

# Decide which python to use: prefer .venv/python if available
PYTHON=python3
if [ -x ".venv/bin/python" ]; then
  PYTHON=.venv/bin/python
  echo "[run.sh] using project venv python: $PYTHON"
else
  echo "[run.sh] using system python3"
fi

# Start server
echo "[run.sh] starting server with $PYTHON web/app.py — logs -> $LOG"
nohup "$PYTHON" web/app.py > "$LOG" 2>&1 &
newpid=$!
echo "$newpid" > "$PIDFILE"
# give it a moment to start
sleep 2
if ps -p "$newpid" > /dev/null 2>&1; then
  echo "[run.sh] server started (PID $newpid)"
  echo "[run.sh] tail of logs:" 
  tail -n 40 "$LOG" || true
  exit 0
else
  echo "[run.sh] server failed to start or exited immediately" >&2
  echo "[run.sh] last 200 lines of log:" 
  tail -n 200 "$LOG" || true
  exit 1
fi
