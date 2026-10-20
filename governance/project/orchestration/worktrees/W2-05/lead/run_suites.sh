#!/bin/bash
# Runs each named acceptance suite in its own pytest process; writes <log>/<suite>.txt and <log>/<suite>.exit.
# Usage: run_suites.sh <batch-name> <suite> [<suite> ...]
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/suites
mkdir -p "$LOG"
batch="$1"; shift
for s in "$@"; do
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
    python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$LOG/$s.txt" 2>&1
  echo $? > "$LOG/$s.exit"
done
echo done > "$LOG/batch-$batch.done"
