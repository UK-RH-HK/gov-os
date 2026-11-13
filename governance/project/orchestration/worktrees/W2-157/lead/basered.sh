#!/usr/bin/env bash
# The base-red check: W2-153's two composition cases at the merged integrate head 5d915dc6c, in a temporary detached worktree.
set -u
T=/tmp/w2-157-basered-tree
OUT=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/basered.txt
git -C /home/usain/gov-os-worktrees/W2-157 worktree add --detach "$T" 5d915dc6c > /dev/null 2>&1 || { echo "worktree add failed" > "$OUT"; exit 2; }
mkdir -p /tmp/w2-157-lead /tmp/w2-157-basered-home
cd "$T" || exit 2
env TMPDIR=/tmp/w2-157-lead HOME=/tmp/w2-157-basered-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition" \
  "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed > "$OUT" 2>&1
echo "exit $? at $(git rev-parse --short=12 HEAD)" >> "$OUT"
cd /home/usain/gov-os-worktrees/W2-157 || exit 2
git -C /home/usain/gov-os-worktrees/W2-157 worktree remove --force "$T"
