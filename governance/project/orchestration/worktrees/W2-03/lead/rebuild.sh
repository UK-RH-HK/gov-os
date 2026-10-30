#!/bin/bash
# Run 3's full rebuild from this worktree's code, under the machine's rebuild lock (DEC-939 item 2).
cd /home/usain/gov-os-worktrees/W2-03
LOG=/home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log
mkdir -p /tmp/gov-os-lead-W2-03
export TMPDIR=/tmp/gov-os-lead-W2-03
PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > $LOG/r3-rebuild.json 2> $LOG/r3-rebuild.err
echo $? > $LOG/r3-rebuild.exit
