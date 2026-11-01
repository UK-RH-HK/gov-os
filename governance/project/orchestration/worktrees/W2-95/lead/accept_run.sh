#!/bin/bash
# The W2-95 acceptance tests against this worktree's own src (DEC-732), writing nothing in tests/acceptance.
cd /home/usain/gov-os-worktrees/W2-95 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-95
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src
python3 -B -c "import gov; print(gov.__file__)"
timeout 500 python3 -B -m pytest tests/acceptance/W2-95 tests/unit/check/test_w2_95_pathmap.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/accept-1.txt 2>&1
echo "pytest exit=$?"
