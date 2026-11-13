#!/usr/bin/env bash
# Run 5: W2-171's own F5 path case and W2-170's F5 path case at the new head.
mkdir -p /home/usain/.cache/w2-171-tmp-run5 /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-171 || exit 2
git rev-parse --short=12 HEAD
env TMPDIR=/home/usain/.cache/w2-171-tmp-run5 PYTHONUSERBASE=/home/usain/.local \
  HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-171/test_w2_171_f5_paths.py tests/acceptance/W2-170/test_w2_170_f5_paths.py \
  -v -p no:cacheprovider -o tmp_path_retention_policy=failed \
  --junitxml=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/lead/log/f5-run5.xml
echo "exit=$?"
