#!/bin/bash
# gov check on this worktree's code (DEC-732). Usage: check.sh <tag>  writes log/check-<tag>.json and .rc
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
TMPDIR=/tmp/gov-os-lead-W2-84 PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -m gov.cli.main check --json > "$LOG/check-$TAG.json" 2>&1
echo $? > "$LOG/check-$TAG.rc"
