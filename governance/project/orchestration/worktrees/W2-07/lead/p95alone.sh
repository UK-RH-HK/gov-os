#!/usr/bin/env bash
# W1-02's p95 case alone, once the 1-minute load is below 20 (the serial run's one red).
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; } > "$L/p95-alone.txt"
TMPDIR=/tmp/gov-os-lead-W2-07 PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src \
  python3 -m pytest "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" -q -p no:cacheprovider -rs \
  >> "$L/p95-alone.txt" 2>&1; echo $? > "$L/p95-alone.exit"
cat /proc/loadavg >> "$L/p95-alone.txt"
