#!/bin/bash
# Run every acceptance suite one after another, then the builder tests; one output and exit file each.
# A suite with an exit file already is skipped (resume after a stopped run).
cd /home/usain/gov-os-worktrees/W2-49 || exit 9
OUT=/home/usain/gov-os-worktrees/W2-49/.gov-runtime/scratch/lead/log/run2-suites
mkdir -p "$OUT"
for d in tests/acceptance/W*/; do
  s=$(basename "$d")
  [ -s "$OUT/$s.exit" ] && continue
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src \
    python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$OUT/$s.txt" 2>&1
  echo $? > "$OUT/$s.exit"
done
if [ ! -s "$OUT/unit.exit" ]; then
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$OUT/unit.txt" 2>&1
  echo $? > "$OUT/unit.exit"
fi
echo done > "$OUT/ALL.done"
