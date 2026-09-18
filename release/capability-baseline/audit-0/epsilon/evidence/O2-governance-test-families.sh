#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== O2: Governance test families ==="
echo "--- TEST_POLICY.governance_families ---"
cat "$ROOT/governance/kernel/policies/TEST_POLICY.yaml" | grep governance_families
echo ""
echo "--- gov audit --json (all families, no-persist) ---"
$GOV audit --no-persist --root "$ROOT" --json 2>&1
