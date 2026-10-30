#!/bin/bash
# Run 3, merged head: gov check --json from this worktree's code, timed, with an exit-code file.
cd /home/usain/gov-os-worktrees/W2-03
export TMPDIR=/tmp/gov-os-lead-W2-03
date > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.time
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.time
PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.json 2> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.err
echo $? > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.exit
date >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.time
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-check.time
