#!/usr/bin/env bash
# P2-AR-0010 — F1 Skill lifecycle (Contract v3 lines 398-402).
source "$(dirname "$0")/lib.sh"
R=$(mkproj f1)
echo "project: $R"
audit_family() { g "$R" orchestrator S0 audit --no-persist --family "$1" | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  audit family",sys.argv[1],"->",r["families"].get(sys.argv[1]),[f["message"] for f in r["findings"]])' "$1"; }

hdr "F1.b1 skills are versioned methods (version + method steps), resolved per task and recorded with their version"
g "$R" orchestrator S0 skills list | python3 -c '
import json,sys
for s in json.load(sys.stdin)["result"]:
    print("  %-26s v%-6s %-7s source=%-7s method_steps=%d classes=%s" % (s["id"], s["version"], s["status"], s["_source"], len(s.get("method",[])), s.get("task_classes")))'
g "$R" orchestrator S0 task create --id TASK-S1 --class implementation --objective "impl with a skill" --status READY --fields '{"role":"backend-engineer","required_skills":["SKL-BACKEND-IMPL"]}' >/dev/null
g "$R" orchestrator S0 skills resolve TASK-S1 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  resolve TASK-S1: resolved=",r["resolved"],"missing=",r["missing"],"gap=",r["capability_gap"])'
g "$R" orchestrator S0 context compile TASK-S1 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  context packet required_skills (with version):",r["deterministic_authority"]["required_skills"])'

hdr "F1.b1.b skills are not authority: a project skill that 'grants' everything changes no authority decision"
mkdir -p "$R/governance/project/skills"
cat > "$R/governance/project/skills/SKL-GOD-MODE.yaml" <<'EOF'
id: SKL-GOD-MODE
name: grants everything
version: 1.0.0
status: ACTIVE
model_agnostic: true
roles: [all]
task_classes: [implementation, release, governance]
required_permissions: [SECRET_READ, DEPLOY_PRODUCTION, SYSTEM_INSTALL]
purpose: "attempts to confer authority"
method:
  - {step: act, description: "act with full authority"}
validation_scenarios:
  - {id: V1, expect: "nothing"}
EOF
g "$R" orchestrator S0 task create --id TASK-S2 --class release --objective "release with god-mode skill" --status READY --fields '{"role":"backend-engineer","required_skills":["SKL-GOD-MODE"]}' >/dev/null
g "$R" orchestrator S0 skills resolve TASK-S2 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  resolve TASK-S2: resolved=",r["resolved"])'
cmd "backend-engineer (holds the skill on its task) still cannot create tasks, pause, or use a SECRET_READ tool"
gq "$R" backend-engineer S-be task create --class release --objective x
gq "$R" backend-engineer S-be pause
g "$R" backend-engineer S-be tools resolve --capability secret_scan | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  tools resolve secret_scan as backend-engineer:",[t["tool_id"] for t in r["tools"]],"(TOOL-SECRETS-001 needs READ_REPO only)")'
g "$R" orchestrator S0 tools registry | python3 -c 'import json,sys;x=json.load(sys.stdin)["result"]["role_exposure"]["backend-engineer"];print("  backend-engineer permission classes unchanged:",x["permissions"])'
cmd "source: no authority/permission path reads skills"
grep -n 'skills' "$WT/runtime/src/authority.rs" "$WT/runtime/src/tools.rs" "$WT/runtime/src/capabilities/governance.rs" "$WT/runtime/src/policy.rs" | sed 's/^/  /' ; echo "  (no matches = skills are not consulted by authority, tool permissions, plugin authorisation or policy)"

hdr "F1.b2 applicability / inputs / outputs / evidence"
cmd "applicability is executable: resolution filters by task class and role"
g "$R" orchestrator S0 task create --id TASK-S3 --class implementation --objective "impl by frontend" --status READY --fields '{"role":"frontend-engineer"}' >/dev/null
g "$R" orchestrator S0 skills resolve TASK-S3 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  implementation/frontend-engineer ->",[s["id"] for s in r["candidates_by_class_role"]])'
g "$R" orchestrator S0 skills resolve TASK-S1 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  implementation/backend-engineer  ->",[s["id"] for s in r["candidates_by_class_role"]])'
cmd "inputs/outputs of the kernel skills (declared data)"
g "$R" orchestrator S0 skills list | python3 -c '
import json,sys
for s in json.load(sys.stdin)["result"]:
    if s["_source"]=="kernel": print("  %-26s inputs=%s outputs=%s" % (s["id"], s.get("inputs"), s.get("outputs")))'
cmd "a project skill with NO task_classes, inputs, outputs or evidence is accepted by the suite (schema requires only id,name,version,status,roles,method,validation_scenarios)"
cat > "$R/governance/project/skills/SKL-BARE.yaml" <<'EOF'
id: SKL-BARE
name: bare skill
version: 1.0.0
status: ACTIVE
roles: [backend-engineer]
method:
  - {step: do}
validation_scenarios:
  - {id: V1, expect: "something"}
EOF
audit_family skill_regression
cmd "is 'evidence' a skill element anywhere? (skill schema properties)"
python3 -c 'import json,sys;print("  ",sorted(json.load(open(sys.argv[1]))["properties"]))' "$R/governance/kernel/schemas/skill.schema.json"
cmd "are a skill's declared inputs/outputs checked against the task or the worker return? (source search)"
grep -rn '"inputs"\|"outputs"\|\["inputs"\]\|\["outputs"\]' "$WT/runtime/src/skills.rs" "$WT/runtime/src/orchestration/" "$WT/runtime/src/context/" | sed 's/^/  /'; echo "  (the only match listed, if any, is handoffs.rs defaulting the HANDOFF record's own inputs block -- unrelated to skills; skills.rs never reads a skill's inputs/outputs)"

hdr "F1.b3 skill regression is testable"
cmd "the skill_regression suite family on the installed kernel"
audit_family skill_regression
cmd "a project skill with no validation scenarios / an invalid version / an invalid status is reported"
cat > "$R/governance/project/skills/SKL-NOVAL.yaml" <<'EOF'
id: SKL-NOVAL
name: no validation scenarios
version: one
status: SHINY
roles: [backend-engineer]
method:
  - {step: do}
validation_scenarios: []
EOF
audit_family skill_regression
rm -f "$R/governance/project/skills/SKL-NOVAL.yaml"
cmd "a skill's method is changed without a version change: is anything stale, re-validated or refused?"
python3 - "$R/governance/project/skills/SKL-BARE.yaml" <<'PY'
import sys; p=sys.argv[1]; s=open(p).read().replace("- {step: do}", "- {step: do-something-else-entirely, description: silently rewritten method}"); open(p,"w").write(s)
PY
g "$R" orchestrator S0 task create --id TASK-S4 --class implementation --objective "uses bare" --status READY --fields '{"required_skills":["SKL-BARE"]}' >/dev/null
g "$R" orchestrator S0 skills resolve TASK-S4 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  resolved (same version, different method):",r["resolved"])'
audit_family skill_regression
cmd "is there any executable runner for a skill's validation_scenarios? (source search for validation_scenarios)"
grep -rn 'validation_scenarios' "$WT/runtime/src" | sed "s|$WT/||;s/^/  /"

hdr "F1.b4 lessons can propose skill updates through governed promotion"
cmd "a worker return carries a lesson about a skill; it becomes a PROVISIONAL PROJECT-scoped lesson (evidence)"
g "$R" orchestrator S0 handoff create --to-role backend-engineer --task TASK-S1 >/dev/null
HID=$(ls "$R/spec/planning" | grep HND | head -1 | sed 's/.yaml//')
printf '{"task":"TASK-S1","status":"success","work_completed":"x","files_changed":[],"evidence":[],"tests":{"status":"passed"},"discoveries":[],"risks":[],"lessons":["SKL-BACKEND-IMPL should require checked arithmetic for money"],"proposed_decisions":[],"unresolved":[],"recommended_next_action":"update SKL-BACKEND-IMPL"}' > "$R/.governance-runtime/ret.json"
g "$R" backend-engineer S-be handoff return "$HID" --file "$R/.governance-runtime/ret.json" | python3 -c 'import json,sys;print("  lessons_created:",json.load(sys.stdin)["result"]["lessons_created"])'
L=$(ls "$R/spec/lessons" | head -1 | sed 's/.yaml//'); grep -E '^(status|scope|lifecycle|state_class):' "$R/spec/lessons/$L.yaml" | sed 's/^/  /'
cmd "any project-level promotion command? (gov subcommands with lesson/skill/promote in their name)"
"$GOV" --help | grep -i -E 'lesson|skill|promot' | sed 's/^/  /'
"$GOV" skills --help | sed -n '/Commands:/,/Options:/p' | sed 's/^/  /'
cmd "the only promotion path: upstream (FRAMEWORK scope only). PROJECT-scoped lesson:"
gq "$R" backend-engineer S-be upstream prepare "$L"
cmd "re-scope the lesson to FRAMEWORK with a generic suggested change, then prepare / submit / cluster"
python3 - "$R/spec/lessons/$L.yaml" <<'PY'
import yaml,sys; p=sys.argv[1]; d=yaml.safe_load(open(p))
d.update({"scope":"FRAMEWORK","lifecycle":"classified","category":"skill","generic_failure_mode":"implementation skill does not require overflow-checked arithmetic for monetary totals","suggested_change":"update the backend implementation skill method: require checked arithmetic for monetary totals","impact":"medium","evidence_strength":"medium","sources":["HND-0001","TASK-S1"]})
yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
out=$(g "$R" backend-engineer S-be upstream prepare "$L"); echo "$out" | python3 -c 'import json,sys;e=json.load(sys.stdin);print("  prepare ok=",e["ok"],(e.get("result") or {}).get("packet_id") or (e.get("result") or {}).get("id"),(e.get("error") or {}).get("code"),str((e.get("error") or e.get("result") or {}).get("message", ""))[:200])'
PK=$(ls "$R/.governance-runtime/outbound" 2>/dev/null | head -1)
INBOX=$PROBES/f1-canonical/lessons/inbox; rm -rf "$PROBES/f1-canonical"; mkdir -p "$INBOX"
cmd "submit without --approved-by (LEARNING_POLICY.upstream.approval=human)"; gq "$R" change-controller S-cc upstream submit "$PK" --destination "$INBOX"
cmd "submit with --approved-by <any string> (the human approval is a CLI string)"; gq "$R" change-controller S-cc upstream submit "$PK" --destination "$INBOX" --approved-by owner
cmd "canonical intake clusters it into a Framework Change Proposal"
g "$R" orchestrator S0 lessons cluster --inbox "$INBOX" --proposals "$PROBES/f1-canonical/change-proposals" --write | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  clusters:",[(c["trigger"],c["release_action"],c.get("proposal")) for c in r["clusters"]],"written:",r["proposals_written"])'
ls "$PROBES/f1-canonical/change-proposals" 2>/dev/null | sed 's/^/  /'
cmd "a single framework lesson accumulates; the same lesson from three packets (repeated_low_level) writes an FCP"
for i in 2 3; do cp -r "$INBOX/$(ls $INBOX | head -1)" "$INBOX/copy$i"; done
g "$R" orchestrator S0 lessons cluster --inbox "$INBOX" --proposals "$PROBES/f1-canonical/change-proposals" --write | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  clusters:",[(c["trigger"],c["release_action"],c.get("proposal")) for c in r["clusters"]],"written:",r["proposals_written"])'
for f in "$PROBES"/f1-canonical/change-proposals/FCP-*.yaml; do [ -f "$f" ] && grep -E '^(id|type|status|suggested_framework_change|next):' "$f" | sed 's/^/  /'; done
echo "  lesson lifecycle after submit: $(grep -E '^lifecycle' "$R/spec/lessons/$L.yaml")"
echo END
