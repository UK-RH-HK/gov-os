#!/bin/bash
# Wait for the gates of a heavy run, then write a marker. Usage: wait_gates.sh <marker-name> [lock]
# Gates: no close quiet window, no nightly, 1-minute load below 20, the disk gate open, and (with "lock") the
# verification lock free at that moment. Each check is repeated until all hold at once.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log
rm -f "$LOG/gate-$1.ok"
while true; do
  if [ ! -e $ORCH/CLOSE-RUNNING ] && [ ! -e $ORCH/NIGHTLY-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg \
     && bash $ORCH/tools/disk_gate.sh > /dev/null 2>&1; then
    if [ "$2" != "lock" ] || flock -n /tmp/gov-os-verify.lock true; then
      break
    fi
  fi
  sleep 60
done
{ date; uptime; bash $ORCH/tools/disk_gate.sh; du -s --inodes /tmp/gov-os-lead-W2-60a; du -sh /tmp/gov-os-lead-W2-60a; } > "$LOG/gate-$1.ok" 2>&1
