#!/usr/bin/env bash
# DEC-958: every 10 minutes, harvest the five-rule hook's refusals from all session transcripts; exit (waking the
# orchestrator) when a new one is found, so it is judged and recorded at once. Re-arm after each.
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
while true; do
  out=$(python3 "$O/tools/guard_refusals.py" 2>&1)
  if echo "$out" | grep -q "^NEW "; then echo "$(date '+%F %T')"; echo "$out"; exit 0; fi
  sleep 600
done
