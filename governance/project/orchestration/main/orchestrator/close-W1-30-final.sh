#!/bin/bash
# Final close of DAEO-2lwj after the owner's apply block (DEC-648, DEC-649).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
echo "--- rebuild ---"
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-30-final.json 2> $L/rebuild-W1-30-final.err
echo "rebuild exit $?"
echo "--- close ---"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-2lwj --json --role orchestrator > $L/close-W1-30-final.json 2> $L/close-W1-30-final.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
