#!/bin/bash
# The one close of DAEO-emkd after the W1-02 round's merge (DEC-685): rebuild, validator, gov close once.
# The close on the merge counts as the post-merge regression (DEC-536); an exit 4 falls back to reg.sh by hand.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-02R9-close.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-02R9-close.err
echo "rebuild exit $?"
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-emkd --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-02R9.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-02R9.err
echo "close DAEO-emkd exit $?"
git status --short | head -5
