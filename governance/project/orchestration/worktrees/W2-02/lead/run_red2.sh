#!/bin/bash
# Lead's red check, run 2: W2-02 and W1-26 to their end, each with its exit file.
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)" > "$OUT/red-2-import.txt" 2>&1
for s in W2-02 W1-26; do
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 3000 python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$OUT/red-2-$s.txt" 2>&1
  echo $? > "$OUT/red-2-$s.exit"
done
echo done > "$OUT/red-2.done"
