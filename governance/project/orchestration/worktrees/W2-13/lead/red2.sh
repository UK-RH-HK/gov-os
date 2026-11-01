#!/bin/bash
# red2.sh: the rewritten W2-13 acceptance tests (tests worktree) against the base's code (the base clone).
cd /home/usain/gov-os-worktrees/W2-13-tests || exit 9
LOG=/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log
TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=/home/usain/gov-os-runs/W2-13/base/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/red2.txt 2>&1
TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=/home/usain/gov-os-runs/W2-13/base/src python3 -m pytest tests/acceptance/W2-13 --ignore tests/acceptance/W2-13/test_w2_13_latency.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs >> /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/red2.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/red2.exit
