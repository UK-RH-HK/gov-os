#!/bin/bash
# Lead's latency re-runs (DEC-372): each latency file alone, after the other suites have ended.
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log/latency
mkdir -p "$OUT"
uptime > "$OUT/uptime-start.txt"
for f in tests/acceptance/W1-02/test_w1_02_guard_hook.py tests/acceptance/W1-05/test_w1_05_live_hooks.py tests/acceptance/W1-19/test_w1_19_real_models.py; do
  b=$(basename "$f" .py)
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 2400 python3 -m pytest "$f" -q -p no:cacheprovider -rs > "$OUT/$b.txt" 2>&1
  echo $? > "$OUT/$b.exit"
done
echo done > "$OUT/all.done"
