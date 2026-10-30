#!/usr/bin/env bash
# The lead's full verification, part 2: the serial-only cases alone, as gov close runs them; then gov check.
LOG=/home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log
WT=/home/usain/gov-os-worktrees/W2-77
rm -f "$LOG/serial.exit" "$LOG/check.exit"
bash "$WT/.gov-runtime/scratch/lead/gates.sh" > "$LOG/serial-gates.txt" 2>&1 || { echo 9 > "$LOG/serial.exit"; exit 9; }
cd "$WT" || exit 8
grep -v '^[[:space:]]*#' tests/acceptance/serial-only.txt | sed 's/ #.*//; s/[[:space:]]*$//' | grep -v '^$' > "$LOG/serial-entries.txt"
mapfile -t ENTRIES < "$LOG/serial-entries.txt"
export TMPDIR=/tmp/gov-os-lead-W2-77
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src:$WT/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$WT
GOV_CLOSE_SERIAL_ONLY_GIVEN=$(cat "$LOG/serial-entries.txt")
export GOV_CLOSE_SERIAL_ONLY_GIVEN
date -u +%H:%M:%S > "$LOG/serial.start"
flock /tmp/gov-os-verify.lock python3 -m pytest "${ENTRIES[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/serial.xml" > "$LOG/serial.txt" 2>&1
echo $? > "$LOG/serial.exit"
date -u +%H:%M:%S > "$LOG/serial.end"
PYTHONPATH=$WT/src python3 -m gov.cli.main check --json > "$LOG/check.json" 2> "$LOG/check.err"
echo $? > "$LOG/check.exit"
