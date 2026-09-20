#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate N (Contract v3:715-745)
#   N1 a structured checkpoint records session/role/task/mode/claim, last completed step, next action, pending
#      decisions/questions, open transactions, files changed, test status, context packet hash, memory snapshot
#   N2 the mandatory triggers: task transition, material decision, accepted CIT, significant mutation, before
#      handoff, before model/provider switch, before session close, before known compaction
#   N3 a provider-independent watchdog: not solely proprietary hooks; can mark a checkpoint stale; handoff/session
#      close can be blocked or degraded when checkpoint freshness violates policy
#   N4 the worker return contract: a structured result survives a subagent's conversation death
# Also delta's iteration-1 duty: `handoff.create` as a remedy for remediation handoffs.
cd "$(dirname "$0")" && . ./lib.sh
machine nck && seed_spec && seed_acceptance_test

T="$(res task create --class implementation --objective "Implement ledger totals" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
SESSION=w1 ROLE=backend-engineer g task claim "$T" >/dev/null
SESSION=w1 ROLE=backend-engineer g context compile "$T" >/dev/null

echo "== N1  a structured checkpoint records every declared field"
CK="$(SESSION=w1 ROLE=backend-engineer res checkpoint create --next-action "continue the ledger implementation" --task "$T" --step "wrote total_cents" --tests-status passed)"
CKID="$(echo "$CK" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
echo "   checkpoint $CKID"
FIELDS="$(python3 -c "
import yaml;print(' '.join(yaml.safe_load(open('$MROOT/governance/kernel/policies/CHECKPOINT_POLICY.yaml'))['fields']))")"
for f in $FIELDS; do
  check "$(echo "$CK" | python3 -c "
import json,sys;d=json.load(sys.stdin)
v=d.get('$f')
print(1 if ('$f' in d and v is not None and v != '') else 0)")" "N1.1 the checkpoint records '$f'" "$(echo "$CK" | python3 -c "import json,sys;print(list(json.load(sys.stdin).keys()))")"
done
check "$(echo "$CK" | python3 -c "
import json,sys;d=json.load(sys.stdin)
print(1 if d.get('context_packet_hash') and d.get('state_reference',{}).get('repo_commit') and d.get('state_reference',{}).get('governed_state_digest') and d.get('state_reference',{}).get('index') else 0)")" "N1.2 it binds the context packet hash and a state reference (commit + governed digest + index)" ""
check "$(echo "$CK" | python3 -c "
import json,sys;d=json.load(sys.stdin);i=d.get('inputs') or []
print(1 if i and all(('id' in x) and ('current_hash' in x or 'delivered_hash' in x or 'hash' in x) for x in i) else 0)")" "N1.3 it records each mandatory input with its version/hash (N <-> W9)" "$(echo "$CK" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('inputs'))[:300])")"
# open questions are supplyable, not hard-wired empty
CKQ="$(SESSION=w1 ROLE=backend-engineer res checkpoint create --next-action "continue" --task "$T" --step "s" 2>/dev/null | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('open_questions')))")"
echo "   NOTE open_questions on a plain checkpoint: $CKQ"

