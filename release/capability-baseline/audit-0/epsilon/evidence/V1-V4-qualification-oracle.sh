#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"; PRODUCT_ROOT="$3"
echo "=== V: Qualification Oracle ==="

echo "--- V: Searching for oracle-related schemas/types ---"
find "$PRODUCT_ROOT/framework" "$PRODUCT_ROOT/runtime" "$PRODUCT_ROOT/docs" -name '*.yaml' -o -name '*.rs' -o -name '*.md' 2>/dev/null | xargs grep -l "oracle\|fault.manifest\|hidden.path.map\|hidden.memory\|qualification.scor" 2>/dev/null | head -20
echo ""

echo "--- V: Searching for oracle format schemas ---"
find "$PRODUCT_ROOT/framework/schemas" -name '*.yaml' -o -name '*.json' 2>/dev/null | head -20
echo ""
for f in $(find "$PRODUCT_ROOT/framework/schemas" -name '*.yaml' 2>/dev/null); do
  if grep -q "oracle\|fault.manifest\|qualification" "$f" 2>/dev/null; then
    echo "ORACLE SCHEMA FOUND: $f"
    head -5 "$f"
    echo "..."
  fi
done

echo "--- V: Check tests/certification for oracle-related tests ---"
ls "$PRODUCT_ROOT/tests/certification/" 2>/dev/null
echo ""
for f in $(ls "$PRODUCT_ROOT/tests/certification/"*.rs 2>/dev/null); do
  if grep -q "oracle\|fault_manifest\|hidden_path\|hidden_memory\|qualification_scoring" "$f" 2>/dev/null; then
    echo "ORACLE TEST: $f"
    grep "fn.*oracle\|fn.*fault_manifest\|fn.*hidden_path\|fn.*hidden_memory\|fn.*qualification_scoring" "$f" | head -5
  fi
done

echo "--- V: Check fixtures for oracle-related structures ---"
find "$PRODUCT_ROOT/fixtures" -name '*.yaml' -o -name '*.json' 2>/dev/null | xargs grep -l "oracle\|fault.manifest\|hidden.path\|hidden.memory\|qualification.scor" 2>/dev/null | head -10
echo ""

echo "--- V: Search for schema definitions of oracle types ---"
find "$PRODUCT_ROOT" -name '*.yaml' -path '*/schemas/*' 2>/dev/null | xargs grep -l "fault-manifest\|oracle\|qualification-score" 2>/dev/null | head -5
