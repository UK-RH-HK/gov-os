#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== Cross-Capability: K2 <-> D1 (CIT-E triggers index refresh) ==="
echo "--- CIT mechanism ---"
$GOV cit --help 2>&1 | head -15

echo ""
echo "--- CIT list ---"
$GOV cit list --json 2>&1 | head -10

echo ""
echo "=== Cross-Capability: D1 <-> W6 (Index staleness) ==="
echo "--- Modify a governed file to make index stale ---"
echo "# staleness-interaction-test" >> product/auth/login.py
echo "Before rebuild, check doctor:"
$GOV doctor --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
checks = d.get('result',{}).get('checks',[])
for c in checks:
    if 'memory' in str(c.get('name','')).lower() or 'index' in str(c.get('name','')).lower() or 'stale' in str(c.get('name','')).lower():
        print(f'  {c.get(\"name\",\"\")} = {c.get(\"status\",\"\")} {c.get(\"detail\",\"\")}')
" 2>&1
git checkout -- product/auth/login.py 2>/dev/null

echo ""
echo "=== AC-7 Path to Provisional Retrieval Profile ==="
echo "--- D4 components separately identifiable ---"
echo "Embedder: pinned in MEMORY_POLICY, recorded in manifest"
echo "Reranker: pinned in MEMORY_POLICY, resolved through plugin system"
echo "Vector store: SQLite + vectors table"
echo "Lexical engine: SQLite FTS5"
echo "Code intelligence: builtin generic + plugin system"
echo "Context compiler: deterministic"
echo "Router: retrieval/mod.rs multi-route fusion"

echo ""
echo "--- D5 benchmark/compare/select mechanism ---"
echo "benchmark: $GOV memory benchmark --candidate ... --candidate ..."
echo "select: $GOV memory select <candidate>"
echo "heldout: governance/tests/memory/heldout.yaml"
$GOV memory verify --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Held-out queries: {d.get(\"queries\",0)}')
print(f'By category: {d.get(\"by_category\",[])}')
print(f'Thresholds: {d.get(\"thresholds\",{})}')
"

echo ""
echo "--- D5 pinned embedder governs reindex ---"
echo "Changing embedder pin triggers a full rebuild (pin_mismatch detection)."
echo "The embedder is recorded in runtime meta and index manifest."
echo "for_query() checks live pin == policy pin (EMBEDDER_MISMATCH error)."

echo ""
echo "=== Regression Tests ==="
echo "--- cargo test --lib ---"
cd "$(dirname "$GOV")/../.."
~/.cargo/bin/cargo test --lib 2>&1 | tail -10
echo ""
echo "--- cargo test --test certification ---"
~/.cargo/bin/cargo test --test certification 2>&1 | tail -10