echo "== N2  the mandatory triggers"
TR() { res checkpoint latest | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('trigger'))"; }
# BOUND: the triggers the OS observed at this boundary — from the watchdog's own report and from the checkpoints it
# wrote for them (observe_boundaries checkpoints each one, so a later call no longer reports it).
BOUND() {
  local w; w="$(res checkpoint watchdog --next-action "gov continue")"
  python3 - "$w" "$(res checkpoint latest)" <<'PY'
import json, sys
w = json.loads(sys.argv[1]); latest = json.loads(sys.argv[2])
t = [b.get('trigger') for b in (w.get('boundaries') or [])]
if latest.get('trigger') and latest['trigger'] not in t:
    t.append(latest['trigger'])
print(json.dumps(t))
PY
}
# (a) task transition
SESSION=w1 ROLE=backend-engineer g task release "$T" >/dev/null
B="$(BOUND)"; echo "   after a task transition, observed boundaries: $B"
check "$(echo "$B" | python3 -c "import json,sys;print(1 if 'task_transition' in json.load(sys.stdin) else 0)")" "N2.1 a task transition is observed as a mandatory checkpoint trigger" "$B"
SESSION=w1 ROLE=backend-engineer g task claim "$T" >/dev/null 2>&1
# (b) material decision
GM="$(res gate create --question "Adopt the batched writer?" --fields '{"why_now":"the write path is being finalised","current_state":"per-row writes","options":[{"id":"A","description":"batch","authorises_blocked_work":true},{"id":"B","description":"keep","authorises_blocked_work":false}],"impact":"the write path","reversibility":"reversible: removable in a day","cost_rework":"a day","recommendation":"A","confidence":0.8,"trigger":"vendor_choice","impact_radius":"R3"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
decide_human "$GM" A >/dev/null
B="$(BOUND)"; echo "   after a material decision: $B"
check "$(echo "$B" | python3 -c "import json,sys;print(1 if 'material_decision' in json.load(sys.stdin) else 0)")" "N2.2 a material decision is observed as a mandatory checkpoint trigger" "$B"
# (c) accepted CIT
cat > "$MROOT/.governance-runtime/mf-n.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals, restated"}]
JSON
CI="$(res cit propose --proposal "restate" --trigger behaviour_change --title n --manifest "$MROOT/.governance-runtime/mf-n.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
CG="$(res cit show "$CI" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate'])")"
decide_human "$CG" A >/dev/null; g cit approve "$CI" >/dev/null; g cit execute "$CI" >/dev/null 2>&1
check_eq "$(TR)" accepted_cit "N2.3 an accepted CIT writes its own checkpoint automatically"
# (d) significant mutation
for i in $(seq 1 30); do echo "line $i" > "$MROOT/docs-n-$i.txt"; done
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm bulk >/dev/null 2>&1
B="$(BOUND)"; echo "   after 30 changed files: $B"
check "$(echo "$B" | python3 -c "import json,sys;print(1 if 'significant_mutation' in json.load(sys.stdin) else 0)")" "N2.4 a significant mutation is observed as a mandatory checkpoint trigger" "$B"
# run enough gov commands and file changes AFTER the last checkpoint for the OS's own counters to cross the policy
for i in $(seq 1 30); do g task list >/dev/null 2>&1; done
W="$(res checkpoint watchdog --next-action "gov continue")"
echo "   watchdog with NO caller-supplied counters: $(echo "$W" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'fired':d.get('fired'),'observed':d.get('observed'),'reason':d.get('reason')}))")"
check "$(echo "$W" | python3 -c "import json,sys;d=json.load(sys.stdin);o=d.get('observed',{});print(1 if d.get('fired') and (o.get('commands',0)>0 or o.get('files_changed',0)>0) and o.get('caller_ops')==0 else 0)")" "N3.1 the watchdog fires on state the OS observes itself, not on caller-supplied counters" "$(echo "$W" | head -c 400)"
# (e) before handoff
H="$(SESSION=w1 res handoff create --to-role independent-test-designer --task "$T" --fields '{"summary":"hand the ledger work to the test designer","next_action":"author the acceptance test"}')"
HID="$(echo "$H" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('id') or d.get('handoff',{}).get('id'))")"
check_eq "$(TR)" before_handoff "N2.5 a handoff writes its before_handoff checkpoint automatically"
# (f) before model/provider switch
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
d = yaml.safe_load(open(p)) or {}
d["providers"] = [{"name": "provider-beta", "models": [{"id": "beta-large", "tier": "T3", "max_reasoning": "extra_high", "cost_per_1k_in": 0.4, "cost_per_1k_out": 0.8}]}]
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1
B="$(BOUND)"; echo "   after the provider map changed: $B"
check "$(echo "$B" | python3 -c "import json,sys;print(1 if 'before_model_switch' in json.load(sys.stdin) else 0)")" "N2.6 a model/provider routing change is observed as a mandatory checkpoint trigger" "$B"
# (g) before session close
SC="$(SESSION=w1 ROLE=backend-engineer res session close --next-action "gov continue" --task "$T")"
echo "   session close: $(echo "$SC" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'checkpoint':d['checkpoint'],'blocked':d['blocked'],'degraded':d['degraded'],'resumable':d['resumable']}))" | head -c 500)"
check_eq "$(TR)" before_session_close "N2.7 gov session close writes the before_session_close checkpoint"
# (h) before known compaction
check "$(res checkpoint watchdog --utilisation 0.9 --next-action "gov continue" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d.get('fired') and d.get('reason')=='context_utilisation' else 0)")" "N2.8 an approaching compaction (context utilisation over the policy threshold) fires a checkpoint" ""
check "$(python3 -c "
import yaml;t=yaml.safe_load(open('$MROOT/governance/kernel/policies/CHECKPOINT_POLICY.yaml'))['mandatory_triggers']
print(1 if set(t)=={'task_transition','material_decision','accepted_cit','significant_mutation','before_handoff','before_model_switch','before_session_close','before_compaction'} else 0)")" "N2.9 the policy declares exactly the eight Contract v3 triggers"

