#!/usr/bin/env bash
# Run 2's closing runs, one after another, on this worktree's src (DEC-732): the builder tests, the load-sensitive and
# flaked cases alone, then gov check in a quiet machine. Each waits for both gates (no close, load below 20).
W=/home/usain/gov-os-worktrees/W2-59
L=/home/usain/gov-os-worktrees/W2-59/.gov-runtime/scratch/lead/log
BT=/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-59/5116ebd4-4968-4639-ba28-0c5da4fd82d4/scratchpad/bt
cd "$W" || exit 99
gate() {
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  echo "$1 start $(date -Is) load $(cut -d' ' -f1 /proc/loadavg)" >> "$L/after-summary.txt"
}
run() {  # name, then the pytest arguments
  name="$1"; shift
  gate "$name"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src \
    python3 -m pytest "$@" -q -p no:cacheprovider -rs -rf > "$L/after-$name.txt" 2>&1
  echo "$name rc=$? :: $(tail -1 "$L/after-$name.txt")" >> "$L/after-summary.txt"
}
run unit tests/unit
run w1-05-switch-over "tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over"
run w1-02-p95 "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms"
run w1-05-p95 "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook"
rm -rf "$BT"; mkdir -p "$BT"
run w1-25 tests/acceptance/W1-25 --basetemp "$BT/w1-25"
gate check-3
PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main check --json > "$L/check-3.json" 2>&1
echo "check-3 rc=$? end $(date -Is)" >> "$L/after-summary.txt"
echo done > "$L/after.exit"
