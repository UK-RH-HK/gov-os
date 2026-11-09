#!/bin/bash
# Run named acceptance suites (and "unit") in this worktree, each to its end, one output and exit file each.
# Usage: run_suites.sh <outdir> <batch-name> <suite>...
out=$1; batch=$2; shift 2
cd /home/usain/gov-os-worktrees/W2-20 || exit 99
mkdir -p "$out"
for s in "$@"; do
  if [ "$s" = unit ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$out/unit.txt" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$out/$s.txt" 2>&1
  fi
  rc=$?
  echo "$s exit=$rc $(tail -n 1 "$out/$s.txt")" >> "$out/summary-$batch.txt"
done
echo done > "$out/$batch.done"
