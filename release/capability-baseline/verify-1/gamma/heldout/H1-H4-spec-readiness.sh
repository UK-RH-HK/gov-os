#!/usr/bin/env bash
# Gamma held-out probe: H1 (SPEC lineage, 17 node kinds), H2 (26-dimension readiness contract and its five
# statuses, silent N/A invalid), H3 (readiness generates work), H4 (scenarios drive data/tests).
# Contract v3 :460-527, and P2-ADJ-0003 (H4 gaps degrade health, refuse nothing).
. "$(dirname "$0")/lib.sh"
newproj hspec --provision >/dev/null
S="$PROJ/spec"
mkdir -p "$S/features" "$S/scenarios" "$S/requirements" "$S/interfaces" "$S/architecture" "$S/research" "$S/experiments" "$S/data" "$S/tasks" "$S/decisions"

w() { python3 - "$1" "$2" <<'PY'
import sys, yaml, json
yaml.safe_dump(json.loads(sys.argv[2]), open(sys.argv[1], "w"))
PY
}
cat > "$S/PRJ-0001.yaml" <<'Y'
id: PRJ-0001
type: project
status: ACTIVE
state_class: AUTHORITATIVE
title: Gamma verification demo product
product_intent: "the idea: a governed demo product used to trace SPEC lineage end to end"
mission: "prove that every SPEC element is traceable"
outcomes: ["every lineage node is reachable from the feature"]
actors: ["operator", "auditor"]
Y
w "$S/features/FEAT-0001.yaml" '{"id":"FEAT-0001","type":"feature","status":"ACTIVE","state_class":"AUTHORITATIVE","title":"Traceable feature","capability_category":"core","requirements":["REQ-0001","REQ-0002"],"scenarios":["SCN-0001"],"interfaces":["API-0001"],"acceptance_tests":["TST-0001"],"governed_by":["PRJ-0001"],"readiness":{}}'
w "$S/requirements/REQ-0001.yaml" '{"id":"REQ-0001","type":"requirement","status":"ACTIVE","title":"Functional requirement","kind":"functional","feature":"FEAT-0001","acceptance_criteria":["the operator sees the trace"]}'
w "$S/requirements/REQ-0002.yaml" '{"id":"REQ-0002","type":"requirement","status":"ACTIVE","title":"Non-functional requirement","kind":"non-functional","feature":"FEAT-0001","acceptance_criteria":["the trace returns in under 1s"]}'
w "$S/interfaces/API-0001.yaml" '{"id":"API-0001","type":"interface","status":"ACTIVE","title":"Trace API","kind":"cli","version":"1.0.0","contract":{"command":"gov artefact lineage"},"producers":["FEAT-0001"],"consumers":["operator"]}'
w "$S/architecture/ARCH-0001.yaml" '{"id":"ARCH-0001","type":"architecture","status":"ACTIVE","title":"Trace architecture","summary":"records + graph edges","governed_by":["PRJ-0001"],"affects":["FEAT-0001"]}'
w "$S/research/RSH-0001.yaml" '{"id":"RSH-0001","type":"research","status":"ACTIVE","title":"How should the trace be computed?","question":"graph or scan?","method":"comparison","sources":["internal"],"conclusion":"graph","confidence":0.8,"influences":["D-0001"]}'
w "$S/experiments/EXP-0001.yaml" '{"id":"EXP-0001","type":"experiment","status":"ACTIVE","title":"Trace latency","hypothesis":"graph traversal is faster","method":"benchmark","influences":["D-0001"]}'
w "$S/decisions/D-0001.yaml" '{"id":"D-0001","type":"decision","status":"ACTIVE","title":"Compute the trace over canonical edges","state_class":"AUTHORITATIVE","chosen_option":"A","rationale":"deterministic","derived_from":["RSH-0001","EXP-0001"],"affects":["FEAT-0001","ARCH-0001"],"human_approved":false}'
mkdir -p "$S/workflows"
w "$S/workflows/WF-0001.yaml" '{"id":"WF-0001","type":"workflow","status":"ACTIVE","title":"Operator journey: trace a feature","summary":"the end-to-end journey an operator follows","governed_by":["PRJ-0001"],"affects":["FEAT-0001"]}'
w "$S/architecture/ALG-0001.yaml" '{"id":"ALG-0001","type":"algorithm","status":"ACTIVE","title":"Lineage traversal algorithm","summary":"breadth-first over canonical edges","governed_by":["ARCH-0001"]}'
w "$S/architecture/SEC-0001.yaml" '{"id":"SEC-0001","type":"security","status":"ACTIVE","title":"Trace security analysis","summary":"no secret is exposed by a lineage trace","affects":["FEAT-0001"]}'
w "$S/scenarios/SCN-0001.yaml" '{"id":"SCN-0001","type":"scenario","status":"ACTIVE","title":"Operator traces a feature","feature":"FEAT-0001","actor":"operator","given":"a governed feature","when":"the operator asks for its lineage","then":"every upstream element is listed","success_criteria":["every upstream element is listed"],"failure_criteria":["an upstream element is missing"],"data_requirements":["DATA-0001"],"tests":["TST-0001"]}'

