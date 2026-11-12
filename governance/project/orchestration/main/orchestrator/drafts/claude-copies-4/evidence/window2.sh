#!/bin/bash
# usage: window2.sh <tree> <log>  -- the other folders that read .claude/templates, .claude/agents or .rulesync/subagents
T=$1; L=$2; D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/claude-copies-4
: > $L
cd $T
for f in tests/acceptance/W1-02 tests/acceptance/W1-05 tests/acceptance/W1-10 tests/acceptance/W1-28 tests/acceptance/W1-31 tests/acceptance/W1-46 tests/acceptance/W2-116 tests/acceptance/W2-136 tests/acceptance/W2-148 tests/acceptance/W2-20 tests/acceptance/W2-50 tests/acceptance/W2-56 tests/acceptance/W2-58 tests/acceptance/W2-61h tests/acceptance/W2-62 tests/acceptance/W2-90 tests/unit/launch tests/unit/operator tests/unit/orchestration tests/unit/retrieval tests/unit/telemetry; do
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=$D/tmp PYTHONPATH=$T/src python3 -m pytest $f -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $L.$$ 2>&1
  echo "== $f exit $? :: $(tail -1 $L.$$)" >> $L
  grep -E "^(FAILED|ERROR)" $L.$$ | cut -c1-200 >> $L
done
rm -f $L.$$
echo done >> $L
