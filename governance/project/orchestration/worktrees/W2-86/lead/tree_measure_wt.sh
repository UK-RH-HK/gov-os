#!/bin/bash
# W2-86 supplementary head: the measure, visible half only, on this worktree's own store (built by its own code at
# the head 338c14fa6475, identical in files and vectors to the head clone's), retrieving with this worktree's code.
L=/home/usain/gov-os-runs/W2-86/logs
mkdir -p /home/usain/gov-os-runs/W2-86/records-tree
python3 -c "import time; print('start', time.strftime('%H:%M:%S', time.gmtime()))" > "$L/tree-measure-wt.times"
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-worktrees/W2-86 --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible --gov /tmp/claude-1000/-home-usain-gov-os-worktrees-W2-86/8032324e-fe9a-455f-b1f8-0ddb0d1ba6d3/scratchpad/bin/gov-wt --out /home/usain/gov-os-runs/W2-86/records-tree --json > "$L/tree-measure-wt.json" 2> "$L/tree-measure-wt.err"
RC=$?
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> "$L/tree-measure-wt.times"
ls -t /home/usain/gov-os-runs/W2-86/records-tree/*.json | head -1 > "$L/tree-measure-wt.record"
echo $RC > "$L/tree-measure-wt.exit"
