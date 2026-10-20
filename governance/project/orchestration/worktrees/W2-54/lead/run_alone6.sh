#!/bin/sh
# Run 5: the cases red under load in run_v6.sh, each alone after every other suite ended; and the four DEC-874 cases
# by node id. Logs alone6-*; the end is alone6.end.
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
  uptime > "$LOG/alone6-$name.load"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
    python3 -m pytest "$@" -q -p no:cacheprovider -rs > "$LOG/alone6-$name.txt" 2>&1
  echo $? > "$LOG/alone6-$name.exit"
  uptime >> "$LOG/alone6-$name.load"
}
one dec874 "tests/acceptance/W2-54/test_w2_54_audit_report.py::test_no_schema_file_of_w2_02_s_other_types_comes_with_it" "tests/acceptance/W2-54/test_w2_54_audit_report.py::test_w2_02_s_other_types_are_judged_as_an_unknown_type" "tests/unit/check/test_schema_audit_report.py" -v
one timelimit "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit"
one greenhere tests/acceptance/W2-54/test_w2_54_green_here.py -v
one W1-25 tests/acceptance/W1-25
one W1-46 tests/acceptance/W1-46
echo end > "$LOG/alone6.end"
