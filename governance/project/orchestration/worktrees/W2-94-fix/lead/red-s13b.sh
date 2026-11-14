#!/usr/bin/env bash
# the one lead_verify red at 900035fdd, re-run alone once (load-sensitive check)
cd /home/usain/gov-os-worktrees/W2-94-fix || exit 2
mkdir -p /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/empty-home
env HOME=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src TMPDIR=/home/usain/.cache/gov-tmp-w2-94 \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/acceptance/W2-94/test_w2_94_fix_flow.py::test_s9_a_result_of_a_wrong_form_is_20_nothing_delivered_and_the_action_null" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short \
  --junitxml=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-s13b.xml
echo "rc=$?"
