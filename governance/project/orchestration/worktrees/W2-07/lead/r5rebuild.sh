#!/usr/bin/env bash
# Lead run 5: the full rebuild from this worktree's src (DEC-719, DEC-732), after the load and disk gates.
# Exit code in log/r5-rebuild.exit.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
export TMPDIR=/tmp/gov-os-lead-W2-07
mkdir -p "$TMPDIR"
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/r5-rebuild.gate" 2>&1 \
  || { echo 91 > "$L/r5-rebuild.exit"; exit 91; }
PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m gov.cli.main rebuild --json > "$L/r5-rebuild.json" 2> "$L/r5-rebuild.err"
echo $? > "$L/r5-rebuild.exit"
date -Is >> "$L/r5-rebuild.gate"
