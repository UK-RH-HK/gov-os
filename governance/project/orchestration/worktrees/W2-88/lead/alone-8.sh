#!/bin/bash
# The lead's re-run alone, once, of the two load-sensitive reds of verify-7 (DEC: a load-sensitive case re-run alone once).
cd /home/usain/gov-os-worktrees/W2-88 || exit 9
L=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/alone-8
mkdir -p /home/usain/gov-os-runs/W2-88/tmp-lead
env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=/home/usain/gov-os-runs/W2-88/tmp-lead \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=short --junitxml="$L-reranker.xml" > "$L-reranker.txt" 2>&1
echo $? > "$L-reranker.exit"
env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=/home/usain/gov-os-runs/W2-88/tmp-lead \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/acceptance/W2-88/test_w2_88_f1_codegraph.py::test_s25_real_redis_copy_a9_is_ok_or_names_the_cause" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=short --junitxml="$L-redis.xml" > "$L-redis.txt" 2>&1
echo $? > "$L-redis.exit"
