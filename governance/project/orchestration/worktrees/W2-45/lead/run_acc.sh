#!/usr/bin/env bash
# Lead: the W2-45 acceptance suite and the older suites that touch the runner, at the tree's head.
cd /home/usain/gov-os-worktrees/W2-45 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/lead/log
env TMPDIR=/tmp/gov-os-lead-W2-45 PYTHONUSERBASE=/home/usain/.local \
  HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "$@" -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" -n auto
