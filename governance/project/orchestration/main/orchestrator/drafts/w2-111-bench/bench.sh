#!/usr/bin/env bash
# W2-111 S2/S3: the CTO's benchmark. The 15 revised cases quiet, at load ~20 and at load >=50; the planted 150 ms hook at 20 and 50.
# Load = N unpinned busy loops at nice 0 in one process group (setsid), each bounded by timeout; stopped by -pgid (proc.sh).
set -u
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
W=/home/usain/gov-os-worktrees/W2-111
EV=$W/.gov-runtime/scratch/lead/td-1-evidence
OUT=$O/drafts/w2-111-bench
T=/tmp/claude-1000/w2-111-bench; mkdir -p $T/tmp $T/home
burn_pg=
start_load() { setsid bash -c "for i in \$(seq $1); do timeout 1500 sh -c 'while :; do :; done' & done; wait" & burn_pg=$!; sleep 1; }
stop_load() { [ -n "$burn_pg" ] && bash $O/tools/proc.sh stop --grace 5 -$burn_pg; burn_pg=; }
trap stop_load EXIT
wait_load() { local n=0; while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk -v l=$l -v t=$1 'BEGIN{exit !(l>=t)}' && break; n=$((n+1)); [ $n -gt 60 ] && { echo "load never reached $1 (at $l)"; break; }; sleep 5; done; }
run() {  # label [env...]
  local label=$1; shift; local figs=$OUT/$label.figs; rm -f $figs
  { echo "== $label start $(date -Is) load: $(cat /proc/loadavg)"
    ( cd $W && env "$@" TMPDIR=$T/tmp PYTHONUSERBASE=/home/usain/.local HOME=$T/home PYTHONPATH=$W/src:$EV TD_FIGURES=$figs \
      bash $O/tools/heavy_slot.sh python3 -m pytest \
      tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms \
      tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook \
      tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95 \
      -q -p td_plugin -p no:cacheprovider -o tmp_path_retention_policy=failed )
    echo "== $label exit $? end $(date -Is) load: $(cat /proc/loadavg)"; } > $OUT/$label.log 2>&1
  grep -E '^== |passed|failed' $OUT/$label.log
}
run quiet
start_load 22; wait_load 19; run load20; run load20-planted TD_PLANT_S=0.15; stop_load
start_load 56; wait_load 50; run load50; run load50-planted TD_PLANT_S=0.15; stop_load
echo BENCH DONE
