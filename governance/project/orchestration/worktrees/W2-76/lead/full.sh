#!/usr/bin/env bash
# The lead's full verification run in the close's form (DEC-889, DEC-952 scope full), one phase per call:
# arg 1 = parallel | serial. The verification lock, the retention option, the gates first (DEC-898, DEC-933, DEC-847).
PHASE=$1
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
mkdir -p /tmp/gov-os-lead-W2-76
cd "$W" || exit 2
until [ ! -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
until [ ! -e "$ORCH/CLOSE-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" > "$LOG/full-$PHASE.gate" 2>&1 || { echo 3 > "$LOG/full-$PHASE.exit"; exit 3; }
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/full-$PHASE.scratch-before" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/full-$PHASE.scratch-before" 2>&1
PLUG=$W/src/gov/close/pytest_plugin
date '+start %F %T' > "$LOG/full-$PHASE.summary"
if [ "$PHASE" = parallel ]; then
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
    flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --ignore=$W/tests/acceptance/W2-76 --junitxml="$LOG/parallel.xml" > "$LOG/full-parallel.out" 2>&1
  code=$?
else
  ENTRIES=$(PYTHONPATH=$W/src python3 "$W/.gov-runtime/scratch/lead/entries.py" "$W")
  [ -n "$ENTRIES" ] || { echo 4 > "$LOG/full-$PHASE.exit"; exit 4; }
  # shellcheck disable=SC2086
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
    GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" \
    flock /tmp/gov-os-verify.lock python3 -m pytest $ENTRIES -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --ignore=$W/tests/acceptance/W2-76 --junitxml="$LOG/serial.xml" > "$LOG/full-serial.out" 2>&1
  code=$?
fi
date '+end %F %T' >> "$LOG/full-$PHASE.summary"
echo "exit $code: $(tail -1 "$LOG/full-$PHASE.out")" >> "$LOG/full-$PHASE.summary"
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/full-$PHASE.scratch-after" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/full-$PHASE.scratch-after" 2>&1
echo "$code" > "$LOG/full-$PHASE.exit"
