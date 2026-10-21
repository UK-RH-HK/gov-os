#!/bin/sh
# Run 5, after the second test-design batch (92ba6f02): the four DEC-874 cases by node id, W2-54 in full in its own
# process, the pre-close gate's collection. Logs v8-*; the end is v8.end.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
FLAG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
quiet() {
  until [ ! -e $FLAG ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
}
one() {
  name="$1"; shift
  quiet
  uptime > "$LOG/v8-$name.load"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
    python3 -m pytest "$@" -p no:cacheprovider -rs > "$LOG/v8-$name.txt" 2>&1
  echo $? > "$LOG/v8-$name.exit"
  uptime >> "$LOG/v8-$name.load"
}
git log --oneline -1 > "$LOG/v8.head"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)" > "$LOG/v8-import.txt"
one dec874 -v "tests/acceptance/W2-54/test_w2_54_audit_report.py::test_no_schema_file_of_w2_02_s_other_types_comes_with_it" "tests/acceptance/W2-54/test_w2_54_audit_report.py::test_w2_02_s_other_types_are_judged_as_an_unknown_type" "tests/unit/check/test_schema_audit_report.py"
one W2-54 -q tests/acceptance/W2-54
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/v8-collect.txt" 2>&1
echo $? > "$LOG/v8-collect.exit"
echo end > "$LOG/v8.end"
