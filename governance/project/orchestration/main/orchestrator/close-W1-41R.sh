#!/bin/bash
# The one close of DAEO-cdoi after the W1-41 round's merge (DEC-694): rebuild, validator, gov close once.
# An exit 3 or 4 goes to the owner; reg-W1-41 is the post-merge regression already (13,168 + 263, ALL PASS).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-41R-close.json 2> $L/rebuild-W1-41R-close.err
echo "rebuild exit $?"
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-cdoi --json --role orchestrator > $L/close-W1-41R.json 2> $L/close-W1-41R.err
echo "close DAEO-cdoi exit $?"
git status --short | head -5
