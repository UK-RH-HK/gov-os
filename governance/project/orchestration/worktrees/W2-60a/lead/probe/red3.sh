#!/bin/bash
# Round 3's red check in the tests worktree, against the ticket's code before round 3 (DEC-963).
T=/home/usain/gov-os-worktrees/W2-60a-tests
L=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
date > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3-start.txt
cd /home/usain/gov-os-worktrees/W2-60a-tests || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-60a
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3-gov-file.txt
n=0
for f in tests/acceptance/W2-60a/test_w2_60a_main_checkout_and_adopted_layout.py tests/unit/launch/test_runs.py tests/unit/launch/test_w1_28.py tests/unit/launch/test_w1_32.py tests/acceptance/W1-30/test_w1_30_r11_declared_here.py tests/acceptance/W2-57/test_w2_57_serial_list.py; do
  n=$((n+1))
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src python3 -m pytest "$f" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -rf --junitxml=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3-$n.xml > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3-$n.txt 2>&1
  echo "$n $f exit $?" >> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3-summary.txt
done
echo done > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red3.exit
