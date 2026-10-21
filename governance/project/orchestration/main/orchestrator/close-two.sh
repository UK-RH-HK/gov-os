#!/bin/bash
# After the W1-38 round's merge and regression: rebuild, gov close DAEO-3ef2 once, then the one further
# gov close DAEO-6mk8 (DEC-672). An exit 4 of the first stops the script: the owner decides (DEC-651).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-close-two.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-close-two.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-3ef2 --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-38M.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-38M.err
first=$?
echo "close DAEO-3ef2 exit $first"
git status --short | head -5
if [ "$first" -ne 0 ] || [ "$1" != "both" ] || [ -n "$(git status --porcelain)" ]; then
  echo "stopping after the first close (exit $first); the second is not run here"
  exit "$first"
fi
PYTHONPATH=src python3 -m gov.cli.main close DAEO-6mk8 --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-31b-second.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-31b-second.err
echo "close DAEO-6mk8 exit $?"
git status --short | head -5
cut -d' ' -f1-3 /proc/loadavg
