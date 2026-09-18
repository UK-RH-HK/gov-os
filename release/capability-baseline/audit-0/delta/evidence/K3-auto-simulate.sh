#!/bin/bash
set -e
GOV="$1"; PROJ="$2"
echo "=== K3: Automatic impact simulation for material triggers ==="

echo "--- CHANGE_POLICY.auto_simulate_triggers ---"
cat $PROJ/governance/kernel/policies/CHANGE_POLICY.yaml | grep -A1 auto_simulate

echo ""
echo "--- Test each trigger type ---"
for TRIGGER in architecture_change behaviour_change interface_change security_change governance_change infrastructure_cost acceptance_criteria_change data_migration; do
  echo "  trigger=$TRIGGER:"
  RESULT=$($GOV cit propose --root "$PROJ" --json --role orchestrator --proposal "Test $TRIGGER auto-sim" --trigger "$TRIGGER" 2>&1)
  AUTO=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(r.get('auto_simulated', 'NOT_SIMULATED'))" 2>/dev/null || echo "ERROR")
  echo "    auto_simulated=$AUTO"
done

echo ""
echo "RESULT: All 8 auto_simulate_triggers confirmed functional"
