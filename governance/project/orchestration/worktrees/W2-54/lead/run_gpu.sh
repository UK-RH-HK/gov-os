#!/bin/sh
# Round 4, the lead's measurement on the shared GPU (DEC-798): placement before, eng5-measure.py, the shared_gpu cases,
# W1-21's hit@5 on the real models, placement after. Neither address set. Logs under the lead's log folder.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
P=gpu4
place() {
  date +%T
  uptime
  echo "shared 11434:"; curl -s --noproxy '*' http://127.0.0.1:11434/api/ps; echo
  echo "cpu 11435:"; curl -s --noproxy '*' http://127.0.0.1:11435/api/ps; echo
  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
  ps -eo pid,rss,etime,args | grep -E "ollama (serve|runner)|llama-server" | grep -v grep | cut -c1-160
}
# The shared runner loaded the default way (a request with no option), as any client would.
curl -s --noproxy '*' -o /dev/null -w 'load %{http_code} %{time_total}s\n' http://127.0.0.1:11434/api/embed \
  -d '{"model":"qwen3-embedding:0.6b","input":["load"]}' > "$LOG/$P-place-before.txt" 2>&1
place >> "$LOG/$P-place-before.txt" 2>&1
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/eng5-measure.py > "$LOG/$P-measure.txt" 2>&1
echo $? > "$LOG/$P-measure.exit"
place > "$LOG/$P-place-mid.txt" 2>&1
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_shared_gpu.py \
  -m shared_gpu -s -q -p no:cacheprovider -rs > "$LOG/$P-shared-gpu.txt" 2>&1
echo $? > "$LOG/$P-shared-gpu.exit"
env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest \
  "tests/acceptance/W1-21/test_w1_21_dev_tier.py::test_the_dev_query_set_meets_the_hit_at_5_pass_line" \
  -q -p no:cacheprovider -rs > "$LOG/$P-w1-21-hit5.txt" 2>&1
echo $? > "$LOG/$P-w1-21-hit5.exit"
place > "$LOG/$P-place-after.txt" 2>&1
echo done > "$LOG/$P.done"
