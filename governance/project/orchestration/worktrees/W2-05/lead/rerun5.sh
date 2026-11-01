#!/bin/bash
# Run 5: every red of the pinned runs, re-run unpinned (the brief's literal environment), one process, to the end.
# Splits package I's reds (green unpinned) from the others.
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v5
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
rm -f "$LOG/rerun.exit"
python3 $S/reds5.py "$LOG/reds.txt" "$LOG/parallel-F.xml" "$LOG/serial-F.xml" > "$LOG/reds-count.txt" 2>&1
mapfile -t REDS < "$LOG/reds.txt"
if [ "${#REDS[@]}" -eq 0 ]; then echo 0 > "$LOG/rerun.exit"; exit 0; fi
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
date > "$LOG/rerun.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs \
  --junitxml="$LOG/rerun.xml" "${REDS[@]}" > "$LOG/rerun.txt" 2>&1
echo $? > "$LOG/rerun.exit"
date >> "$LOG/rerun.start"
