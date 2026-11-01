#!/bin/bash
# Run 3: after the rebuild, gov check, then the scoped run (run_verify4.sh).
until [ -s /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rebuild-4.exit ]; do sleep 20; done
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/govfile4.txt 2>&1
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/check4.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/check4.exit
bash /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/run_verify4.sh
