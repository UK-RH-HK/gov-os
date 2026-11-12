#!/usr/bin/env bash
# Run 5 diagnostics, each in a heavy slot with an exit file:
# (a) W2-52's suite with CODEINTEL_OFF_PATH set empty beforehand (tests/conftest.py then takes no folder off PATH),
#     to show the reds are the code-graph tool's absence only;
# (b) the six W2-96 reds, alone, after the parallel run (load-sensitive candidates).
WT=/home/usain/gov-os-worktrees/W2-52
OUT=$WT/.gov-runtime/scratch/lead/runs3
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
cd "$WT" || exit 2
export TMPDIR=/tmp/gov-os-lead-W2-52
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src
COMMON="-q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed -rs"
CODEINTEL_OFF_PATH= bash "$SLOT" python3 -m pytest tests/acceptance/W2-52 -n 4 $COMMON --junitxml="$OUT/w252-onpath.xml" > "$OUT/w252-onpath.txt" 2>&1
echo $? > "$OUT/w252-onpath.exit"
bash "$SLOT" python3 -m pytest $COMMON --junitxml="$OUT/w296-alone.xml" \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  > "$OUT/w296-alone.txt" 2>&1
echo $? > "$OUT/w296-alone.exit"
echo done > "$OUT/diag5.exit"
