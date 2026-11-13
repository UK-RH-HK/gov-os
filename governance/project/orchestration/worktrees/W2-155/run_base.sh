#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-155
B=/tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng/base
rm -rf $B; mkdir -p $B
git archive 25fc5f5c8 src tests/unit/retrieval pyproject.toml | tar -x -C $B || exit 9
T=/tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng
H=/home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/empty-home
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
cd $B && env TMPDIR=$T PYTHONUSERBASE=/home/usain/.local HOME=$H PYTHONPATH=$B/src bash $SLOT python3 -m pytest tests/unit/retrieval/test_w2_112_shared_reranker.py tests/unit/retrieval/test_w2_13_rerank_work.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" 2>&1 | grep -E "^FAILED|passed|failed" | sed 's/ - .*//'
