#!/bin/bash
# Rebuild without embeddings, then gov close DAEO-2lwj on the merge (post-merge regression, DEC-536).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-30G.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-30G.err
echo "rebuild exit $?"
cut -d' ' -f1-3 /proc/loadavg
PYTHONPATH=src python3 -m gov.cli.main close DAEO-2lwj --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-30G.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-30G.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
