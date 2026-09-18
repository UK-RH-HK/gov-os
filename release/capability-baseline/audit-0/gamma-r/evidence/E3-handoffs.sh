#!/usr/bin/env bash
# P2-AR-0010 — E3 Typed A2A handoffs (Contract v3 lines 377-385): work completed, files changed, evidence/tests,
# discoveries/risks, lessons/proposed decisions, unresolved items, next action — persist beyond conversation lifetime.
source "$(dirname "$0")/lib.sh"
R=$(mkproj e3)
echo "project: $R"
g "$R" orchestrator S0 task create --id TASK-H1 --class implementation --objective "handoff target" --status READY --allowed 'src/**' >/dev/null
( cd "$R" && git add -A && git commit -qm fx )

hdr "E3.0 handoff creation is typed and persisted (session S-orch, process 1)"
g "$R" orchestrator S-orch handoff create --to-role backend-engineer --task TASK-H1 --fields '{"inputs":{"spec":"F-0001","scenarios":["SCN-0001"]}}' > /tmp/e3.$$.json
python3 -c 'import json,sys;e=json.load(open(sys.argv[1]));r=e["result"];print("  ok=",e["ok"],"id=",r["id"]);[print("   ",k,"=",json.dumps(r.get(k))) for k in ["from_role","to_role","task","inputs","expected_outputs","authority","required_return","handoff_status","state_class"]]' /tmp/e3.$$.json
HID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result"]["id"])' /tmp/e3.$$.json)
echo "  on disk: $(ls "$R"/spec/planning/)"
echo "  mandatory checkpoint before_handoff: $(grep -l 'before_handoff' "$R"/spec/reports/checkpoints/*.yaml | xargs -n1 basename)"

hdr "E3.1 the worker return contract is enforced field by field (each bullet's field removed -> typed refusal)"
full='{"task":"TASK-H1","status":"success","work_completed":"implemented totals","files_changed":["src/lib.rs"],"evidence":["cargo test: 3 passed"],"tests":{"status":"passed","command":"cargo test"},"discoveries":["overflow at u32"],"risks":["rounding"],"lessons":["check arithmetic width before implementing totals"],"proposed_decisions":["use u64 cents"],"unresolved":["currency conversion"],"recommended_next_action":"independent test design for totals"}'
for f in work_completed files_changed evidence tests discoveries risks lessons proposed_decisions unresolved recommended_next_action; do
  python3 -c 'import json,sys;d=json.loads(sys.argv[1]);d.pop(sys.argv[2]);json.dump(d,open(sys.argv[3],"w"))' "$full" "$f" /tmp/e3r.$$.json
  printf '  without %-24s ' "$f"; gq "$R" backend-engineer S-worker handoff return "$HID" --file /tmp/e3r.$$.json | cut -c1-170
done
printf '  %-32s ' "status: 'done' (not in enum)"; python3 -c 'import json,sys;d=json.loads(sys.argv[1]);d["status"]="done";json.dump(d,open(sys.argv[2],"w"))' "$full" /tmp/e3r.$$.json; gq "$R" backend-engineer S-worker handoff return "$HID" --file /tmp/e3r.$$.json | cut -c1-170
echo "  handoff status after refused returns: $(grep handoff_status "$R/spec/planning/$HID.yaml")"

hdr "E3.2 a complete return is recorded (worker session S-worker, process N)"
echo "$full" > /tmp/e3r.$$.json
g "$R" backend-engineer S-worker handoff return "$HID" --file /tmp/e3r.$$.json | python3 -c 'import json,sys;e=json.load(sys.stdin);print("  ok=",e["ok"],json.dumps(e.get("result"))[:400])'

hdr "E3.3 persistence beyond the conversation: a fresh session/process reads every returned field from the governed record"
g "$R" orchestrator S-fresh task show "$HID" | python3 -c '
import json,sys; r=json.load(sys.stdin)["result"]; ret=r.get("return",{})
print("  handoff_status=",r.get("handoff_status"),"returned_at=",r.get("returned_at"))
for k,b in [("work_completed","work completed"),("files_changed","files changed"),("evidence","evidence"),("tests","tests"),("discoveries","discoveries"),("risks","risks"),("lessons","lessons"),("proposed_decisions","proposed decisions"),("unresolved","unresolved items"),("recommended_next_action","next action")]:
    print("   [%-18s] %-24s = %s" % (b, k, json.dumps(ret.get(k))))'
