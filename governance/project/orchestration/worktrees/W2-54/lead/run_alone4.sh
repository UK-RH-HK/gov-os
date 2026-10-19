#!/bin/sh
# Round 4: the load-sensitive cases that failed in the full run, each alone (DEC-372, DEC-760, DEC-762).
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
uptime > "$LOG/alone4.load"
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider -rs -k test_a_warm_query_answers_within_half_a_second_at_p95 > "$LOG/alone4-W1-19.txt" 2>&1
echo $? > "$LOG/alone4-W1-19.exit"
uptime >> "$LOG/alone4.load"
python3 -m pytest tests/acceptance/W1-05 -q -p no:cacheprovider -rs -k test_a_call_waits_under_100_ms_p95_for_the_hook > "$LOG/alone4-W1-05.txt" 2>&1
echo $? > "$LOG/alone4-W1-05.exit"
uptime >> "$LOG/alone4.load"
echo done > "$LOG/alone4.done"
