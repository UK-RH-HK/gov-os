#!/bin/bash
# gov check of this worktree with its own code (DEC-732), after the rebuild. Outputs in the lead's log folder.
cd /home/usain/gov-os-worktrees/W2-61 || exit 90
TMPDIR=/tmp/gov-os-lead-W2-61 PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/log/gov-check.json 2> /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/log/gov-check.err
echo $? > /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/log/gov-check.exit
