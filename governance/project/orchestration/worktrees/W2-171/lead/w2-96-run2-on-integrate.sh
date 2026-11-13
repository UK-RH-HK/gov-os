#!/usr/bin/env bash
# The six W2-96 reds on w2/integrate's head (the main tree, clean in src/ and tests/): shared-base evidence for run 3.
mkdir -p /tmp/W2-171-lead-tmp
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
echo "integrate head: $(git rev-parse HEAD)"
TMPDIR=/tmp/W2-171-lead-tmp PYTHONDONTWRITEBYTECODE=1 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m pytest \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" 2>&1 | tail -20
