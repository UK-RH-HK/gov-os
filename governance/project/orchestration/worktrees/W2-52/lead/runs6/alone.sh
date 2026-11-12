#!/usr/bin/env bash
# Run 6: (1) the 8 signal/timing reds alone; (2) the 2 PATH reds, run from this worktree and from a symlink whose
# path has no "W2-52" part (no copy: a link to this worktree), to show the worktree's folder name is the cause.
WT=/home/usain/gov-os-worktrees/W2-52
OUT=$WT/.gov-runtime/scratch/lead/runs6
export TMPDIR=/tmp/gov-os-lead-W2-52
cd "$WT" || exit 2
PYTHONPATH=$WT/src python3 -m pytest -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed \
  "tests/acceptance/W2-56/test_w2_56_endings.py::test_s12_an_ending_signal_to_the_launcher_reaches_the_sessions_process_group[SIGINT]" \
  "tests/acceptance/W2-56/test_w2_56_endings.py::test_s12_the_temp_folder_is_removed_when_the_launcher_is_signalled[SIGINT]" \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  --junitxml=$OUT/alone-signal.xml > $OUT/alone-signal.log 2>&1
echo $? > $OUT/alone-signal.exit
PYTHONPATH=$WT/src python3 -m pytest -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed \
  "tests/acceptance/W2-56/test_w2_56_suite_daemon.py::test_s1_the_code_graph_tool_is_off_path_in_a_suite_other_than_w1_16_and_w1_20" \
  "tests/unit/codeintel/test_codeintel.py::test_the_running_suite_has_a_folder_of_its_own_and_no_code_graph_tool_on_path" \
  > $OUT/alone-path-here.log 2>&1
echo $? > $OUT/alone-path-here.exit
ln -sfn /home/usain/gov-os-worktrees/W2-52 /tmp/gov-os-lead-W2-52/wt52link
L=/tmp/gov-os-lead-W2-52/wt52link
PYTHONPATH=$L/src python3 -m pytest -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed --rootdir=$L \
  "$L/tests/acceptance/W2-56/test_w2_56_suite_daemon.py::test_s1_the_code_graph_tool_is_off_path_in_a_suite_other_than_w1_16_and_w1_20" \
  "$L/tests/unit/codeintel/test_codeintel.py::test_the_running_suite_has_a_folder_of_its_own_and_no_code_graph_tool_on_path" \
  > $OUT/alone-path-link.log 2>&1
echo $? > $OUT/alone-path-link.exit
rm -f /tmp/gov-os-lead-W2-52/wt52link
echo done > $OUT/alone.done
