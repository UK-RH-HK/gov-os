#!/bin/bash
# DEC-847/DEC-961's load gate, then the command: wait while the 1-minute and 15-minute loads are both at or above
# the number of processors; the disk gate (DEC-898) just before. Usage: load_gate.sh <command and arguments>
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 97
"$@"
