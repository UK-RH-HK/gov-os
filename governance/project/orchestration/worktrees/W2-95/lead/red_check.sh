#!/bin/bash
# Red check (step 2): the designer's tests against the base code in the tests worktree, writing nothing there.
cd /home/usain/gov-os-worktrees/W2-95-tests || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-95
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-95-tests/src
python3 -B -c "import gov; print(gov.__file__)"
timeout 500 python3 -B -m pytest tests/acceptance/W2-95 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/red-check.txt 2>&1
echo "pytest exit=$?"
