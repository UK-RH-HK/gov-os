#!/usr/bin/env bash
# The three revised files whole, no -m/-k filter, through heavy_slot.sh.
set -u
T=/home/usain/gov-os-worktrees/W2-111
L=$T/.gov-runtime/scratch/lead
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
cd $T
cat /proc/loadavg
env TMPDIR=/tmp/w2-111-lead3-tmp PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  bash $HS python3 -m pytest tests/acceptance/W1-02/test_w1_02_guard_hook.py tests/acceptance/W1-05/test_w1_05_live_hooks.py tests/acceptance/W2-57/test_w2_57_designer_read_p95.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs --junitxml=$L/log/lead-files-3b.xml > $L/log/lead-files-3b.log 2>&1
echo "rc=$?"
cat /proc/loadavg
tail -25 $L/log/lead-files-3b.log
