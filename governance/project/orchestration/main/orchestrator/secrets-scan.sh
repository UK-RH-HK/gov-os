#!/bin/bash
# The secrets-indexing check's own command, run alone in the main tree, with its output and time kept.
# Usage: bash secrets-scan.sh <label>   (outputs go to log/secrets-<label>.out, .err and .time)
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
label="$1"
start=$(date +%s)
PYTHONPATH=src python3 -m gov.secrets > "$L/secrets-$label.out" 2> "$L/secrets-$label.err"
code=$?
echo "$(( $(date +%s) - start )) s, exit $code" > "$L/secrets-$label.time"
cat "$L/secrets-$label.time"
