#!/bin/bash
# The clone's store build by the pinned gov (DEC-877, DEC-939 item 2). Argument: the run label (rebuild-1, rebuild-2).
# Gates first (DEC-847, DEC-898, DEC-933): no close or nightly running, 1-minute load under 20, disk gate open.
# Outputs under the lead's scratch: <label>.json, <label>.err, <label>.time, <label>.exit, <label>.gate.
set -u
label="$1"
out=/home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs
orch=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd /home/usain/gov-os-runs/W2-61/repo || exit 90
while true; do
  until [ ! -e "$orch/CLOSE-RUNNING" ] && [ ! -e "$orch/NIGHTLY-RUNNING" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  if bash "$orch/tools/disk_gate.sh" > "$out/$label.gate" 2>&1; then
    [ ! -e "$orch/CLOSE-RUNNING" ] && [ ! -e "$orch/NIGHTLY-RUNNING" ] && break
  fi
  sleep 60
done
cat /proc/loadavg >> "$out/$label.gate"
date -u +%FT%TZ > "$out/$label.time"
env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json > "$out/$label.json" 2> "$out/$label.err"
code=$?
date -u +%FT%TZ >> "$out/$label.time"
echo "$code" > "$out/$label.exit"
