set -u
B=/home/usain/gov-os-worktrees/W2-172-basecheck
git -C /home/usain/gov-os-worktrees/W2-172 worktree add --detach "$B" 80da3fbcc >/dev/null 2>&1 || exit 9
cd "$B"
TMPDIR=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/tmp-lead bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$B/src" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
 "tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request" 2>&1 | tail -25
cd /home/usain/gov-os-worktrees/W2-172
git worktree remove --force "$B"
