#!/usr/bin/env bash
# The load-sensitive W1-19 case, alone, after the other suites (DEC-757).
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
TMPDIR=/tmp/gov-os-lead-W2-90b PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src timeout 3000 python3 -m pytest "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/w1-19-alone.xml > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/w1-19-alone.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/w1-19-alone.exit
