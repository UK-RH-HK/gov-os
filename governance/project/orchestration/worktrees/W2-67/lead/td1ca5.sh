#!/bin/bash
# Run 5: TD1C-A's code-graph case, run by the lead outside the sandbox on the merged head, with the daemon folders
# under /tmp/gov-cbm-1000 counted before and after (as run 4 did).
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$TMPDIR"
cd "$W" || exit 99
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 30; done
{
  echo "head=$(git rev-parse --short=12 HEAD) start=$(date -Is) load=$(cut -d' ' -f1 /proc/loadavg)"
  echo "gov_file=$(PYTHONPATH=$W/src python3 -c 'import gov; print(gov.__file__)')"
  echo "cbm_entries_before=$(ls -A /tmp/gov-cbm-1000 | wc -l)"
} > "$LOG/cg-run5.txt"
ls -A /tmp/gov-cbm-1000 | sort > "$LOG/cg-run5-before.list"
PYTHONPATH=$W/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -n 3 \
  tests/acceptance/W1-27/test_w2_67_codegraph_folders.py > "$LOG/cg-run5.out" 2>&1
e=$?
ls -A /tmp/gov-cbm-1000 | sort > "$LOG/cg-run5-after.list"
{
  echo "exit=$e end=$(date -Is)"
  echo "result: $(tail -1 $LOG/cg-run5.out)"
  echo "cbm_entries_after=$(ls -A /tmp/gov-cbm-1000 | wc -l)"
  echo "added: $(comm -13 $LOG/cg-run5-before.list $LOG/cg-run5-after.list | tr '\n' ' ')"
  echo "removed: $(comm -23 $LOG/cg-run5-before.list $LOG/cg-run5-after.list | wc -l)"
} >> "$LOG/cg-run5.txt"
echo "$e" > "$LOG/cg-run5.exit"
