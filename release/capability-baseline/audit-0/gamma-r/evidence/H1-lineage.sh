#!/usr/bin/env bash
# P2-AR-0010 — H1 SPEC lineage (Contract v3 lines 460-478): the system can trace idea -> ... -> live evidence.
# One governed record (or record field) per lineage stage, linked by the product's typed relation fields; the derived
# graph is rebuilt from Git + records and each consecutive stage pair is traced with `gov memory graph`.
source "$(dirname "$0")/lib.sh"
R=$(mkproj h1)
echo "project: $R"
python3 - "$R" <<'PY'
import json, os, sys
r = sys.argv[1]
def w(rel, d):
    p = os.path.join(r, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(json.dumps(d, indent=1) + "\n")
A = "ACTIVE"
w("spec/product/PRJ-0100.yaml", {"id":"PRJ-0100","type":"project","title":"Orders ledger","status":A,"product_intent":"IDEA: an append-only order ledger with exact totals",
   "mission":"let clerks trust totals","outcomes":["exact totals","auditable history"],"actors":["clerk","auditor"]})
w("spec/workflows/WF-0001.yaml", {"id":"WF-0001","type":"workflow","title":"Journey: clerk records a day of orders","status":A,"actor":"clerk","derived_from":["PRJ-0100"]})
w("spec/scenarios/SCN-0001.yaml", {"id":"SCN-0001","type":"scenario","title":"Append two orders and total","status":A,"feature":"F-0001","actor":"clerk","derived_from":["WF-0001"],
   "given":["an empty ledger"],"when":["two orders are appended"],"then":["total_cents is 399"],"data_requirements":["DATA-0001"],"success_criteria":["exact total"],"failure_criteria":["duplicate ids accepted"]})
w("spec/features/F-0001.yaml", {"id":"F-0001","type":"feature","title":"Order totals","status":A,"capability_category":"backend","scenarios":["SCN-0001"],"requirements":["REQ-0001","REQ-0002"],"interfaces":["API-0101"],"readiness":{},"derived_from":["PRJ-0100"]})
w("spec/data/DATA-0001.yaml", {"id":"DATA-0001","type":"data","title":"Representative order dataset","status":A,"feature":"F-0001","derived_from":["SCN-0001"],"provenance":{"source":"synthetic"}})
w("spec/requirements/REQ-0001.yaml", {"id":"REQ-0001","type":"requirement","title":"Totals are exact integer cents","status":A,"feature":"F-0001","kind":"functional","derived_from":["SCN-0001","DATA-0001"],"acceptance_criteria":["sum of quantity*unit_cents"]})
w("spec/requirements/REQ-0002.yaml", {"id":"REQ-0002","type":"requirement","title":"NFR: total of 10k orders in < 50 ms","status":A,"feature":"F-0001","kind":"non_functional","derived_from":["SCN-0001"],"acceptance_criteria":["p95 < 50ms"]})
w("spec/research/RES-0001.yaml", {"id":"RES-0001","type":"research","title":"Integer vs decimal money","status":A,"question":"which representation?","method":"benchmark","conclusion":"integer cents","confidence":0.8,"derived_from":["REQ-0001","REQ-0002"]})
w("spec/experiments/EXP-0001.yaml", {"id":"EXP-0001","type":"experiment","title":"Overflow experiment","status":A,"hypothesis":"u64 suffices","derived_from":["RES-0001"],"production_merge_allowed":False})
w("spec/decisions/D-0101.yaml", {"id":"D-0101","type":"decision","title":"Use u64 integer cents","status":A,"question":"money type","chosen_option":"u64 cents","derived_from":["RES-0001","EXP-0001"],"affects":["REQ-0001"]})
w("spec/architecture/ALG-0001.yaml", {"id":"ALG-0001","type":"architecture","title":"Algorithm: checked summation of line totals","status":A,"kind":"algorithm","governed_by":["D-0101"]})
w("spec/architecture/ARCH-0101.yaml", {"id":"ARCH-0101","type":"architecture","title":"Ledger module architecture","status":A,"derived_from":["ALG-0001"],"governed_by":["D-0101"]})
w("spec/interfaces/API-0101.yaml", {"id":"API-0101","type":"interface","title":"Ledger API","status":A,"kind":"library","governed_by":["ARCH-0101"]})
w("spec/security/SEC-0001.yaml", {"id":"SEC-0001","type":"security","title":"Threat model for ledger API","status":A,"derived_from":["API-0101"]})
w("spec/performance/PERF-0001.yaml", {"id":"PERF-0001","type":"performance","title":"Performance budget","status":A,"derived_from":["API-0101","REQ-0002"]})
w("spec/workflows/OPS-0001.yaml", {"id":"OPS-0001","type":"workflow","title":"Operations runbook: ledger recovery","status":A,"kind":"operations","derived_from":["ARCH-0101"]})
w("spec/tasks/TASK-0100.yaml", {"id":"TASK-0100","type":"task","title":"Design ledger types","status":A,"class":"architecture","task_status":"DONE","objective":"types","feature":"F-0001","derived_from":["SEC-0001","PERF-0001","OPS-0001"]})
w("spec/tasks/TASK-0101.yaml", {"id":"TASK-0101","type":"task","title":"Implement totals","status":A,"class":"implementation","task_status":"READY","objective":"implement totals","feature":"F-0001",
   "requirements":["REQ-0001","REQ-0002"],"decisions":["D-0101"],"scenarios":["SCN-0001"],"dependencies":["TASK-0100"],"acceptance_tests":["TST-0001"],"allowed_paths":["src/**"]})
w("spec/tasks/TST-0001.yaml", {"id":"TST-0001","type":"test-obligation","title":"Ledger acceptance tests","status":A,"feature":"F-0001","scenario":"SCN-0001","family":"acceptance","test_path":"tests/ledger_test.rs",
   "author_role":"independent-test-designer","independent_of_implementer":True,"data_provenance":"DATA-0001","tests":["REQ-0001"]})
print("lineage records written")
PY
( cd "$R" && git add -A && git commit -qm "lineage" )
g "$R" orchestrator S0 task claim TASK-0101 >/dev/null
echo "// totals" >> "$R/src/lib.rs"
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
g "$R" orchestrator S0 task close TASK-0101 --report "$(report_file "$R" impl "implemented totals" src/lib.rs passed)" | python3 -c 'import json,sys;e=json.load(sys.stdin);print("live evidence: close ok=",e["ok"],"report=",e.get("result",{}).get("report"),(e.get("error") or {}).get("code"))'
RPT=$(ls "$R/spec/reports" | grep '^RPT' | head -1 | sed 's/.yaml//')
g "$R" orchestrator S0 rebuild-memory >/dev/null

hdr "H1 stage-by-stage trace (gov memory graph <stage> --depth 1 must reach the next stage)"
trace() { # trace <bullet> <from> <to>
  g "$R" orchestrator S0 memory graph "$2" --depth 1 | python3 -c '
import json,sys
b,frm,to=sys.argv[1],sys.argv[2],sys.argv[3]
res=json.load(sys.stdin)["result"]
hit=[x for x in res if x["node"]==to]
print("  [%-28s] %-9s -> %-9s %s" % (b, frm, to, ("TRACED via "+hit[0]["via"]) if hit else "NOT REACHED (neighbours: %s)" % [x["node"] for x in res][:8]))' "$1" "$2" "$3"
}
cmd "idea, mission/outcomes, users/actors are fields of the project record PRJ-0100 (the product has no separate idea/mission/actor record types)"
g "$R" orchestrator S0 task show PRJ-0100 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  idea(product_intent)=%r mission=%r outcomes=%r actors=%r" % (r.get("product_intent"),r.get("mission"),r.get("outcomes"),r.get("actors")))'
trace "users/actors -> journeys"            PRJ-0100 WF-0001
trace "journeys -> scenarios"               WF-0001 SCN-0001
trace "scenarios -> features"               SCN-0001 F-0001
trace "features -> data"                    F-0001 DATA-0001
trace "data -> requirements"                DATA-0001 REQ-0001
trace "requirements -> NFRs"                F-0001 REQ-0002
trace "requirements -> research"            REQ-0001 RES-0001
trace "research -> experiments"             RES-0001 EXP-0001
trace "research/experiments -> decisions"   EXP-0001 D-0101
trace "decisions -> algorithms"             D-0101 ALG-0001
trace "algorithms -> architecture"          ALG-0001 ARCH-0101
trace "architecture -> interfaces"          ARCH-0101 API-0101
trace "interfaces -> security"              API-0101 SEC-0001
trace "interfaces -> performance"           API-0101 PERF-0001
trace "architecture -> operations"          ARCH-0101 OPS-0001
trace "sec/perf/ops -> WBS/task DAG"        SEC-0001 TASK-0100
trace "WBS: task -> task (DAG edge)"        TASK-0101 TASK-0100
trace "task DAG -> acceptance/test oblig."  TASK-0101 TST-0001
trace "test obligation -> requirement"      TST-0001 REQ-0001
trace "task -> live evidence (report)"      TASK-0101 "$RPT"
hdr "H1 end-to-end: forward from the idea record, and reverse impact from a requirement"
g "$R" orchestrator S0 memory graph PRJ-0100 --depth 30 | python3 -c '
import json,sys; res=json.load(sys.stdin)["result"]; nodes={x["node"]:x["hop"] for x in res}
chain=["WF-0001","SCN-0001","F-0001","DATA-0001","REQ-0001","REQ-0002","RES-0001","EXP-0001","D-0101","ALG-0001","ARCH-0101","API-0101","SEC-0001","PERF-0001","OPS-0001","TASK-0100","TASK-0101","TST-0001",sys.argv[1]]
print("  reached from PRJ-0100 (hop):", [(n,nodes.get(n)) for n in chain])
print("  unreached:", [n for n in chain if n not in nodes])' "$RPT"
g "$R" orchestrator S0 memory impact REQ-0001 --depth 4 | python3 -c 'import json,sys;res=json.load(sys.stdin)["result"];print("  impact(REQ-0001) ->",sorted({x["node"] for x in res}))'
cmd "graph integrity over the lineage (suite family graph_integrity)"
g "$R" orchestrator S0 audit --no-persist --family graph_integrity | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  ",r["families"],[f["message"] for f in r["findings"]][:6])'
cmd "a broken link is detected: SCN-0001 now derives from a journey that does not exist"
python3 - "$R/spec/scenarios/SCN-0001.yaml" <<'PY'
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["derived_from"]=["WF-9999"]; open(p,"w").write(json.dumps(d)+"\n")
PY
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
g "$R" orchestrator S0 audit --no-persist --family graph_integrity | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  ",r["families"],[f["message"] for f in r["findings"]][:6])'
echo END
