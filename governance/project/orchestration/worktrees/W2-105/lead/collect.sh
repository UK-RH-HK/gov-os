#!/bin/bash
# DEC-868: the collection check, in one process, as the close runs it.
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -c "import gov; print(gov.__file__)" > $L/govfile.txt 2>&1
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > $L/collect.txt 2>&1
echo $? > $L/collect.exit
