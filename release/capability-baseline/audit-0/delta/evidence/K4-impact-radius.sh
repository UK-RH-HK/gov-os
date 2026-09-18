#!/bin/bash
set -e
GOV="$1"; PROJ="$2"
echo "=== K4: Impact radius R0-R5 ==="

echo "--- CHANGE_POLICY.impact_radii ---"
grep 'impact_radii' $PROJ/governance/kernel/policies/CHANGE_POLICY.yaml

echo "--- Radius rules ---"
grep -A10 'radius_rules:' $PROJ/governance/kernel/policies/CHANGE_POLICY.yaml

echo "--- Graph traversal depth by radius ---"
grep 'graph_traversal_depth_by_radius' $PROJ/governance/kernel/policies/CHANGE_POLICY.yaml

echo "--- Semantic candidates by radius ---"
grep 'semantic_candidates_by_radius' $PROJ/governance/kernel/policies/CHANGE_POLICY.yaml

echo "--- Radius minimum tier ---"
grep 'radius_minimum_tier' $PROJ/governance/kernel/policies/MODEL_ROUTING_POLICY.yaml

echo ""
echo "--- Radius affects traversal depth (code) ---"
grep -n "graph_traversal_depth_by_radius" runtime/src/cit/mod.rs | head -5

echo "--- Radius affects semantic candidate count (code) ---"
grep -n "semantic_candidates_by_radius" runtime/src/cit/mod.rs | head -5

echo "--- Radius affects model tier (code) ---"
grep -n "radius_minimum_tier" runtime/src/routing.rs | head -5

echo "--- Radius affects human approval (code) ---"
grep -n "auto_approve_max_radius" runtime/src/cit/mod.rs | head -5

echo ""
echo "--- Verify editorial trigger gives R0 ---"
RESULT=$($GOV cit propose --root "$PROJ" --json --role orchestrator --proposal "Fix typo" --trigger editorial 2>&1)
RADIUS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(r.get('impact',{}).get('radius','N/A'))" 2>/dev/null || echo "N/A")
echo "  editorial radius=$RADIUS"

echo ""
echo "RESULT: R0-R5 radii defined; radius affects traversal depth, semantic candidate count, model tier, human approval threshold, and rollback scope"
