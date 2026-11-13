#!/bin/bash
# One run of the W2-177 cases in whatever start form the caller gave this shell (run_forms.sh); HOME from the caller.
set -u
TREE=/home/usain/gov-os-worktrees/W2-177
cd "$TREE" || exit 2
export PYTHONPATH=$TREE/src PYTHONUSERBASE=/home/usain/.local
python3 -c 'import signal; print("SIGINT-ignored-at-start:", int(signal.getsignal(signal.SIGINT) == signal.SIG_IGN))'
CASES=(
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]"
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]"
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]"
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it"
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]"
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]"
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r11_an_inherited_ignore_is_kept"
)
for f in tests/unit/accept/test_w2_177*.py; do [ -e "$f" ] && CASES+=("$f"); done
# every run inside a heavy slot (the CTO, 2026-11-12, incident T1 0556): a job in a slot holds no lead's admission
exec bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "${CASES[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed
