#!/usr/bin/env bash
# DEC-973: wake the CTO right after the nightly ends: when a night run's run.txt newer than this watcher's start
# holds its verdict (or its final "done"/"NOT STARTED" line), print the folder and exit. Checked every 5 minutes.
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
stamp=$(mktemp); trap 'rm -f "$stamp"' EXIT
while true; do
  for r in $(find "$O/log/nightly" -maxdepth 2 -name run.txt -newer "$stamp" 2>/dev/null); do
    head -1 "$r" | grep -q "nightly night" || continue
    if grep -qE "^verdict:|NOT STARTED| done$" "$r"; then echo "$(date '+%F %T') the nightly ended: $(dirname "$r")"; grep -E "^verdict:|NOT STARTED" "$r" | tail -1; exit 0; fi
  done
  sleep 300
done
