#!/bin/bash
# DEC-713, DEC-716: the worktree list and the after-merge lines of the exit report; stage, rebuild (DEC-709), commit.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
echo "hooks: $(ls .git/hooks | grep -v '\.sample$' | tr '\n' ' ')"
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
git add docs/plan/wave-1-exit/EXIT-REPORT.md docs/plan/wave-1-exit/evidence/git-worktree-list.txt
git status --short
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-42-wtlist.json 2> $L/rebuild-W1-42-wtlist.err
echo "rebuild exit $?"
git commit -q -m "W1-42: the worktree list after the worktree's removal, and the exit report's lines after the merge (no run 8c, the lead's scratch folder; DEC-713, DEC-715, DEC-716)" --trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-23.c" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "commit exit $?"
git log --oneline -1
git status --short | head -5
