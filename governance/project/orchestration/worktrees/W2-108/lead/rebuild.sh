#!/usr/bin/env bash
# The lead's full rebuild of this worktree's store (DEC-719, DEC-732), under the machine-wide rebuild lock (DEC-939 item 2).
# usage: rebuild.sh <tag>   writes log/rebuild-<tag>.json and log/rebuild-<tag>.exit
cd /home/usain/gov-os-worktrees/W2-108 || exit 9
TAG="$1"
LOG=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || { echo 8 > "$LOG/rebuild-$TAG.exit"; exit 8; }
date +%s > "$LOG/rebuild-$TAG.start"
TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-$TAG.json" 2>&1
echo $? > "$LOG/rebuild-$TAG.exit"
date +%s > "$LOG/rebuild-$TAG.end"
