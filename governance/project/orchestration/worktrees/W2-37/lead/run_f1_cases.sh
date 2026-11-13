#!/usr/bin/env bash
# The W2-37 acceptance suite and unit/impact at the merged head, with the code-graph tool on PATH (CODEINTEL_OFF_PATH empty).
set -u
mkdir -p /tmp/gov-os-w237-lead4
cd /home/usain/gov-os-worktrees/W2-37 || exit 2
env CODEINTEL_OFF_PATH= TMPDIR=/tmp/gov-os-w237-lead4 PYTHONUSERBASE=/home/usain/.local \
  PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-37 tests/unit/impact -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs \
  --junitxml=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/acc-cbm-4.xml \
  > /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/acc-cbm-4.txt 2>&1
echo "rc $?"
tail -8 /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/acc-cbm-4.txt
