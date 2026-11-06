#!/usr/bin/env bash
# Waits, bounded, until the dispatcher reports a quiet machine twice in a row (no heavy slot held, no job by phase),
# for the score-once window's start condition. Exit 0 when quiet; 124 at the bound (default 3 h). Reads only.
#   quiet_wait.sh [max seconds]
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/status.txt
MAX=${1:-10800}; t=0; ok=0
while [ $t -lt "$MAX" ]; do
  if grep -q "heavy slots held: none" "$S" && grep -q "^Jobs by phase: none" "$S"; then ok=$((ok + 1)); else ok=0; fi
  [ $ok -ge 2 ] && { echo "quiet at $(date '+%F %T')"; exit 0; }
  sleep 60; t=$((t + 60))
done
echo "not quiet within $MAX s"; exit 124
