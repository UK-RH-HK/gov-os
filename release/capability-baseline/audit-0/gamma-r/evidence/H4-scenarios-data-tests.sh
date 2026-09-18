#!/usr/bin/env bash
# P2-AR-0010 — H4 Scenarios drive data/tests (Contract v3 lines 524-527).
source "$(dirname "$0")/lib.sh"
R=$(mkproj h4)
echo "project: $R"
python3 - "$R" "$(readiness_json '' 'ux_interactions')" <<'PY'
import json, os, sys
r, rd = sys.argv[1], json.loads(sys.argv[2])
def w(rel, d):
    p = os.path.join(r, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(json.dumps(d, indent=1) + "\n")
A = "ACTIVE"
w("spec/features/F-0001.yaml", {"id":"F-0001","type":"feature","title":"Order totals","status":A,"capability_category":"backend","readiness":rd,"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"]})
# the product's OWN fields for the chain: scenario.data_requirements, test-obligation.scenario / data_provenance
w("spec/scenarios/SCN-0001.yaml", {"id":"SCN-0001","type":"scenario","title":"Append two orders and total","status":A,"feature":"F-0001","actor":"clerk",
   "given":["an empty ledger"],"when":["two orders are appended"],"then":["total_cents is 399"],
   "data_requirements":["DATA-0001"],"success_criteria":["exact integer total"],"failure_criteria":["duplicate order ids accepted"]})
w("spec/data/DATA-0001.yaml", {"id":"DATA-0001","type":"data","title":"Data requirement: order lines","status":A,"author_role":"backend-engineer"})
w("spec/data/TD-0001.yaml", {"id":"TD-0001","type":"data","title":"Test dataset: 1k synthetic orders","status":A,"author_role":"backend-engineer"})
w("spec/tasks/TST-0001.yaml", {"id":"TST-0001","type":"test-obligation","title":"Ledger acceptance tests","status":A,"feature":"F-0001","scenario":"SCN-0001","family":"acceptance",
   "test_path":"tests/ledger_test.rs","author_role":"independent-test-designer","independent_of_implementer":True,"data_provenance":"TD-0001 (synthetic, generated)"})
w("spec/tasks/TASK-0001.yaml", {"id":"TASK-0001","type":"task","title":"Implement totals","status":A,"class":"implementation","task_status":"READY","objective":"implement totals",
   "feature":"F-0001","role":"backend-engineer","allowed_paths":["src/**"]})
print("records written")
PY
( cd "$R" && git add -A && git commit -qm h4 )
g "$R" orchestrator S0 rebuild-memory >/dev/null

