#!/bin/bash
# Lead's gov check after rebuild-4 (this worktree's src, DEC-732).
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
date > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/check-4.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/check-4.json 2> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/check-4.err
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/check-4.exit
date >> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/check-4.start
