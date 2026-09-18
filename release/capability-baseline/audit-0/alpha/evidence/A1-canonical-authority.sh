#!/bin/bash
set -euo pipefail
WT="$1"; GOV="$2"; SCRATCH="$3"

echo "=== A1 Probe: Canonical authority and policy precedence ==="
PROJ="$SCRATCH/a1-test"
rm -rf "$PROJ" && mkdir -p "$PROJ"
cd "$PROJ" && git init -q && git add -A 2>/dev/null; git commit -m "init" --allow-empty -q

echo "--- 1. gov init (greenfield) ---"
$GOV init --project-name a1-test --skip-index 2>&1 || true

echo "--- 2. Constitution and hard invariants are identifiable and machine-readable ---"
ls governance/kernel/constitution/ 2>&1
cat governance/kernel/constitution/HARD_INVARIANTS.yaml | head -10

echo "--- 3. Policy precedence: check that policy keys are loaded ---"
$GOV status --role orchestrator 2>&1 | grep -i "precedence\|policy_precedence\|kernel_trust\|constitutional" | head -10

echo "--- 4. Try to weaken a security floor via project policy override ---"
cat > governance/project/PROJECT_POLICY.yaml << 'EOF'
project:
  name: a1-test
  alias: a1
policy_overrides:
  SECURITY_POLICY.never_index_classes: []
  AUTHORITY_POLICY.authority_levels_required.emergency_control: "L0"
EOF

$GOV doctor --role orchestrator 2>&1 | grep -i "refused\|precedence\|cannot\|weakening\|override" | head -20
$GOV status --role orchestrator 2>&1 | grep -i "refused_overrides\|refused\|weakening" | head -10

echo "--- 5. Check that refused overrides are recorded ---"
$GOV status --role orchestrator --json 2>&1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
ps = data.get('policies', {})
refused = ps.get('refused_overrides', [])
print(f'refused_overrides count: {len(refused)}')
for r in refused[:5]:
    print(f'  - {r.get(\"policy\",\"?\")}.{r.get(\"key\",\"?\")}: {r.get(\"reason\",\"?\")}')
" 2>&1 || echo "JSON parse not supported, checking raw output"

echo "--- 6. Verify override modes are enforced ---"
cat governance/kernel/policies/POLICY_PRECEDENCE.yaml | head -30

echo "=== A1 Probe Complete ==="