echo "== N3  checkpoint staleness and degraded handoff/session close"
CK2="$(SESSION=w1 ROLE=backend-engineer res checkpoint create --next-action "continue" --task "$T" --step "before the upstream change" --tests-status passed)"
CK2ID="$(echo "$CK2" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
check_eq "$(res checkpoint freshness "$CK2ID" | python3 -c "import json,sys;print(json.load(sys.stdin)['state'])")" CURRENT "N3.2 a checkpoint taken over current state is CURRENT (not stale)"
cat > "$MROOT/.governance-runtime/mf-n2.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"acceptance_criteria","value":["totals are exact and reject negative quantities"]}]
JSON
CI2="$(res cit propose --proposal "tighten" --trigger acceptance_criteria_change --title n2 --manifest "$MROOT/.governance-runtime/mf-n2.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
CG2="$(res cit show "$CI2" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate'])")"
decide_human "$CG2" A >/dev/null; g cit approve "$CI2" >/dev/null; g cit execute "$CI2" >/dev/null 2>&1
FR="$(res checkpoint freshness "$CK2ID")"
echo "   freshness after the upstream change: $(echo "$FR" | head -c 400)"
check_eq "$(echo "$FR" | python3 -c "import json,sys;print(json.load(sys.stdin)['state'])")" STALE "N3.3 the checkpoint is marked stale once the material state it captured changed"
SC2="$(SESSION=w1 ROLE=backend-engineer res session close --next-action "gov continue" --task "$T")"
echo "   session close after the change: $(echo "$SC2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'blocked':d['blocked'],'resumable':d['resumable'],'degraded':d['degraded']}))" | head -c 600)"
check "$(echo "$SC2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['degraded'] and d['resumable'] is False else 0)")" "N3.4 session close is explicitly degraded (never refused) when the checkpoint or inputs are stale" "$(echo "$SC2" | head -c 400)"
H2="$(SESSION=w1 res handoff create --to-role independent-test-designer --task "$T" --fields '{"summary":"hand over after the upstream change","next_action":"revalidate against the new criterion"}')"
echo "   handoff after the change: $(echo "$H2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k in ('id','degraded','freshness','blocked','warnings')}))" | head -c 600)"
check "$(echo "$H2" | python3 -c "
import json,sys;d=json.load(sys.stdin);f=d.get('freshness') or {}
print(1 if (str(f.get('state')).upper() not in ('CURRENT','FRESH','NONE')) or f.get('degraded') or f.get('reasons') else 0)")" "N3.5 a handoff over stale state is degraded and says so" "$(echo "$H2" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('freshness')))")"
check "$(python3 -c "print(1 if 'proprietary' not in open('$WT/runtime/src/checkpoints.rs').read().split('pub fn watchdog')[1][:2000].lower() else 0)")" "N3.6 the watchdog needs no proprietary hook (it reads git and the command log)" ""

