#!/bin/bash
# W2-50 run 8: the load-sensitive reds re-run alone, after every other suite ended, below load 20.
W=/home/usain/gov-os-worktrees/W2-50
O=$W/.gov-runtime/scratch/lead/log/v7-alone
mkdir -p $O
cd $W || exit 9
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
for t in "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" \
         "tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over"; do
  n=$(echo "$t" | sed 's/.*:://')
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  cat /proc/loadavg > $O/$n.load
  PYTHONPATH=$W/src python3 -m pytest "$t" -q -p no:cacheprovider -rs > $O/$n.txt 2>&1
  echo $? > $O/$n.exit
done
echo done > $O/all.done
