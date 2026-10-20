#!/bin/sh
# Round 4c: the load-sensitive cases that failed in the full run, each alone (DEC-372, DEC-760, DEC-762).
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
uptime > "$LOG/alone5.load"
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider -rs -k test_a_warm_query_answers_within_half_a_second_at_p95 > "$LOG/alone5-W1-19.txt" 2>&1
echo $? > "$LOG/alone5-W1-19.exit"
uptime >> "$LOG/alone5.load"
python3 -m pytest tests/acceptance/W1-46/test_w1_46_live_sessions.py -q -p no:cacheprovider -rs > "$LOG/alone5-W1-46.txt" 2>&1
echo $? > "$LOG/alone5-W1-46.exit"
uptime >> "$LOG/alone5.load"
sh /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/run_place.sh "$LOG/alone5-place-after.txt"
echo done > "$LOG/alone5.done"