echo "== delta duty: handoff.create is available as a remedy while a health block is active"
# make the suite unhealthy for a subject, then check that the remedy handoff is not refused by the block
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "spec/scenarios/SCN-0001.yaml")
d = yaml.safe_load(open(p)); d.pop("data_requirements_not_applicable", None)
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1
g health run >/dev/null 2>&1 || g audit >/dev/null 2>&1
BLK="$(res health blocks 2>/dev/null || echo '{}')"
echo "   active blocks: $(echo "$BLK" | head -c 400)"
HR="$(SESSION=w1 code handoff create --to-role independent-test-designer --task "$T" --fields '{"summary":"remediation handoff: the scenario chain needs its data declaration","next_action":"declare the scenario data requirement"}')"
echo "   handoff.create while blocks are active -> $HR"
check_eq "$HR" OK "N.remedy handoff.create stays available as a listed remedy while a block is active"

echo "== N4  the worker return contract: a structured result survives the subagent"
H3="$(SESSION=w1 res handoff create --to-role independent-test-designer --task "$T" --fields '{"summary":"author the acceptance test","next_action":"write tests/ledger_test.rs"}')"
H3ID="$(echo "$H3" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('id') or d.get('handoff',{}).get('id'))")"
RET="$MROOT/.governance-runtime/worker-return.json"
echo 'pub fn checks() {}' > "$MROOT/src/ledger_checks.rs"
python3 - "$RET" "$T" <<'PY'
import json, sys
json.dump({"task": sys.argv[2], "status": "success",
           "work_completed": "authored the acceptance obligation and src/ledger_checks.rs",
           "files_changed": ["src/ledger_checks.rs"], "evidence": [],
           "tests": {"status": "not_applicable_with_reason", "reason": "no product test runner is configured here"},
           "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
           "recommended_next_action": "the implementer runs the acceptance test",
           "outputs_produced": ["src/ledger_checks.rs"]}, open(sys.argv[1], "w"))
PY
RR="$(SESSION=other-session ROLE=independent-test-designer res handoff return "$H3ID" --file "$RET")"
RRC="$(SESSION=other-session ROLE=independent-test-designer code handoff return "$H3ID" --file "$RET")"
echo "   handoff return code: $RRC"
echo "   handoff return: $(echo "$RR" | head -c 400)"
check "$(echo "$RR" | python3 -c "import json,sys;print(1 if json.load(sys.stdin) else 0)")" "N4.1 a structured worker return is accepted and persisted by the OS" "$RR"
STORED="$(find "$MROOT/spec" -name "$H3ID.yaml" | head -1)"
check "$([ -n "$STORED" ] && echo 1 || echo 0)" "N4.2 the return is a governed record on disk, independent of any conversation" "no record for $H3ID"
check "$(python3 -c "
import yaml
print(1 if 'authored the acceptance obligation' in str(yaml.safe_load(open('$STORED'))) else 0)" 2>/dev/null || echo 0)" "N4.3 the returned result survives in the record after the subagent's session ends" "$STORED"
# S0-W5-01 (iteration-0): can that same schema-valid worker return serve as the task-close receipt?
CLOSECODE="$(SESSION=w1 ROLE=backend-engineer code task close "$T" --report "$RET")"
echo "   NOTE the same worker return used as a task-close receipt -> $CLOSECODE"
# a fresh session with no conversation history can read it back
READBACK="$(SESSION=fresh-session ROLE=orchestrator res artefact show "$H3ID" 2>/dev/null | head -c 200)"
check "$([ -n "$READBACK" ] && echo 1 || echo 0)" "N4.4 a fresh session reads the returned result back with no conversation state" "$READBACK"

summary
