#!/bin/bash
# Round 2 red check, one file at a time (the nightly is running).
cd /home/usain/gov-os-worktrees/W2-60a || exit 9
for f in test_w2_60a_command_skills.py test_w2_60a_user_permissions.py test_w2_60a_no_compaction_threshold.py test_w2_60a_refused_arguments.py test_w2_60a_kept_out.py; do
  TMPDIR=/tmp/gov-os-lead-W2-60a PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests/acceptance/W2-60a/$f -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -rf --junitxml=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red2-$f.xml > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red2-$f.txt 2>&1
  echo "$f $(tail -1 /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red2-$f.txt)" >> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red2-summary.txt
done
echo done > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/red2.exit
