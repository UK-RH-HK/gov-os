#!/bin/bash
# Run 6: the scoped verification in the close's form (DEC-952, DEC-968, DEC-889 items 6 and 12, DEC-905).
# $1 = "parallel" or "serial". Arguments in log/v6 (select_tests.py at ba807a032603, v5_args.py).
# The close's test runs now get runner_env (package I (b), DEC-970): no GIT_* of the caller, the system
# configuration unread, GIT_CONFIG_GLOBAL a generated file with only the person's user.name, user.email and
# init.defaultBranch. runner6.py gives this run exactly that, through this worktree's own helper.
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v6
PHASE="$1"; NAME="$PHASE"
rm -f "$LOG/$NAME.exit"
mapfile -t OPTS < "$LOG/parallel-opts.txt"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/$NAME-disk.txt" 2>&1 || { echo 97 > "$LOG/$NAME.exit"; exit 97; }
du -sh /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime > "$LOG/$NAME-scratch-before.txt" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-05 /home/usain/gov-os-worktrees/W2-05/.gov-runtime >> "$LOG/$NAME-scratch-before.txt" 2>&1
date > "$LOG/$NAME.start"
cat /proc/loadavg >> "$LOG/$NAME.start"
if [ "$PHASE" = parallel ]; then
  TMPDIR=/tmp/gov-os-lead-W2-05 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 \
  python3 "$S/runner6.py" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$LOG/$NAME.xml" "${OPTS[@]}" > "$LOG/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
else
  mapfile -t ARGS < "$LOG/serial-args.txt"
  # The plugin requires every given entry to name a collected case: give it the entries run (those in the
  # selection), not the whole list (the first serial run of 17:24 ended "no case is named" on five ignored ones).
  GIVEN="$(cat "$LOG/serial-args.txt")"
  TMPDIR=/tmp/gov-os-lead-W2-05 \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-05 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" \
  python3 "$S/runner6.py" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
    python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$LOG/$NAME.xml" "${OPTS[@]}" "${ARGS[@]}" > "$LOG/$NAME.txt" 2>&1
  echo $? > "$LOG/$NAME.exit"
fi
cat /proc/loadavg >> "$LOG/$NAME.start"
date >> "$LOG/$NAME.start"
