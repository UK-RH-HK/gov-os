#!/bin/bash
# W2-86 supplementary pair: a clone's stores rebuilt by the tree's own code (the clone's src/, through the pinned
# interpreter, as W2-87's launchers), under the rebuild lock. usage: tree_rebuild.sh base|head
case "$1" in
  base) cd /home/usain/gov-os-runs/W2-86/base || exit 9 ;;
  head) cd /home/usain/gov-os-runs/W2-86/head || exit 9 ;;
  *) exit 7 ;;
esac
L=/home/usain/gov-os-runs/W2-86/logs
mkdir -p /home/usain/gov-os-runs/W2-86/logs
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/tree-rebuild-$1.gate" 2>&1 || { echo 8 > "$L/tree-rebuild-$1.exit"; exit 8; }
python3 -c "import os, time; print('gate', time.strftime('%H:%M:%S', time.gmtime()), os.getloadavg())" >> "$L/tree-rebuild-$1.gate"
env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock /tmp/claude-1000/-home-usain-gov-os-worktrees-W2-86/8032324e-fe9a-455f-b1f8-0ddb0d1ba6d3/scratchpad/bin/gov-"$1" rebuild --json > "$L/tree-rebuild-$1.json" 2> "$L/tree-rebuild-$1.err"
echo $? > "$L/tree-rebuild-$1.exit"
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> "$L/tree-rebuild-$1.gate"
