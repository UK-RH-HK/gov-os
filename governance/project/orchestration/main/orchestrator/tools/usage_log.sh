#!/usr/bin/env bash
# The owner's plan usage, recorded only (owner, 2026-11-07, DEC-1089 (3)): no ping, no alarm, no threshold; the owner
# manages the plan's limits. Replaces usage_watch.sh (DEC-942 item 6's pings ended). Every EVERY seconds (default
# 1800) reads `claude -p "/usage"` and appends one line to log/usage.txt: each "Current ..." figure as printed, and
# the last 24 h's request and session counts. The digests show the latest line and the change since the last digest.
#   bash usage_log.sh            run until stopped
#   bash usage_log.sh --once     one reading, then exit
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=${USAGE_LOG:-$ORCH/log/usage.txt}
EVERY=${EVERY:-1800}
read_once() {
  local out cur day
  out=$(/home/usain/.local/bin/claude -p "/usage" 2>&1)
  cur=$(printf '%s\n' "$out" | sed -n 's/^Current \(.*\): \([0-9]*\)% used · resets \(.*\)$/\1=\2% (resets \3)/p' | paste -sd ';' -)
  day=$(printf '%s\n' "$out" | sed -n 's/^Last 24h · \(.*\)$/\1/p' | head -1)
  echo "$(date '+%F %T') ${cur:-unread}; last 24h: ${day:-unread}" >> "$LOG"
}
read_once
[ "${1:-}" = --once ] && exit 0
while sleep "$EVERY"; do read_once; done
