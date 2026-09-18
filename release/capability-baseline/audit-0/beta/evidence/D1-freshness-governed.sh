#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== D1 Freshness with governed paths ==="

echo "--- Source files under product/ now indexed ---"
cat governance/generated/index-manifest.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
arts = d.get('artifacts',{})
prod_files = [p for p in arts if p.startswith('product/')]
print(f'Product files indexed: {len(prod_files)}')
for f in sorted(prod_files):
    print(f'  {f}')
"

echo ""
echo "--- Modify product/auth/login.py (uncommitted) ---"
echo "# freshness-test-marker" >> product/auth/login.py
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after uncommitted modification: {d[\"fresh\"]}')
print(f'Stale: {d[\"stale\"]}')
print(f'Checked: {d[\"checked\"]}')
"

echo ""
echo "--- Commit and re-check ---"
git add product/auth/login.py && git commit -m "modify login" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after committed modification: {d[\"fresh\"]}')
print(f'Stale: {d[\"stale\"]}')
"

echo ""
echo "--- Incremental rebuild ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Indexed: {d[\"indexed\"]}')
print(f'Unchanged: {d[\"unchanged\"]}')
"

echo ""
echo "--- Add new product file ---"
cat > product/auth/utils.py << 'PYEOF'
def sanitize_input(text):
    """Sanitize user input for security."""
    return text.strip().replace('<', '&lt;').replace('>', '&gt;')
PYEOF
git add product/auth/utils.py && git commit -m "add utils" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after add: {d[\"fresh\"]}')
print(f'Added: {d[\"added\"]}')
"

echo ""
echo "--- Rename product file ---"
git mv product/auth/utils.py product/auth/helpers.py
git commit -m "rename" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after rename: {d[\"fresh\"]}')
print(f'Added: {d[\"added\"]}')
print(f'Removed: {d[\"removed\"]}')
"

echo ""
echo "--- Rebuild and re-check freshness ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Moved: {d[\"moved\"]}')
"
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after rebuild: {d[\"fresh\"]}')
"

echo ""
echo "--- Delete product file ---"
git rm product/auth/helpers.py 2>&1 | tail -1
git commit -m "delete helpers" 2>&1 | tail -1
$GOV memory freshness --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Fresh after delete: {d[\"fresh\"]}')
print(f'Removed: {d[\"removed\"]}')
"

echo ""
echo "--- Symbol query for product source ---"
$GOV rebuild-memory --json 2>&1 > /dev/null
$GOV memory query "hash_password" --k 5 --route symbol --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Symbol hits for hash_password: {len(hits)}')
for h in hits[:3]:
    print(f'  {h[\"artifact_id\"]} path={h.get(\"path\",\"\")} routes={h.get(\"routes\",[])}')
"

