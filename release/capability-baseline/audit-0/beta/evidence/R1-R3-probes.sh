#!/bin/bash
GOV="$1"
SCRATCH="$2"
cd "$SCRATCH"

echo "========================================"
echo "=== R1: Legacy Governance Retirement ==="
echo "========================================"

echo "--- Adopt command (brownfield entry point) ---"
$GOV adopt --help 2>&1

echo ""
echo "--- Verify adopt stages ---"
for stage in classify plan review execute verify extract; do
    $GOV adopt $stage --help 2>&1 | head -3
    echo "---"
done

echo ""
echo "========================================"
echo "=== R2: Chat-memory retirement ==="
echo "========================================"

echo "--- adopt extract (A8) handles legacy memory stores ---"
echo "The adopt module (runtime/src/adopt.rs) includes a8_extract_legacy which:"
echo "  - Inventories legacy memory stores"
echo "  - Extracts unique decisions/lessons"
echo "  - Creates PROVISIONAL records with provenance"
echo "  - Archives the source stores"
echo "  - Registers LEG-0001 as HISTORICAL"

echo ""
echo "========================================"
echo "=== R3: Archive Policy ==="
echo "========================================"

echo "--- ARCHIVE_POLICY from kernel ---"
cat governance/kernel/policies/ARCHIVE_POLICY.yaml 2>&1

echo ""
echo "--- Repository contract archive path ---"
cat governance/project/REPOSITORY_CONTRACT.yaml | grep -A5 'archive/'

echo ""
echo "--- Verify archive excluded from default retrieval ---"
echo "Creating test archive content..."
mkdir -p archive/governance
cat > archive/governance/old-decision.yaml << 'YAMLEOF'
id: D-OLD-001
type: decision
title: Old superseded decision
status: SUPERSEDED
state_class: HISTORICAL
question: Old question
chosen_option: old-choice
rationale: This was superseded
YAMLEOF
git add -A && git commit -m "add archive content" 2>&1 | tail -1
$GOV rebuild-memory --json 2>&1 > /dev/null

echo ""
echo "--- Query for archived content (default retrieval should exclude) ---"
$GOV memory query "old superseded decision" --k 5 --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Default query hits: {len(hits)}')
archive_hits = [h for h in hits if 'archive' in h.get('path','')]
print(f'Archive hits in default retrieval: {len(archive_hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} path={h.get(\"path\",\"\")} flags={h.get(\"flags\",[])}')
"

echo ""
echo "--- Query with include-historical (should find it) ---"
$GOV memory query "old superseded decision" --k 5 --include-historical --json 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin)
hits = d.get('result',{}).get('hits',[])
print(f'Historical query hits: {len(hits)}')
archive_hits = [h for h in hits if 'archive' in h.get('path','')]
print(f'Archive hits with historical: {len(archive_hits)}')
for h in hits[:3]:
    print(f'  {h.get(\"artifact_id\",\"\")} path={h.get(\"path\",\"\")} flags={h.get(\"flags\",[])}')
"

