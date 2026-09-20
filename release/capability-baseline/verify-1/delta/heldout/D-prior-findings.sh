#!/usr/bin/env bash
# P2-AR-0049 held-out probe — disposition checks for the low-severity iteration-0 findings in family delta's scope
# that the capability probes do not already settle: A0-K2-02, A0-K2-03, A0-L1-02, A0-M2-01, A0-M4-02, A0-N1-01.
# This probe does not grade a bullet; it records what the candidate does now for each prior finding.
cd "$(dirname "$0")" && . ./lib.sh
machine dprior && seed_spec && seed_acceptance_test

echo "== A0-K2-02  a failed CIT-E leaving the derived views regenerated from the rolled-back state"
REG="$MROOT/governance/generated/tool-registry.json"
cat > "$MROOT/.governance-runtime/d-bad.json" <<'JSON'
[{"op":"write_file","path":"governance/project/tools/probe-tool.yaml","content":"tool_id: probe-tool\nname: Probe Tool\ntype: CLI\nstatus: active\nversion: 1.0.0\ncapabilities: [lint]\napproved_roles: [backend-engineer]\n"},
 {"op":"set_field","target":"REQ-0001","field":"governed_by","value":["D-9999"]}]
JSON
C="$(res cit propose --proposal "write a tool descriptor and break the graph in one transaction" --trigger governance_change --title bad --manifest "$MROOT/.governance-runtime/d-bad.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
G="$(res cit show "$C" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
[ "$G" != None ] && [ -n "$G" ] && decide_human "$G" A >/dev/null 2>&1
g cit approve "$C" >/dev/null 2>&1
CONTENT() { python3 -c "
import json,hashlib
def strip(v):
    if isinstance(v,dict): return {k:strip(x) for k,x in v.items() if k!='generated_at'}
    if isinstance(v,list): return [strip(x) for x in v]
    return v
print(hashlib.sha256(json.dumps(strip(json.load(open('$REG'))),sort_keys=True).encode()).hexdigest()[:16])"; }
BEFORE="$(CONTENT)"
echo "   execute -> $(code cit execute "$C")   status -> $(res cit show "$C" | python3 -c "import json,sys;print(json.load(sys.stdin)['os_state']['cit_status'])")"
AFTER="$(CONTENT)"
check_eq "$BEFORE" "$AFTER" "D.K2-02 the derived views carry no content from a rolled-back transaction (digest taken without the regeneration timestamp)"
check "$(python3 -c "print(0 if 'probe-tool' in open('$REG').read() else 1)")" "D.K2-02a the rolled-back tool descriptor is not listed in the regenerated registry"
check "$([ ! -f "$MROOT/governance/project/tools/probe-tool.yaml" ] && echo 1 || echo 0)" "D.K2-02b the rolled-back descriptor file is removed"
check "$(python3 -c "
import yaml;d=yaml.safe_load(open('$MROOT/spec/requirements/REQ-0001.yaml'))
print(1 if 'D-9999' not in str(d.get('governed_by','')) else 0)")" "D.K2-02c the authoritative record is restored"
echo "   NOTE the derived views are rewritten by the failed transaction; only their regeneration timestamp differs."

echo "== A0-K2-03  CIT-E verification attributing pre-existing, not-yet-indexed damage to the transaction"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "spec/scenarios/SCN-0001.yaml")
d = yaml.safe_load(open(p)); d["derived_from"] = ["D-8888"]          # a dangling reference made outside any CIT
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
cat > "$MROOT/.governance-runtime/d-harmless.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals, retitled harmlessly"}]
JSON
C2="$(res cit propose --proposal "a harmless editorial retitle" --trigger behaviour_change --title harmless --manifest "$MROOT/.governance-runtime/d-harmless.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
G2="$(res cit show "$C2" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
[ "$G2" != None ] && [ -n "$G2" ] && decide_human "$G2" A >/dev/null 2>&1
g cit approve "$C2" >/dev/null 2>&1
E2="$(code cit execute "$C2")"
echo "   a harmless CIT executed while an unrelated dangling edge exists -> $E2"
check_eq "$E2" OK "D.K2-03 pre-existing graph damage is not attributed to an unrelated transaction"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "spec/scenarios/SCN-0001.yaml")
d = yaml.safe_load(open(p)); d.pop("derived_from", None)
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1

echo "== A0-L1-02  a resolution with no rationale, and evidence references on the decision"
GA="$(res gate create --question "Warm the cache on boot?" --fields '{"why_now":"the boot path is finalised this week","current_state":"cold start takes 4s","options":[{"id":"A","description":"warm it","authorises_blocked_work":true},{"id":"B","description":"leave it","authorises_blocked_work":false}],"impact":"one module of the boot path","reversibility":"reversible: a single call","cost_rework":"under an hour","recommendation":"A","confidence":0.92,"trigger":"ux_direction","impact_radius":"R0"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
g gate present "$GA" >/dev/null
NOR="$(SESSION=o ROLE=change-controller code decide "$GA" --option A --by change-controller)"
echo "   an agent resolution with no --rationale -> $NOR"
check "$([ "$NOR" != OK ] && echo 1 || echo 0)" "D.L1-02 an agent resolution without a recorded rationale is refused" "returned $NOR"
RID="$(res research record --fields '{"question":"Does warming the cache help?","reason":"the boot path misses its budget","method":"measure cold start with and without a warm-up","sources":["src/lib.rs"],"measurements":[{"warm":true,"ms":300},{"warm":false,"ms":4000}],"uncertainty":"one machine","conclusion":"warming helps","confidence":0.9}' | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['id'])")"
OKE="$(SESSION=o2 ROLE=change-controller code decide "$GA" --option A --by change-controller --rationale "low impact, reversible, high confidence" --evidence "$RID")"
echo "   an agent resolution citing governed evidence -> $OKE"
check_eq "$OKE" OK "D.L1-02b a resolution may cite governed evidence on the decision"
BADE="$(SESSION=o3 ROLE=change-controller code decide "$GA" --option A --by change-controller --rationale "r" --evidence "RES-9999")"
check "$([ "$BADE" != OK ] && echo 1 || echo 0)" "D.L1-02c an evidence reference that is not a governed record is refused" "returned $BADE"

