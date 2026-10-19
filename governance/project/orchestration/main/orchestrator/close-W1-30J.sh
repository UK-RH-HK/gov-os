#!/bin/bash
# Rebuild without embeddings, then gov close DAEO-2lwj on the fix round's merge and the data fixes of DEC-614.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-30J.json 2> $L/rebuild-W1-30J.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-2lwj --json --role orchestrator > $L/close-W1-30J.json 2> $L/close-W1-30J.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
