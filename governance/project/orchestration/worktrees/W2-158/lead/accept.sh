#!/usr/bin/env bash
# gov accept for W2-158, outside the sandbox, through the heavy slot (tests run inside it).
mkdir -p /tmp/w2-158-lead/home
cd /home/usain/gov-os-worktrees/W2-158 || exit 2
env TMPDIR=/tmp/w2-158-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m gov.cli.main accept W2-158 --root /home/usain/gov-os-worktrees/W2-158
