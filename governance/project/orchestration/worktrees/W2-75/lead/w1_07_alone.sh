#!/usr/bin/env bash
# W1-07's latency case alone, after the nightly, at a quiet load, under the machine-wide lock (and quiet again
# once the lock is held). Output: log/verify/w1-07-alone2.*
WT=/home/usain/gov-os-worktrees/W2-75
V=$WT/.gov-runtime/scratch/lead/log/verify
NIGHT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
cd "$WT" || exit 9
until [ ! -e "$NIGHT" ] && [ ! -e "$CLOSE" ] && awk '{exit !($1 < 10)}' /proc/loadavg; do sleep 60; done
TMPDIR=/tmp/gov-os-lead-W2-75 PYTHONPATH=$WT/src flock /tmp/gov-os-verify.lock bash -c '
  until awk "{exit !(\$1 < 10)}" /proc/loadavg; do sleep 30; done
  { date; cat /proc/loadavg; } > "$1/w1-07-alone2.start"
  python3 -m pytest "tests/acceptance/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms" -q \
    -p no:cacheprovider -o tmp_path_retention_policy=failed > "$1/w1-07-alone2.log" 2>&1
  echo $? > "$1/w1-07-alone2.code"' _ "$V"
{ cat "$V/w1-07-alone2.code"; cat /proc/loadavg; date; } > "$V/w1-07-alone2.exit"
