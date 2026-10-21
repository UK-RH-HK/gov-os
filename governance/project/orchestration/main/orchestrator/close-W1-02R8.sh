#!/bin/bash
# Rebuild without embeddings, then gov close DAEO-emkd on the merge (post-merge regression, DEC-536).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-02R8.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/rebuild-W1-02R8.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-emkd --json --role orchestrator > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-02R8.json 2> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-W1-02R8.err
echo "close exit $?"
