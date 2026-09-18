#!/usr/bin/env bash
# P2-AR-0010 — I1 Unified task DAG, 22 task classes (Contract v3 lines 535-558); I2 Task contract (560-569).
source "$(dirname "$0")/lib.sh"
R=$(mkproj i1i2)
echo "project: $R"

hdr "I1 one task per class in ONE DAG: created, schema-valid, class-specific minimum tier, runnable"
n=0
for cls in discovery research experiment specification decision-preparation data architecture implementation integration test-design test-execution security devops performance validation refactor repair documentation release tooling memory governance; do
  n=$((n+1)); id=$(printf 'TASK-C%02d' $n)
  o=$(g "$R" orchestrator S0 task create --id "$id" --class "$cls" --objective "a $cls task" --status READY)
  echo "$o" | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  I1.%-2s %-20s %s ok=%s tier=%s merge_allowed=%s %s" % (sys.argv[2],sys.argv[1],r.get("id"),e["ok"],r.get("minimum_model_tier"),r.get("production_merge_allowed"),(e.get("error") or {}).get("code") or ""))' "$cls" "$n"
done
g "$R" orchestrator S0 task dag | python3 -c '
import json,sys; r=json.load(sys.stdin)["result"]
ids=["TASK-C%02d"%i for i in range(1,23)]
print("  in one DAG: runnable %d/22, blocked %s" % (sum(1 for i in ids if i in r["runnable"]), [b for b in r["blocked"] if b["task"] in ids]))'
cmd "classes outside the taxonomy are rejected; one cross-class dependency (implementation depends on research) blocks in the same DAG"
gq "$R" orchestrator S0 task create --class coding --objective x
g "$R" orchestrator S0 task create --id TASK-X1 --class implementation --objective "impl after research" --status READY --deps TASK-C02 --fields '{"scenarios":["SCN-1"],"acceptance_tests":["TST-1"]}' >/dev/null
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-X1:",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-X1"])'
cmd "the 23rd enum value (migration) is extra to the owner list"
python3 -c 'import json,sys;print("  task.class enum:",json.load(open(sys.argv[1]))["properties"]["class"]["enum"])' "$R/governance/kernel/schemas/task.schema.json"

hdr "I2 task contract: every field declared on one task, then each field's consumer exercised"
mkdir -p "$R/spec/requirements" "$R/spec/scenarios" "$R/spec/decisions"
printf '{"id":"REQ-0001","type":"requirement","title":"exact totals","status":"ACTIVE","kind":"functional","acceptance_criteria":["exact"]}\n' > "$R/spec/requirements/REQ-0001.yaml"
printf '{"id":"SCN-0001","type":"scenario","title":"two orders","status":"ACTIVE","success_criteria":["399"],"failure_criteria":["dup ids"]}\n' > "$R/spec/scenarios/SCN-0001.yaml"
printf '{"id":"D-0100","type":"decision","title":"u64 cents","status":"ACTIVE","chosen_option":"u64"}\n' > "$R/spec/decisions/D-0100.yaml"
printf '{"id":"TST-0001","type":"test-obligation","title":"acc","status":"ACTIVE","family":"unit","independent_of_implementer":true}\n' > "$R/spec/tasks/TST-0001.yaml"
g "$R" orchestrator S0 task create --id TASK-FULL --class implementation --objective "implement exact totals" --status READY --allowed 'src/**' --fields '{
  "requirements":["REQ-0001"],"decisions":["D-0100"],"dependencies":[],"blocks":["TASK-BLOCKED-BY-FULL"],
  "scenarios":["SCN-0001"],"required_data":["DATA-9999"],"acceptance_tests":["TST-0001"],
  "required_skills":["SKL-BACKEND-IMPL","SKL-DOES-NOT-EXIST"],"required_tools":["TOOL-CARGO-001","TOOL-DOES-NOT-EXIST"],
  "minimum_model_tier":"T3","minimum_reasoning":"high","forbidden_paths":["src/secret_core.rs"],"production_merge_allowed":true,"role":"backend-engineer"}' | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-FULL fields:",sorted(k for k in r if k not in ("id","type","title","status","created")))'
g "$R" orchestrator S0 task create --id TASK-BLOCKED-BY-FULL --class documentation --objective "must wait for TASK-FULL" --status READY >/dev/null
( cd "$R" && git add -A && git commit -qm i2 )
g "$R" orchestrator S0 rebuild-memory >/dev/null
g "$R" orchestrator S0 context compile TASK-FULL > /tmp/i2ctx.$$.json
ctx() { python3 -c 'import json,sys;d=json.load(open(sys.argv[1]))["result"]["deterministic_authority"];print("  [%s] %s" % (sys.argv[2], eval(sys.argv[3])))' /tmp/i2ctx.$$.json "$1" "$2"; }
ctx "I2.b1 objective           " 'd["objective"]'
ctx "I2.b2 requirements        " '[x["id"] for x in d["governing_requirements"]]'
ctx "I2.b2 decisions           " '[x["id"] for x in d["active_decisions"]]'
ctx "I2.b4 scenarios           " '[x["id"] for x in d["scenarios"]]'
ctx "I2.b4 required_data       " '"required_data" in json.dumps(d) and "DATA-9999" in json.dumps(d)'
ctx "I2.b5 acceptance tests    " 'd["acceptance_criteria"]'
ctx "I2.b6 required skills     " 'd["required_skills"]'
ctx "I2.b6 required tools      " 'd["required_tools"]'
ctx "I2.b7 tier/reasoning      " '(d["minimum_model_tier"], d["minimum_reasoning"])'
ctx "I2.b8 allowed/prohibited  " '(d["allowed_writes"], d["prohibited_writes"])'
ctx "I2.b9 production merge    " '"production_merge_allowed" in json.dumps(d)'
cmd "I2.b3 dependencies are enforced by the DAG; 'blocks' is not (TASK-FULL.blocks = [TASK-BLOCKED-BY-FULL], TASK-FULL still open)"
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-BLOCKED-BY-FULL runnable:", "TASK-BLOCKED-BY-FULL" in r["runnable"])'
g "$R" orchestrator S0 memory graph TASK-FULL --depth 1 | python3 -c 'import json,sys;print("  graph edge TASK-FULL->TASK-BLOCKED-BY-FULL:",[(x["node"],x["via"]) for x in json.load(sys.stdin)["result"] if x["node"]=="TASK-BLOCKED-BY-FULL"])'
cmd "I2.b6 skills are resolved with a capability gap; missing tools are never checked"
g "$R" orchestrator S0 skills resolve TASK-FULL | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  skills resolved=",r["resolved"],"missing=",r["missing"],"gap=",r["capability_gap"])'
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-FULL runnable despite TOOL-DOES-NOT-EXIST and SKL-DOES-NOT-EXIST:", "TASK-FULL" in r["runnable"])'
cmd "I2.b7 tier/reasoning are validated at creation and drive routing"
gq "$R" orchestrator S0 task create --class research --objective x --fields '{"minimum_model_tier":"T9"}'
gq "$R" orchestrator S0 task create --class research --objective x --fields '{"minimum_reasoning":"ludicrous"}'
g "$R" orchestrator S0 route --task TASK-FULL | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  route TASK-FULL: min_tier=%s reasoning=%s" % (r["minimum_tier"],r["reasoning"]))'
cmd "I2.b8 allowed/forbidden paths at close (observed mutations since the claim baseline)"
g "$R" backend-engineer S-be task claim TASK-FULL >/dev/null
echo "// forbidden edit" > "$R/src/secret_core.rs"; echo "// ok" >> "$R/src/lib.rs"
g "$R" backend-engineer S-be rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-be task close TASK-FULL --report "$(report_file "$R" full "x" "src/lib.rs,src/secret_core.rs" passed)"
rm "$R/src/secret_core.rs"; echo "  (forbidden file removed)"
mkdir -p "$R/docs"; echo "x" > "$R/docs/outside.md"
g "$R" backend-engineer S-be rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-be task close TASK-FULL --report "$(report_file "$R" full2 "x" "src/lib.rs,docs/outside.md" passed)"
rm -f "$R/docs/outside.md"
cmd "I2.b8.x any path once touched by ANY committed CIT is permanently accepted as in scope for every later task"
printf '[{"op":"set_field","target":"REQ-0001","field":"priority","value":"high"}]' > "$R/.governance-runtime/mf.json"
c=$(g "$R" orchestrator S0 cit propose --proposal "priority" --trigger editorial --targets REQ-0001 --manifest "$R/.governance-runtime/mf.json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
g "$R" orchestrator S0 cit simulate "$c" >/dev/null; g "$R" change-controller S-cc cit approve "$c" --by change-controller --method auto >/dev/null; g "$R" change-controller S-cc cit execute "$c" | python3 -c 'import json,sys;print("  ",json.load(sys.stdin)["result"].get("cit_status"))'
( cd "$R" && git add -A && git commit -qm cit )
g "$R" orchestrator S0 task create --id TASK-LATER --class implementation --objective "later src-only task" --status READY --allowed 'src/**' >/dev/null
( cd "$R" && git add -A && git commit -qm later )
g "$R" backend-engineer S-be2 task claim TASK-LATER >/dev/null
python3 - "$R/spec/requirements/REQ-0001.yaml" <<'PY'
import yaml,sys;p=sys.argv[1];d=yaml.safe_load(open(p));d["acceptance_criteria"]=["rewritten by a src-only task"];yaml.safe_dump(d,open(p,"w"))
PY
g "$R" backend-engineer S-be2 rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-be2 task close TASK-LATER --report "$(report_file "$R" later "x" "spec/requirements/REQ-0001.yaml" passed)"
echo "  REQ-0001 acceptance_criteria now: $(python3 -c 'import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))["acceptance_criteria"])' "$R/spec/requirements/REQ-0001.yaml")"
cmd "I2.b8.y close without a claim baseline falls back to 'git status --porcelain'; the first path loses its first character"
( cd "$R" && git add -A && git commit -qm x )
g "$R" orchestrator S0 task create --id TASK-NOCLAIM --class documentation --objective "closed without claim" --status READY --allowed 'README.md' >/dev/null
( cd "$R" && git add -A && git commit -qm y )
echo "more" >> "$R/README.md"
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
( cd "$R" && git status --porcelain | head -3 | sed 's/^/  porcelain: [/;s/$/]/' )
gq "$R" backend-engineer S-nc task close TASK-NOCLAIM --report "$(report_file "$R" nc "x" "README.md" passed)"
cmd "I2.b9 production-merge permission: an experiment task (production_merge_allowed false) changing production source"
g "$R" orchestrator S0 task create --id TASK-EXP --class experiment --objective "try an idea" --status READY --allowed 'src/**' | python3 -c 'import json,sys;print("  TASK-EXP production_merge_allowed =",json.load(sys.stdin)["result"]["production_merge_allowed"])'
( cd "$R" && git add -A && git commit -qm exp )
g "$R" backend-engineer S-exp task claim TASK-EXP >/dev/null
echo "// experimental change merged into production source" >> "$R/src/lib.rs"
g "$R" backend-engineer S-exp rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-exp task close TASK-EXP --report "$(report_file "$R" exp "experiment" "src/lib.rs" passed)"
grep -rn 'production_merge_allowed' "$WT/runtime/src" --include=*.rs | sed "s|$WT/||;s/^/  consumer? /"
rm -f /tmp/i2*.$$.*
echo END
