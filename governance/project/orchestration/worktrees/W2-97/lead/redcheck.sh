#!/bin/bash
# Red check (step 2): the merged tests on the ticket's base. The tests worktree is the base (c6118ced826a) plus the
# designer's commit only, so it is the base with the tests branch merged; run with its own src (DEC-732).
cd /home/usain/gov-os-worktrees/W2-97-tests || exit 9
rm -f /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.rc
PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.txt 2>&1
git log --oneline -2 >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.txt
ls governance/project/orchestration/tools >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.txt 2>&1
TMPDIR=/tmp/gov-os-lead-W2-97 PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed -rA --junitxml=/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.xml >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/redcheck.rc
