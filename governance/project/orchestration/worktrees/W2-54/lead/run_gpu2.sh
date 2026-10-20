#!/bin/sh
# Round 4, the lead's real-model cases (DEC-798), neither address set: the two shared_gpu cases, then W1-21's hit@5.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
P=gpu4b
NODEPATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
place() {
  date +%T
  uptime
  echo "shared 11434:"; curl -s --noproxy '*' http://127.0.0.1:11434/api/ps; echo
  echo "cpu 11435:"; curl -s --noproxy '*' http://127.0.0.1:11435/api/ps; echo
  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
  ps -eo pid,rss,etime,args | grep -E "ollama (serve|runner)|llama-server" | grep -v grep | cut -c1-160
}
place > "$LOG/$P-place-before.txt" 2>&1
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST "PATH=$NODEPATH" PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 -m pytest tests/acceptance/W2-54/test_w2_54_shared_gpu.py -m shared_gpu -s -q -p no:cacheprovider -rs \
  > "$LOG/$P-shared-gpu.txt" 2>&1
echo $? > "$LOG/$P-shared-gpu.exit"
place > "$LOG/$P-place-mid.txt" 2>&1
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST "PATH=$NODEPATH" PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 -m pytest "tests/acceptance/W1-21/test_w1_21_dev_tier.py::test_the_dev_query_set_meets_the_hit_at_5_pass_line" \
  -q -p no:cacheprovider -rs > "$LOG/$P-w1-21-hit5.txt" 2>&1
echo $? > "$LOG/$P-w1-21-hit5.exit"
place > "$LOG/$P-place-after.txt" 2>&1
echo done > "$LOG/$P.done"
