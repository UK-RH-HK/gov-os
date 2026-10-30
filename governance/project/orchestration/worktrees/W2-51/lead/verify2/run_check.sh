#!/bin/bash
# Run 2: the governance checks on this worktree's code, after the rebuild.
cd /home/usain/gov-os-worktrees/W2-51 || exit 99
date > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/check-time.txt
TMPDIR=/tmp/gov-os-lead-W2-51 PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/check.json 2> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/check.err
echo $? > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/check.exit
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/check-time.txt
