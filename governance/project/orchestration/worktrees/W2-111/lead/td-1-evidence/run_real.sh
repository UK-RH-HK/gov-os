#!/usr/bin/env bash
# usage: run_real.sh <label> [extra pytest args / plugin env]   -- the 15 cases on the real hook, through the heavy slot
LABEL=$1; shift
W=/home/usain/gov-os-worktrees/W2-111-tests
LOG=$W/.gov-runtime/scratch/td/real-$LABEL.log; export TD_FIGURES=$W/.gov-runtime/scratch/td/real-$LABEL.figs; rm -f $TD_FIGURES
mkdir -p "$TMPDIR/w2-111-td" "$W/.gov-runtime/scratch/empty-home"
{
echo "== $LABEL start $(date -Is) load: $(cat /proc/loadavg)"
cd $W
env TMPDIR=$TMPDIR/w2-111-td PYTHONUSERBASE=/home/usain/.local HOME=$W/.gov-runtime/scratch/empty-home PYTHONPATH=$W/src:$W/.gov-runtime/scratch/td TD_FIGURES=$TD_FIGURES \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest \
  "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" \
  "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  "tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95" \
  -q -p td_plugin -p no:cacheprovider -o tmp_path_retention_policy=failed "$@"
echo "== $LABEL exit $? end $(date -Is) load: $(cat /proc/loadavg)"
} > $LOG 2>&1
tail -30 $LOG
