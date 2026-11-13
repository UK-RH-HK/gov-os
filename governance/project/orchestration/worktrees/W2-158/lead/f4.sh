#!/usr/bin/env bash
mkdir -p /tmp/w2-158-lead/home
cd /home/usain/gov-os-worktrees/W2-158 || exit 2
env HOME=/tmp/w2-158-lead/home TMPDIR=/tmp/w2-158-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-158/test_w2_158_nothing_else.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed
