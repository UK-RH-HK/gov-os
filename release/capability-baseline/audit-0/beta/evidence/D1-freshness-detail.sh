#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== D1 Freshness Detailed Investigation ==="

echo "--- Check if source files are indexed ---"
cat governance/generated/index-manifest.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
arts = d.get('artifacts',{})
src_files = [p for p in arts if p.startswith('src/')]
print(f'Source files indexed: {len(src_files)}')
for f in sorted(src_files)[:10]:
    print(f'  {f}')
print()
all_types = {}
for p,info in arts.items():
    rt = info.get('record_type','')
    all_types[rt] = all_types.get(rt,0)+1
print(f'Artifact types:')
for k,v in sorted(all_types.items()):
    print(f'  {k}: {v}')
"

echo ""
echo "--- Check what the contract says about indexing ---"
cat governance/kernel/contracts/governance-capability-acceptance.yaml 2>/dev/null | head -30 || echo "no contract yaml found"

echo ""
echo "--- Check if src/ files exist in the freshness check ---"
echo "Testing freshness with uncommitted modification to login.py..."
echo "# test-change-$(date +%s)" >> src/auth/login.py
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh: {d[\"fresh\"]}')
print(f'Stale: {d[\"stale\"]}')
print(f'Checked: {d[\"checked\"]}')
"
git checkout -- src/auth/login.py 2>/dev/null

echo ""
echo "--- Check what governance/kernel/constitution/PATH_MAP.yaml says ---"
cat governance/kernel/constitution/PATH_MAP.yaml 2>/dev/null | head -40

echo ""
echo "--- Check excluded from index ---"
cat governance/generated/index-manifest.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
exc = d.get('excluded',[])
print(f'Excluded from index: {len(exc)}')
for e in exc[:10]:
    print(f'  {e}')
"

