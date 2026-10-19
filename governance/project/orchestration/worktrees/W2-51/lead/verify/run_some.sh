#!/bin/bash
# Lead verification for DAEO-egsy, second part: the named suites, one after another ("unit" = the builder tests).
# Usage: run_some.sh <tag> <suite>...
cd /home/usain/gov-os-worktrees/W2-51 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify
tag=$1; shift
for s in "$@"; do
  if [ "$s" = unit ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$OUT/unit.log" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src \
      python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$OUT/suite-$s.log" 2>&1
  fi
  echo "$s $?" >> "$OUT/suites.exit"
done
echo finished > "$OUT/$tag.done"
