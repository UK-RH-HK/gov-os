#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== Doctor checks relevant to beta family ==="
$GOV doctor --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
checks = d.get('result',{}).get('checks',[])
print(f'Total checks: {len(checks)}')
for c in checks:
    status = c.get('status','')
    name = c.get('name','')
    detail = c.get('detail','')
    print(f'  [{status}] {name}: {detail}')
"

echo ""
echo "=== C5 Code-structural memory - symbol extraction detail ==="
$GOV memory query "login" --k 5 --route symbol --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Symbol hits for \"login\": {len(hits)}')
for h in hits:
    print(f'  {h.get(\"artifact_id\",\"\")} path={h.get(\"path\",\"\")} section={h.get(\"section\",\"\")} level={h.get(\"level\",\"\")}')
"

echo ""
echo "=== C5 - verify language adapters resolved via capability registry ==="
echo "Capability ecosystems:"
$GOV capabilities ecosystems --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
eco = d.get('result',{})
print(json.dumps(eco, indent=2)[:800])
"

echo ""
echo "=== C6 Temporal - supersession/version lineage ==="
# Create a superseding decision
cat > spec/decisions/D-002.yaml << 'EOF'
id: D-002
type: decision
title: Use argon2id for password hashing
status: ACTIVE
state_class: AUTHORITATIVE
question: Which hashing algorithm for passwords?
chosen_option: argon2id
rationale: More modern and memory-hard than bcrypt
supersedes:
  - D-001
EOF
git add spec/decisions/D-002.yaml && git commit -m "supersede D-001 with D-002" 2>&1 | tail -1
$GOV rebuild-memory --json 2>&1 > /dev/null

echo "--- Verify supersession tracking ---"
$GOV memory query "D-001" --k 3 --route structured --include-historical --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'D-001 query hits: {len(hits)}')
for h in hits:
    print(f'  {h[\"artifact_id\"]} status={h.get(\"status\",\"\")} flags={h.get(\"flags\",[])}')
"
echo ""
$GOV memory query "D-002" --k 3 --route structured --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'D-002 query hits: {len(hits)}')
for h in hits:
    print(f'  {h[\"artifact_id\"]} status={h.get(\"status\",\"\")} flags={h.get(\"flags\",[])}')
"

echo ""
echo "=== C9 Working Memory - verify context packet with conflicting decisions ==="
$GOV context compile TASK-001 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
det = d.get('deterministic_authority',{})
print(f'Active decisions: {len(det.get(\"active_decisions\",[]))}')
for dec in det.get('active_decisions',[]):
    print(f'  {dec.get(\"id\",\"\")} title={dec.get(\"title\",\"\")}')
print(f'Conflicting decisions: {len(det.get(\"conflicting_decisions\",[]))}')
for dec in det.get('conflicting_decisions',[]):
    print(f'  {dec.get(\"id\",\"\")} title={dec.get(\"title\",\"\")} flag={dec.get(\"authority_flag\",\"\")}')
"

echo ""
echo "=== C9 - duplicate suppression, bounded size ==="
$GOV context compile TASK-001 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Chars: {d.get(\"chars\",0)}')
print(f'Truncated slices: {d.get(\"truncated_slices\",\"none\")}')
print(f'Packet ID: {d.get(\"packet_id\",\"\")}')
ret = d.get('retrieved_intelligence',{})
ranked = ret.get('ranked_evidence',[])
ids = [h['artifact_id'] for h in ranked]
unique_ids = set(ids)
print(f'Retrieved evidence items: {len(ranked)}')
print(f'Unique artifact IDs: {len(unique_ids)}')
dupes = len(ranked) - len(unique_ids)
print(f'Duplicate artifact IDs: {dupes}')
"

echo ""
echo "=== C10 Capability Memory - environment/tool versions ==="
$GOV tools list --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
tools = d.get('result',{}).get('tools',[])
print(f'Registered tools: {len(tools)}')
for t in tools[:5]:
    print(f'  {t.get(\"tool_id\",\"\")} {t.get(\"name\",\"\")} type={t.get(\"type\",\"\")}')
"

echo ""
echo "=== Adopter routes for R1 legacy retirement ==="
$GOV adopt status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
r = d.get('result',{})
print(f'Adoption stage: {r.get(\"stage\",\"\")}')
print(f'Status: {r.get(\"status\",\"\")}')
" 2>&1

