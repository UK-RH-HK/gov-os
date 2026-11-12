#!/bin/bash
# usage: port.sh <tree>  -- portability from the tree as cwd; prints exit, count, findings
cd "$1" || exit 9
out=$(env HOME=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/claude-copies-4/home PYTHONPATH=$PWD/src python3 -m gov.adapters.portability); rc=$?
echo "$out" | python3 -c "
import sys,json; d=json.load(sys.stdin); print('exit $rc; findings', len(d['findings']), d['compared']); [print(' ',f['code'],f.get('file')) for f in d['findings']]"
