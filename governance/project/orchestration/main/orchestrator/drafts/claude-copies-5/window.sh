#!/bin/bash
# usage: window.sh <tree> <log> <folder>...  -- each folder on its own pytest run (the folders' conftests clash in one run),
# through the heavy-job gate; real HOME for pytest (the user site holds pytest)
T=$1; L=$2; shift 2
R=/home/usain/gov-os-runs/W2-00/claude-copies-5
: > $L
cd $T
for f in "$@"; do
  [ -d "$f" ] || { echo "== $f ABSENT (no such folder in this tree)" >> $L; continue; }
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=$R/tmp PYTHONPATH=$T/src python3 -m pytest $f -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $L.$$ 2>&1
  echo "== $f exit $? :: $(grep -E ' in [0-9.]+s' $L.$$ | tail -1)" >> $L
  grep -E "^(FAILED|ERROR)" $L.$$ | cut -c1-220 >> $L
done
rm -f $L.$$
echo done >> $L
