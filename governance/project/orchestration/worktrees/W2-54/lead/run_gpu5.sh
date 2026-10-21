#!/bin/sh
# Round 4c, the lead's real-model cases (DEC-798), neither address set: the two shared_gpu cases, then W1-21's hit@5.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
L=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead
LOG=$L/log
P=gpu5
NODEPATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
git log --oneline -1 > "$LOG/$P-head.txt"
sh $L/run_place.sh "$LOG/$P-place-before.txt"
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST "PATH=$NODEPATH" PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 -m pytest tests/acceptance/W2-54/test_w2_54_shared_gpu.py -m shared_gpu -s -q -p no:cacheprovider -rs \
  > "$LOG/$P-shared-gpu.txt" 2>&1
echo $? > "$LOG/$P-shared-gpu.exit"
sh $L/run_place.sh "$LOG/$P-place-mid.txt"
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST "PATH=$NODEPATH" PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 -m pytest "tests/acceptance/W1-21/test_w1_21_dev_tier.py::test_the_dev_query_set_meets_the_hit_at_5_pass_line" \
  -s -q -p no:cacheprovider -rs > "$LOG/$P-w1-21-hit5.txt" 2>&1
echo $? > "$LOG/$P-w1-21-hit5.exit"
sh $L/run_place.sh "$LOG/$P-place-after.txt"
echo done > "$LOG/$P.done"
