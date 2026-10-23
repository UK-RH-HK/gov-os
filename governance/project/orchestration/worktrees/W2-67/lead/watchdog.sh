#!/bin/bash
# DEC-898 budget watchdog for verify-r2: stop the run if the lead's temp folder nears 1,000,000 files and folders or 20 GB.
LOG=/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/log
until [ -s "$LOG/verify-r2.exit" ]; do
  n=$(du -s --inodes /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1); kb=$(du -s -k /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1)
  if [ "${n:-0}" -gt 930000 ] || [ "${kb:-0}" -gt 19000000 ]; then
    echo "$(date +%T) WATCHDOG inodes=$n kb=$kb: stopping verify-r2" >> "$LOG/watchdog.txt"
    pkill -TERM -f "verify.sh r2"; pkill -TERM -f "junitxml=$LOG/verify-r2"
    echo stopped > "$LOG/watchdog.stopped"; exit 1
  fi
  sleep 10
done
echo "$(date +%T) verify-r2 ended under the budget" >> "$LOG/watchdog.txt"
