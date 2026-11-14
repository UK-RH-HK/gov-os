#!/usr/bin/env bash
# R (W2-121 S1): 20 runs in a row beside a busy loop of 20 workers (the nightly's load), all in this one call.
# The busy workers are stopped by pid (proc.sh) when the script ends, whatever happens.
P=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh
L=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/log/r_load20
mkdir -p "$L" /tmp/w2-182-lead
pids=()
cleanup() { [ ${#pids[@]} -gt 0 ] && bash "$P" stop --grace 2 "${pids[@]}" >/dev/null 2>&1; }
trap cleanup EXIT
for i in $(seq 1 20); do python3 -c 'while True: pass' & pids+=($!); done
sleep 3; echo "busy pids: ${pids[*]}"; cat /proc/loadavg
cd /home/usain/gov-os-worktrees/W2-182 || exit 2
pass=0
for n in $(seq 1 20); do
  env TMPDIR=/tmp/w2-182-lead PYTHONUSERBASE=/home/usain/.local \
    HOME=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/empty-home \
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-182/src \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
    --junitxml="$L/run-$n.xml" \
    "tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing" > "$L/run-$n.txt" 2>&1
  rc=$?
  echo "run $n rc=$rc $(tail -1 "$L/run-$n.txt") load=$(cut -d' ' -f1 /proc/loadavg)"
  [ $rc = 0 ] && pass=$((pass+1)) || break
done
echo "R: $pass of 20 passed in a row"
