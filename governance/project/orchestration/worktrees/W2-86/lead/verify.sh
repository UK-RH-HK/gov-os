#!/bin/bash
# W2-86's scoped verification: the selection at the head, then the parallel and serial runs (verify.py).
# usage: verify.sh <tag>
cd /home/usain/gov-os-worktrees/W2-86 || exit 9
L=/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-86 W2-86 DAEO-jsg1 > "$L/select-$1.json" 2> "$L/select-$1.err"
echo $? > "$L/select-$1.exit"
[ "$(cat "$L/select-$1.exit")" = "0" ] || exit 2
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/verify-$1.gate" 2>&1 || exit 8
python3 -c "import os, time; print('start', time.strftime('%H:%M:%S', time.gmtime()), os.getloadavg())" >> "$L/verify-$1.gate"
du -sh /home/usain/gov-os-worktrees/W2-86/.gov-runtime /tmp/gov-os-lead-W2-86 >> "$L/verify-$1.gate" 2>&1
du -s --inodes /home/usain/gov-os-worktrees/W2-86/.gov-runtime /tmp/gov-os-lead-W2-86 >> "$L/verify-$1.gate" 2>&1
python3 /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/verify.py "$L/select-$1.json" "$1"
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> "$L/verify-$1.gate"
du -sh /tmp/gov-os-lead-W2-86 >> "$L/verify-$1.gate" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-86 >> "$L/verify-$1.gate" 2>&1
