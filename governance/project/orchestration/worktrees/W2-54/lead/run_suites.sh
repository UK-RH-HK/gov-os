#!/bin/sh
# Run each named acceptance suite in its own pytest process, to its end; one .txt and one .exit per suite.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
for suite in "$@"; do
  uptime > "$LOG/v2-$suite.load"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
    python3 -m pytest "tests/acceptance/$suite" -q -p no:cacheprovider -rs > "$LOG/v2-$suite.txt" 2>&1
  echo $? > "$LOG/v2-$suite.exit"
done
