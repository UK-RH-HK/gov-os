#!/usr/bin/env bash
# gov accept W2-42a on the tree's head (through a heavy slot); log and exit file named by $1.
TREE=/home/usain/gov-os-worktrees/W2-42a
L=$TREE/.gov-runtime/scratch/lead/log
mkdir -p /tmp/w242a-lead/tmp
cd "$TREE"
git rev-parse HEAD > $L/gacc-$1.head
env TMPDIR=/tmp/w242a-lead/tmp PYTHONUSERBASE=/home/usain/.local \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-42a --root /home/usain/gov-os-worktrees/W2-42a > $L/gacc-$1.log 2>&1
echo $? > $L/gacc-$1.exit
