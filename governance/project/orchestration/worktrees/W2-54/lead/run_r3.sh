#!/bin/sh
# Run 3: each named acceptance suite in its own pytest process, to its end; PREFIX names the log files.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
PREFIX="$1"; shift
for suite in "$@"; do
  uptime > "$LOG/$PREFIX-$suite.load"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
    python3 -m pytest "tests/acceptance/$suite" -q -p no:cacheprovider -rs > "$LOG/$PREFIX-$suite.txt" 2>&1
  echo $? > "$LOG/$PREFIX-$suite.exit"
  uptime >> "$LOG/$PREFIX-$suite.load"
done
echo done > "$LOG/$PREFIX.done"
