#!/bin/bash
# Run 3: red check of review 3's cases (588e43ae, c348af6b) on run 2's code (382e6d8f), the tests worktree detached at c348af6b.
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 30; done
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4.start
python3 /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/red_check.py /home/usain/gov-os-worktrees/W2-96-tests /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4.xml > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4.out 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4.exit
cd /home/usain/gov-os-worktrees/W2-96-tests && TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96/test_w2_96_at_review_3.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4-file.out 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r4-file.exit
