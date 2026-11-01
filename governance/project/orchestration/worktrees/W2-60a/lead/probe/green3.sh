#!/bin/bash
# Round 3's green check in this worktree (merged head), then W2-58's live pair alone (DEC-951 item 4 (v)).
L=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-60a || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-60a
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-gov-file.txt
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests/acceptance/W2-60a/test_w2_60a_main_checkout_and_adopted_layout.py tests/unit/launch/test_runs.py tests/unit/launch/test_w1_28.py tests/unit/launch/test_w1_32.py tests/unit/launch/test_role.py tests/unit/launch/test_launch_record.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -rf --junitxml=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-1.xml > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-1.txt 2>&1
echo "1 exit $?" >> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-summary.txt
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest "tests/acceptance/W2-58/test_w2_58_launched_sessions.py::test_a_launched_session_shows_no_phantom_deletion" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs --junitxml=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-w258.xml > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-w258.txt 2>&1
echo "w258 exit $?" >> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3-summary.txt
echo done > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/green3.exit
