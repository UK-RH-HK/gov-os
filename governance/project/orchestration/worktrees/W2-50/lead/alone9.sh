#!/bin/bash
# W2-50 run 9: the reds of the parallel and serial runs, each re-run alone after the other suites ended.
W=/home/usain/gov-os-worktrees/W2-50
OUT=$W/.gov-runtime/scratch/lead/log/v9-alone
mkdir -p $OUT
cd $W || exit 9
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
run() {  # run <name> <node ids...>
  local n=$1; shift
  [ -e $OUT/$n.exit ] && return
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  echo "$n $(date -Is) $(cat /proc/loadavg) $(df -i --output=ipcent / | tail -1)" >> $OUT/starts.txt
  PYTHONPATH=$W/src python3 -m pytest "$@" -q -p no:cacheprovider -rs --junitxml=$OUT/$n.xml > $OUT/$n.txt 2>&1
  echo $? > $OUT/$n.exit
}
run w1-38 "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestGenerateCheck::test_check_clean_after_generate" "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family"
run w1-05-live "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook"
run w1-05-switch "tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over"
run w1-46-live "tests/acceptance/W1-46/test_w1_46_live_sessions.py"
touch $OUT/ALL.done
