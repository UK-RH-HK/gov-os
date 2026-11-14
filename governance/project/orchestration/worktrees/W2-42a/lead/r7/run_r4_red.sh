#!/usr/bin/env bash
# The R4/R5 cases (td-10) on the tree's head, through a heavy slot: the failing output for the engineer.
TREE=/home/usain/gov-os-worktrees/W2-42a
LOG=$TREE/.gov-runtime/scratch/lead/log/r4-red.log
mkdir -p /tmp/w2-42a-lead/tmp "$TREE/.gov-runtime/scratch/empty-home"
cd "$TREE"
env HOME=$TREE/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-lead/tmp PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=$TREE/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py tests/acceptance/W2-42a/test_w2_42a_r5_error_path.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short -rf > "$LOG" 2>&1
echo $? > $TREE/.gov-runtime/scratch/lead/log/r4-red.exit
