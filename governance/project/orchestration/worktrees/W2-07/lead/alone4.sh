#!/usr/bin/env bash
# Run 4: the two load-sensitive reds re-run alone, each in its own process, after the other suites ended (W1-19's warm
# query on load_sensitive; W2-54's green-here case, row W2-L429). Exit codes in log/alone4-*.exit; log/alone4.done.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
export TMPDIR=/tmp/gov-os-lead-W2-07
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src
rm -f "$L/alone4.done"
trap 'echo done > "$L/alone4.done"' EXIT
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; } > "$L/alone4-w1-19.gate"
flock /tmp/gov-os-verify.lock python3 -m pytest "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/alone4-w1-19.txt" 2>&1; echo $? > "$L/alone4-w1-19.exit"
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; } > "$L/alone4-w2-54.gate"
flock /tmp/gov-os-verify.lock python3 -m pytest "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/alone4-w2-54.txt" 2>&1; echo $? > "$L/alone4-w2-54.exit"
