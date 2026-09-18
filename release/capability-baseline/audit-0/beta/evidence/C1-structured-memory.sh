#!/bin/bash
set -e
GOV="$1"
DIR="$2"
cd "$DIR"

echo "=== C1: Deterministic Structured Memory ==="
echo "--- gov status --json to verify record tracking ---"
$GOV status --json 2>&1 | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Records tracked: {d[\"result\"][\"records\"]}')
print(f'Memory fresh: {d[\"result\"][\"memory\"][\"index_fresh\"]}')
print(f'Tasks: {d[\"result\"][\"tasks\"]}')
"

echo ""
echo "--- Query record types indexed ---"
$GOV memory query --sql "SELECT record_type, COUNT(*) as cnt FROM artifacts WHERE record_type IS NOT NULL GROUP BY record_type ORDER BY record_type" 2>&1

echo ""
echo "--- Verify 17 record kinds are representable ---"
echo "Record types from the codebase TYPE_DIR mapping:"
echo "project, feature, requirement, decision, task, scenario, test-obligation, interface, experiment, lesson, report, research, human-gate, cit, checkpoint, handoff, audit"
echo ""
echo "Records created and indexed:"
for type in project feature requirement decision task scenario test-obligation interface experiment lesson research; do
    count=$($GOV memory query --sql "SELECT COUNT(*) as c FROM artifacts WHERE record_type='$type'" 2>&1 | grep -oP '\d+' | head -1)
    echo "  $type: ${count:-0}"
done

echo ""
echo "--- Verify artifact provenance (content_hash, namespace, state_class) ---"
$GOV memory query --sql "SELECT artifact_id, record_type, state_class, namespace, content_hash IS NOT NULL as has_hash FROM artifacts WHERE record_type != 'file' LIMIT 15" 2>&1

echo ""
echo "--- Verify derived DB is separate from authoritative Git records ---"
echo "Authoritative: spec/ directory with YAML files"
ls spec/decisions/D-001.yaml spec/features/F-001.yaml spec/tasks/TASK-001.yaml 2>&1
echo "Derived: .gov-os/state.db"
ls -la .gov-os/state.db 2>&1
