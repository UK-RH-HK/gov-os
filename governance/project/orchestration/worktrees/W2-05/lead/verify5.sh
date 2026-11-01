#!/bin/bash
# Run 5: the scoped verification in the close's form (DEC-952, DEC-968, DEC-889 items 6 and 12, DEC-905).
# $1 = "parallel" or "serial"; $2 = "A" (the selection less W1-02 and W2-05) or "B" (those two suites, after the
# repair batch's merge). Arguments come from log/v5 (v5_args.py, v5_split.py).
# The close now starts its test runs with git's configuration pinned (W2-M161, this ticket's _started), so this
# run pins it too (GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1); every red is re-run unpinned afterwards,
# which splits package I's reds from the others.
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v5
PHASE="$1"; PART="$2"; NAME="$PHASE-$PART"
rm -f "$LOG/$NAME.exit"
mapfile -t OPTS < "$LOG/parallel-opts-$PART.txt"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/$NAME-disk.txt" 2>&1 || { echo 97 > "$LOG/$NAME.exit"; exit 97; }
du -sh /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime > "$LOG/$NAME-scratch-before.txt" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime >> "$LOG/$NAME-scratch-before.txt" 2>&1
date > "$LOG/$NAME.start"
cat /proc/loadavg >> "$LOG/$NAME.start"
if [ "$PHASE" = parallel ]; then
  if [ "$PART" != B ]; then TARGETS=(tests); else mapfile -t TARGETS < "$LOG/parallel-args-B.txt"; fi
  TMPDIR=/tmp/gov-os-lead-W2-05 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest "${TARGETS[@]}" -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$LOG/$NAME.xml" "${OPTS[@]}" > "$LOG/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
else
  mapfile -t ARGS < "$LOG/serial-args-$PART.txt"
  GIVEN="$(cat "$LOG/serial-given.txt")"
  TMPDIR=/tmp/gov-os-lead-W2-05 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$LOG/$NAME.xml" "${OPTS[@]}" "${ARGS[@]}" > "$LOG/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
fi
cat /proc/loadavg >> "$LOG/$NAME.start"
date >> "$LOG/$NAME.start"
