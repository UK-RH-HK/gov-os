#!/usr/bin/env bash
# The W2-88 acceptance folder with a JUnit report, to name gov accept's three reds at a5144a3ec (accept-9).
mkdir -p /tmp/w2-88-lead-junit
cd /home/usain/gov-os-worktrees/W2-88 || exit 2
env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-88-lead-junit \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-88 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  --junitxml=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/acc-junit-9.xml \
  > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/acc-junit-9.txt 2>&1
rc=$?
echo "$rc" > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/acc-junit-9.exit
exit "$rc"
