#!/bin/bash
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== D6: Rebuild Guarantee (Thorough) ==="

echo "--- Save authoritative state snapshot ---"
echo "Authoritative records:"
find spec/ -name "*.yaml" | sort | head -20
echo ""
echo "Claims before rebuild:"
$GOV claims list --json 2>&1 | python3 -c "import json,sys; print(json.load(sys.stdin)['result'])"

echo ""
echo "--- Save index manifest before ---"
BEFORE_HASH=$(cat governance/generated/index-manifest.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('manifest_hash',''))")
echo "Manifest hash before: $BEFORE_HASH"

echo ""
echo "--- Delete all derived state ---"
RUNTIME=$(ls -d .gov-os 2>/dev/null || echo ".governance-runtime")
echo "Runtime dir: $RUNTIME"
if [ -d "$RUNTIME" ]; then
    rm -rf "$RUNTIME"
    echo "Deleted runtime directory"
fi
# Also delete generated manifests
rm -f governance/generated/index-manifest.json governance/generated/memory-manifest.json
echo "Deleted generated manifests"

echo ""
echo "--- gov status after deleting derived state ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Records: {d[\"records\"]}')
print(f'Memory fresh: {d[\"memory\"][\"index_fresh\"]}')
print(f'Memory present: {d[\"memory\"][\"runtime_present\"]}')
print(f'Tasks: {d[\"tasks\"][\"counts\"]}')
"

echo ""
echo "--- Full rebuild from scratch ---"
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Mode: {d[\"mode\"]}')
print(f'Indexed: {d[\"indexed\"]}')
print(f'Problems: {d[\"problems\"]}')
print(f'Degradations: {d[\"degradations\"]}')
print(f'Manifest hash: {d[\"manifest_hash\"]}')
"

echo ""
echo "--- Verify authoritative state preserved ---"
echo "Records still exist in Git:"
ls spec/decisions/D-001.yaml spec/features/F-001.yaml spec/tasks/TASK-001.yaml 2>&1

echo ""
echo "--- Verify status works after rebuild ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Records: {d[\"records\"]}')
print(f'Memory fresh: {d[\"memory\"][\"index_fresh\"]}')
print(f'Tasks: {d[\"tasks\"][\"counts\"]}')
"

echo ""
echo "--- Compare manifest hash ---"
AFTER_HASH=$(cat governance/generated/index-manifest.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('manifest_hash',''))")
echo "Manifest hash after: $AFTER_HASH"
echo "Match: $([ "$BEFORE_HASH" = "$AFTER_HASH" ] && echo 'YES' || echo 'NO (expected if file timestamps differ)')"

echo ""
echo "--- Verify held-out regression after rebuild ---"
$GOV memory verify --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Recall@K: {d[\"recall_at_k\"]}')
print(f'Pass: {d[\"pass\"]}')
"

echo ""
echo "--- Rebuild at different path (copy project, rebuild) ---"
ALTDIR="$DIR/../greenfield-alt"
if [ -d "$ALTDIR" ]; then rm -rf "$ALTDIR"; fi
cp -r "$DIR" "$ALTDIR"
cd "$ALTDIR"
# Delete runtime in copy
rm -rf .gov-os .governance-runtime
rm -f governance/generated/index-manifest.json governance/generated/memory-manifest.json
$GOV rebuild-memory --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
print(f'Alt path rebuild - Mode: {d[\"mode\"]}')
print(f'Alt path rebuild - Indexed: {d[\"indexed\"]}')
print(f'Alt path rebuild - Manifest hash: {d[\"manifest_hash\"]}')
"
ALT_HASH=$(cat governance/generated/index-manifest.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('manifest_hash',''))")
echo "Alt manifest hash: $ALT_HASH"
echo "Match original: $([ "$AFTER_HASH" = "$ALT_HASH" ] && echo 'YES' || echo 'NO')"
cd "$DIR"

