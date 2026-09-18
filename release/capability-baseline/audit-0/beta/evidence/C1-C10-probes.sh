#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "========================================"
echo "=== C1: Deterministic Structured Memory ==="
echo "========================================"

echo "--- gov status shows tracked record count ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Records: {d[\"records\"]}')
print(f'Index fresh: {d[\"memory\"][\"index_fresh\"]}')
"

echo ""
echo "--- All 17 record kinds representable (gov status reconstructs from Git) ---"
echo "Verify by querying each record type via retrieval:"
for type in PRJ F REQ D TASK SCN TST API EXP L RES; do
    result=$($GOV memory query "${type}-001" --k 3 --route structured --json 2>&1)
    found=$(echo "$result" | python3 -c "import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[]); print(len([h for h in hits if '${type}-' in h.get('artifact_id','')]))" 2>/dev/null || echo "0")
    echo "  ${type}-001: found=$found"
done

echo ""
echo "--- Verify statuses tracked ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Task statuses: {d[\"tasks\"][\"counts\"]}')
print(f'Features: {len(d[\"features\"])}')
print(f'Human gates: {len(d[\"human_gates\"])}')
"

echo ""
echo "--- Verify claims table exists ---"
$GOV claims --help 2>&1 | head -5

echo ""
echo "--- Verify tool/skill tracking ---"
$GOV tools --help 2>&1 | head -3
$GOV skills --help 2>&1 | head -3

