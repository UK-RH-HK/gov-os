#!/bin/bash
# W2-50 run 8: gov check twice in a row on this worktree's real stores, after the rebuild (DEC-853's proof).
W=/home/usain/gov-os-worktrees/W2-50
L=$W/.gov-runtime/scratch/lead/log
cd $W || exit 9
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
PYTHONPATH=$W/src python3 -c "import gov; print(gov.__file__)" > $L/gov-file-7.txt
ls -la $W/.gov-runtime/secrets-clean.json > $L/check-7.pre 2>&1
for r in a b; do
  cat /proc/loadavg > $L/check-7$r.load
  s=$(date +%s.%N)
  PYTHONPATH=$W/src python3 -m gov.cli.main check --json > $L/check-7$r.json 2> $L/check-7$r.err
  echo $? > $L/check-7$r.code
  e=$(date +%s.%N)
  echo "$s $e" > $L/check-7$r.time
  ls -la $W/.gov-runtime/secrets-clean.json >> $L/check-7$r.load 2>&1
done
echo done > $L/check-7.done
