#!/bin/bash
# Run 7: the scoped verification in the close's form (DEC-952, DEC-968, DEC-889 items 6 and 12, DEC-905), through
# verify_lock.sh (since DEC-983 a heavy-job slot, -n auto capped at 6 workers). The parallel run over the selection is
# split by folder so that each part ends well within the Bash tool's two hours; every part keeps the selection's whole
# pytest_options, so it runs exactly the selected cases under its folder. Arguments in log/v7 (select_tests.py at
# 110125ddda0b, v5_args.py). Outputs (JUnit, pytest text) under /tmp/gov-os-lead-W2-05/v7-results, never .gov-runtime
# (they hold full commit ids: row W2-L423's rule).
# The close's test runs get runner_env (DEC-970); runner6.py gives this run exactly that, through this worktree's helper.
#   verify7.sh unit | w1 | w2 | serial
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v7
OUT=/tmp/gov-os-lead-W2-05/v7-results
mkdir -p "$OUT"
NAME="$1"
rm -f "$LOG/$NAME.exit"
mapfile -t OPTS < "$LOG/parallel-opts.txt"
case "$NAME" in
  unit|w1|w2) mapfile -t PARTS < "$LOG/targets-$NAME.txt" ;;
  serial) mapfile -t PARTS < "$LOG/serial-args.txt" ;;
  *) echo "unknown part $NAME"; exit 2 ;;
esac
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/$NAME-disk.txt" 2>&1 || { echo 97 > "$LOG/$NAME.exit"; exit 97; }
du -sh /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime > "$LOG/$NAME-scratch-before.txt" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime >> "$LOG/$NAME-scratch-before.txt" 2>&1
date > "$LOG/$NAME.start"
cat /proc/loadavg >> "$LOG/$NAME.start"
if [ "$NAME" = serial ]; then
  # The plugin requires every given entry to name a collected case: the entries run (inside the selection) only.
  GIVEN="$(cat "$LOG/serial-args.txt")"
  TMPDIR=/tmp/gov-os-lead-W2-05 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" \
  python3 "$S/runner6.py" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$OUT/$NAME.xml" "${OPTS[@]}" "${PARTS[@]}" > "$OUT/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
else
  TMPDIR=/tmp/gov-os-lead-W2-05 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 \
  python3 "$S/runner6.py" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$OUT/$NAME.xml" "${OPTS[@]}" "${PARTS[@]}" > "$OUT/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
fi
tail -3 "$OUT/$NAME.txt" > "$LOG/$NAME-tail.txt"
cat /proc/loadavg >> "$LOG/$NAME.start"
date >> "$LOG/$NAME.start"
