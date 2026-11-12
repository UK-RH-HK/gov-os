#!/bin/bash
# usage: window.sh <tree> <log>  -- each folder on its own (the folders' conftests clash in one run)
T=$1; L=$2; D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/claude-copies-4
: > $L
cd $T
for f in tests/acceptance/W1-26 tests/acceptance/W1-30 tests/acceptance/W1-33 tests/acceptance/W1-35 tests/acceptance/W1-36 tests/acceptance/W1-38 tests/acceptance/W1-40 tests/acceptance/W2-05 tests/acceptance/W2-57 tests/acceptance/W2-66 tests/acceptance/W2-128 tests/acceptance/W2-153 tests/unit/adapters tests/unit/gitenv; do
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=$D/tmp PYTHONPATH=$T/src python3 -m pytest $f -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $L.$$ 2>&1
  echo "== $f exit $? :: $(tail -1 $L.$$)" >> $L
  grep -E "^(FAILED|ERROR)" $L.$$ | cut -c1-200 >> $L
done
rm -f $L.$$
echo done >> $L
