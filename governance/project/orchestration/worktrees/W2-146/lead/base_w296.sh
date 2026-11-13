cd /home/usain/gov-os-worktrees/W2-146 || exit 2
B=/tmp/gov-os-lead-W2-146-base
rm -rf "$B" && mkdir -p "$B/tree" "$B/tmp" || exit 2
head=$(git rev-parse w2/integrate)
echo "w2/integrate head $head"
git archive "$head" src tests pyproject.toml | tar -x -C "$B/tree" || exit 2
cd "$B/tree" || exit 2
uptime
env TMPDIR="$B/tmp" PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/empty-home PYTHONPATH="$B/tree/src" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" 2>&1 | tail -8
echo "exit ${PIPESTATUS[0]}"
