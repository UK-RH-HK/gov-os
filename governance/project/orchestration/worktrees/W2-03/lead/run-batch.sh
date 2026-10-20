#!/usr/bin/env bash
# Run 2 verification: each suite in its own pytest process, to its end (never -x).
# Usage: run-batch.sh <batch-name> <suite>...   (a suite is a folder name under tests/acceptance, or "unit")
cd /home/usain/gov-os-worktrees/W2-03 || exit 2
log=/home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log
batch="$1"; shift
: > "$log/r2-batch-$batch.progress"
worst=0
for s in "$@"; do
  if [ "$s" = unit ]; then target=tests/unit; else target="tests/acceptance/$s"; fi
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src \
    python3 -m pytest "$target" -q -p no:cacheprovider -rs > "$log/r2-suite-$s.txt" 2>&1
  rc=$?
  [ "$rc" -gt "$worst" ] && worst=$rc
  echo "$s exit $rc: $(tail -n 1 "$log/r2-suite-$s.txt")" >> "$log/r2-batch-$batch.progress"
done
echo "$worst" > "$log/r2-batch-$batch.exit"
