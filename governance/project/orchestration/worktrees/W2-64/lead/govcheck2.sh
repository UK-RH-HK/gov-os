#!/bin/bash
# gov check --json on run 2's head, this worktree's code (DEC-732); exit code to a file.
cd /home/usain/gov-os-worktrees/W2-64 || exit 98
cat /proc/loadavg > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/govcheck-2.load
TMPDIR=/tmp/gov-os-lead-W2-64 PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/govcheck-2.json 2> /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/govcheck-2.err
echo $? > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/govcheck-2.exit
