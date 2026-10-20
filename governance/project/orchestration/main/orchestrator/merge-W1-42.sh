#!/bin/bash
# DEC-713, DEC-716: merge w1/W1-42 into w1/integrate (one committing command); rebuild before it (DEC-709); hooks absent (DEC-712).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
echo "hooks: $(ls .git/hooks | grep -v '\.sample$' | tr '\n' ' ')"
git status --short | head -5
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-merge-W1-42.json 2> $L/rebuild-merge-W1-42.err
echo "rebuild exit $?"
git merge --no-ff w1/W1-42 -m "Merge w1/W1-42: the Wave 1 exit run on the dev tiers, with its three red cases named in the exit report (DEC-713) and without a run 8c (DEC-716)" -m "Task: DAEO-gjjf
Role: orchestrator
Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "merge exit $?"
git log --oneline -2
git status --short | head -5
echo "-- acceptance diff vs branch:"; git diff --stat w1/W1-42 HEAD -- tests/acceptance | tail -3
