#!/usr/bin/env bash
# P2-AR-0010 — H2 26-dimension readiness contract + statuses + silent-N/A rule (Contract v3 lines 480-515);
#              H3 readiness generates work (lines 517-522).
source "$(dirname "$0")/lib.sh"
R=$(mkproj h2h3)
echo "project: $R"
check() { g "$R" orchestrator S0 readiness check "$1"; }

hdr "H2.dims every dimension is tracked explicitly: feature F-ALL with an EMPTY readiness map (each line = one dimension)"
write_feature "$R" F-ALL '{}'
check F-ALL | python3 -c '
import json,sys; r=json.load(sys.stdin)["result"]
for i,c in enumerate(r["cells"],1): print("  dim %2d %-30s state=%-8s pre_implementation=%-5s gap_task_class=%s" % (i,c["dimension"],c["state"],c["pre_implementation"],c["gap_task_class"]))
print("  cells=%d coverage=%s pre_implementation_ok=%s invalid=%s" % (len(r["cells"]),r["coverage"],r["pre_implementation_ok"],r["invalid"]))'

hdr "H2.statuses one cell per status/form on feature F-ST (others PRESENT)"
RD=$(readiness_json '' '')
RD=$(python3 - "$RD" <<'PY'
import json,sys; d=json.loads(sys.argv[1])
d.update({"intent_outcome":"PRESENT","user_actor":"MISSING","journey_workflow":"PROVISIONAL","scenarios":"BLOCKED",
  "inputs":{"status":"N/A_WITH_REASON","reason":"library has no external inputs"},
  "data_model_schema":{"status":"N/A_WITH_REASON"},
  "representative_test_data":"N/A",
  "processing_algorithm":"DONE",
  "expected_outputs":{"status":"PRESENT"},
  "functional_requirements":{"status":"N/A_WITH_REASON","reason":"ok"}})
del d["non_functional_requirements"]
print(json.dumps(d))
PY
)
write_feature "$R" F-ST "$RD"
check F-ST | python3 -c '
import json,sys; r=json.load(sys.stdin)["result"]
show=["intent_outcome","user_actor","journey_workflow","scenarios","inputs","data_model_schema","representative_test_data","processing_algorithm","expected_outputs","functional_requirements","non_functional_requirements"]
lab={"intent_outcome":"PRESENT","user_actor":"MISSING","journey_workflow":"PROVISIONAL","scenarios":"BLOCKED","inputs":"N/A_WITH_REASON + reason","data_model_schema":"N/A_WITH_REASON, no reason (silent)","representative_test_data":"\"N/A\" (silent)","processing_algorithm":"unknown status \"DONE\"","expected_outputs":"object {status: PRESENT}","functional_requirements":"N/A_WITH_REASON, 2-char reason","non_functional_requirements":"cell absent"}
for c in r["cells"]:
    if c["dimension"] in show: print("  %-28s given %-34s -> state=%-16s ok=%-5s" % (c["dimension"], lab[c["dimension"]], c["state"], c["ok"]))
print("  invalid (silent-N/A / malformed) list:", r["invalid"])
print("  gaps:", r["gaps"]); print("  pre_implementation_ok:", r["pre_implementation_ok"], " coverage:", round(r["coverage"],3))'
cmd "does the governance suite flag the malformed cells? (feature F-ST against the kernel feature schema)"
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  ",[ (f["family"],f["severity"],f["message"][:170]) for f in r["findings"] if "F-ST" in json.dumps(f)])'
cmd "status/feature views"
g "$R" orchestrator S0 status | python3 -c 'import json,sys;[print("  ",f) for f in json.load(sys.stdin)["result"]["features"]]'

hdr "H3 readiness generates work (readiness plan F-ALL): one generated task per missing cell, in the same DAG"
g "$R" orchestrator S0 task create --id TASK-IMPL-ALL --class implementation --objective "implement F-ALL" --feature F-ALL --status READY --fields '{"scenarios":["SCN-X"],"acceptance_tests":["TST-X"]}' >/dev/null
g "$R" orchestrator S0 readiness plan F-ALL > /tmp/h3plan.$$.json
python3 - /tmp/h3plan.$$.json "$R" <<'PY'
import json,sys,os
r=json.load(open(sys.argv[1]))["result"]; root=sys.argv[2]
print("  created:",len(r["created_tasks"]),"pre-implementation gap tasks:",len(r["pre_implementation_gap_tasks"]),"implementation tasks now blocked:",r["implementation_tasks_blocked"])
import re
for t in r["created_tasks"]:
    d=json.loads(json.dumps(__import__("yaml").safe_load(open(os.path.join(root,"spec/tasks",t+".yaml")))))
    print("  %-10s cell=%-30s class=%-20s status=%-6s role=%s allowed=%s" % (t,d["readiness_cell"],d["class"],d["task_status"],d.get("role"),d["allowed_paths"]))
PY
cmd "H3.b1 data / b2 performance / b3 security / b4 independent test-design: the generated classes for those cells"
python3 - "$R" <<'PY'
import yaml,glob,sys,os
m={}
for f in glob.glob(os.path.join(sys.argv[1],"spec/tasks/TASK-*.yaml")):
    d=yaml.safe_load(open(f))
    if d.get("feature")=="F-ALL" and d.get("readiness_cell"): m[d["readiness_cell"]]=(d["id"],d["class"],d["objective"])
for cell,b in [("data_model_schema","H3.b1 missing data"),("representative_test_data","H3.b1 missing data"),("performance_capacity","H3.b2 missing performance target"),("security_privacy","H3.b3 missing security analysis"),("independent_acceptance_tests","H3.b4 missing independent test")]:
    print("  [%-32s] %-28s -> %s" % (b,cell,m.get(cell)))
PY
cmd "skills the generated performance / test-design tasks resolve to (is the performance task a benchmark/research task? is the test-design task bound to an independent author?)"
for cell in performance_capacity independent_acceptance_tests; do
  T=$(python3 - "$R" "$cell" <<'PY'
import yaml,glob,sys,os
for f in glob.glob(os.path.join(sys.argv[1],"spec/tasks/TASK-*.yaml")):
    d=yaml.safe_load(open(f))
    if d.get("readiness_cell")==sys.argv[2] and d.get("feature")=="F-ALL": print(d["id"])
PY
)
  printf '  %-28s %s skills=' "$cell" "$T"; g "$R" orchestrator S0 skills resolve "$T" | python3 -c 'import json,sys;print([s["id"] for s in json.load(sys.stdin)["result"]["candidates_by_class_role"]])'
done
TD=$(grep -l 'readiness_cell: independent_acceptance_tests' "$R"/spec/tasks/TASK-*.yaml | head -1 | xargs basename | sed 's/.yaml//')
cmd "who may take the generated independent test-design task $TD? the implementer role"
gq "$R" backend-engineer S-impl task claim "$TD"
g "$R" orchestrator S0 task release "$TD" --force >/dev/null
cmd "re-planning does not duplicate gap tasks (idempotent)"
g "$R" orchestrator S0 readiness plan F-ALL | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  second plan created:",r["created_tasks"],"existing gap tasks linked:",len(r["pre_implementation_gap_tasks"]))'

