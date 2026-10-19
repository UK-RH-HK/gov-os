#!/bin/bash
# DEC-703: confirm adapter-portability green after the operator's apply (75b57d40), in the close script's environment.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
git log --oneline -1
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-41-check.json 2> $L/rebuild-W1-41-check.err
echo "rebuild exit $?"
PYTHONPATH=src python3 -m gov.cli.main check --json > $L/check-W1-41-close.json 2> $L/check-W1-41-close.err
echo "check exit $?"
python3 -c "
import json
d=json.load(open('$L/check-W1-41-close.json'))
cs=(d.get('error') or {}).get('details',{}).get('checks') or (d.get('result') or {}).get('checks') or []
for c in cs:
  if c['status']!='GREEN': print(c['id'], c['status'], [f.get('code') for f in c['findings']])
  if c['id']=='adapter-portability': print('adapter-portability', c['status'], c['provenance']['commit'][:8])
"
git status --short | head -5
