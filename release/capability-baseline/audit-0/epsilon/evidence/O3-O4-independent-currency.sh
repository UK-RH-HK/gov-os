#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== O3: Independent test authorship ==="
echo "--- TEST_POLICY.independent_test_author_required_for ---"
cat "$ROOT/governance/kernel/policies/TEST_POLICY.yaml" | grep independent
echo ""
echo "--- product_traceability family checks independent_of_implementer ---"
grep -n "independent_of_implementer" "$3/runtime/src/verification/mod.rs" || echo "not found"
echo ""
echo "=== O4: Governance suite currency ==="
echo "--- O4 bullet 1: green_record_currency = inputs_hash ---"
grep green_record_currency "$ROOT/governance/kernel/policies/TEST_POLICY.yaml"
echo ""
echo "--- O4 implementation: inputs_hash used to mark stale ---"
grep -n "inputs_hash" "$3/runtime/src/verification/mod.rs" | head -10
echo ""
echo "--- O4 bullet 2: task_close_requires_tests_status ---"
grep task_close "$ROOT/governance/kernel/policies/TEST_POLICY.yaml"
echo ""
echo "--- D021 doctor check: governance suite green and current ---"
$GOV doctor --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); [print(json.dumps(c,indent=2)) for c in d['result']['checks'] if c['id']=='D021']"
echo ""
echo "=== O4 staleness probe: mutate an input and check currency ==="
echo "extra_field: true" >> "$ROOT/governance/project/PROJECT_POLICY.yaml"
git -C "$ROOT" add -A && git -C "$ROOT" commit -m "mutate project policy"
$GOV doctor --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); [print('D021 after mutation:', json.dumps(c,indent=2)) for c in d['result']['checks'] if c['id']=='D021']"
# revert
git -C "$ROOT" revert HEAD --no-edit
