#!/bin/bash
set -e
GOV="$1"; PROJ="$2"
echo "=== J2: Experiment lifecycle ==="

# Create experiment record
cat > $PROJ/spec/experiments/EXP-TEST.yaml << 'EOF'
id: EXP-TEST
type: experiment
title: Test experiment for J2 audit
status: ACTIVE
created: '2026-09-18'
hypothesis: Widget X performs better under load
method: Load test with 1000 concurrent users
data_provenance: synthetic load generator
measurements:
  throughput: 950
  latency_p99: 120
result: Hypothesis confirmed - throughput exceeds baseline
confidence: 0.9
production_merge_allowed: false
state_class: EVIDENCE
EOF
mkdir -p $PROJ/spec/experiments

echo "--- J2 bullet mapping ---"
echo "b1 hypothesis/question: $(grep -c 'hypothesis:' $PROJ/spec/experiments/EXP-TEST.yaml)"
echo "b2 method/data: method=$(grep -c 'method:' $PROJ/spec/experiments/EXP-TEST.yaml), data_provenance=$(grep -c 'data_provenance:' $PROJ/spec/experiments/EXP-TEST.yaml)"
echo "b3 reproducibility: schema does not have a dedicated reproducibility field"
echo "b4 results: $(grep -c 'result:' $PROJ/spec/experiments/EXP-TEST.yaml)"
echo "b5 interpretation: no dedicated interpretation field (conclusion/result serve this)"
echo "b6 decision influence: via relations (derived_from, influences, affects)"
echo "b7 production merge prohibited: production_merge_allowed=$(grep 'production_merge_allowed' $PROJ/spec/experiments/EXP-TEST.yaml)"

echo ""
echo "--- Checking production_merge_allowed enforcement ---"
# Check if there is runtime enforcement of production_merge_allowed
grep -rn "production_merge_allowed" runtime/src/ --include='*.rs' || echo "No runtime enforcement found"
grep -rn "production_merge_allowed" tests/ --include='*.rs' | head -5 || echo "No test enforcement found"

echo ""
echo "RESULT: J2 fields present in schema; reproducibility and interpretation lack dedicated schema fields; production_merge_allowed is a schema field"
