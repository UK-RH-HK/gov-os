#!/usr/bin/env bash
# The closing runs on head 3c2d88b5 (after the F1 fix): builder tests, W1-05's load-sensitive live-hook p95 case alone,
# then gov check. Each waits for both gates (no close in its quiet window, load below 20; the p95 case below 8).
W=/home/usain/gov-os-worktrees/W2-59
L=/home/usain/gov-os-worktrees/W2-59/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
S="$L/after3-summary.txt"
cd "$W" || exit 99
gate() { until [ ! -e "$F" ] && awk -v m="$2" '{exit !($1 < m)}' /proc/loadavg; do sleep 60; done
         echo "$1 start $(date -Is) load $(cut -d' ' -f1 /proc/loadavg)" >> "$S"; }
gate unit 20
PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$L/unit-3.txt" 2>&1
echo "unit rc=$? :: $(tail -1 "$L/unit-3.txt")" >> "$S"
gate w1-05-p95 8
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src \
  python3 -m pytest "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  -q -p no:cacheprovider -rs -rf > "$L/after3-w1-05-p95.txt" 2>&1
echo "w1-05-p95 rc=$? :: $(tail -1 "$L/after3-w1-05-p95.txt")" >> "$S"
gate check-5 20
PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main check --json > "$L/check-5.json" 2>&1
echo "check-5 rc=$? end $(date -Is)" >> "$S"
echo done > "$L/after3.exit"
