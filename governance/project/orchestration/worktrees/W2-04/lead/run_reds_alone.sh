#!/usr/bin/env bash
# The scoped run's 6 reds (W2-96 signal cases, tests/unit/accept) re-run alone once, one process, no xdist
# (lead, DAEO-u4oz review run). Logs this shell's ignored-signal mask first: lead_verify.sh starts its run with
# `setsid ... &`, which leaves SIGINT ignored for every child.
L=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log
rm -f "$L/reds-alone.exit"
grep SigIgn /proc/$$/status > "$L/reds-alone.txt"
cd /home/usain/gov-os-worktrees/W2-04 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-04 \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  --junitxml="$L/reds-alone.xml" >> "$L/reds-alone.txt" 2>&1
echo $? > "$L/reds-alone.exit"
