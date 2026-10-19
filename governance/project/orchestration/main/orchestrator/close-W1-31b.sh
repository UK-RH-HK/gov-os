#!/bin/bash
# The one close of DAEO-6mk8 after the W1-31 round's merge (DEC-655): rebuild without embeddings, then gov close once.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > "$L/rebuild-W1-31b-close.json" 2> "$L/rebuild-W1-31b-close.err"
echo "rebuild exit $?"
echo "--- close ---"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-6mk8 --json --role orchestrator > "$L/close-W1-31b.json" 2> "$L/close-W1-31b.err"
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
