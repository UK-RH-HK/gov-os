#!/bin/bash
# Lead's full store rebuild in this worktree (DEC-719, DEC-732, DEC-939 item 2): gates first, the exit code to a file.
L=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log
N=$1
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/disk-gate-rebuild.txt 2>&1 || { echo 99 > "$L/rebuild-$N.exit"; exit 99; }
cd /home/usain/gov-os-worktrees/W2-64 || exit 98
PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$L/rebuild-$N.json" 2> "$L/rebuild-$N.err"
echo $? > "$L/rebuild-$N.exit"
