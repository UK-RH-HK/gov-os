#!/bin/bash
# Round 3: the unexplained reds of the scoped run, each file alone (a red alone is a red; a pass alone a flaky candidate).
cd /home/usain/gov-os-worktrees/W2-60a || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-60a
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
n=0
for f in tests/acceptance/W1-50/test_w1_50_acceptance_test_changed_on_both_sides.py tests/acceptance/W1-50/test_w1_50_read_merge_brought.py tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner"; do
  n=$((n+1))
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest "$f" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --junitxml=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/alone3-$n.xml > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/alone3-$n.txt 2>&1
  echo "$n $f exit $?" >> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/alone3-summary.txt
done
echo done > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/alone3.exit
