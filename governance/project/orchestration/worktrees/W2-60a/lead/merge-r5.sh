#!/bin/bash
# Merge w2/integrate into w2/W2-60a in one script: b11's four resolutions from the backups
# (integrate unchanged on them since 84cc42343ffb), integrate's role-lead template, and the
# four acceptance conflicts committed with their markers for the test designer (b12).
set -u
cd /home/usain/gov-os-worktrees/W2-60a || exit 1
B=.gov-runtime/scratch/lead/merge-r4
git merge --no-ff --no-commit w2/integrate
echo "merge exit $?"
cp "$B/launcher.py" src/gov/launch/launcher.py
cp "$B/test_runs.py" tests/unit/launch/test_runs.py
cp "$B/test_w1_28.py" tests/unit/launch/test_w1_28.py
cp "$B/test_w1_32.py" tests/unit/launch/test_w1_32.py
git checkout --theirs -- .claude/templates/role-lead.md
git add -- src/gov/launch/launcher.py tests/unit/launch/test_runs.py tests/unit/launch/test_w1_28.py tests/unit/launch/test_w1_32.py .claude/templates/role-lead.md \
  tests/acceptance/W2-50/w2_50_support.py tests/acceptance/W2-58/README.md tests/acceptance/W2-58/test_w2_58_launched_sessions.py tests/acceptance/W2-58/w2_58_support.py
git diff --name-only --diff-filter=U
git commit -m "Merge w2/integrate into w2/W2-60a (WIP): conflict resolutions follow; 4 acceptance files keep their markers for the test designer (b12); launcher.py and 3 unit files from b11's resolution; role-lead template integrate's" \
  --trailer "Task: DAEO-cv58" --trailer "Role: orchestrator" \
  --trailer "Implements: DEC-826, DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941, CAP-35.c, CAP-36.a, DEC-1014, DEC-1015, DEC-1119, DEC-1120, DEC-1126"
rc=$?
echo "commit exit $rc"
if [ $rc -ne 0 ]; then git merge --abort; echo "ABORTED"; fi
git status --short | head
git log --oneline -1
