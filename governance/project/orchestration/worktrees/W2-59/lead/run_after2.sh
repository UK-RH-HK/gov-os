#!/usr/bin/env bash
# gov check again (check-3 was stopped by the background limit), then W1-05's live-hook p95 case alone at low load.
W=/home/usain/gov-os-worktrees/W2-59
L=/home/usain/gov-os-worktrees/W2-59/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
cd "$W" || exit 99
until [ ! -e "$F" ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
echo "check-4 start $(date -Is) load $(cut -d' ' -f1 /proc/loadavg)" >> "$L/after-summary.txt"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main check --json > "$L/check-4.json" 2>&1
echo "check-4 rc=$? end $(date -Is)" >> "$L/after-summary.txt"
for i in $(seq 1 60); do [ ! -e "$F" ] && awk '{exit !($1 < 8)}' /proc/loadavg && break; sleep 60; done
until [ ! -e "$F" ]; do sleep 60; done
echo "w1-05-p95-b start $(date -Is) load $(cut -d' ' -f1 /proc/loadavg)" >> "$L/after-summary.txt"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src \
  python3 -m pytest "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  -q -p no:cacheprovider -rs -rf > "$L/after-w1-05-p95-b.txt" 2>&1
echo "w1-05-p95-b rc=$? :: $(tail -1 "$L/after-w1-05-p95-b.txt")" >> "$L/after-summary.txt"
echo done > "$L/after2.exit"
