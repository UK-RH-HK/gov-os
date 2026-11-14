#!/usr/bin/env bash
# The six W2-33 copy_folder reds of the scoped run, on the merged base d9e7dc859 (the tests worktree, detached), and
# lead_verify's one retrieval red alone on the head, each through a heavy slot.
L=/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log
B=/home/usain/gov-os-worktrees/W2-42a-tests
mkdir -p /tmp/w2-42a-lead/tmp /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/empty-home
git -C "$B" checkout -q --detach d9e7dc8599bec803e11c672586a379372663e6e0 || exit 9
git -C "$B" rev-parse HEAD > $L/r4-base-reds.head
cd "$B"
env HOME=/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-lead/tmp \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$B/src GOV_TESTS_OPTIN=lifted,breadth \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py tests/acceptance/W1-28/test_w1_28_fixture_copies.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" \
  -k "copy_folder and not real and not green_here and not time_limit" > $L/r4-base-reds.log 2>&1
echo $? > $L/r4-base-reds.rc
git -C "$B" checkout -q w2/W2-42a-tests
cd /home/usain/gov-os-worktrees/W2-42a
env HOME=/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-lead/tmp \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $L/r4-rerank-alone.log 2>&1
echo $? > $L/r4-rerank-alone.rc
