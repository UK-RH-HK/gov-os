#!/bin/bash
# The one further gov close of DAEO-6mk8 after the designer pass merged (DEC-672).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
git log --oneline -1
git status --short | head -5
PYTHONPATH=src python3 -m gov.cli.main close DAEO-6mk8 --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-31b-second.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-31b-second.err
echo "close DAEO-6mk8 exit $?"
git status --short | head -5
