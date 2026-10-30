#!/bin/bash
# Re-run the serial phase's three latency reds alone, after the suites ended (brief: a pass alone counts).
# Gates: no close or nightly, 1-minute load under 20, disk gate; then under the verify lock. Argument: a label.
set -u
label="$1"
log=/home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/log
orch=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd /home/usain/gov-os-worktrees/W2-61 || exit 90
while true; do
  until [ ! -e "$orch/CLOSE-RUNNING" ] && [ ! -e "$orch/NIGHTLY-RUNNING" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  bash "$orch/tools/disk_gate.sh" > /dev/null 2>&1 && break
  sleep 60
done
date -u +%FT%TZ > "$log/$label.time"
cat /proc/loadavg >> "$log/$label.time"
TMPDIR=/tmp/gov-os-lead-W2-61 PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src flock /tmp/gov-os-verify.lock \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs \
  "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  tests/acceptance/W2-57/test_w2_57_designer_read_p95.py \
  --junitxml="$log/$label.xml" > "$log/$label.txt" 2>&1
echo $? > "$log/$label.exit"
date -u +%FT%TZ >> "$log/$label.time"
cat /proc/loadavg >> "$log/$label.time"
