#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-155
B=/tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng/base
rm -rf $B; mkdir -p $B
git archive 25fc5f5c8 src tests/unit/retrieval tests/unit/semantic tests/conftest.py pyproject.toml conftest.py 2>/dev/null | tar -x -C $B
git archive 25fc5f5c8 | tar -x -C $B --wildcards 'conftest.py' 'tests/conftest.py' 'pyproject.toml' 2>/dev/null
T=/tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng
H=/home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/empty-home
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
OPTS=(-q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit")
echo "=== BASE test_w2_112"
(cd $B && env TMPDIR=$T PYTHONUSERBASE=/home/usain/.local HOME=$H PYTHONPATH=$B/src bash $SLOT python3 -m pytest tests/unit/retrieval/test_w2_112_shared_reranker.py "${OPTS[@]}" 2>&1 | tail -3)
echo "=== BRANCH edited + new + semantic fusion"
env TMPDIR=$T PYTHONUSERBASE=/home/usain/.local HOME=$H PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src bash $SLOT python3 -m pytest tests/unit/retrieval/test_w2_155_one_request.py tests/unit/retrieval/test_w2_137_request_cap.py tests/unit/retrieval/test_w2_32_whole_chunk.py tests/unit/retrieval/test_w2_13_rerank_work.py tests/unit/retrieval/test_w2_32_routing.py tests/unit/retrieval/test_w2_32_pool.py "${OPTS[@]}" 2>&1 | tail -5
echo "=== BRANCH semantic/test_fusion.py"
env TMPDIR=$T PYTHONUSERBASE=/home/usain/.local HOME=$H PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src bash $SLOT python3 -m pytest tests/unit/semantic/test_fusion.py "${OPTS[@]}" 2>&1 | tail -8
echo done
