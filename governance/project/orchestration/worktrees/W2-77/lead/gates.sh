#!/usr/bin/env bash
# The lead's gates before a heavy run: no close or nightly running, the 1-minute load below 20, the disk gate open.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
while true; do
  until [ ! -e "$ORCH/CLOSE-RUNNING" ] && [ ! -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  if [ ! -e "$ORCH/CLOSE-RUNNING" ] && [ ! -e "$ORCH/NIGHTLY-RUNNING" ]; then break; fi
done
bash "$ORCH/tools/disk_gate.sh" || exit 9
echo "gates passed $(date -u +%H:%M:%S) load $(cut -d' ' -f1 /proc/loadavg)"
du -sh /tmp/gov-os-lead-W2-77 /home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch 2>/dev/null
du -s --inodes /tmp/gov-os-lead-W2-77 /home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch 2>/dev/null
