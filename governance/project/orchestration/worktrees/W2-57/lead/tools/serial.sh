#!/usr/bin/env bash
# The serial-only cases alone, as gov close runs them today (every entry of the list), under the lock.
cd /home/usain/gov-os-worktrees/W2-57 || exit 1
V=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/verify
mapfile -t E < "$V/serial-entries.txt"
GIVEN=$(cat "$V/serial-entries.txt")
TMPDIR=/tmp/gov-os-lead-W2-57 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src:/home/usain/gov-os-worktrees/W2-57/src/gov/close/pytest_plugin \
GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-57 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" \
flock /tmp/gov-os-verify.lock python3 -m pytest "${E[@]}" -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs --tb=line --junitxml="$V/serial.xml" > "$V/serial.txt" 2>&1
echo $? > "$V/serial.exit"
