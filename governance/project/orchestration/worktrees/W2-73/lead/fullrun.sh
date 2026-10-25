#!/usr/bin/env bash
# The lead's full verification (W2-73), in the close's form: one parallel run, then the serial-only cases alone.
# Called under flock /tmp/gov-os-verify.lock by the lead.
cd /home/usain/gov-os-worktrees/W2-73 || exit 2
export TMPDIR=/tmp/gov-os-lead-W2-73
LOG=/tmp/gov-os-lead-W2-73/verify
mkdir -p "$LOG"
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-73/src:/home/usain/gov-os-worktrees/W2-73/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-73
date -u +%FT%TZ > "$LOG/parallel.start"
python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/parallel.xml" > "$LOG/parallel.txt" 2>&1
echo $? > "$LOG/parallel.exit"
ENTRIES=$(python3 -c "import gov_close_serial_only as m; print('\n'.join(m.entries('.')))")
printf '%s\n' "$ENTRIES" > "$LOG/serial.entries"
export GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES"
mapfile -t ARGS <<< "$ENTRIES"
date -u +%FT%TZ > "$LOG/serial.start"
python3 -m pytest "${ARGS[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/serial.xml" > "$LOG/serial.txt" 2>&1
echo $? > "$LOG/serial.exit"
date -u +%FT%TZ > "$LOG/done"
