#!/bin/bash
# Run 2: the load-sensitive cases alone, and W1-46 without the caller's CLAUDE* variables (P-W1-46).
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/suites2
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src
python3 -m pytest tests/acceptance/W1-05 -k test_a_call_waits_under_100_ms_p95_for_the_hook -q -p no:cacheprovider -rs > "$LOG/rerun-W1-05.txt" 2>&1
echo $? > "$LOG/rerun-W1-05.exit"
python3 -m pytest tests/acceptance/W1-19 -k test_a_warm_query_answers_within_half_a_second_at_p95 -q -p no:cacheprovider -rs > "$LOG/rerun-W1-19.txt" 2>&1
echo $? > "$LOG/rerun-W1-19.exit"
for v in $(env | grep -oE '^CLAUDE[A-Z_]*=' | tr -d =); do unset "$v"; done
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -rs > "$LOG/rerun-W1-46-noclaude.txt" 2>&1
echo $? > "$LOG/rerun-W1-46-noclaude.exit"
echo done > "$LOG/reruns.done"
