mkdir -p /tmp/gov-os-lead-W2-116-rerun
cd /home/usain/gov-os-worktrees/W2-116
env TMPDIR=/tmp/gov-os-lead-W2-116-rerun PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/orchestration/test_w2_97_merge_queue.py::test_a_conflict_is_ejected_and_the_rest_go_on" \
  "tests/unit/orchestration/test_w2_97_merge_queue.py::test_a_head_that_moves_under_test_gets_a_new_merge_and_a_new_run" 2>&1 | tail -8
