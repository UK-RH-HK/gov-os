#!/bin/bash
# Lead verification for W2-63: each suite in its own pytest process, to the end, with an exit-code file.
cd /home/usain/gov-os-worktrees/W2-63 || exit 99
L=/home/usain/gov-os-worktrees/W2-63/.gov-runtime/scratch/lead/log
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
PYTHONPATH=/home/usain/gov-os-worktrees/W2-63/src python3 -c "import gov; print(gov.__file__)" > $L/verify-gov-file.txt 2>&1
for s in W1-49 W1-29 W2-62; do
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-63/src python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -rs > $L/verify-$s.txt 2>&1
  echo $? > $L/verify-$s.exit
done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-63/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider > $L/verify-unit-hooks.txt 2>&1
echo $? > $L/verify-unit-hooks.exit
echo done > $L/verify-all.done
