#!/bin/bash
# gov check --json with this worktree's own code (DEC-732), after the rebuild; exit code to log/govcheck.rc.
cd /home/usain/gov-os-worktrees/W2-97 || exit 9
PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/check.json 2> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/check.err
echo $? > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/govcheck.rc