echo "  lessons in the return became governed lesson records (evidence, never authority):"
grep -l "from_handoff: $HID" "$R"/spec/lessons/*.yaml 2>/dev/null | while read f; do echo "   $(basename $f): $(grep -E '^(status|state_class|scope):' $f | tr '\n' ' ')"; done
cmd "derived memory deleted and rebuilt: the handoff record is unaffected and is found by structured lookup"
rm -rf "$R/.governance-runtime/state.db"*
g "$R" orchestrator S-fresh rebuild-memory >/dev/null
g "$R" orchestrator S-fresh memory query "$HID" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  routes=",r.get("routes"),"top hit=",[(h.get("id") or h.get("record_id") or h.get("path")) for h in r["hits"][:2]])'
cmd "git commit + fresh clone on another path (another machine/session): the full return is present"
( cd "$R" && git add -A && git commit -qm "handoff returned" )
C=$PROBES/e3-clone; rm -rf "$C"; git clone -q "$R" "$C"
python3 - "$C/spec/planning/$HID.yaml" <<'PY'
import yaml,sys; d=yaml.safe_load(open(sys.argv[1])); r=d["return"]
print("  clone:", sys.argv[1].split("/")[-1], "status", d["handoff_status"], "fields:", sorted(r.keys()))
PY

hdr "E3.4 authority on the return: files outside the handoff's authority are refused and recorded"
g "$R" orchestrator S-orch handoff create --to-role backend-engineer --task TASK-H1 > /tmp/e3.$$.json
H2=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result"]["id"])' /tmp/e3.$$.json)
python3 -c 'import json,sys;d=json.loads(sys.argv[1]);d["files_changed"]=["src/lib.rs","governance/kernel/policies/AUTHORITY_POLICY.yaml","docs/x.md"];json.dump(d,open(sys.argv[2],"w"))' "$full" /tmp/e3r.$$.json
gq "$R" backend-engineer S-worker handoff return "$H2" --file /tmp/e3r.$$.json | cut -c1-240
grep -A3 authority_violations "$R/spec/planning/$H2.yaml" | sed 's/^/  /'
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  suite mutation_scope:",[f["message"][:120] for f in r["findings"] if f.get("family")=="mutation_scope"])'

hdr "E3.5 binding of a return to its handoff (recipient role / session / single return)"
g "$R" orchestrator S-orch handoff create --to-role backend-engineer --task TASK-H1 > /tmp/e3.$$.json
H3=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result"]["id"])' /tmp/e3.$$.json)
echo "$full" > /tmp/e3r.$$.json
cmd "$H3 is addressed to backend-engineer; a frontend-engineer session returns it"
gq "$R" frontend-engineer S-other handoff return "$H3" --file /tmp/e3r.$$.json
cmd "a second, different return to the same (already RETURNED) handoff"
python3 -c 'import json,sys;d=json.loads(sys.argv[1]);d["work_completed"]="SECOND RETURN overwrote the first";d["unresolved"]=[];json.dump(d,open(sys.argv[2],"w"))' "$full" /tmp/e3r2.$$.json
gq "$R" backend-engineer S-worker handoff return "$H3" --file /tmp/e3r2.$$.json
python3 - "$R/spec/planning/$H3.yaml" <<'PY'
import yaml,sys; d=yaml.safe_load(open(sys.argv[1])); print("  record now: work_completed=%r unresolved=%r" % (d["return"]["work_completed"], d["return"]["unresolved"]))
PY
cmd "return to an unknown handoff id"
gq "$R" backend-engineer S-worker handoff return HND-9999 --file /tmp/e3r.$$.json
rm -f /tmp/e3*.$$.json
echo END
