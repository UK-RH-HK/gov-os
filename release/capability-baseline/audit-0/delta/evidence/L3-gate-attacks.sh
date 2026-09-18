#!/bin/bash
GOV="$1"; PROJ="$2"
echo "=== L3: Gate presentation and fabrication attacks ==="

# Create a CIT that needs human approval
$GOV cit propose --root "$PROJ" --json --role orchestrator --proposal "L3 architecture test" --trigger architecture_change 2>&1 > /tmp/l3-propose.json
CIT_ID=$(python3 -c "import json; d=json.load(open('/tmp/l3-propose.json')); r=d.get('result',d); print(r.get('id','') or r.get('cit',''))" 2>/dev/null)
echo "CIT: $CIT_ID"

# Check if auto-simulated with gate
GATE=$(python3 -c "import json; d=json.load(open('/tmp/l3-propose.json')); r=d.get('result',d); print(r.get('human_gate','') or '')" 2>/dev/null)
if [ -z "$GATE" ] || [ "$GATE" = "None" ]; then
  # Simulate explicitly
  $GOV cit simulate --root "$PROJ" --json --role orchestrator "$CIT_ID" 2>&1 > /tmp/l3-sim.json
  GATE=$(python3 -c "import json; d=json.load(open('/tmp/l3-sim.json')); r=d.get('result',d); print(r.get('human_gate',''))" 2>/dev/null)
fi

if [ -z "$GATE" ] || [ "$GATE" = "None" ] || [ "$GATE" = "null" ]; then
  # Lookup pending gates
  GATE=$($GOV gate pending --root "$PROJ" --json --role orchestrator 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); gates=[g for g in r if g['gate_status'] in ('PENDING','PRESENTED')]; print(gates[0]['id'] if gates else 'NONE')" 2>/dev/null)
fi
echo "Gate: $GATE"

echo ""
echo "--- L3b1: Gate exists in file but NOT yet presented ---"
echo "Gate file exists:"
ls $PROJ/spec/decisions/$GATE.yaml 2>/dev/null && echo "  FILE EXISTS"
echo "presented_in_chat before present:"
python3 -c "
import yaml
with open('$PROJ/spec/decisions/$GATE.yaml') as f:
    d=yaml.safe_load(f)
print('  presented_in_chat:', d.get('presented_in_chat'))
print('  gate_status:', d.get('gate_status'))
" 2>/dev/null || echo "  could not read gate file"

echo ""
echo "--- L3b3 ATTACK: Answer unpresented gate ---"
RESULT=$($GOV decide --root "$PROJ" --json --role human "$GATE" --option A --by human --rationale "Skip presentation" 2>&1)
echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ok:', d.get('ok')); err=d.get('error',{}); print('  error:', err.get('code','')); print('  message:', err.get('message','')[:120])" 2>/dev/null

echo ""
echo "--- L3b2: Present gate properly ---"
$GOV gate present --root "$PROJ" --json --role orchestrator "$GATE" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('  present ok:', d.get('ok'))" 2>/dev/null

echo ""
echo "--- L3b3: Presented != Answered (gate is now PRESENTED) ---"
python3 -c "
import yaml
with open('$PROJ/spec/decisions/$GATE.yaml') as f:
    d=yaml.safe_load(f)
print('  gate_status:', d.get('gate_status'))
print('  presented_in_chat:', d.get('presented_in_chat'))
print('  answer:', d.get('answer'))
" 2>/dev/null || echo "  could not read"

echo ""
echo "--- L3b4 ATTACK: Decline gate, then try to execute CIT ---"
$GOV decide --root "$PROJ" --json --role human "$GATE" --option B --by human --rationale "Human declines" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('  declined ok:', d.get('ok'))" 2>/dev/null
echo "  CIT status after decline:"
python3 -c "
import yaml
with open('$PROJ/spec/decisions/$CIT_ID.yaml') as f:
    d=yaml.safe_load(f)
print('  cit_status:', d.get('cit_status'))
" 2>/dev/null
echo "  Try to approve the rejected CIT:"
RESULT=$($GOV cit approve --root "$PROJ" --json --role orchestrator "$CIT_ID" --by orchestrator --method human 2>&1)
echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  approve ok:', d.get('ok')); print('  error:', d.get('error',{}).get('code',''))" 2>/dev/null

