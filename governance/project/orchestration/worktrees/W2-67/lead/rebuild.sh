#!/bin/bash
# A full rebuild of this worktree (DEC-719, DEC-732), after the gates: no close in its quiet window, load under 20,
# the disk gate open. Usage: rebuild.sh <n>
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
N=$1
cd "$W" || exit 99
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/rebuild-$N.gate" 2>&1 || { echo gate-shut > "$LOG/rebuild-$N.exit"; exit 1; }
date -Is > "$LOG/rebuild-$N.start"
PYTHONPATH=$W/src python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-$N.json" 2> "$LOG/rebuild-$N.err"
echo $? > "$LOG/rebuild-$N.exit"
