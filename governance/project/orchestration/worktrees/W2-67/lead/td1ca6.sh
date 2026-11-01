#!/bin/bash
# Run 6: TD1C-A's code-graph case, run by the lead outside the sandbox on the merged head, with the daemon folders
# under /tmp/gov-cbm-1000 counted before and after (as runs 3 to 5 did).
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-67
cd "$W" || exit 99
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 30; done
{
  echo "head=$(git rev-parse --short=12 HEAD) start=$(date -Is) load=$(cut -d' ' -f1 /proc/loadavg)"
  echo "gov_file=$(PYTHONPATH=$W/src python3 -c 'import gov; print(gov.__file__)')"
  echo "cbm_entries_before=$(ls -A /tmp/gov-cbm-1000 | wc -l)"
} > "$LOG/cg-run6.txt"
ls -A /tmp/gov-cbm-1000 | sort > "$LOG/cg-run6-before.list"
PYTHONPATH=$W/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -n 3 \
  tests/acceptance/W1-27/test_w2_67_codegraph_folders.py > "$LOG/cg-run6.out" 2>&1
e=$?
ls -A /tmp/gov-cbm-1000 | sort > "$LOG/cg-run6-after.list"
{
  echo "exit=$e end=$(date -Is)"
  echo "result: $(tail -1 $LOG/cg-run6.out)"
  echo "cbm_entries_after=$(ls -A /tmp/gov-cbm-1000 | wc -l)"
  echo "added: $(comm -13 $LOG/cg-run6-before.list $LOG/cg-run6-after.list | tr '\n' ' ')"
  echo "removed: $(comm -23 $LOG/cg-run6-before.list $LOG/cg-run6-after.list | wc -l)"
} >> "$LOG/cg-run6.txt"
echo "$e" > "$LOG/cg-run6.exit"