hdr "H4.b1 FEATURE -> SCENARIOS -> DATA -> TEST DATA -> SUCCESS/FAILURE -> INDEPENDENT TESTS, traced with the product's own fields"
nb() { g "$R" orchestrator S0 memory graph "$1" --depth 1 | python3 -c 'import json,sys;res=json.load(sys.stdin)["result"];t=sys.argv[2];h=[x for x in res if x["node"]==t];print("  %-9s -> %-8s %s" % (sys.argv[1],t,("TRACED via "+h[0]["via"]) if h else "NOT an edge (neighbours: %s)" % sorted(x["node"] for x in res)))' "$1" "$2"; }
nb F-0001 SCN-0001
nb SCN-0001 DATA-0001
nb DATA-0001 TD-0001
nb TD-0001 TST-0001
nb SCN-0001 TST-0001
nb TST-0001 F-0001
cmd "the relation fields the graph derives edges from (records.rs RELATION_FIELDS) — is data_requirements / data_provenance among them?"
grep -n '("data_requirements"\|("data_provenance"\|("scenario",\|("scenarios",' "$WT/runtime/src/records.rs" | sed 's/^/  /'
cmd "success/failure criteria reach the implementer's context packet (via the scenario)"
g "$R" orchestrator S0 context compile TASK-0001 | python3 -c 'import json,sys;d=json.load(sys.stdin)["result"]["deterministic_authority"];s=d["scenarios"][0] if d["scenarios"] else {};print("  scenario:",s.get("id"),"success:",s.get("success_criteria"),"failure:",s.get("failure_criteria"));print("  acceptance_criteria block:",d["acceptance_criteria"])'
cmd "the chain gates implementation: TEST_POLICY.implementation_task_requires + independent_test_author_required_for"
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  complete chain -> TASK-0001 runnable:", "TASK-0001" in r["runnable"])'
python3 - "$R/spec/features/F-0001.yaml" <<'PY'
import json,sys;p=sys.argv[1];d=json.load(open(p));d["scenarios"]=[];json.dump(d,open(p,"w"))
PY
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  no scenarios   ->",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-0001"])'
python3 - "$R/spec/features/F-0001.yaml" <<'PY'
import json,sys;p=sys.argv[1];d=json.load(open(p));d["scenarios"]=["SCN-0001"];d["acceptance_tests"]=[];json.dump(d,open(p,"w"))
PY
mv "$R/spec/tasks/TST-0001.yaml" /tmp/h4tst.$$.yaml
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  no tests       ->",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-0001"])'
mv /tmp/h4tst.$$.yaml "$R/spec/tasks/TST-0001.yaml"
python3 - "$R/spec/tasks/TST-0001.yaml" <<'PY'
import json,sys;p=sys.argv[1];d=json.load(open(p));d["independent_of_implementer"]=False;json.dump(d,open(p,"w"))
PY
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  non-independent acceptance obligation ->",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-0001"])'
python3 - "$R/spec/tasks/TST-0001.yaml" <<'PY'
import json,sys;p=sys.argv[1];d=json.load(open(p));d["independent_of_implementer"]=True;json.dump(d,open(p,"w"))
PY
cmd "missing success or failure criteria on the scenario: is the chain refused anywhere?"
python3 - "$R/spec/scenarios/SCN-0001.yaml" <<'PY'
import json,sys;p=sys.argv[1];d=json.load(open(p));d.pop("success_criteria");d.pop("failure_criteria");json.dump(d,open(p,"w"))
PY
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  scenario without success/failure criteria -> TASK-0001 runnable:", "TASK-0001" in r["runnable"])'
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  suite findings mentioning SCN-0001:",[f["message"][:120] for f in r["findings"] if "SCN-0001" in f.get("message","")])'
cmd "(readiness still says success_criteria / failure_criteria PRESENT for F-0001: the cell is author-asserted)"
g "$R" orchestrator S0 readiness check F-0001 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  ",[(c["dimension"],c["state"]) for c in r["cells"] if c["dimension"] in ("success_criteria","failure_criteria","representative_test_data","independent_acceptance_tests")])'

hdr "H4.b2 test-data author independence"
cmd "the kernel has a data-author role"; g "$R" data-author S-da route --class data | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  data-author:",r["role"],r["minimum_tier"])'
cmd "the test dataset TD-0001 was authored by the implementer role (author_role: backend-engineer, same as TASK-0001.role): anything refused or flagged?"
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-0001 blocked reasons:",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-0001"],"runnable:","TASK-0001" in r["runnable"])'
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  suite findings mentioning TD-0001/DATA-0001/author:",[f["message"][:120] for f in r["findings"] if any(s in f.get("message","") for s in ("TD-0001","DATA-0001","author"))])'
cmd "source: where is a data author's independence recorded or compared? (search for data author / data_author / author_role consumers)"
grep -rn 'author_role\|data_author\|data-author' "$WT/runtime/src" --include=*.rs | grep -v 'owner_role' | sed "s|$WT/||;s/^/  /"

hdr "H4.b3 data provenance is recorded"
cmd "TST-0001 carries data_provenance; a second obligation without it, and a readiness cell 'representative_test_data: PRESENT' with no dataset record at all"
printf '{"id":"TST-0002","type":"test-obligation","title":"no provenance","status":"ACTIVE","feature":"F-0001","scenario":"SCN-0001","family":"acceptance","independent_of_implementer":true}\n' > "$R/spec/tasks/TST-0002.yaml"
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  findings mentioning TST-0002 or provenance:",[f["message"][:120] for f in r["findings"] if "TST-0002" in f.get("message","") or "provenance" in f.get("message","")])'
g "$R" orchestrator S0 task show TST-0001 | python3 -c 'import json,sys;print("  TST-0001.data_provenance =",json.load(sys.stdin)["result"].get("data_provenance"))'
cmd "is data_provenance consumed anywhere (DAG, close, suite, context)?"
grep -rn 'data_provenance' "$WT/runtime/src" --include=*.rs | sed "s|$WT/||;s/^/  /"; echo "  (no lines above = the field is stored when an author writes it, never required or read)"
rm -f /tmp/h4*.$$.*
echo END
