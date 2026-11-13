#!/usr/bin/env bash
# Find the test that hung lead_verify run 3a: candidate files changed since run 2's verify, sequential, per-test timeout.
cd /home/usain/gov-os-worktrees/W2-45
mkdir -p /tmp/gov-os-lead-W2-45/hang1
export TMPDIR=/tmp/gov-os-lead-W2-45/hang1
export PYTHONUSERBASE=/home/usain/.local
export HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -v -p no:cacheprovider -o tmp_path_retention_policy=failed -p no:xdist \
  --timeout=240 --timeout-method=thread -m "not local_only" -k "not real and not green_here and not time_limit" \
  tests/unit/retrieval/test_w2_146_id_forms.py tests/unit/retrieve/test_w2_146_stop.py \
  tests/unit/hooks/test_w2_176_context_watch.py tests/unit/hooks/test_w2_176_precompact.py \
  tests/unit/hooks/test_resume_hooks.py tests/unit/hooks/test_w29_hooks.py \
  tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/check tests/unit/ci/test_ci_command.py
echo "exit=$?"
