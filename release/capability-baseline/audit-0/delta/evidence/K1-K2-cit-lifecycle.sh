#!/bin/bash
set -e
GOV="$1"; PROJ="$2"
echo "=== K1/K2: CIT propose, simulate, approve, execute lifecycle ==="

echo "--- K1b1-b4: CIT-P propose (deterministic graph traversal) ---"
$GOV cit propose --root "$PROJ" --json --role orchestrator \
  --proposal "Rename config key MAX_RETRIES to MAX_RETRY_COUNT" \
  --trigger behaviour_change 2>&1 | tee /tmp/cit-propose.json | head -20
echo ""

CIT_ID=$( python3 -c "import json; d=json.load(open('/tmp/cit-propose.json')); r=d.get('result',d); print(r.get('id','') or r.get('cit',''))" 2>/dev/null || echo "" )
if [ -z "$CIT_ID" ]; then
  # try alternate path  
  CIT_ID=$(python3 -c "import json; d=json.load(open('/tmp/cit-propose.json')); print(d.get('result',{}).get('cit','CIT-0001'))" 2>/dev/null || echo "CIT-0001")
fi
echo "CIT_ID: $CIT_ID"

echo ""
echo "--- K1b2-b4: CIT-P simulate (graph traversal + semantic candidates + impact radius + consequences) ---"
$GOV cit simulate --root "$PROJ" --json --role orchestrator "$CIT_ID" 2>&1 | tee /tmp/cit-sim.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',d)
imp=r.get('impact',{})
print('radius:', imp.get('radius'))
print('seeds:', len(imp.get('seeds',[])))
print('affected count:', len(imp.get('affected',[])))
print('semantic_candidates count:', len(imp.get('semantic_candidates',[])))
print('consequences:')
for c in imp.get('consequences',[]):
    print('  -', c)
print('human_gate_required:', imp.get('human_gate_required'))
print('human_gate:', r.get('human_gate'))
" 2>&1
echo ""

GATE=$(python3 -c "import json; d=json.load(open('/tmp/cit-sim.json')); r=d.get('result',d); print(r.get('human_gate') or '')" 2>/dev/null || echo "")
echo "Gate: '$GATE'"

if [ -n "$GATE" ] && [ "$GATE" != "None" ] && [ "$GATE" != "null" ]; then
  echo "--- Present gate ---"
  $GOV gate present --root "$PROJ" --json --role orchestrator "$GATE" 2>&1 | head -5
  echo ""
  echo "--- Answer gate (human approval) ---"
  $GOV decide --root "$PROJ" --json --role human "$GATE" --option A --by human --rationale "Approved for audit" 2>&1 | head -10
  echo ""
  echo "--- Approve CIT ---"
  $GOV cit approve --root "$PROJ" --json --role orchestrator "$CIT_ID" --by orchestrator --method human 2>&1 | head -10
  echo ""
  echo "--- Execute CIT-E ---"
  $GOV cit execute --root "$PROJ" --json --role orchestrator "$CIT_ID" 2>&1 | tee /tmp/cit-exec.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',d)
print('cit_status:', r.get('cit_status'))
print('propagation keys:', list(r.get('propagation',{}).keys()))
print('checkpoint:', r.get('checkpoint'))
" 2>&1
  echo ""
  echo "--- Rollback CIT ---"
  $GOV cit rollback --root "$PROJ" --json --role orchestrator "$CIT_ID" --reason "audit rollback test" 2>&1 | head -10
else
  echo "No gate raised (auto-approve path)"
  echo "--- Approve CIT (auto) ---"
  $GOV cit approve --root "$PROJ" --json --role orchestrator "$CIT_ID" --by orchestrator --method auto 2>&1 | head -10
  echo ""
  echo "--- Execute CIT-E ---"
  $GOV cit execute --root "$PROJ" --json --role orchestrator "$CIT_ID" 2>&1 | tee /tmp/cit-exec.json | head -20
  echo ""
  echo "--- Rollback CIT ---"
  $GOV cit rollback --root "$PROJ" --json --role orchestrator "$CIT_ID" --reason "audit rollback test" 2>&1 | head -10
fi

echo ""
echo "RESULT: CIT lifecycle exercised end-to-end"
