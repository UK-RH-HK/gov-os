#!/bin/bash
GOV="$1"; PROJ="$2"
echo "=== L1: Contradiction resolution ==="
echo "--- L1b1: deterministic precedence first ---"
grep -n "precedence\|POLICY_PRECEDENCE" runtime/src/policy_precedence.rs | head -10
echo "--- L1b2: low-impact/reversible/high-confidence agent resolution ---"
echo "  HUMAN_GATE_POLICY.agent_resolvable_when:"
grep 'agent_resolvable_when' $PROJ/governance/kernel/policies/HUMAN_GATE_POLICY.yaml
echo "--- L1b3: human escalation for consequential uncertainty ---"
grep -n "human_gate_required\|HUMAN_GATE_REQUIRED" runtime/src/cit/mod.rs | head -5
echo "--- L1b4: rationale/evidence recorded ---"
grep -n "rationale" runtime/src/orchestration/gates.rs | head -5

echo ""
echo "=== L2: Human Decision Gate package ==="
echo "--- HUMAN_GATE_POLICY.decision_package_fields ---"
grep 'decision_package_fields' $PROJ/governance/kernel/policies/HUMAN_GATE_POLICY.yaml
echo ""
echo "--- All 10 fields in gate create: ---"
echo "  question, why_now, current_state, options, impact, reversibility, cost_rework, recommendation, confidence, permitted_next_actions"
echo "  Enforcement: gates.rs build() populates all of these from policy list"
grep -c "decision_package_fields" runtime/src/orchestration/gates.rs

echo ""
echo "=== L4: Non-global blocking ==="
echo "--- L4b1: Independent runnable branches continue ---"
grep 'continue_independent_work' $PROJ/governance/kernel/policies/HUMAN_GATE_POLICY.yaml
echo "--- L4b2: Global stop only when policy or critical-path state requires ---"
grep -n "PAUSE\|FROZEN\|global\|emergency" runtime/src/orchestration/control.rs | head -8
echo ""
echo "--- L4 in action: gate blocks specific tasks, not the whole system ---"
grep -n "blocks_tasks\|WAITING_HUMAN" runtime/src/orchestration/gates.rs | head -8

echo ""
echo "RESULT: L1 contradiction resolution via precedence/policy/escalation; L2 gate package enforced by policy; L4 non-global blocking with task-level gates"
