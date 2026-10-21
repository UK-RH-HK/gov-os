#!/bin/bash
# Lead's run-5 after-batch: gov check, the pre-close collection (DEC-868), then the reds re-run alone, one after
# another (load-sensitive cases, W1-46's setup errors, W1-25's setup error), after waiting for no close and a load under 20.
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log/suites5/after
mkdir -p "$OUT"
NODE=/home/usain/.nvm/versions/node/v22.23.3/bin
SRC=/home/usain/gov-os-worktrees/W2-02/src
PATH=$NODE:$PATH PYTHONPATH=$SRC python3 -m gov.cli.main check --json > "$OUT/gov-check.json" 2>&1; echo $? > "$OUT/gov-check.exit"
PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$OUT/collect.txt" 2>&1; echo $? > "$OUT/collect.exit"
run_alone() {
  name="$1"; shift
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  uptime > "$OUT/$name.uptime"
  PATH=$NODE:$PATH PYTHONPATH=$SRC timeout 3000 python3 -m pytest "$@" -q -p no:cacheprovider -rs > "$OUT/$name.txt" 2>&1
  echo $? > "$OUT/$name.exit"
}
run_alone W1-05-p95 "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook"
run_alone W1-05-switch "tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over"
run_alone W1-19 "tests/acceptance/W1-19/test_w1_19_real_models.py"
run_alone W1-25 "tests/acceptance/W1-25"
run_alone W1-46 "tests/acceptance/W1-46"
echo done > "$OUT/all.done"
