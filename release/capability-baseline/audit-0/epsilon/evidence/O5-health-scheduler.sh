#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== O5: Governance Health Scheduler ==="

echo "--- O5 Tier checks: which tiers exist? ---"
echo "The audit command with --family selects individual governance families."
echo "Doctor runs a fixed set of checks."
echo "Tiered checks would map to G0-G6 levels."
echo ""

echo "--- O5 Impacted-test selection: --family flag ---"
echo "Probing: run a single family (schema_invariants)"
time $GOV audit --family schema_invariants --no-persist --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('families_run:', list(d['result']['families'].keys()))"
echo ""

echo "--- O5 Full suite ---"
time $GOV audit --no-persist --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('families_run:', len(d['result']['families']), 'verdict:', d['result']['verdict'])"
echo ""

echo "--- O5 Deep mode ---"
echo "(skipping deep mode in this probe for time, but it exists: --deep flag)"
$GOV audit --help 2>&1 | grep deep
echo ""

echo "--- O5 Reproducibility: audit runs twice and compares result_hash ---"
$GOV audit --no-persist --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('reproducible:', d['result']['reproducible'], 'result_hash:', d['result']['result_hash'])"
echo ""

echo "--- O5 machine state: RED/YELLOW/GREEN equivalent ---"
echo "The audit produces: HEALTHY (green), DEGRADED (yellow), UNHEALTHY (red)"
echo ""

echo "--- O5 hard-block vs warning semantics ---"
echo "critical+high → UNHEALTHY (hard-block); medium → DEGRADED (warning); low → ok"
echo "Doctor D021 marks stale suite as 'medium' severity (DEGRADED/warning)"
echo ""

echo "--- O5 health result provenance: audit record has run_at, session, role ---"
$GOV audit --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); r=d['result']; print('audit_id:', r['audit'], 'verdict:', r['verdict'], 'inputs_hash:', r['inputs_hash'])"
echo ""

echo "--- O5 remediation/task generation: doctor provides remediation ---"
$GOV doctor --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('remediation:', d['result']['remediation'])"
echo ""

echo "--- O5 cache keyed by content/policy/framework hashes: inputs_hash ---"
echo "inputs_hash covers governance/kernel, governance/project, governance/tests, spec/decisions, governance/framework.lock"
echo "This was demonstrated in O4 probe: mutating an input changes inputs_hash"
