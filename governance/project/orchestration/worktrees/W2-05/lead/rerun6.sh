#!/bin/bash
# Run 6: every red of the close-form runs, re-run alone in one process, to the end, in the plain environment
# (unpinned, the brief's literal form). A load-sensitive case that passes here counts (DEC-762); a red that is
# green here and red in the close's form is package I's kind.
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v6
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
rm -f "$LOG/rerun.exit"
python3 $S/reds5.py "$LOG/reds.txt" "$LOG/parallel.xml" "$LOG/serial.xml" > "$LOG/reds-count.txt" 2>&1
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
