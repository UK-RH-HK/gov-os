#!/bin/bash
# Final close of DAEO-3ef2 after the owner's apply block (DEC-648).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
echo "--- close ---"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-3ef2 --json --role orchestrator > $L/close-W1-38-final.json 2> $L/close-W1-38-final.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
