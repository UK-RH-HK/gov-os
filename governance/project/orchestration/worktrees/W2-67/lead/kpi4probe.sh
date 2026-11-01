#!/bin/bash
# Run 6: which selected file starts nested pytest sessions that inherit the run's TMPDIR (KPI 4: the scoped run left
# four base folders, pytest-0 and pytest-20..22, the last three empty and made at 08:26). Each candidate file runs
# alone with a TMPDIR of its own; the base folders it leaves are counted.
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log/kpi4probe.txt
cd "$W" || exit 99
n=0
for f in tests/acceptance/W1-30/test_w1_30_test_runner.py tests/acceptance/W1-30/test_w1_30_r10_interpreter.py \
         tests/acceptance/W1-30/test_w1_30_r11_parallel_runs.py tests/acceptance/W1-30/test_w1_30_r11_declared_here.py \
         tests/unit/close/test_follow_up.py tests/unit/close/test_evidence.py \
         tests/acceptance/W1-27/test_w2_67_sweep_namespaces.py tests/acceptance/W1-27/test_w2_67_basetemp_refusal.py \
         tests/acceptance/W1-27/test_w2_67_temp_folders.py; do
  n=$((n+1))
  mkdir -p /tmp/gov-os-lead-W2-67/kpi4/$n
  until python3 $W/.gov-runtime/scratch/lead/loadwait.py; do sleep 30; done
  TMPDIR=/tmp/gov-os-lead-W2-67/kpi4/$n PYTHONPATH=$W/src python3 -m pytest "$f" -n 4 -q -p no:cacheprovider \
    -o tmp_path_retention_policy=failed > /tmp/gov-os-lead-W2-67/kpi4/$n.out 2>&1
  e=$?
  echo "$n $f exit=$e result=$(tail -1 /tmp/gov-os-lead-W2-67/kpi4/$n.out) bases=$(ls -d /tmp/gov-os-lead-W2-67/kpi4/$n/pytest-of-*/pytest-[0-9]* 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')" >> "$LOG"
done
echo done >> "$LOG"
