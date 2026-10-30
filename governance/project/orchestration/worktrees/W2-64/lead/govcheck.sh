#!/bin/bash
# Lead's gov check on this worktree's code, and core-schema timed alone three times (before/after figures).
L=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log
N=$1
cd /home/usain/gov-os-worktrees/W2-64 || exit 98
cat /proc/loadavg > "$L/govcheck-$N.load"
for i in 1 2 3; do
  /usr/bin/time -f '%e' -a -o "$L/core-schema-time-$N.txt" env PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.check.schema > "$L/core-schema-$N.out" 2>&1
  echo "exit $?" >> "$L/core-schema-time-$N.txt"
done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.cli.main check --json > "$L/govcheck-$N.json" 2> "$L/govcheck-$N.err"
echo $? > "$L/govcheck-$N.exit"
