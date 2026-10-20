#!/bin/bash
# Lead verification for W2-20: each acceptance suite to its end, the builder tests, the validator.
W=/home/usain/gov-os-worktrees/W2-20
L=$W/.gov-runtime/scratch/lead/log/verify
mkdir -p "$L"
cd "$W" || exit 99
PYTHONPATH=$W/src python3 -c "import gov; print(gov.__file__)" > "$L/import.txt" 2>&1
: > "$L/summary.txt"
for d in tests/acceptance/*/; do
  s=$(basename "$d")
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$W/src python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$L/$s.txt" 2>&1
  echo "$s exit=$? $(tail -n 1 "$L/$s.txt")" >> "$L/summary.txt"
done
PYTHONPATH=$W/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$L/unit.txt" 2>&1
echo "unit exit=$? $(tail -n 1 "$L/unit.txt")" >> "$L/summary.txt"
PYTHONPATH=$W/src python3 docs/plan/tools/validate_s1.py > "$L/validate.txt" 2>&1
echo "validate exit=$? $(tail -n 1 "$L/validate.txt")" >> "$L/summary.txt"
echo done > "$L/DONE"