echo ""
echo "--- Index manifest (version tracking) ---"
cat governance/generated/index-manifest.json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Index version: {d.get(\"index_version\")}')
print(f'Artifact count: {len(d.get(\"artifacts\",{}))}')
print(f'Manifest hash: {d.get(\"manifest_hash\",\"\")}')
print(f'Embedder: {d.get(\"embedder\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C2: Relationship/Graph Memory ==="
echo "========================================"

echo "--- Verify typed relationships ---"
$GOV memory graph --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
data = d.get('result',{})
print(f'Edge type counts: {data.get(\"edge_types\",{})}')
print(f'Orphan nodes: {data.get(\"orphan_nodes\",[])}')
print(f'Dangling edges: {len(data.get(\"dangling_edges\",[]))}')
" 2>&1

echo ""
echo "--- Verify impact traversal ---"
$GOV memory impact "REQ-001" --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
data = d.get('result',{})
print(f'Impact set for REQ-001: {len(data.get(\"impact\",[]))} nodes')
for n in data.get('impact',[]):
    print(f'  {n}')
" 2>&1

echo ""
echo "========================================"
echo "=== C3: Semantic Memory ==="
echo "========================================"

echo "--- Semantic query: decision rationale ---"
$GOV memory query "password hashing rationale" --k 5 --route semantic --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Semantic hits for \"password hashing rationale\": {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} score={h.get(\"score\",0):.3f} route={h.get(\"routes\",[])}')
" 2>&1

echo ""
echo "--- Semantic query: lesson about security ---"
$GOV memory query "preventing brute force attacks" --k 5 --route semantic --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Semantic hits for \"brute force\": {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} score={h.get(\"score\",0):.3f}')
" 2>&1

echo ""
echo "--- Verify namespace/authority filters ---"
$GOV memory query "password hashing" --k 5 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
r = d.get('result',{})
print(f'Excluded by authority: {r.get(\"excluded_by_authority\",0)}')
print(f'Excluded by namespace: {r.get(\"excluded_by_namespace\",0)}')
print(f'Embedder: {r.get(\"embedder\",{})}')
print(f'Index manifest hash: {r.get(\"index_manifest_hash\",\"\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C4: Lexical Memory ==="
echo "========================================"

echo "--- Lexical exact query: identifier ---"
$GOV memory query "hash_password" --k 5 --route lexical --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Lexical hits for \"hash_password\": {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} score={h.get(\"score\",0):.3f} route={h.get(\"routes\",[])}')
" 2>&1

echo ""
echo "--- Lexical exact query: error string ---"
$GOV memory query "\"Missing credentials\"" --k 5 --route lexical --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Lexical hits for error string: {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"path\",\"\")} score={h.get(\"score\",0):.3f}')
" 2>&1

echo ""
echo "--- Lexical exact query: filename ---"
$GOV memory query "login.py" --k 5 --route path --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Path hits for \"login.py\": {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"path\",\"\")} id={h.get(\"artifact_id\",\"\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C5: Code-Structural Memory ==="
echo "========================================"

echo "--- Symbol query ---"
$GOV memory query "hash_password" --k 5 --route symbol --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Symbol hits for \"hash_password\": {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} path={h.get(\"path\",\"\")} score={h.get(\"score\",0):.3f}')
" 2>&1

echo ""
echo "--- Verify code intelligence extracted symbols ---"
$GOV memory verify --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
data = d.get('result',{})
print(f'Verify result: {json.dumps(data, indent=2)[:1000]}')
" 2>&1

echo ""
echo "========================================"
echo "=== C6: Temporal Memory ==="
echo "========================================"

echo "--- Verify temporal tracking (what changed, when, why) ---"
echo "CIT mechanism tracks changes:"
$GOV cit --help 2>&1 | head -5

echo ""
echo "--- Index records repo_commit ---"
cat governance/generated/index-manifest.json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Repo commit: {d.get(\"repo_commit\",\"\")}')
print(f'Built at: {d.get(\"built_at\",\"\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C7: Episodic Execution Memory ==="
echo "========================================"

echo "--- Verify session/claims tracking ---"
$GOV claims --json 2>&1 | head -20

echo ""
echo "--- Checkpoints ---"
$GOV checkpoint --help 2>&1 | head -5

echo ""
echo "--- Handoffs ---"  
$GOV handoff --help 2>&1 | head -5

echo ""
echo "========================================"
echo "=== C8: Failure Memory ==="
echo "========================================"

echo "--- Verify lesson records with failure tags ---"
$GOV memory query "rate limiting brute force" --k 5 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Lesson retrieval hits: {len(hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} type={h.get(\"record_type\",\"\")} state={h.get(\"state_class\",\"\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C9: Working Memory / Context Packet ==="
echo "========================================"

echo "--- Compile context for TASK-001 ---"
$GOV context compile TASK-001 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
pkt = d.get('result',{})
print(f'Packet ID: {pkt.get(\"packet_id\",\"\")}')
print(f'Chars: {pkt.get(\"chars\",0)}')
print(f'Packet hash: {pkt.get(\"packet_hash\",\"\")[:16]}...')
print(f'Deterministic hash: {pkt.get(\"deterministic_hash\",\"\")[:16]}...')
det = pkt.get('deterministic_authority',{})
print(f'Authority layers: {len(det.get(\"authority_layers\",[]))}')
print(f'Active decisions: {len(det.get(\"active_decisions\",[]))}')
print(f'Requirements: {len(det.get(\"governing_requirements\",[]))}')
print(f'Prohibited writes: {len(det.get(\"prohibited_writes\",[]))}')
ret = pkt.get('retrieved_intelligence',{})
print(f'Retrieved evidence: {len(ret.get(\"ranked_evidence\",[]))}')
print(f'Routes used: {ret.get(\"routes\",[])}')
print(f'Strategy: {ret.get(\"retrieval_strategy\",\"\")}')
print(f'Index version: {ret.get(\"index_snapshot\",{}).get(\"index_version\",\"\")}')
" 2>&1

echo ""
echo "========================================"
echo "=== C10: Capability Memory ==="
echo "========================================"

echo "--- List tools ---"
$GOV tools list --json 2>&1 | head -10

echo "--- List skills ---"
$GOV skills list --json 2>&1 | head -10

echo "--- List plugins ---"
$GOV plugins list --json 2>&1 | head -10

echo "--- Capability table in DB ---"
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Memory freshness: {json.dumps(d.get(\"result\",{}), indent=2)[:500]}')
" 2>&1