echo "== A0-M2-01  routing evidence recorded below the task's declared minimum"
TA="$(res task create --class documentation --objective "Work declaring an extra-high minimum" --status READY --allowed 'docs/**' --fields '{"role":"routine-documentation","minimum_reasoning":"extra_high","minimum_model_tier":"T3"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
python3 - "$MROOT" "$TA" <<'PY'
import json, sys
json.dump({"task": sys.argv[2], "model": "tiny-1", "provider": "p", "task_class": "documentation",
           "reasoning_effort": "low", "cost": 0.01, "latency_ms": 10, "pass": True,
           "repair_count": 0, "reviewer_findings": 0}, open(sys.argv[1] + "/.governance-runtime/below.json", "w"))
PY
BEL="$(code route --record "$MROOT/.governance-runtime/below.json")"
echo "   recording an extra_high task's run at reasoning 'low' -> $BEL"
check "$([ "$BEL" != OK ] && echo 1 || echo 0)" "D.M2-01 a run recorded below the task's declared reasoning minimum is refused or flagged" "route --record returned $BEL (the run was accepted with no refusal and no flag)"

echo "== A0-M4-02  untyped routing evidence and the policy's own field names"
python3 - "$MROOT" <<'PY'
import json, sys
json.dump({"model": "m2", "provider": "p", "task_class": "implementation", "reasoning_effort": "high",
           "cost": "expensive", "latency_ms": "slow", "pass": True, "repair_count": "many",
           "reviewer_findings": 0}, open(sys.argv[1] + "/.governance-runtime/untyped.json", "w"))
json.dump({"model": "m3", "provider": "p", "task_class": "implementation", "reasoning_effort": "high",
           "cost": 1.0, "latency": 500, "pass_fail": True, "repair_count": 0,
           "reviewer_findings": 0}, open(sys.argv[1] + "/.governance-runtime/aliased.json", "w"))
PY
U="$(code route --record "$MROOT/.governance-runtime/untyped.json")"
A="$(code route --record "$MROOT/.governance-runtime/aliased.json")"
echo "   non-numeric cost/latency/repair_count -> $U ; the policy's own alias names (latency, pass_fail) -> $A"
check "$([ "$U" != OK ] && echo 1 || echo 0)" "D.M4-02 a run with non-numeric cost/latency/repair_count is refused" "route --record returned $U"
RPT="$(res route --report | python3 -c "
import json,sys;rows=json.load(sys.stdin)['rows']
print(json.dumps([r for r in rows if r['model'] in ('m2','m3')]))")"
echo "   how they aggregate: $RPT"
check "$(echo "$RPT" | python3 -c "
import json,sys;rows=json.load(sys.stdin)
m3=[r for r in rows if r['model']=='m3']
print(1 if m3 and (m3[0]['avg_latency_ms']>0 and m3[0]['pass_rate']>0) else 0)")" "D.M4-02b a run recorded with the policy's own field names is aggregated correctly" "$RPT"

echo "== A0-N1-01  checkpoint open questions and files_changed"
GB="$(res gate create --question "An open question for the checkpoint?" --fields '{"why_now":"it is open now","current_state":"undecided","options":[{"id":"A","description":"yes","authorises_blocked_work":true},{"id":"B","description":"no","authorises_blocked_work":false}],"impact":"the boot path","reversibility":"reversible: one call","cost_rework":"an hour","recommendation":"A","confidence":0.8,"trigger":"ux_direction","impact_radius":"R0"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
mkdir -p "$MROOT/product/newdir"; echo "a" > "$MROOT/product/newdir/a.rs"; echo "b" > "$MROOT/product/newdir/b.rs"
CK="$(res checkpoint create --next-action "continue" --step "after raising a gate and adding two untracked files")"
echo "   open_questions: $(echo "$CK" | python3 -c "import json,sys;print(json.load(sys.stdin)['open_questions'])")"
check "$(echo "$CK" | python3 -c "import json,sys;q=json.load(sys.stdin)['open_questions'];print(1 if any('$GB' in str(x) for x in q) else 0)")" "D.N1-01 the checkpoint records the OS's open questions (the pending gate)" "$(echo "$CK" | python3 -c "import json,sys;print(json.load(sys.stdin)['open_questions'])")"
FC="$(echo "$CK" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['files_changed']))")"
echo "   files_changed: $(echo "$FC" | head -c 300)"
check "$(echo "$FC" | python3 -c "
import json,sys;f=json.load(sys.stdin)
print(1 if 'product/newdir/a.rs' in f and 'product/newdir/b.rs' in f else 0)")" "D.N1-01b files_changed names each file in a new untracked directory, not the directory" "$FC"

summary
