#!/bin/bash
# Run 2 verification: each suite in its own pytest process, to its end, with exit-code files.
cd /home/usain/gov-os-worktrees/W2-62 || exit 9
L=/home/usain/gov-os-worktrees/W2-62/.gov-runtime/scratch/lead/log
S=/home/usain/gov-os-worktrees/W2-62/src
for suite in W2-62 W1-49 W1-29; do
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$S python3 -m pytest tests/acceptance/$suite -q -p no:cacheprovider -rs > $L/r2-$suite.txt 2>&1
  echo $? > $L/r2-$suite.exit
done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
PYTHONPATH=$S python3 -m pytest tests/unit -q -p no:cacheprovider > $L/r2-unit.txt 2>&1
echo $? > $L/r2-unit.exit
