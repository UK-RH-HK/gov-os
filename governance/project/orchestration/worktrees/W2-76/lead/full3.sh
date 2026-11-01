#!/usr/bin/env bash
# Run 3, verification step 3: the selection's scope is full (SHARED_CORE tests/conftest.py), so one full run in the
# close's form, each phase through verify_lock.sh (the gate's room only, DEC-961, DEC-962), the retention option
# (DEC-905), the load and disk gates first (DEC-847, DEC-898). Arg 1: parallel | serial. Writes log/f3-<phase>.*.
PHASE=$1
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
PLUG=$W/src/gov/close/pytest_plugin
cd "$W" || exit 2
until python3 "$W/.gov-runtime/scratch/lead/loadok.py"; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" > "$LOG/f3-$PHASE.gate" 2>&1 || { echo 3 > "$LOG/f3-$PHASE.exit"; exit 3; }
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/f3-$PHASE.scratch-before" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/f3-$PHASE.scratch-before" 2>&1
date '+queued %F %T' > "$LOG/f3-$PHASE.summary"
if [ "$PHASE" = parallel ]; then
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_REBUILD_LOCK TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
    bash "$ORCH/tools/verify_lock.sh" bash "$W/.gov-runtime/scratch/lead/stamp.sh" "$LOG/f3-$PHASE.summary" \
    python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfEs \
    --junitxml="$LOG/f3-parallel.xml" > "$LOG/f3-parallel.out" 2>&1
  code=$?
else
  ENTRIES=$(PYTHONPATH=$W/src python3 "$W/.gov-runtime/scratch/lead/entries.py" "$W")
  [ -n "$ENTRIES" ] || { echo 4 > "$LOG/f3-$PHASE.exit"; exit 4; }
  echo "$ENTRIES" > "$LOG/f3-serial.entries"
  # shellcheck disable=SC2086
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_REBUILD_LOCK TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
    GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" \
    bash "$ORCH/tools/verify_lock.sh" bash "$W/.gov-runtime/scratch/lead/stamp.sh" "$LOG/f3-$PHASE.summary" \
    python3 -m pytest $ENTRIES -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfEs \
    --junitxml="$LOG/f3-serial.xml" > "$LOG/f3-serial.out" 2>&1
  code=$?
fi
date '+end %F %T' >> "$LOG/f3-$PHASE.summary"
echo "exit $code: $(tail -1 "$LOG/f3-$PHASE.out")" >> "$LOG/f3-$PHASE.summary"
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/f3-$PHASE.scratch-after" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/f3-$PHASE.scratch-after" 2>&1
echo "$code" > "$LOG/f3-$PHASE.exit"
