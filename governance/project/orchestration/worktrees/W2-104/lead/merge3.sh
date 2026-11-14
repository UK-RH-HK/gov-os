#!/usr/bin/env bash
# Run 3: merge w2/integrate; save a WIP commit with the conflict markers in place (resolutions follow in own commits).
set -u
cd /home/usain/gov-os-worktrees/W2-104 || exit 2
INT=$(git rev-parse --short=12 w2/integrate)
git merge --no-ff --no-commit w2/integrate > .gov-runtime/scratch/lead/merge-integrate-3.txt 2>&1
echo "merge exit $?"
git diff --name-only --diff-filter=U | tee .gov-runtime/scratch/lead/merge-3-conflicts.txt
git add -u
git commit -q -m "W2-104: merge w2/integrate (head $INT) into the ticket branch for run 3, WIP with conflict markers; the resolutions follow in their own commits" \
  --trailer "Task: DAEO-drhj" --trailer "Role: orchestrator" --trailer "Implements: DEC-959, DEC-820" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "commit exit $?"
git log --oneline -1
git status --short | head
grep -c '^<<<<<<<' $(cat .gov-runtime/scratch/lead/merge-3-conflicts.txt)
