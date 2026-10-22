#!/bin/bash
# W2-50 run 9: one full rebuild (never --no-embeddings), after the close-quiet and load gates.
W=/home/usain/gov-os-worktrees/W2-50
L=$W/.gov-runtime/scratch/lead/log
cd $W || exit 9
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
date -Is > $L/rebuild-9.start; cat /proc/loadavg >> $L/rebuild-9.start
PYTHONPATH=$W/src python3 -m gov.cli.main rebuild --json > $L/rebuild-9.json 2> $L/rebuild-9.err
echo $? > $L/rebuild-9.exit
date -Is >> $L/rebuild-9.start
