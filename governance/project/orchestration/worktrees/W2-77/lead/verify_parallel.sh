#!/usr/bin/env bash
# The lead's full verification, part 1: every suite in one parallel run, in the close's form (DEC-889, DEC-905).
LOG=/home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log
WT=/home/usain/gov-os-worktrees/W2-77
rm -f "$LOG/parallel.exit"
bash "$WT/.gov-runtime/scratch/lead/gates.sh" > "$LOG/parallel-gates.txt" 2>&1 || { echo 9 > "$LOG/parallel.exit"; exit 9; }
cd "$WT" || exit 8
export TMPDIR=/tmp/gov-os-lead-W2-77
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src:$WT/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$WT
date -u +%H:%M:%S > "$LOG/parallel.start"
flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/parallel.xml" > "$LOG/parallel.txt" 2>&1
echo $? > "$LOG/parallel.exit"
date -u +%H:%M:%S > "$LOG/parallel.end"
