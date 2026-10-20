#!/bin/bash
# Lead verification for DAEO-egsy: every acceptance suite, one after another, then the builder tests.
cd /home/usain/gov-os-worktrees/W2-51 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify
for d in tests/acceptance/W2-51 $(ls -d tests/acceptance/W1-* | sort -V); do
  s=$(basename "$d")
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src \
    python3 -m pytest "$d" -q -p no:cacheprovider -rs > "$OUT/suite-$s.log" 2>&1
  echo "$s $?" >> "$OUT/suites.exit"
done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$OUT/unit.log" 2>&1
echo "unit $?" >> "$OUT/suites.exit"
echo finished > "$OUT/suites.done"
