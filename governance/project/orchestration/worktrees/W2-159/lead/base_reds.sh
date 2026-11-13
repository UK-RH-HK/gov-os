#!/usr/bin/env bash
# Runs the 11 reds that are not this ticket's on the base tree (w2/integrate's head) and on the ticket's tree, the same way.
T=(
"tests/acceptance/W2-96/test_w2_96_at_no_leak.py::test_an_interrupted_run_stops_its_child_and_leaves_nothing"
"tests/acceptance/W2-96/test_w2_96_at_run_2.py::test_r9_a_ctrl_c_during_the_clean_up_is_held_back_until_the_clean_up_ends"
"tests/acceptance/W2-96/test_w2_96_at_run_2.py::test_r12_a_signal_that_ends_the_run_ends_gov_by_an_ordinary_exit_with_128_plus_the_signal"
"tests/acceptance/W2-96/test_w2_96_at_run_2.py::test_premise_r11_a_process_started_this_way_begins_with_the_signal_ignored"
"tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal"
"tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up"
"tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back"
"tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up"
"tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it"
"tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it"
"tests/unit/orchestration/test_w2_149_setup_a.py::test_labeller_two_round_one_half_only_round_two_the_overlap_by_rule"
)
mkdir -p /tmp/w2-159-lead
for tree in /home/usain/gov-os-worktrees/W2-159-base /home/usain/gov-os-worktrees/W2-159; do
  echo "=== $tree $(git -C $tree rev-parse --short=12 HEAD)"
  cd "$tree" || exit 2
  env TMPDIR=/tmp/w2-159-lead HOME=$tree/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$tree/src \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest "${T[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -n 4 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | sed 's/ - .*//' | tail -20
done
