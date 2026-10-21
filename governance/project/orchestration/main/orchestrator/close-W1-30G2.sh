#!/bin/bash
# Rebuild without embeddings, then gov close DAEO-2lwj with the owner's decision DEC-593 (P-36 a).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-30G2.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-30G2.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-2lwj --owner-decision DEC-593 --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-30G2.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-30G2.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
