#!/bin/bash
# The serial phase's reds re-run alone, one after another, each through the gate (DEC-757/762 load_sensitive; DEC-1038 (4)).
# The same environment as the close's serial phase, with this tree's code (DEC-732); the real PATH (no shim).
cd /home/usain/gov-os-worktrees/W2-112 || exit 99
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src:/home/usain/gov-os-worktrees/W2-112/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-112
export TMPDIR=/tmp/gov-os-lead-W2-112
L=/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/log
G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
T1=tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95
T2=tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written
T3=tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95
T4=tests/acceptance/W1-46/test_w1_46_live_sessions.py
/usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader > $L/rerun-3.log 2>&1
for T in $T1 $T2 $T3 $T4; do
  echo "=== $T" >> $L/rerun-3.log
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$T" bash $G python3 -m pytest "$T" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs >> $L/rerun-3.log 2>&1
  echo "exit $?" >> $L/rerun-3.log
  /usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader >> $L/rerun-3.log 2>&1
done
echo done > $L/rerun-3.exit
