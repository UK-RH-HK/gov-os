#!/usr/bin/env bash
# The other four scoped-run reds, alone, normal HOME, this tree.
T=/home/usain/gov-os-worktrees/W2-05
L=$T/.gov-runtime/scratch/lead/log
cd "$T" || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$T/src \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml="$L/reds-alone-2.xml" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  > "$L/reds-alone-2.txt" 2>&1
echo "exit $?"
tail -3 "$L/reds-alone-2.txt"
