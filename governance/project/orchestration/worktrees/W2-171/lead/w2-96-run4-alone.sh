#!/usr/bin/env bash
# Run 4: the six W2-96 reds of lead_verify re-run alone once on this branch (load-sensitive signal cases).
mkdir -p /tmp/W2-171-lead4
cd /home/usain/gov-os-worktrees/W2-171 || exit 2
echo "branch head: $(git rev-parse HEAD)"
TMPDIR=/tmp/W2-171-lead4 PYTHONDONTWRITEBYTECODE=1 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" 2>&1 | tail -12
