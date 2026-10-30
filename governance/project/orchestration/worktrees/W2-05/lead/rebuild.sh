#!/bin/bash
# Gated full rebuild of this worktree's store (DEC-719, DEC-732, DEC-939 item 2), with an exit-code file.
# $1 = log name stem
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
STEM="$1"
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
rm -f "$LOG/$STEM.exit"
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || { echo 97 > "$LOG/$STEM.exit"; exit 97; }
date > "$LOG/$STEM.start"
cat /proc/loadavg >> "$LOG/$STEM.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/$STEM.json" 2> "$LOG/$STEM.err"
echo $? > "$LOG/$STEM.exit"
date >> "$LOG/$STEM.start"
