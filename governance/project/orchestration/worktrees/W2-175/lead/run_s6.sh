#!/usr/bin/env bash
# S6: the ticket's own command over W2-128, W2-152, W2-153 with the common filters, through the heavy slot.
L=/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-175 || exit 2
mkdir -p /tmp/gov-os-lead-W2-175
env HOME=/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src TMPDIR=/tmp/gov-os-lead-W2-175 \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-128 tests/acceptance/W2-152 tests/acceptance/W2-153 -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/s6.xml > $L/s6.txt 2>&1
echo $? > $L/s6.exit
