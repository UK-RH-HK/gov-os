#!/usr/bin/env bash
# The acceptance suite of W2-42a on the tree's head, through a heavy slot.
TREE=/home/usain/gov-os-worktrees/W2-42a
LOG=$TREE/.gov-runtime/scratch/lead/log/accept-$1.log
mkdir -p /tmp/w2-42a-lead/tmp "$TREE/.gov-runtime/scratch/empty-home"
cd "$TREE"
env HOME=$TREE/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-lead/tmp PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=$TREE/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-42a -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$TREE/.gov-runtime/scratch/lead/log/accept-$1.xml > "$LOG" 2>&1
echo $? > $TREE/.gov-runtime/scratch/lead/log/accept-$1.exit
