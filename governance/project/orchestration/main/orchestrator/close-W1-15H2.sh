#!/bin/bash
# Rebuild without embeddings, measure the secrets-indexing check on this repository's real store
# (DEC-595) on a quiet machine, then gov close DAEO-7nne on the round's merge.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-15H2.json 2> $L/rebuild-W1-15H2.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main close DAEO-7nne --json --role orchestrator > $L/close-W1-15H2.json 2> $L/close-W1-15H2.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
