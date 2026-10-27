#!/usr/bin/env bash
# Run 4: W1-19's warm-query case alone, a second time, once the 1-minute load is below 8 (the first alone run at load 19
# met two other sessions' CPU llama-servers). Waits at most 50 minutes for the quiet. Exit code in log/alone4b.exit.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
export TMPDIR=/tmp/gov-os-lead-W2-07
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src
for i in $(seq 1 50); do
  [ ! -e "$CLOSE" ] && awk '{exit !($1 < 8)}' /proc/loadavg && break
  sleep 60
done
{ date -Is; cat /proc/loadavg; ps -eo pcpu,args --sort=-pcpu | head -4 | cut -c1-90; } > "$L/alone4b.gate"
flock /tmp/gov-os-verify.lock python3 -m pytest "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/alone4b.txt" 2>&1; echo $? > "$L/alone4b.exit"
