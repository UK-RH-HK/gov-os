#!/bin/bash
# The lead's full store rebuild for this worktree (DEC-719, DEC-732, DEC-939 item 2, DEC-943).
# Usage: rebuild.sh <tag>   writes log/rebuild-<tag>.out and log/rebuild-<tag>.rc
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
while [ -e "$ORCH/CLOSE-RUNNING" ] || [ -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" || { echo 97 > "$LOG/rebuild-$TAG.rc"; exit 97; }
mkdir -p /tmp/gov-os-lead-W2-84
date > "$LOG/rebuild-$TAG.out"
TMPDIR=/tmp/gov-os-lead-W2-84 PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json >> "$LOG/rebuild-$TAG.out" 2>&1
RC=$?
date >> "$LOG/rebuild-$TAG.out"
echo $RC > "$LOG/rebuild-$TAG.rc"
