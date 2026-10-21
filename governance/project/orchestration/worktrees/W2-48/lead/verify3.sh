#!/usr/bin/env bash
# Usage: verify2.sh <batch-name> <suite> [<suite> ...]   (suite "unit" runs tests/unit; "collect" the collection check)
# Run 2's final-head verification: each suite in its own pytest process, to its end (never -x); output and exit code per suite.
# Waits for no close and a 1-minute load under 20 before the batch (DEC-847, DEC-780).
cd /home/usain/gov-os-worktrees/W2-48 || exit 2
out=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/log/verify3
mkdir -p "$out"
batch=$1; shift
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
for s in "$@"; do
  start=$(date +%s)
  name=${s//\//_}
  if [ "$s" = unit ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests/unit -q -p no:cacheprovider -rs > "$out/$name.txt" 2>&1
  elif [ "$s" = collect ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$out/$name.txt" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$out/$name.txt" 2>&1
  fi
  echo "$s $? $(( $(date +%s) - start ))s load=$(cut -d' ' -f1 /proc/loadavg)" >> "$out/$batch.codes"
done
echo done > "$out/$batch.exit"
