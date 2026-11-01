#!/usr/bin/env bash
# Run 3, verification step 2 (DEC-956 item 2, DEC-964): run 1's lock-made reds (W1-07, W1-27, W1-41, W2-69, W1-30,
# W2-50, W2-54) run whole while hold.sh's real clone rebuild holds /tmp/gov-os-rebuild.lock, in the close's form: the
# parallel part with the serial-only plugin, then these suites' serial-only entries alone. Writes log/s2-*.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
PLUG=$W/src/gov/close/pytest_plugin
cd "$W" || exit 2
# wait for the hold's first rebuild to be running under the lock
until grep -q '^rebuild 1 start' "$LOG/s2.times" 2>/dev/null; do sleep 5; done
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/s2-held.scratch-before" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/s2-held.scratch-before" 2>&1
{ date '+parallel start %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } > "$LOG/s2-held.times"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_REBUILD_LOCK TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
  python3 -m pytest tests/acceptance/W1-07 tests/acceptance/W1-27 tests/acceptance/W1-30 tests/acceptance/W1-41 tests/acceptance/W2-50 tests/acceptance/W2-54 tests/acceptance/W2-69 \
  -n 12 -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfEs \
  --junitxml="$LOG/s2-parallel.xml" > "$LOG/s2-parallel.out" 2>&1
echo "parallel exit $? $(tail -1 "$LOG/s2-parallel.out")" >> "$LOG/s2-held.times"
{ date '+serial start %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } >> "$LOG/s2-held.times"
ENTRIES=$(PYTHONPATH=$W/src python3 "$W/.gov-runtime/scratch/lead/entries.py" "$W" | grep -E '^tests/acceptance/(W1-07|W1-27|W1-30|W1-41|W2-50|W2-54|W2-69)/')
echo "$ENTRIES" > "$LOG/s2-serial.entries"
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_REBUILD_LOCK TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" python3 -m pytest $ENTRIES -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfEs \
  --junitxml="$LOG/s2-serial.xml" > "$LOG/s2-serial.out" 2>&1
echo "serial exit $? $(tail -1 "$LOG/s2-serial.out")" >> "$LOG/s2-held.times"
{ date '+end %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } >> "$LOG/s2-held.times"
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/s2-held.scratch-after" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/s2-held.scratch-after" 2>&1
: > "$LOG/s2-stop"
echo done > "$LOG/s2-held.exit"
