#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== O1: Product test families ==="
echo "--- TEST_POLICY.product_families ---"
cat "$ROOT/governance/kernel/policies/TEST_POLICY.yaml" | grep product_families
echo ""
echo "--- gov verify --help ---"
$GOV verify --help --root "$ROOT" 2>&1 || true
echo ""
echo "--- gov audit --family schema_invariants ---"
$GOV audit --family schema_invariants --no-persist --root "$ROOT" --json 2>&1 || true
echo ""
echo "--- Checking Rust test infrastructure ---"
ls -la tests/ 2>/dev/null || echo "no tests/ dir at root"
echo ""
echo "--- cargo test --lib count (run from product tree, not the scratch project) ---"
cd "$(dirname "$GOV")/../.."
~/.cargo/bin/cargo test --lib -- --list 2>&1 | tail -20
