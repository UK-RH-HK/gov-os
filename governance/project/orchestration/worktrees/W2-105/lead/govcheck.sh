#!/bin/bash
# gov check after the full rebuild, with this worktree's code (DEC-732).
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m gov.cli.main check --json > $L/check.json 2> $L/check.err
echo $? > $L/check.exit
