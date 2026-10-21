#!/bin/bash
# After the adoption: rebuild without embeddings, gov check with the dev tiers, gov doctor, the unit suite.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-adopted.json 2> $L/rebuild-adopted.err
echo "rebuild exit $?"
GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic PYTHONPATH=src python3 -m gov.cli.main check --json > $L/check-adopted.json 2> $L/check-adopted.err
echo "gov check exit $?"
PYTHONPATH=src python3 -m gov.cli.main doctor --json > $L/doctor-adopted.json 2> $L/doctor-adopted.err
echo "gov doctor exit $?"
PYTHONPATH=src python3 -m pytest tests/unit -q -n 4 -p no:cacheprovider > $L/unit-adopted.txt 2>&1
echo "unit exit $?"
tail -1 $L/unit-adopted.txt
