#!/bin/bash
# Run 7: gov check after the rebuild (this worktree's code). Output under the temp folder (row W2-L423's rule).
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
OUT=/tmp/gov-os-lead-W2-05/v7-results
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v7
mkdir -p "$OUT"
date > "$LOG/check.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main check --json > "$OUT/check.json" 2> "$OUT/check.err"
echo $? > "$LOG/check.exit"
date >> "$LOG/check.start"