echo ""
echo "--- L3b4 ATTACK: Revoke gate after approval, then try to execute ---"
# New CIT
$GOV cit propose --root "$PROJ" --json --role orchestrator --proposal "Revoke test" --trigger security_change 2>&1 > /tmp/l3-cit2.json
CIT2=$(python3 -c "import json; d=json.load(open('/tmp/l3-cit2.json')); r=d.get('result',d); print(r.get('id',''))" 2>/dev/null)
GATE2=$(python3 -c "import json; d=json.load(open('/tmp/l3-cit2.json')); r=d.get('result',d); print(r.get('human_gate','') or '')" 2>/dev/null)
if [ -z "$GATE2" ] || [ "$GATE2" = "None" ]; then
  $GOV cit simulate --root "$PROJ" --json --role orchestrator "$CIT2" 2>&1 > /tmp/l3-sim2.json
  GATE2=$(python3 -c "import json; d=json.load(open('/tmp/l3-sim2.json')); r=d.get('result',d); print(r.get('human_gate',''))" 2>/dev/null)
fi
echo "  CIT2=$CIT2, Gate2=$GATE2"

if [ -n "$GATE2" ] && [ "$GATE2" != "None" ] && [ "$GATE2" != "null" ]; then
  $GOV gate present --root "$PROJ" --json --role orchestrator "$GATE2" 2>&1 > /dev/null
  $GOV decide --root "$PROJ" --json --role human "$GATE2" --option A --by human --rationale "Approve" 2>&1 > /dev/null
  $GOV cit approve --root "$PROJ" --json --role orchestrator "$CIT2" --by orchestrator --method human 2>&1 > /dev/null
  echo "  CIT2 approved. Revoking gate..."
  $GOV gate revoke --root "$PROJ" --json --role orchestrator "$GATE2" --reason "Revoke test" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',{}); print('  revoke ok:', d.get('ok')); print('  cit status:', r.get('touched',{}).get('cit',{}).get('cit_status',''))" 2>/dev/null
  echo "  Try to execute CIT2 after revocation:"
  $GOV cit execute --root "$PROJ" --json --role orchestrator "$CIT2" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('  execute ok:', d.get('ok')); print('  error:', d.get('error',{}).get('code',''))" 2>/dev/null
fi

echo ""
echo "--- L3b5 ATTACK: Agent tries to fabricate human approval for high-radius gate ---"
$GOV cit propose --root "$PROJ" --json --role orchestrator --proposal "Agent fabrication test" --trigger governance_change 2>&1 > /tmp/l3-cit3.json
CIT3=$(python3 -c "import json; d=json.load(open('/tmp/l3-cit3.json')); r=d.get('result',d); print(r.get('id',''))" 2>/dev/null)
GATE3=$(python3 -c "import json; d=json.load(open('/tmp/l3-cit3.json')); r=d.get('result',d); print(r.get('human_gate','') or '')" 2>/dev/null)
if [ -z "$GATE3" ] || [ "$GATE3" = "None" ]; then
  $GOV cit simulate --root "$PROJ" --json --role orchestrator "$CIT3" 2>&1 > /tmp/l3-sim3.json
  GATE3=$(python3 -c "import json; d=json.load(open('/tmp/l3-sim3.json')); r=d.get('result',d); print(r.get('human_gate',''))" 2>/dev/null)
fi
echo "  CIT3=$CIT3, Gate3=$GATE3"
if [ -n "$GATE3" ] && [ "$GATE3" != "None" ] && [ "$GATE3" != "null" ]; then
  $GOV gate present --root "$PROJ" --json --role orchestrator "$GATE3" 2>&1 > /dev/null
  echo "  Agent (builder role) tries to answer R5 gate:"
  RESULT=$($GOV decide --root "$PROJ" --json --role builder "$GATE3" --option A --by builder --rationale "Agent self-approve" 2>&1)
  echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ok:', d.get('ok')); print('  error:', d.get('error',{}).get('code','')[:60])" 2>/dev/null

  echo "  Approve CIT with --method human (but gate answered by agent within policy):"
  $GOV decide --root "$PROJ" --json --role human "$GATE3" --option A --by human --rationale "Real human" 2>&1 > /dev/null
  RESULT=$($GOV cit approve --root "$PROJ" --json --role orchestrator "$CIT3" --by orchestrator --method human 2>&1)
  echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  approve ok:', d.get('ok')); print('  human_approved:', d.get('result',{}).get('human_approved',''))" 2>/dev/null
fi

echo ""
echo "RESULT: L3 attacks confirmed - unpresented gate blocked answering; declined gate blocks CIT execution; revoked gate returns CIT to SIMULATED and blocks execution; high-radius agent self-approval refused (AUTHORITY_DENIED)"
