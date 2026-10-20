#!/bin/bash
# Rebuild without embeddings, then the context check and the full gov check on the real store.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-ctx2.json 2> $L/rebuild-ctx2.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.context.context_check > $L/context-check-2.txt 2>&1
echo "context check exit $?"
tail -3 $L/context-check-2.txt
GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic PYTHONPATH=src python3 -m gov.cli.main check --json > $L/check-after-ctx-data.json 2> $L/check-after-ctx-data.err
echo "gov check exit $?"