hdr "H3.b5 production implementation does not become READY before prerequisite cells satisfy policy"
write_feature "$R" F-5 "$(readiness_json 'performance_capacity,security_privacy' 'ux_interactions')"
g "$R" orchestrator S0 task create --id TASK-IMPL5 --class implementation --objective "implement F-5" --feature F-5 --status DRAFT --fields '{"scenarios":["SCN-X"],"acceptance_tests":["TST-X"]}' >/dev/null
( cd "$R" && git add -A && git commit -qm h3 )
cmd "the DAG computes it BLOCKED; replan persists BLOCKED; continue never offers it"
g "$R" orchestrator S0 task status TASK-IMPL5 BLOCKED >/dev/null
g "$R" orchestrator S0 task replan | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  runnable contains TASK-IMPL5:", "TASK-IMPL5" in r["runnable"])'
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  blocked reasons:",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-IMPL5"])'
echo "  stored: $(grep task_status "$R/spec/tasks/TASK-IMPL5.yaml")"
cmd "an L2 role sets it READY directly (task status), and an implementer claims it"
gq "$R" product-spec-agent S-ps task status TASK-IMPL5 READY
echo "  stored: $(grep task_status "$R/spec/tasks/TASK-IMPL5.yaml")"
gq "$R" backend-engineer S-impl task claim TASK-IMPL5
echo "  stored: $(grep task_status "$R/spec/tasks/TASK-IMPL5.yaml")"
g "$R" orchestrator S0 task release TASK-IMPL5 --force >/dev/null
cmd "the same at creation: task create --status READY on an unready feature is accepted"
gq "$R" orchestrator S0 task create --id TASK-IMPL5B --class implementation --objective "x" --feature F-5 --status READY --fields '{"scenarios":["SCN-X"],"acceptance_tests":["TST-X"]}'
echo "  stored: $(grep task_status "$R/spec/tasks/TASK-IMPL5B.yaml")"
cmd "the project overlay can switch the rule off (PROJECT_POLICY.readiness.enforce_pre_implementation_cells: false)"
python3 - "$R/governance/project/PROJECT_POLICY.yaml" <<'PY'
import yaml,sys; p=sys.argv[1]; d=yaml.safe_load(open(p)); d["readiness"]["enforce_pre_implementation_cells"]=False; yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  with enforcement off: TASK-IMPL5 runnable:", "TASK-IMPL5" in r["runnable"])'
g "$R" orchestrator S0 policy overrides | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  policy overrides report applied=",r["applied"],"refused=",r["refused"])'
g "$R" orchestrator S0 doctor | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  doctor mentions the readiness switch:", [c["id"] for c in r["checks"] if "enforce_pre_implementation" in json.dumps(c) or "readiness" in c["message"].lower()])'
python3 - "$R/governance/project/PROJECT_POLICY.yaml" <<'PY'
import yaml,sys; p=sys.argv[1]; d=yaml.safe_load(open(p)); d["readiness"]["enforce_pre_implementation_cells"]=True; yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
cmd "cells satisfied -> the DAG makes it runnable (replan READY)"
write_feature "$R" F-5 "$(readiness_json '' 'ux_interactions')"
g "$R" orchestrator S0 task status TASK-IMPL5 BLOCKED >/dev/null
g "$R" orchestrator S0 task replan | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  runnable contains TASK-IMPL5:", "TASK-IMPL5" in r["runnable"], [c for c in r["changed"] if c["task"]=="TASK-IMPL5"])'
cmd "which kernel file defines the dimensions, and what happens when it is tampered/removed in the installed kernel"
cp "$R/governance/kernel/taxonomy/READINESS_DIMENSIONS.yaml" /tmp/h3dims.$$.bak
write_feature "$R" F-5 "$(readiness_json 'performance_capacity,security_privacy' 'ux_interactions')"
rm "$R/governance/kernel/taxonomy/READINESS_DIMENSIONS.yaml"
check F-5 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  dims file removed -> readiness check: cells=",len(r["cells"]),"coverage=",r["coverage"],"pre_implementation_ok=",r["pre_implementation_ok"])'
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  dag: TASK-IMPL5 runnable:", "TASK-IMPL5" in r["runnable"])'
gq "$R" backend-engineer S-impl task claim TASK-IMPL5
cp /tmp/h3dims.$$.bak "$R/governance/kernel/taxonomy/READINESS_DIMENSIONS.yaml"; rm -f /tmp/h3*.$$.*
echo END
