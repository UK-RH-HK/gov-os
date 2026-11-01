#!/bin/bash
# Run 7: gov check on this worktree's code and store, after rebuild-9 (DEC-732); exit code to log/check-7.exit.
LOG=/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-67 || exit 99
date -Is > "$LOG/check-7.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main check --json > "$LOG/check-7.json" 2> "$LOG/check-7.err"
echo $? > "$LOG/check-7.exit"
date -Is >> "$LOG/check-7.start"
