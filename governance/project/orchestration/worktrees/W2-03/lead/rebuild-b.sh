#!/bin/bash
# Run 3, after the second merge: gates, then the full rebuild under the machine's rebuild lock (DEC-939 item 2).
bash /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/gates.sh > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-gates-rebuild.txt 2>&1
cd /home/usain/gov-os-worktrees/W2-03
export TMPDIR=/tmp/gov-os-lead-W2-03
PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-rebuild.json 2> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-rebuild.err
echo $? > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-rebuild.exit
