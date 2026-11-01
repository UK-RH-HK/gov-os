#!/bin/bash
# The lead's full store rebuild for this worktree (DEC-719, DEC-732, DEC-939 item 2), run 1c: no close/nightly hold
# (DEC-953, DEC-961); the load gate of DEC-847/DEC-961 and the disk gate of DEC-898.
# Usage: rebuild2.sh <tag>   writes log/rebuild-<tag>.out and log/rebuild-<tag>.rc
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" > "$LOG/rebuild-$TAG.out" 2>&1 || { echo 97 > "$LOG/rebuild-$TAG.rc"; exit 97; }
mkdir -p /tmp/gov-os-lead-W2-84
date >> "$LOG/rebuild-$TAG.out"
TMPDIR=/tmp/gov-os-lead-W2-84 PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json >> "$LOG/rebuild-$TAG.out" 2>&1
RC=$?
date >> "$LOG/rebuild-$TAG.out"
echo $RC > "$LOG/rebuild-$TAG.rc"
