#!/bin/bash
# Usage: run-batch-3.sh <batch name> <suite dir>...   (suite dirs relative to the worktree, e.g. tests/acceptance/W1-07)
# Runs each suite to its end (never -x) with this worktree's src/, one after another; one log and one exit file per suite.
W=/home/usain/gov-os-worktrees/W2-16
LOG=$W/.gov-runtime/scratch/lead/log/verify-3
mkdir -p "$LOG"
name=$1; shift
cd "$W" || exit 99
for suite in "$@"; do
  tag=$(basename "$suite")
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$W/src python3 -m pytest "$suite" -q -p no:cacheprovider -rfs > "$LOG/$tag.log" 2>&1
  echo $? > "$LOG/$tag.exit"
done
echo done > "$LOG/batch-$name.done"
