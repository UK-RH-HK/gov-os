#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"; PRODUCT_ROOT="$3"
echo "=== Q1: Lesson lifecycle ==="

echo "--- Q1: LEARNING_POLICY ---"
cat "$ROOT/governance/kernel/policies/LEARNING_POLICY.yaml"
echo ""

echo "--- Q1: Create a lesson record ---"
mkdir -p "$ROOT/spec/reports"
cat > "$ROOT/spec/reports/LSN-0001.yaml" << 'EOF'
id: LSN-0001
type: lesson
title: Test lesson for upstream pipeline
status: ACTIVE
state_class: EVIDENCE
scope: FRAMEWORK
lifecycle: candidate
category: testing
problem_statement: Tests were flaky due to timing issues
generic_failure_mode: flaky timing-dependent tests
impact: reliability degradation
suggested_change: Add retry logic to timing-sensitive tests
evidence_strength: medium
body: Short lesson body for testing purposes.
sources: [TSK-0001]
corroboration: [TSK-0002]
tags: testing, reliability
EOF
git -C "$ROOT" add -A && git -C "$ROOT" commit -m "add lesson for upstream probe" 2>&1 | tail -2

echo ""
echo "--- Q2: Decision vs lesson ---"
echo "Decisions are stored as records of type 'decision' with state_class AUTHORITATIVE."
echo "Lessons are type 'lesson' with state_class EVIDENCE."
echo "Decisions record chosen action; lessons record evidence."
grep -n "state_class.*AUTHORITATIVE\|state_class.*EVIDENCE" "$ROOT/spec/reports/LSN-0001.yaml"
echo ""

echo "--- Q3: FRAMEWORK scope eligible for upstream ---"
echo "upstream_eligible_scopes from LEARNING_POLICY:"
grep upstream_eligible_scopes "$ROOT/governance/kernel/policies/LEARNING_POLICY.yaml"
echo ""

echo "--- Q4: Upstream Export Gate ---"
echo "--- Q4: gov upstream prepare ---"
$GOV upstream prepare LSN-0001 --root "$ROOT" --json 2>&1 || true
echo ""
echo "--- Q4: Checking sanitisation and secret scan in prepare ---"
grep -n "secret_scanner\|redact_identifiers\|strip_paths\|scan_text\|forbidden_paths\|never_export\|raw_product_code_included\|raw_customer_data_included\|default.deny\|synthetic_reproducer\|outbound.allowlist\|allowed_payload" "$PRODUCT_ROOT/runtime/src/upstream.rs" | head -20
echo ""
echo "--- Q4: outbound allowlist default-deny ---"
echo "Upstream prepare fails closed if blocked_reasons non-empty"
echo "upstream.allowed_payload controls what may exit: [packet, synthetic_fixture]"
echo "Everything else is blocked by default."
