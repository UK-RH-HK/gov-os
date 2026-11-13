cd /home/usain/gov-os-worktrees/W2-172
TMPDIR=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/tmp-lead bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
 "tests/unit/resources/test_w2_157_backstop.py::test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item" \
 "tests/unit/resources/test_w2_157_backstop.py::test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on" \
 "tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request" 2>&1 | tail -5
