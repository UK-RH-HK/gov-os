#!/bin/bash
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log
until [ ! -e $ORCH/CLOSE-RUNNING ] && [ ! -e $ORCH/NIGHTLY-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg \
      && bash $ORCH/tools/disk_gate.sh > /dev/null 2>&1; do
  sleep 30
done
{ date; uptime; bash $ORCH/tools/disk_gate.sh; du -s --inodes /tmp/gov-os-lead-W2-60a; du -sh /tmp/gov-os-lead-W2-60a; } > $LOG/hold$1.acquired 2>&1
until { [ -e $LOG/verify2-parallel.exit ] && [ -e $LOG/verify2-serial.exit ]; } || [ -e $LOG/hold.release ]; do
  sleep 20
done
date >> $LOG/hold$1.acquired
