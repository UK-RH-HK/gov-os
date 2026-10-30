#!/bin/bash
# After engineer batch 1: W2-05 alone, then W1-02's three deadline files, outside the sandbox, gated.
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
bash /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/run_w205.sh b1-W2-05
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
date > "$LOG/b1-W1-02.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W1-02/test_w1_02_deadline.py tests/acceptance/W1-02/test_w1_02_deadline_in_time.py tests/acceptance/W1-02/test_w1_02_unknown_tools_failure.py -q -p no:cacheprovider -rs > "$LOG/b1-W1-02.txt" 2>&1
echo $? > "$LOG/b1-W1-02.exit"
date >> "$LOG/b1-W1-02.start"
