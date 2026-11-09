#!/bin/bash
# Lead verification for W2-20, in batches: $1 names the batch; the rest are acceptance suites, or "unit", "validate".
W=/home/usain/gov-os-worktrees/W2-20
L=$W/.gov-runtime/scratch/lead/log/verify
B=$1; shift
cd "$W" || exit 99
for s in "$@"; do
  case "$s" in
    unit) PYTHONPATH=$W/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$L/unit.txt" 2>&1 ;;
    validate) PYTHONPATH=$W/src python3 docs/plan/tools/validate_s1.py > "$L/validate.txt" 2>&1 ;;
    *) PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$W/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$L/$(echo "$s" | tr '/' '_').txt" 2>&1 ;;
  esac
  echo "$s exit=$? $(tail -n 1 "$L/$(echo "$s" | tr '/' '_' | sed 's/^validate$/validate/').txt")" >> "$L/summary-$B.txt"
done
echo done > "$L/$B.done"
