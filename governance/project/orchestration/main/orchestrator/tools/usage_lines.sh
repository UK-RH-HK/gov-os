#!/usr/bin/env bash
# The usage lines of DEC-1140 (6), for the week to the reset of 11-15, made report-only by DEC-1149 (3) (2026-11-12:
# usage never stops leads or workers; it is tracked and reported in every report and digest). The CTO arms it in the
# background (the Bash tool's own background run). It reads `claude -p "/usage"` every EVERY seconds (600), every NEAR
# seconds (180) from NEAR_PCT (93), appends each reading to log/usage-lines.log, and exits at the first line crossed,
# printing one line:
#   USAGE_LINE 97 <pct> ...   report only, no stop (DEC-1149 (3)): the CTO reports it; no lead or worker is held,
#                             refused or stopped
#   USAGE_LINE 99 <pct> ...   the CTO pushes the owner at any hour (DEC-1089 (3) excepted), who presses the reset;
#                             report only, no stop (DEC-1149 (3))
# A start at or above 99 prints the 99 line at once; at or above 97 (below 99), it waits only for 99 (LINES="99").
# Waits by its own sleep only (no process match). --max bounds it (default 86400 s).
set -u
ORCH=${ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
EVERY=${EVERY:-600} NEAR=${NEAR:-180} NEAR_PCT=${NEAR_PCT:-93} MAX=${MAX:-86400} LINES=${LINES:-"97 99"}
READ=${USAGE_READ:-'timeout 90 /home/usain/.local/bin/claude -p "/usage"'}
LOG=$ORCH/log/usage-lines.log end=$(( $(date +%s) + MAX ))
while :; do
  out=$(bash -c "$READ" 2>&1)
  pct=$(sed -n 's/.*Current week (all models): *\([0-9]\{1,3\}\)% used.*/\1/p' <<< "$out" | head -n 1)
  echo "$(date -u '+%F %T') ${pct:-unread}" >> "$LOG"
  if [ -n "$pct" ]; then
    for line in 99 97; do
      case "$line" in 99) what="push the owner (report only, no stop; DEC-1149 (3))";;
        *) what="report only, no stop (DEC-1149 (3))";; esac
      case " $LINES " in *" $line "*) [ "$pct" -ge "$line" ] && { echo "USAGE_LINE $line $pct $what"; exit 0; };; esac
    done
  fi
  [ "$(date +%s)" -ge "$end" ] && { echo "USAGE_LINES timeout ${MAX}s, last ${pct:-unread}"; exit 124; }
  if [ -n "$pct" ] && [ "$pct" -ge "$NEAR_PCT" ]; then sleep "$NEAR"; else sleep "$EVERY"; fi
done
