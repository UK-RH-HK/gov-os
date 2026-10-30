#!/bin/bash
# W2-26 run 3: gov check --json on this worktree's code.
cd /home/usain/gov-os-worktrees/W2-26 || exit 90
TMPDIR=/tmp/gov-os-lead-W2-26 PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-check.json 2> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-check.err
echo $? > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-check.exit
