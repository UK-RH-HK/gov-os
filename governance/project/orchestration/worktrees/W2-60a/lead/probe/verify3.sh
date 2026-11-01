#!/bin/bash
# Round 3's verification (DEC-953 item 4, DEC-968): gates, rebuild, selection, scoped run in the close's form,
# gov check, collect-only. Each step writes its own file in log/.
L=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-60a || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-60a
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-disk-gate.txt 2>&1 || { echo "disk gate shut" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3.exit; exit 3; }
date > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-rebuild-start.txt
flock /tmp/gov-os-rebuild.lock env PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-rebuild.json 2>&1
echo "exit $? $(date)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-rebuild.exit
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-gov-file.txt
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-60a W2-60a DAEO-cv58 > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-selection.json 2> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-selection.err
SEL=$?
echo "exit $SEL" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-selection.exit
if [ "$SEL" != "0" ]; then echo "selection exit $SEL" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3.exit; exit 2; fi
python3 /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/probe/run_verify3.py /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-selection.json
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-check.json 2>&1
echo "exit $?" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-check.exit
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-collect.txt 2>&1
echo "exit $?" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-collect.exit
echo "done $(date)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3.exit
