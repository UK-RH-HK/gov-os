#!/bin/bash
# W2-86's re-measure: a clone's stores built by the pinned gov (W2-61 §8 step 2), under the rebuild lock.
# usage: rebuild_clone.sh base|head
case "$1" in
  base) cd /home/usain/gov-os-runs/W2-86/base || exit 9 ;;
  head) cd /home/usain/gov-os-runs/W2-86/head || exit 9 ;;
  *) exit 7 ;;
esac
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".gate 2>&1 || { echo 8 > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".exit; exit 8; }
python3 -c "import os, time; print(time.strftime('%H:%M:%S', time.gmtime()), os.getloadavg())" >> /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".gate
env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock /home/usain/.local/bin/gov rebuild --json > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".json 2> /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".err
echo $? > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".exit
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-"$1".gate
