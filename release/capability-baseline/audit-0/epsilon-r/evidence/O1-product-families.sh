#!/usr/bin/env bash
# O1 — Product test families (Contract v3 lines 751-761; framework §62). What does the OS do, executably, for each of
# unit / contract / integration / system / acceptance / scenario / security / performance / recovery / live-smoke?
source "$(dirname "$0")/lib.sh"
B=$(base_project)
R=$(clone "$B" o1)
RF=$(readiness_full)
yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'Ledger totals','status':'ACTIVE','readiness':$RF,'scenarios':['SCN-0001']}"
yw "$R" spec/scenarios/SCN-0001.yaml "{'id':'SCN-0001','type':'scenario','title':'totals','status':'ACTIVE','feature':'F-0001','given':['empty ledger'],'when':['append'],'then':['total 399']}"

say "A. one test-obligation per TEST_POLICY.product_families value; family accepted, independence enforced where policy demands"
gp "$R" "r['effective']['product_families']" policy effective TEST_POLICY
i=0
for fam in unit contract integration system acceptance scenario security performance recovery smoke; do
  i=$((i+1)); id=$(printf 'TO-%04d' $i)
  yw "$R" "spec/tests/$id.yaml" "{'id':'$id','type':'test-obligation','title':'$fam obligation','status':'ACTIVE','family':'$fam','feature':'F-0001','test_path':'tests/ledger_test.rs','author_role':'backend-engineer'}"
done
gp "$R" "[(f['severity'],f['message'][:150]) for f in r['findings'] if f['family']=='product_traceability']" audit --no-persist --family product_traceability

say "B. the contract says 'live/smoke'; an obligation of family 'live' is rejected as outside the policy vocabulary"
yw "$R" spec/tests/TO-0011.yaml "{'id':'TO-0011','type':'test-obligation','title':'live obligation','status':'ACTIVE','family':'live','feature':'F-0001','independent_of_implementer':True}"
gp "$R" "[(f['severity'],f['message'][:150]) for f in r['findings'] if 'TO-0011' in f['message']]" audit --no-persist --family product_traceability
rm -f "$R/spec/tests/TO-0011.yaml"

say "C. with acceptance/scenario/system obligations marked independent, product_traceability is clean"
for id in TO-0005 TO-0006 TO-0004; do ye "$R" "spec/tests/$id.yaml" "d['independent_of_implementer']=True"; done
gp "$R" "[(f['severity'],f['message'][:150]) for f in r['findings'] if f['family']=='product_traceability']" audit --no-persist --family product_traceability

say "D. family vocabulary is freely redefinable by the project (TEST_POLICY.product_families: overridable)"
R2=$(clone "$R" o1-d); ye "$R2" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'TEST_POLICY.product_families':['unit']}"
gp "$R2" "{'applied':r['applied'],'refused':r['refused']}" policy overrides
gp "$R2" "[(f['severity'],f['message'][:120]) for f in r['findings'] if f['family']=='product_traceability']" audit --no-persist --family product_traceability

say "E. no family is required: a feature whose only obligation is 'unit' (no security/performance/recovery/smoke) raises nothing"
R3=$(clone "$B" o1-e)
yw "$R3" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'Ledger totals','status':'ACTIVE','readiness':$RF,'scenarios':['SCN-0001']}"
yw "$R3" spec/scenarios/SCN-0001.yaml "{'id':'SCN-0001','type':'scenario','title':'totals','status':'ACTIVE','feature':'F-0001','given':['g'],'when':['w'],'then':['t']}"
yw "$R3" spec/tests/TO-0001.yaml "{'id':'TO-0001','type':'test-obligation','title':'unit only','status':'ACTIVE','family':'unit','feature':'F-0001'}"
gp "$R3" "{'verdict':r['verdict'],'findings':[(f['family'],f['severity'],f['message'][:120]) for f in r['findings']]}" audit --no-persist

say "F. product suite execution: gov verify product (ecosystem-detected cargo test)"
gp "$R" "{k:r.get(k) for k in ['ran','command','source','status','exit']}" verify product
note "result carries one exit code for the whole command; no per-family result exists"
grep '"name":"product.suite"' "$R/.governance-runtime/telemetry/events.jsonl" | tail -1 | python3 -c "import json,sys; e=json.loads(sys.stdin.read()); print('telemetry event:', e['name'], {k:e['attributes'].get(k) for k in ['status','exit','source','command']})"

say "G. a failing product test: product suite FAILS, but no health surface changes"
R4=$(clone "$B" o1-g)
sed -i 's/assert_eq!(l.total_cents(), 399);/assert_eq!(l.total_cents(), 400);/' "$R4/tests/ledger_test.rs"
gp "$R4" "{k:r.get(k) for k in ['ran','status','exit']}" verify product
( cd "$R4" && git add -A && git commit -qm "broken test" ) >/dev/null 2>&1
g "$R4" rebuild-memory --incremental >/dev/null 2>&1
printf 'doctor: '; doctor_summary "$R4"
printf 'audit : '; audit_summary "$R4"
gp "$R4" "{'memory':r['memory'],'next_action':r['next_action']}" status

say "H. task close accepts a self-attested tests.status=passed while the product suite is failing"
T=$(new_task "$R4" documentation 'docs/**'); echo "task: $T"
( cd "$R4" && git add -A && git commit -qm task ) >/dev/null 2>&1
gp "$R4" "ok" task claim "$T"
mkdir -p "$R4/docs"; echo "probe" > "$R4/docs/note.md"
g "$R4" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/o1-report.json" passed docs/note.md
gp "$R4" "{'ok':ok,'result':r,'error':e.get('code') if e else None}" task close "$T" --report "$SCRATCH/o1-report.json"
gp "$R4" "{k:r.get(k) for k in ['ran','status','exit']}" verify product
