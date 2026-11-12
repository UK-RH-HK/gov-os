#!/bin/bash
# Base check (resume 2): W2-105's install-block cases on w2/integrate's own code, in a throwaway worktree.
B=/tmp/gov-os-lead-W2-110/base-int
L=/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/verify-4
cd /tmp/gov-os-lead-W2-110/base-int || exit 9
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-110 PYTHONPATH=/tmp/gov-os-lead-W2-110/base-int/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-105/test_w2_105_install_block.py -n 4 -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/verify-4/base-int-w2105.xml \
  > /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/verify-4/base-int-w2105.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/verify-4/base-int-w2105.exit
