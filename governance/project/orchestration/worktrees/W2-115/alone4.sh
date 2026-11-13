#!/usr/bin/env bash
# run 4: this head's non-W2-96 reds alone, once; the W2-153 two also on w2/integrate's head (a detached worktree)
export HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
export TMPDIR=/tmp/gov-os-lead-W2-115-alone4
mkdir -p "$TMPDIR"
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
T=/home/usain/gov-os-worktrees/W2-115
B=/home/usain/gov-os-worktrees/W2-115-base
cd "$T" || exit 2
echo "##### $T $(git -C $T rev-parse --short=12 HEAD)"
PYTHONPATH=$T/src bash $SLOT python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/acceptance/W2-115/test_w2_115_batch.py" \
  "tests/acceptance/W2-115/test_w2_115_reds.py" \
  "tests/unit/adapters/test_w2_153_compose.py" \
  "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | cut -c1-300
echo "exit ${PIPESTATUS[0]}"
git -C $T worktree add --detach $B w2/integrate >/dev/null 2>&1
cd "$B" || exit 2
echo "##### $B $(git -C $B rev-parse --short=12 HEAD)"
PYTHONPATH=$B/src bash $SLOT python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/adapters/test_w2_153_compose.py" \
  "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | cut -c1-300
echo "exit ${PIPESTATUS[0]}"
cd "$T"
git -C $T worktree remove --force $B
echo done
