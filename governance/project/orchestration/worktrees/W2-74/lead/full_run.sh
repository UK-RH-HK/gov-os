#!/usr/bin/env bash
# DAEO-2azm (W2-74): the full verification run in the close's form (DEC-889 items 6 and 12, DEC-904, DEC-905):
# one parallel run with the serial-only cases left out, then the serial-only cases alone, both under the lock.
# Usage: full_run.sh parallel|serial
set -u
WT=/home/usain/gov-os-worktrees/W2-74
LOG=$WT/.gov-runtime/scratch/lead/log
cd "$WT" || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-74
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src:$WT/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$WT

case "${1:-}" in
  parallel)
    flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
      -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/parallel.xml" > "$LOG/parallel.txt" 2>&1
    echo $? > "$LOG/parallel.exit"
    ;;
  serial)
    grep -v '^[[:space:]]*#' tests/acceptance/serial-only.txt | sed 's/[[:space:]]#.*$//; s/[[:space:]]*$//' \
      | grep -v '^$' | awk '!seen[$0]++' > "$LOG/serial-entries.txt"
    mapfile -t ENTRIES < "$LOG/serial-entries.txt"
    GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$LOG/serial-entries.txt")"
    export GOV_CLOSE_SERIAL_ONLY_GIVEN
    flock /tmp/gov-os-verify.lock python3 -m pytest "${ENTRIES[@]}" -q -p no:cacheprovider -p gov_close_serial_only \
      -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/serial.xml" > "$LOG/serial.txt" 2>&1
    echo $? > "$LOG/serial.exit"
    ;;
  *)
    echo "usage: full_run.sh parallel|serial" >&2
    exit 2
    ;;
esac
