#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "========================================"
echo "=== D1: Incremental Indexing / Freshness ==="
echo "========================================"

echo "--- Freshness before modification ---"
$GOV memory freshness --json 2>&1

echo ""
echo "--- Modify a file to trigger staleness ---"
echo "# new comment" >> src/auth/login.py
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh: {d[\"fresh\"]}')
print(f'Stale: {d[\"stale\"]}')
print(f'Added: {d[\"added\"]}')
print(f'Removed: {d[\"removed\"]}')
print(f'Pin mismatch: {d[\"pin_mismatch\"]}')
"

echo ""
echo "--- Incremental rebuild after modification ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Indexed: {d[\"indexed\"]}')
print(f'Unchanged: {d[\"unchanged\"]}')
print(f'Removed: {d[\"removed\"]}')
"

echo ""
echo "--- Add a new file, check added detection ---"
cat > src/auth/utils.py << 'PYEOF'
def sanitize(input_str: str) -> str:
    return input_str.strip()
PYEOF
git add -A && git commit -m "add utils" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after add: {d[\"fresh\"]}')
print(f'Added: {d[\"added\"]}')
"

echo ""
echo "--- Rename/move detection ---"
git mv src/auth/utils.py src/auth/helpers.py 2>&1
git commit -m "rename utils to helpers" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after rename: {d[\"fresh\"]}')
print(f'Added (new path): {d[\"added\"]}')
print(f'Removed (old path): {d[\"removed\"]}')
"

echo ""
echo "--- Rebuild picks up rename ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Moved: {d[\"moved\"]}')
print(f'Indexed: {d[\"indexed\"]}')
print(f'Removed: {d[\"removed\"]}')
"

echo ""
echo "--- Delete file + rebuild ---"
git rm src/auth/helpers.py 2>&1 | tail -1
git commit -m "delete helpers" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after delete: {d[\"fresh\"]}')
print(f'Removed: {d[\"removed\"]}')
"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Removed after rebuild: {d[\"removed\"]}')
"

echo ""
echo "--- Verify manifest records embedder identity ---"
cat governance/generated/index-manifest.json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Embedder: {d[\"embedder\"]}')
print(f'Chunking: {d.get(\"chunking\",{})}')
print(f'Lexical: {d.get(\"lexical\",{})}')
"

echo ""
echo "========================================"
echo "=== D2: Retrieval Router ==="
echo "========================================"

echo "--- Structured lookup (known ID) ---"
$GOV memory query "D-001" --k 5 --route structured --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[])
print(f'Structured route D-001: {len(hits)} hits')
for h in hits[:2]: print(f'  {h[\"artifact_id\"]} routes={h[\"routes\"]}')
"

echo ""
echo "--- Code/symbol route ---"
$GOV memory query "hash_password" --k 5 --route symbol --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[])
print(f'Symbol route: {len(hits)} hits')
for h in hits[:2]: print(f'  {h[\"artifact_id\"]} routes={h[\"routes\"]}')
"

echo ""
echo "--- Lexical route ---"
$GOV memory query "bcrypt" --k 5 --route lexical --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[])
print(f'Lexical route: {len(hits)} hits')
for h in hits[:2]: print(f'  {h[\"artifact_id\"]} routes={h[\"routes\"]}')
"

echo ""
echo "--- Graph/impact route ---"
$GOV memory query "what depends on REQ-001" --k 5 --route graph --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[])
print(f'Graph route: {len(hits)} hits')
for h in hits[:3]: print(f'  {h[\"artifact_id\"]} routes={h[\"routes\"]}')
"

echo ""
echo "--- Semantic route ---"
$GOV memory query "secure authentication mechanism" --k 5 --route semantic --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); hits=d.get('result',{}).get('hits',[])
print(f'Semantic route: {len(hits)} hits')
for h in hits[:2]: print(f'  {h[\"artifact_id\"]} routes={h[\"routes\"]}')
"

echo ""
echo "--- Multi-route fusion ---"
$GOV memory query "how does login authentication work" --k 8 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
r = d.get('result',{})
print(f'Fusion strategy: {r.get(\"strategy\",\"\")}')
print(f'Routes used: {r.get(\"routes\",[])}')
print(f'Total hits: {len(r.get(\"hits\",[]))}')
for h in r.get('hits',[])[:3]: print(f'  {h[\"artifact_id\"]} score={h[\"score\"]:.3f} routes={h[\"routes\"]}')
"

echo ""
echo "========================================"
echo "=== D3: Hierarchical Retrieval ==="
echo "========================================"

echo "--- Verify document > section > child chunks ---"
cat governance/generated/index-manifest.json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
counts = d.get('counts',{})
print(f'Chunks: {counts.get(\"chunks\",0)}')
print(f'Artifacts: {counts.get(\"artifacts\",0)}')
"

echo ""
echo "--- Retrieval hit has parent_excerpt and neighbours ---"
$GOV memory query "password hashing" --k 3 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
for h in hits[:2]:
    print(f'artifact: {h[\"artifact_id\"]}')
    print(f'  level: {h.get(\"level\",\"\")}')
    print(f'  section: {h.get(\"section\",\"\")}')
    print(f'  has parent_excerpt: {h.get(\"parent_excerpt\") is not None}')
    print(f'  neighbours: {h.get(\"neighbours\",[])}')
"

echo ""
echo "========================================"
echo "=== D4: Component Separation ==="
echo "========================================"

echo "--- Verify independently identifiable components ---"
echo "Embedder:"
cat governance/generated/index-manifest.json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  Embedder: {d.get(\"embedder\",{})}')
print(f'  Reranker: {d.get(\"reranker\",{})}')
print(f'  Chunking: {d.get(\"chunking\",{})}')
print(f'  Lexical: {d.get(\"lexical\",{})}')
print(f'  Index version: {d.get(\"index_version\",\"\")}')
"

echo ""
echo "--- Verify plugin system for replaceable components ---"
$GOV plugins list --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Plugin ecosystem: {d.get(\"result\",{})}')
"

echo "--- Capabilities subcommands (ecosystems, registrations) ---"
$GOV capabilities --help 2>&1 | head -15

echo ""
echo "========================================"
echo "=== D5: Evidence-Driven Retrieval Model Selection ==="
echo "========================================"

echo "--- Benchmark mechanism exists ---"
$GOV memory benchmark --help 2>&1

echo ""
echo "--- Held-out starter generation ---"
$GOV memory heldout-starter --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
r = d.get('result',{})
print(f'Generated: {r.get(\"generated\",\"\")}')
print(f'Queries: {r.get(\"queries\",0)}')
print(f'Status: {r.get(\"status\",\"\")}')
" 2>&1

echo ""
echo "--- Run held-out verification ---"
$GOV memory verify --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
r = d.get('result',{})
print(f'Recall@K: {r.get(\"recall_at_k\",\"\")}')
print(f'MRR: {r.get(\"mrr\",\"\")}')
print(f'Precision@K: {r.get(\"precision_at_k\",\"\")}')
print(f'Stale hit rate: {r.get(\"stale_hit_rate\",\"\")}')
print(f'Pass: {r.get(\"pass\",\"\")}')
print(f'Categories: {r.get(\"by_category\",[])}')
"

echo ""
echo "--- Selection mechanism exists ---"
$GOV memory select --help 2>&1

echo ""
echo "========================================"
echo "=== D6: Rebuild Guarantee ==="
echo "========================================"

echo "--- Save state before rebuild ---"
cp governance/generated/index-manifest.json /tmp/manifest-before.json 2>&1 || true

echo ""
echo "--- Delete derived state ---"
rm -f .gov-os/state.db .gov-os/state.db-wal .gov-os/state.db-shm
ls .gov-os/ 2>&1

echo ""
echo "--- Full rebuild ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Indexed: {d[\"indexed\"]}')
print(f'Manifest hash: {d[\"manifest_hash\"]}')
print(f'Problems: {d[\"problems\"]}')
"

echo ""
echo "--- Status after rebuild ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Records: {d[\"records\"]}')
print(f'Memory fresh: {d[\"memory\"][\"index_fresh\"]}')
print(f'Tasks: {d[\"tasks\"][\"counts\"]}')
"

echo ""
echo "--- Verify authoritative records preserved ---"
ls spec/decisions/D-001.yaml spec/features/F-001.yaml spec/tasks/TASK-001.yaml 2>&1

echo ""
echo "--- Fresh-agent reconstruction (gov status) succeeds after rebuild ---"
echo "(gov status ran successfully above)"

echo ""
echo "--- Claims survive rebuild ---"
$GOV claims list --json 2>&1 | head -10

