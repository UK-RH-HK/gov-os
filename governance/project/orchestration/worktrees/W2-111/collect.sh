#!/usr/bin/env bash
# Collect-only on the three latency files (the lead's interface check).
mkdir -p /home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/empty-home /home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/lead/briefs /home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/lead/log /tmp/w2-111-lead-tmp
cd /home/usain/gov-os-worktrees/W2-111
env TMPDIR=/tmp/w2-111-lead-tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-111/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q --collect-only -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" \
  "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  "tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95"
