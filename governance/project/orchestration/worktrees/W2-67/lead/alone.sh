#!/bin/bash
# Re-run each red of verify-r1 (other than the known DEC-906 red) alone, one process per case, under the lock.
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-67
cd "$W" || exit 99
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$W/src
: > "$LOG/alone-r1.txt"
while IFS= read -r t; do
  [ -z "$t" ] && continue
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 30; done
  flock /tmp/gov-os-verify.lock python3 -m pytest "$t" -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line --no-header > "$LOG/alone-r1.last" 2>&1
  e=$?
  echo "exit=$e load=$(cut -d' ' -f1 /proc/loadavg) $t :: $(tail -1 $LOG/alone-r1.last)" >> "$LOG/alone-r1.txt"
done < "$W/.gov-runtime/scratch/lead/alone-r1.list"
echo done > "$LOG/alone-r1.exit"
