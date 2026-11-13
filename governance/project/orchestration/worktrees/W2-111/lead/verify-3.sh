#!/usr/bin/env bash
# Run 3 checks: collect-only vs collect-before, hygiene, gov accept, scoped run (all pytest via heavy_slot.sh).
set -u
T=/home/usain/gov-os-worktrees/W2-111
L=$T/.gov-runtime/scratch/lead
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
mkdir -p /tmp/w2-111-lead3-tmp $T/.gov-runtime/scratch/empty-home $L/log
cd $T
F="tests/acceptance/W1-02/test_w1_02_guard_hook.py tests/acceptance/W1-05/test_w1_05_live_hooks.py tests/acceptance/W2-57/test_w2_57_designer_read_p95.py"
IDS="tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95"
ENV="env TMPDIR=/tmp/w2-111-lead3-tmp PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src"
echo "== collect-only (latency ids)"
$ENV bash $HS python3 -m pytest $IDS --collect-only -q -p no:cacheprovider -o tmp_path_retention_policy=failed 2>&1 | grep '::' | sort > $L/log/collect-after-3.txt
sort $L/td-1-evidence/collect-before.txt | grep '::' > $L/log/collect-before-sorted.txt
wc -l < $L/log/collect-after-3.txt
diff $L/log/collect-before-sorted.txt $L/log/collect-after-3.txt && echo "collect: SAME 15 ids"
echo "== hygiene vs 085b4391c (pre-revision)"
git diff --stat 085b4391c HEAD -- . | tail -1
git diff --name-only 085b4391c HEAD
git diff 085b4391c HEAD -- $F | grep -nE '^\+.*(skip|xfail|flaky)' || echo "no skip/xfail/flaky added"
grep -n 'LATENCY_BOUND_S *=' $F
echo "== gov accept"
$ENV bash $HS gov accept W2-111 --root $T > $L/log/accept-3.log 2>&1; echo "accept rc=$?"; tail -15 $L/log/accept-3.log
echo "== scoped run (the 15 latency cases)"
cat /proc/loadavg
$ENV bash $HS python3 -m pytest $IDS -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml=$L/log/lead-cases-3.xml > $L/log/lead-cases-3.log 2>&1; echo "scoped rc=$?"
cat /proc/loadavg
tail -5 $L/log/lead-cases-3.log
echo "== whole three files (scoped, DEC-968)"
$ENV bash $HS python3 -m pytest $F -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --junitxml=$L/log/lead-files-3.xml > $L/log/lead-files-3.log 2>&1; echo "files rc=$?"
tail -8 $L/log/lead-files-3.log
echo VERIFY-3-END
