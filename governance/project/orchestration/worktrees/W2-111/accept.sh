#!/usr/bin/env bash
# gov accept for W2-111, then the 15 latency cases on the merged head (lead's check), through the heavy slot.
mkdir -p /tmp/w2-111-lead-tmp /home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-111
LOG=/home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/lead/log
echo "load before accept: $(cat /proc/loadavg)"
env TMPDIR=/tmp/w2-111-lead-tmp PYTHONUSERBASE=/home/usain/.local \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-111 --root /home/usain/gov-os-worktrees/W2-111 > "$LOG/accept-1.log" 2>&1
echo "accept rc=$?"; tail -15 "$LOG/accept-1.log"
echo "load before cases: $(cat /proc/loadavg)"
env TMPDIR=/tmp/w2-111-lead-tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-111/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml="$LOG/lead-cases-1.xml" \
  "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" \
  "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook" \
  "tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95" \
  > "$LOG/lead-cases-1.log" 2>&1
echo "cases rc=$?"; tail -5 "$LOG/lead-cases-1.log"
echo "load after: $(cat /proc/loadavg)"