# --- H1: the seventeen lineage kinds ---------------------------------------------------------------
g memory-engineer rebuild-memory >/dev/null 2>&1
mkdir -p "$PROJ/product/fixtures"; printf '{"rows":[1,2,3]}\n' > "$PROJ/product/fixtures/trace.json"
ds=$(g data-author data register --fields '{"data_kind":"requirement","id":"DATA-0001","title":"Trace fixture requirement","description":"rows the trace scenario needs","implements":["SCN-0001"]}' | jget "'ok' if d.get('ok') else d['error']['code']")
echo "    data register (requirement) -> $ds"
TD=$(g data-author data register --fields '{"data_kind":"test-dataset","id":"TD-0001","title":"Trace fixture dataset","implements":["DATA-0001"],"location":"product/fixtures/trace.json","provenance":{"source_kind":"synthetic","origin":"generated for this probe"}}' | jget "'ok' if d.get('ok') else d['error']['code']")
echo "    data register (dataset)     -> $TD"
w "$S/tasks/TST-0001.yaml" '{"id":"TST-0001","type":"test-obligation","status":"ACTIVE","title":"Independent acceptance test for SCN-0001","family":"acceptance","feature":"FEAT-0001","scenario":"SCN-0001","test_path":"tests/trace.rs","author_role":"independent-test-designer","independent_of_implementer":true,"test_data":["TD-0001"],"data_provenance":{"origin":"synthesised"}}'
g memory-engineer rebuild-memory >/dev/null 2>&1
lin=$(g orchestrator artefact lineage FEAT-0001 --direction reverse 2>/dev/null | jget "json.dumps(r)" 2>/dev/null)
kinds=$(python3 - <<'PY'
import json, os, subprocess, sys, yaml, glob
root = os.environ["PROJ"]
have = {}
for f in glob.glob(root + "/spec/**/*.yaml", recursive=True):
    try: d = yaml.safe_load(open(f))
    except Exception: continue
    if isinstance(d, dict) and d.get("type"): have.setdefault(d["type"], []).append(d.get("id"))
need = {
 "idea": lambda: any("product_intent" in (yaml.safe_load(open(f)) or {}) for f in glob.glob(root+"/spec/PRJ-*.yaml")),
 "mission/outcomes": lambda: any((yaml.safe_load(open(f)) or {}).get("outcomes") for f in glob.glob(root+"/spec/PRJ-*.yaml")),
 "users/actors": lambda: any((yaml.safe_load(open(f)) or {}).get("actors") for f in glob.glob(root+"/spec/PRJ-*.yaml")),
 "journeys": lambda: "journey" in have or "workflow" in have,
 "scenarios": lambda: "scenario" in have,
 "features/capabilities": lambda: "feature" in have,
 "data": lambda: any(d for d in have if d in ("data-requirement","test-dataset","data")),
 "requirements/NFRs": lambda: "requirement" in have,
 "research/experiments": lambda: "research" in have and "experiment" in have,
 "decisions": lambda: "decision" in have,
 "algorithms/processing": lambda: "algorithm" in have or "processing" in have,
 "architecture": lambda: "architecture" in have,
 "interfaces": lambda: "interface" in have,
 "security/performance/operations": lambda: any(d in have for d in ("security","operations","performance")),
 "WBS/task DAG": lambda: "task" in have,
 "acceptance/test obligations": lambda: "test-obligation" in have,
 "live evidence": lambda: any(d in have for d in ("report","audit","checkpoint")),
}
print(";".join("%s=%s" % (k, "yes" if v() else "NO") for k, v in need.items()))
PY
)
export PROJ
kinds=$(PROJ="$PROJ" python3 -c "
import json,os,glob,yaml
root=os.environ['PROJ']; have={}
for f in glob.glob(root+'/spec/**/*.yaml',recursive=True):
    try: d=yaml.safe_load(open(f))
    except Exception: continue
    if isinstance(d,dict) and d.get('type'): have.setdefault(d['type'],[]).append(d.get('id'))
prj=[yaml.safe_load(open(f)) for f in glob.glob(root+'/spec/PRJ-*.yaml')]
need=[('idea', any(p.get('product_intent') for p in prj)),
 ('mission/outcomes', any(p.get('mission') and p.get('outcomes') for p in prj)),
 ('users/actors', any(p.get('actors') for p in prj)),
 ('journeys', 'journey' in have or 'workflow' in have),
 ('scenarios','scenario' in have), ('features/capabilities','feature' in have),
 ('data', any(k in have for k in ('data-requirement','test-dataset','data'))),
 ('requirements/NFRs','requirement' in have),
 ('research/experiments','research' in have and 'experiment' in have),
 ('decisions','decision' in have),
 ('algorithms/processing', 'algorithm' in have or 'processing' in have),
 ('architecture','architecture' in have), ('interfaces','interface' in have),
 ('security/performance/operations', any(k in have for k in ('security','operations','performance'))),
 ('WBS/task DAG','task' in have), ('acceptance/test obligations','test-obligation' in have),
 ('live evidence', any(k in have for k in ('report','audit','checkpoint')))]
print(';'.join('%s=%s'%(k,'yes' if v else 'NO') for k,v in need))
print('types:', ','.join(sorted(have)))")
echo "    H1 node kinds: $kinds"
miss=$(printf '%s' "$kinds" | tr ';' '\n' | grep '=NO' | cut -d= -f1 | tr '\n' ',')
if [ -z "$miss" ]; then ok "H1: every one of the seventeen lineage kinds is a governed, traceable record kind"
else bad "H1: these lineage kinds have no governed record kind to trace: ${miss%,}"; fi
# the trace itself must run over the chain, not merely list files
tr1=$(g orchestrator artefact lineage FEAT-0001 --direction reverse 2>/dev/null | jget "'ok' if d.get('ok') else d['error']['code']")
echo "    artefact lineage FEAT-0001 -> $tr1"

# --- H2: 26 dimensions, five statuses, silent N/A invalid -------------------------------------------
dims=$(PROJ="$PROJ" python3 -c "
import yaml,os
d=yaml.safe_load(open(os.environ['PROJ']+'/governance/kernel/taxonomy/READINESS_DIMENSIONS.yaml'))
print(len(d['dimensions']))")
check "$dims" "26" "H2: the readiness contract has exactly 26 dimensions"
sts=$(PROJ="$PROJ" python3 -c "
import yaml,os
d=yaml.safe_load(open(os.environ['PROJ']+'/governance/kernel/taxonomy/READINESS_DIMENSIONS.yaml'))
print(','.join(sorted(d['cell_states'])))")
check "$sts" "BLOCKED,MISSING,N/A_WITH_REASON,PRESENT,PROVISIONAL" "H2: exactly the five statuses the contract names"
# every dimension is individually evaluated
rc=$(g orchestrator readiness check FEAT-0001 | jget "len(r['cells'])")
check "$rc" "26" "H2: readiness check evaluates all 26 cells for a feature"
# a silent N/A is invalid; an N/A with a reason is honoured
PROJ="$PROJ" python3 -c "
import yaml,os
p=os.environ['PROJ']+'/spec/features/FEAT-0001.yaml'
d=yaml.safe_load(open(p))
d['readiness']={'ux_interactions':'N/A','cost_constraints':{'status':'N/A_WITH_REASON','reason':'no budget applies to this demo'},'intent_outcome':'PRESENT'}
yaml.safe_dump(d,open(p,'w'))"
sil=$(g orchestrator readiness check FEAT-0001 | jget "'invalid' if any('ux_interactions' in str(x) for x in (r.get('invalid') or [])) else 'honoured'")
check "$sil" "invalid" "H2: a silent N/A is reported invalid, not honoured"
na=$(g orchestrator readiness check FEAT-0001 | jget "[c['state'] for c in r['cells'] if c['dimension']=='cost_constraints'][0]")
check "$na" "N/A_WITH_REASON" "H2: an N/A with a reason is honoured as a distinct state"

# --- H3: readiness generates work -------------------------------------------------------------------
gen=$(g orchestrator readiness plan FEAT-0001 | jget "json.dumps(r.get('created') or r.get('tasks') or r)" )
cls=$(g orchestrator task list | PROJ="$PROJ" python3 -c "
import sys,json,yaml,glob,os
root=os.environ['PROJ']
out={}
for f in glob.glob(root+'/spec/tasks/TASK-*.yaml'):
    d=yaml.safe_load(open(f))
    if d.get('generated_by')=='readiness-planner': out[d.get('readiness_cell')]=d.get('class')
print(json.dumps(out))")
echo "    generated readiness work: $cls"
for pair in "data_model_schema:data" "performance_capacity:performance" "security_privacy:security" "independent_acceptance_tests:test-design"; do
  cell=${pair%%:*}; want=${pair##*:}
  got=$(printf '%s' "$cls" | python3 -c "import sys,json;print(json.load(sys.stdin).get('$cell','none'))")
  check "$got" "$want" "H3: a missing $cell generates a $want task"
done
# the designated role of a generated gap task binds who may claim it
role=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
for f in glob.glob(os.environ['PROJ']+'/spec/tasks/TASK-*.yaml'):
    d=yaml.safe_load(open(f))
    if d.get('readiness_cell')=='independent_acceptance_tests': print(d.get('role') or 'none'); break
else: print('none')")
check "$role" "independent-test-designer" "H3: a generated independent-test gap task carries its designated role"
# production implementation does not become READY before the pre-implementation cells satisfy policy
IMPL=$(g orchestrator task create --class implementation --objective "implement FEAT-0001" --feature FEAT-0001 | jget "r['id']")
g orchestrator task status "$IMPL" READY >/dev/null 2>&1
st=$(g orchestrator task show "$IMPL" | jget "r.get('task_status')")
run=$(g orchestrator task dag | jget "'runnable' if '$IMPL' in [t for t in r['runnable']] else 'blocked'")
check "$run" "blocked" "H3: a production implementation task is not runnable while pre-implementation cells are unsatisfied (stored status $st)"

# --- H4: scenarios drive data and tests --------------------------------------------------------------
tr=$(g orchestrator scenario trace SCN-0001 | jget "json.dumps(r)")
chain=$(printf '%s' "$tr" | python3 -c "
import sys,json
r=json.loads(sys.stdin.read())
def has(k): return bool(r.get(k))
print(';'.join('%s=%s'%(k,'yes' if has(k) else 'NO') for k in ['feature','scenario','data_requirements','test_datasets','success_criteria','failure_criteria','tests']))
print('independent=%s' % any(t.get('independent') for t in (r.get('tests') or [])))")
echo "    H4 chain: $chain"
for k in feature data_requirements test_datasets success_criteria failure_criteria tests; do
  case "$chain" in *"$k=yes"*) ok "H4 b1: the chain carries $k";; *) bad "H4 b1: the chain does not carry $k";; esac
done
# test-data author independence is recorded AND checked
ind=$(g orchestrator data show TD-0001 | jget "json.dumps({k:r.get(k) for k in ('authorship','author_role','author_session','independent_of_test_author')})")
echo "    TD-0001 authorship: $ind"
case "$ind" in *author_role*|*authorship*) ok "H4 b2: the OS records the test-data author";; *) bad "H4 b2: no recorded test-data authorship";; esac
# the end-to-end test author of the scenario may not also author its dataset
PROJ="$PROJ" python3 -c "
import yaml,os
p=os.environ['PROJ']+'/spec/tasks/TST-0001.yaml'
d=yaml.safe_load(open(p)); d['author_role']='data-author'; yaml.safe_dump(d,open(p,'w'))"
g memory-engineer rebuild-memory --incremental >/dev/null 2>&1
dep=$(g data-author data register --fields '{"data_kind":"test-dataset","id":"TD-0002","title":"Second dataset by the test author","implements":["DATA-0001"],"location":"product/fixtures/trace.json","provenance":{"source_kind":"synthetic","origin":"probe"}}' | jget "'ACCEPTED' if d.get('ok') else d['error']['code']")
case "$dep" in
  DATA_AUTHOR_NOT_INDEPENDENT) ok "H4 b2: a dataset authored by the scenario's own end-to-end test author is refused ($dep)";;
  ACCEPTED) bad "H4 b2: test-data author independence is recorded but never enforced (dataset accepted)";;
  *) bad "H4 b2: unexpected outcome '$dep'";;
