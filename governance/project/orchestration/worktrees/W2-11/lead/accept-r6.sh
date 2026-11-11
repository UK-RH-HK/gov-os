#!/bin/bash
# r6 gov accept; arg 1 = tag
TAG=${1:-a}
LOG=/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/accept-r6-$TAG.json
mkdir -p /tmp/gov-os-lead-W2-11
env TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11 > "$LOG" 2>&1
echo "exit $?" >> "$LOG"
tail -c 6000 "$LOG"
