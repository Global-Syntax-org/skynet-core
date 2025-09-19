#!/bin/bash

LOG_FILE="/var/log/skynet-hid-watchdog.log"
ORCHESTRATOR="/stux/repos/skynet-core/skynet-hid-watchdog.sh"

function log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

function check_js0() {
  if [ -e /dev/input/js0 ]; then
    log "✅ js0 detected — no action needed"
    exit 0
  else
    log "⚠️ js0 missing — attempting rebind"
    sudo "$ORCHESTRATOR"
    sleep 2
    if [ -e /dev/input/js0 ]; then
      log "✅ Rebind successful — js0 now present"
    else
      log "❌ Rebind failed — js0 still missing"
    fi
  fi
}

log "🔍 Watchdog triggered"
check_js0

