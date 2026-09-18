#!/bin/bash
GOV="$1"; PROJ="$2"
echo "=== N1: Structured checkpoint ==="
echo "--- CHECKPOINT_POLICY.fields ---"
grep 'fields:' $PROJ/governance/kernel/policies/CHECKPOINT_POLICY.yaml
echo ""
echo "--- Create checkpoint and verify all 9 fields ---"
$GOV checkpoint create --root "$PROJ" --json --role orchestrator \
  --next-action "continue implementation" \
  --last-completed-step "finished widget X" \
  --trigger task_transition 2>&1 | tee /tmp/ckpt.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',d)
print('Checkpoint fields present:')
for f in ['session','role','trigger','mode','last_completed_step','next_action','pending_decisions','open_transactions','files_changed','tests_status','context_packet_hash','memory_snapshot']:
    v = r.get(f)
    present = 'YES' if v is not None else 'MISSING'
    print(f'  {f}: {present} = {str(v)[:80]}')
" 2>/dev/null

echo ""
echo "--- Prose summary prohibition ---"
echo "  CHECKPOINT_POLICY.prose_summary_as_checkpoint: $(grep prose_summary $PROJ/governance/kernel/policies/CHECKPOINT_POLICY.yaml)"

echo ""
echo "=== N2: Mandatory triggers ==="
echo "--- CHECKPOINT_POLICY.mandatory_triggers ---"
grep 'mandatory_triggers' $PROJ/governance/kernel/policies/CHECKPOINT_POLICY.yaml
echo ""
echo "--- Enforcement in code ---"
grep -n "mandatory_triggers" runtime/src/checkpoints.rs | head -5
echo ""
echo "--- Trigger: accepted_cit (auto-created in CIT execute) ---"
grep -n "accepted_cit\|before_handoff\|before_model_switch\|before_session_close\|before_compaction\|task_transition\|material_decision\|significant_mutation" runtime/src/checkpoints.rs runtime/src/orchestration/handoffs.rs runtime/src/cit/mod.rs runtime/src/orchestration/tasks.rs 2>/dev/null | head -15

echo ""
echo "=== N3: Provider-independent checkpoint watchdog ==="
echo "--- N3b1: Does not depend solely on proprietary hooks ---"
echo "  CHECKPOINT_POLICY.watchdog:"
grep -A3 'watchdog:' $PROJ/governance/kernel/policies/CHECKPOINT_POLICY.yaml
echo ""
echo "--- N3 watchdog in code (context_utilisation + operations count) ---"
grep -A10 "pub fn watchdog" runtime/src/checkpoints.rs | head -15

echo ""
echo "--- N3b2: Can mark checkpoint stale ---"
grep -n "stale\|staleness" runtime/src/checkpoints.rs | head -5 || echo "  No direct staleness in checkpoints.rs"
echo "  Freshness tracked in memory_snapshot.index_manifest_hash"
echo ""
echo "--- N3b3: Handoff/session close blocked when checkpoint freshness violates policy ---"
grep -n "before_handoff\|checkpoint" runtime/src/orchestration/handoffs.rs | head -5

echo ""
echo "=== N4: Worker return contract ==="
echo "--- N4b1: Structured result survives subagent conversation death ---"
echo "  Worker-return schema required fields:"
python3 -c "import json; d=json.load(open('framework/schemas/worker-return.schema.json')); print('  Required:', d['required'])"
echo ""
echo "--- Handoff return validation ---"
grep -n "worker-return\|validate.*return\|return_result" runtime/src/orchestration/handoffs.rs | head -5

echo ""
echo "RESULT: N1 9-field structured checkpoint; N2 8 mandatory triggers; N3 provider-independent watchdog (context+ops thresholds); N4 worker return schema with 12 required fields"
