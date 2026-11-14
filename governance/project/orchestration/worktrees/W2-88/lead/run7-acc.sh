#!/bin/bash
# The lead's run of the four run-7 acceptance modules, with the failing lines, through the heavy slot.
cd /home/usain/gov-os-worktrees/W2-88 || exit 9
L=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/run7-acc
mkdir -p /home/usain/gov-os-runs/W2-88/tmp-lead
env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=/home/usain/gov-os-runs/W2-88/tmp-lead \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-88/test_w2_88_p1_installed.py tests/acceptance/W2-88/test_w2_88_f1_codegraph.py \
  tests/acceptance/W2-88/test_w2_88_f3_ignored.py tests/acceptance/W2-88/test_w2_88_scan_speed.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
  -rfE --tb=short --junitxml="$L.xml" > "$L.txt" 2>&1
echo $? > "$L.exit"
