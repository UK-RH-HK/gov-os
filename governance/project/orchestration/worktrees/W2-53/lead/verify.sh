#!/usr/bin/env bash
# Usage: verify.sh <batch-name> <suite> [<suite> ...]   (suite "unit" runs tests/unit)
# Each suite in its own pytest process, to its end; output and exit code per suite.
cd /home/usain/gov-os-worktrees/W2-53 || exit 2
out=/home/usain/gov-os-worktrees/W2-53/.gov-runtime/scratch/lead/log/verify
mkdir -p "$out"
batch=$1; shift
for s in "$@"; do
  if [ "$s" = unit ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$out/$s.txt" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$out/$s.txt" 2>&1
  fi
  echo "$s $?" >> "$out/$batch.codes"
done
echo done > "$out/$batch.exit"
