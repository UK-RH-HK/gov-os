#!/usr/bin/env bash
# Pair 3 of KPI 4's measure, at a load of 40 or more: wait (at most 60 min) until the 1- and 5-minute loads are both
# at or above 40, then run before-3 and after-3 back to back. Writes /tmp/gov-os-lead-W2-108/prof/pair3.state
STATE=/tmp/gov-os-lead-W2-108/prof/pair3.state
echo waiting > "$STATE"
for i in $(seq 1 240); do
  if python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[1]) >= 40 else 1)"; then
    echo "started $(date +%s) $(cat /proc/loadavg)" > "$STATE"
    bash /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/measure.sh before-3 /tmp/gov-os-lead-W2-108/measure/src
    bash /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/measure.sh after-3 /home/usain/gov-os-worktrees/W2-108/src
    echo done >> "$STATE"
    exit 0
  fi
  sleep 15
done
echo "timed out $(date +%s) $(cat /proc/loadavg)" > "$STATE"
exit 1
