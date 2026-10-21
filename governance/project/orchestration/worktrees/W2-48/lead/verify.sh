#!/usr/bin/env bash
# Usage: verify.sh <batch-name> <suite> [<suite> ...]   (suite "unit" runs tests/unit; "collect" the collection check)
# Each suite in its own pytest process, to its end; output and exit code per suite.
cd /home/usain/gov-os-worktrees/W2-48 || exit 2
out=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/log/verify
mkdir -p "$out"
batch=$1; shift
for s in "$@"; do
  start=$(date +%s)
  if [ "$s" = unit ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$out/$s.txt" 2>&1
  elif [ "$s" = collect ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$out/$s.txt" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$out/$s.txt" 2>&1
  fi
  echo "$s $? $(( $(date +%s) - start ))s" >> "$out/$batch.codes"
done
echo done > "$out/$batch.exit"
