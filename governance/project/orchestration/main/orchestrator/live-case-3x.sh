#!/bin/bash
# DEC-671: the W1-49 live-session file three times on its own, one run after another.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
for n in 1 2 3; do
  env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-49/test_w1_49_live_session.py -q -p no:cacheprovider --tb=line --no-header > "$L/live-case-dec671-$n.txt" 2>&1
  echo "run $n: exit $?: $(tail -1 "$L/live-case-dec671-$n.txt") [load $(cut -d' ' -f1 /proc/loadavg)]"
done
