#!/bin/bash
# Rebuild without embeddings, then gov check with the dev tiers, at the current head.
# Usage: bash check-at-head.sh <label>   (outputs go to log/rebuild-<label>.* and log/check-<label>.*)
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
label="$1"
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > "$L/rebuild-$label.json" 2> "$L/rebuild-$label.err"
echo "rebuild exit $?"
GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic PYTHONPATH=src python3 -m gov.cli.main check --json > "$L/check-$label.json" 2> "$L/check-$label.err"
echo "gov check exit $?"
cut -d' ' -f1-3 /proc/loadavg
