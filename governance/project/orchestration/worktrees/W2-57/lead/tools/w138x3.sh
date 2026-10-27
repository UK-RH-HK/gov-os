#!/usr/bin/env bash
# W1-38's suite three times in the close's parallel form (-n auto, the close's plugin), with W1-33 and the unit
# suite beside it for load, each under the lock, each with JUnit XML and the load at start and end.
cd /home/usain/gov-os-worktrees/W2-57 || exit 1
V=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/verify
for n in 1 2 3; do
  echo "run $n start $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$V/w138.txt"
  TMPDIR=/tmp/gov-os-lead-W2-57 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src:/home/usain/gov-os-worktrees/W2-57/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-57 \
  flock /tmp/gov-os-verify.lock python3 -m pytest tests/acceptance/W1-38 tests/acceptance/W1-33 tests/unit -n auto -q \
    -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --tb=line \
    --junitxml="$V/w138-$n.xml" > "$V/w138-$n.txt" 2>&1
  echo "run $n exit $? end $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg) | $(tail -1 "$V/w138-$n.txt")" >> "$V/w138.txt"
done
echo done > "$V/w138.exit"
