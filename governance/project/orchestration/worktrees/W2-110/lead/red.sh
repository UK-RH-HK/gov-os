#!/bin/bash
# The lead's red check (step 2): the merged tests on the ticket's base. The tests worktree is the base 695eea48139f
# plus the tests commit only, so it is the base with the tests merged; its src/ is the base's code.
cd /home/usain/gov-os-worktrees/W2-110-tests || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
git rev-parse --short=12 HEAD
PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -c "import gov; print(gov.__file__)"
TMPDIR=/tmp/gov-os-lead-W2-110 PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/W2-110 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/red.xml