esac
sc=$(g orchestrator scenario check | jget "','.join(sorted({x.get('code','') for x in (r.get('gaps') or r.get('findings') or [])}))")
echo "    scenario check codes: $sc"
# provenance is required and read
prov=$(g data-author data register --fields '{"data_kind":"test-dataset","id":"TD-0003","title":"No provenance","implements":["DATA-0001"],"location":"product/fixtures/trace.json"}' | jget "'ACCEPTED' if d.get('ok') else d['error']['code']")
check "$prov" "DATA_PROVENANCE_REQUIRED" "H4 b3: a test dataset without recorded provenance is refused"
loc=$(g data-author data register --fields '{"data_kind":"test-dataset","id":"TD-0004","title":"Unbound location","implements":["DATA-0001"],"location":"product/fixtures/missing.json","provenance":{"source_kind":"synthetic","origin":"probe"}}' | jget "'ACCEPTED' if d.get('ok') else d['error']['code']")
check "$loc" "DATA_LOCATION_MISSING" "H4 b3: provenance is bound to content that exists, not merely asserted"
# P2-ADJ-0003: an H4 gap degrades health and refuses nothing
hv=$(gp orchestrator audit 2>&1 | grep -m1 '^verdict:' | awk '{print $2}')
blocked=$(gp orchestrator health guard task.close 2>&1 | grep -m1 -E '^(blocked|refused):' | awk '{print $2}')
echo "    audit verdict with an H4 gap: $hv; task.close -> $blocked"
case "$hv" in DEGRADED|RED|UNHEALTHY) ok "P2-ADJ-0003: an incomplete scenario chain degrades suite health ($hv)";; *) bad "P2-ADJ-0003: an incomplete scenario chain leaves the suite $hv";; esac
summary
