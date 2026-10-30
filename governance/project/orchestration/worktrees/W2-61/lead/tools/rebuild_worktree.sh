#!/bin/bash
# The worktree's full store rebuild with this worktree's code (DEC-719, DEC-732), under the rebuild lock (DEC-939 2).
# Gates first: no close or nightly running, 1-minute load under 20, disk gate open. Outputs in the lead's log folder.
set -u
log=/home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/log
orch=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd /home/usain/gov-os-worktrees/W2-61 || exit 90
while true; do
  until [ ! -e "$orch/CLOSE-RUNNING" ] && [ ! -e "$orch/NIGHTLY-RUNNING" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  if bash "$orch/tools/disk_gate.sh" > "$log/wt-rebuild2.gate" 2>&1; then
    [ ! -e "$orch/CLOSE-RUNNING" ] && [ ! -e "$orch/NIGHTLY-RUNNING" ] && break
  fi
  sleep 60
done
cat /proc/loadavg >> "$log/wt-rebuild2.gate"
date -u +%FT%TZ > "$log/wt-rebuild2.time"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$log/wt-rebuild2.json" 2> "$log/wt-rebuild2.err"
code=$?
date -u +%FT%TZ >> "$log/wt-rebuild2.time"
echo "$code" > "$log/wt-rebuild2.exit"
