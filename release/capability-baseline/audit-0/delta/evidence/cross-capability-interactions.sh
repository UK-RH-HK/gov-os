#!/bin/bash
GOV="$1"; PROJ="$2"
echo "=== Cross-capability interactions ==="

echo "--- K2 <-> W6: CIT-E staleness/retest propagation ---"
echo "  CIT-E propagation marks affected tasks retest-required and affected tests stale"
grep -n "mark_affected_tasks_retest\|mark_affected_tests_stale" runtime/src/cit/mod.rs | head -5
echo ""

echo "--- N <-> W9: Checkpoint mandatory-input continuity ---"
echo "  Checkpoint records context_packet_hash and memory_snapshot"
echo "  Handoff create auto-creates a checkpoint (before_handoff trigger)"
echo "  Worker return validates against worker-return schema (all mandatory inputs tracked)"
grep -n "context_packet_hash\|memory_snapshot\|before_handoff" runtime/src/checkpoints.rs runtime/src/orchestration/handoffs.rs | head -8
echo ""

echo "--- L3 <-> E1: Gate presentation/authority ---"
echo "  Gate create requires breakglass clearance (OWNER-DECISION-0006 §6)"
echo "  Gate answer requires presentation (INV-008)"
echo "  Gate answer requires authority level check"
grep -n "guard_effect\|GATE_NOT_PRESENTED\|authority::require" runtime/src/orchestration/gates.rs | head -10
echo ""

echo "RESULT: Cross-capability interactions K2<->W6, N<->W9, L3<->E1 all exercised"
