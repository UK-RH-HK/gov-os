#!/bin/bash
# The one close of DAEO-gjjf after the merge (DEC-713, DEC-716): rebuild, validator, gov close once.
# An exit 3 or 4 goes to the owner; reg-W1-42 is the post-merge regression already.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
echo "hooks: $(ls .git/hooks | grep -v '\.sample$' | tr '\n' ' ')"
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-42-close.json 2> $L/rebuild-W1-42-close.err
echo "rebuild exit $?"
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-gjjf --json --role orchestrator > $L/close-W1-42.json 2> $L/close-W1-42.err
echo "close DAEO-gjjf exit $?"
git log --oneline -2
git status --short | head -5
