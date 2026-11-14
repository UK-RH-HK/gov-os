#!/usr/bin/env bash
# Run 4 (DEC-1173 (1)): merge w2/integrate; every conflicted file takes integrate's side exactly; no markers, no own edits.
set -u
cd /home/usain/gov-os-worktrees/W2-104 || exit 2
INT=$(git rev-parse --short=12 w2/integrate)
LOG=.gov-runtime/scratch/lead/merge-integrate-4.txt
git merge --no-ff --no-commit w2/integrate > "$LOG" 2>&1
echo "merge exit $?"
git diff --name-only --diff-filter=U | tee .gov-runtime/scratch/lead/merge-4-conflicts.txt
while read -r p; do
  [ -n "$p" ] || continue
  git checkout --theirs -- "$p" && git add -- "$p"
done < .gov-runtime/scratch/lead/merge-4-conflicts.txt
echo "markers in tree:"; git diff --cached --name-only | xargs -r grep -l -E '^(<<<<<<<|>>>>>>>|=======$)' || echo none
git diff --name-only --diff-filter=U | wc -l
git commit -q -m "W2-104: merge w2/integrate (head $INT) for run 4; every conflicted file takes integrate's side exactly, no markers and no own edits (DEC-1173 (1)); skilleval is added back in its own commits" \
  --trailer "Task: DAEO-drhj" --trailer "Role: orchestrator" --trailer "Implements: DEC-959, DEC-820" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "commit exit $?"
git log --oneline -1
git status --short | head
echo "diff vs integrate per conflicted file (expect nothing):"
while read -r p; do git diff --stat w2/integrate HEAD -- "$p"; done < .gov-runtime/scratch/lead/merge-4-conflicts.txt
echo end
