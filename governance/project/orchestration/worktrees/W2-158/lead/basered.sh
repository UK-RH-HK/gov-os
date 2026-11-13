#!/usr/bin/env bash
# The six W2-96 signal reds of lead_verify: alone on this head, then on w2/integrate's head (base-red rule).
set -u
T=/home/usain/gov-os-worktrees/W2-158
LOG=$T/.gov-runtime/scratch/lead/log
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
CASES=(
 "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal"
 "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it"
)
mkdir -p /tmp/w2-158-lead /tmp/w2-158-lead/home
run() {  # <tree> <label>
  ( cd "$1" && env HOME=/tmp/w2-158-lead/home TMPDIR=/tmp/w2-158-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$1/src" \
      bash "$SLOT" python3 -m pytest "${CASES[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      --junitxml="$LOG/basered-$2.xml" ) > "$LOG/basered-$2.txt" 2>&1
  echo "$2 exit $? : $(tail -1 "$LOG/basered-$2.txt")"
}
run "$T" head
B=/tmp/w2-158-lead/integrate
rm -rf "$B"
git clone -q --shared --no-checkout "$T" "$B" && git -C "$B" checkout -q --detach "$(git -C "$T" rev-parse w2/integrate)"
echo "integrate head $(git -C "$B" rev-parse --short=12 HEAD)"
run "$B" integrate
rm -rf "$B"
