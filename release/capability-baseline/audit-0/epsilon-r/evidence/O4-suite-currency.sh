#!/usr/bin/env bash
# O4 — Governance suite currency (Contract v3 lines 787-789; framework §64) and the evidence-freshness input classes
# of Contract v3 lines 95-111. Baseline: a project whose latest green governance record is current (doctor D021 ok).
source "$(dirname "$0")/lib.sh"
B=$(base_project)
d021() { gp "$1" "[ (c['ok'], c['message']) for c in (r or det)['checks'] if c['id']=='D021'][0]" doctor; }
say "baseline D021"; d021 "$B"

say "A. invalidation matrix — one input class changed per clone; is the prior green record judged obsolete?"
row() { # <label> <clone-name> <shell mutation using $R>
  local R; R=$(clone "$B" "$2"); eval "$3"; printf '%-62s ' "$1"; d021 "$R"
}
row "policy: PROJECT_POLICY override (governing policy)"            o4-pol  'ye "$R" governance/project/PROJECT_POLICY.yaml "d[\"policy_overrides\"]={\"MEMORY_POLICY.retrieval.default_k\":10}"'
row "model/retrieval profile: MEMORY_POLICY.embedding via overlay"  o4-emb  'ye "$R" governance/project/PROJECT_POLICY.yaml "d[\"policy_overrides\"]={\"MEMORY_POLICY.embedding.dimensions\":256}"'
row "project path map: REPOSITORY_CONTRACT.yaml"                    o4-map  'ye "$R" governance/project/REPOSITORY_CONTRACT.yaml "d.setdefault(\"probe\",1)"'
row "security/sensitivity: DATA_SENSITIVITY.yaml"                   o4-sen  'ye "$R" governance/project/DATA_SENSITIVITY.yaml "d.setdefault(\"classifications\",[]).append({\"pattern\":\"data/**\",\"class\":\"confidential\"})"'
row "authoritative decision: spec/decisions/D-0001.yaml added"      o4-dec  'yw "$R" spec/decisions/D-0001.yaml "{\"id\":\"D-0001\",\"type\":\"decision\",\"title\":\"t\",\"status\":\"ACTIVE\",\"question\":\"q\",\"chosen_option\":\"A\"}"'
row "governance tests: held-out retrieval set"                      o4-ho   'ye "$R" governance/tests/memory/heldout.yaml "d[\"queries\"]=d[\"queries\"][:-1]"'
row "kernel payload / schema / migration (kernel file)"              o4-ker  'printf "\n#x\n" >> "$R/governance/kernel/schemas/task.schema.json"'
row "tool/plugin: project plugin descriptor"                        o4-plg  'yw "$R" governance/project/plugins/probe.yaml "{\"plugin_id\":\"probe\"}"'
row "tool/plugin: generated tool registry"                          o4-tr   'ye "$R" governance/generated/tool-registry.json "d[\"probe\"]=1"'
row "authoritative spec: spec/architecture/ARCH-0001.yaml added"    o4-arch 'yw "$R" spec/architecture/ARCH-0001.yaml "{\"id\":\"ARCH-0001\",\"type\":\"architecture\",\"title\":\"t\",\"status\":\"ACTIVE\"}"'
row "authoritative spec: spec/requirements/REQ-0001.yaml added"     o4-req  'yw "$R" spec/requirements/REQ-0001.yaml "{\"id\":\"REQ-0001\",\"type\":\"requirement\",\"title\":\"t\",\"status\":\"ACTIVE\"}"'
row "authoritative spec: spec/interfaces/API-0001.yaml added"       o4-api  'yw "$R" spec/interfaces/API-0001.yaml "{\"id\":\"API-0001\",\"type\":\"interface\",\"title\":\"t\",\"status\":\"ACTIVE\"}"'
row "relevant source files: src/lib.rs"                             o4-src  'printf "\npub fn probe() {}\n" >> "$R/src/lib.rs"'
row "relevant index manifest: governance/generated/index-manifest"  o4-idx  'python3 -c "import json;p=\"$R/governance/generated/index-manifest.json\";d=json.load(open(p));d[\"probe\"]=1;json.dump(d,open(p,\"w\"))"'
note "runtime/CLI binary: not varied (one candidate binary). The inputs hash is computed only over governance/kernel,"
note "governance/project, governance/tests, spec/decisions, governance/framework.lock (runtime/src/verification/mod.rs:54-71);"
note "the audit record stores no CLI/runtime version:"
python3 -c "import yaml; d=yaml.safe_load(open('$B/spec/audits/AUD-0001.yaml')); print(sorted(k for k in d if k not in ('families','findings')))"

say "B. consequence: an uncovered input breaks the suite, yet the old green is still 'current'"
R=$(clone "$B" o4-b)
yw "$R" spec/tasks/TASK-0801.yaml "{'id':'TASK-0801','type':'task','title':'a','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0802'],'allowed_paths':['docs/**']}"
yw "$R" spec/tasks/TASK-0802.yaml "{'id':'TASK-0802','type':'task','title':'b','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0801'],'allowed_paths':['docs/**']}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
printf 'audit now: '; audit_summary "$R"
printf 'D021     : '; d021 "$R"

say "C. governance-affecting task cannot close on a stale green (decision changed after the last green audit)"
R=$(clone "$B" o4-c)
T=$(new_task "$R" governance 'spec/decisions/**'); echo "task: $T"
( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
AUDIT_PERSIST=1 audit_summary "$R" >/dev/null; printf 'D021 after fresh green: '; d021 "$R"
gp "$R" "ok" task claim "$T"
yw "$R" spec/decisions/D-0002.yaml "{'id':'D-0002','type':'decision','title':'t','status':'ACTIVE','question':'q','chosen_option':'A'}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/o4-rep.json" not_applicable_with_reason spec/decisions/D-0002.yaml "'tests':{'status':'not_applicable_with_reason','reason':'decision record'}"
printf 'close on stale green: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'), (e or {}).get('message','')[:140])" task close "$T" --report "$SCRATCH/o4-rep.json"
printf 'gov audit (full suite): '; AUDIT_PERSIST=1 audit_summary "$R"
printf 'close after re-audit: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T" --report "$SCRATCH/o4-rep.json"

say "D. the currency gate keys on paths: a class=governance task that changes spec/architecture closes on a stale green"
R=$(clone "$B" o4-d)
T=$(new_task "$R" governance 'spec/architecture/**'); echo "task: $T"
( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.retrieval.default_k':9}"
printf 'D021 (made stale by a policy change): '; d021 "$R"
gp "$R" "ok" task claim "$T"
yw "$R" spec/architecture/ARCH-0001.yaml "{'id':'ARCH-0001','type':'architecture','title':'new architecture','status':'ACTIVE'}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/o4-rep2.json" not_applicable_with_reason spec/architecture/ARCH-0001.yaml "'tests':{'status':'not_applicable_with_reason','reason':'architecture record'}"
printf 'close: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'), (r or {}).get('degraded'))" task close "$T" --report "$SCRATCH/o4-rep2.json"

say "E. --force by an L3+ role closes a governance task on a stale green, recorded as degraded"
R=$(clone "$B" o4-e)
T=$(new_task "$R" governance 'spec/decisions/**'); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "ok" task claim "$T"
yw "$R" spec/decisions/D-0003.yaml "{'id':'D-0003','type':'decision','title':'t','status':'ACTIVE','question':'q','chosen_option':'A'}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/o4-rep3.json" not_applicable_with_reason spec/decisions/D-0003.yaml "'tests':{'status':'not_applicable_with_reason','reason':'r'}"
printf 'close --force: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'), (r or {}).get('degraded'))" task close "$T" --report "$SCRATCH/o4-rep3.json" --force

say "F. AC-16 O4<->W6: an upstream authoritative change after a task is DONE leaves its evidence green"
R=$(clone "$B" o4-f)
RF=$(readiness_full)
yw "$R" spec/requirements/REQ-0001.yaml "{'id':'REQ-0001','type':'requirement','title':'totals exact','status':'ACTIVE','feature':'F-0001','acceptance_criteria':['exact cents']}"
yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'Totals','status':'ACTIVE','readiness':$RF,'requirements':['REQ-0001'],'scenarios':['SCN-0001'],'acceptance_tests':['tests/ledger_test.rs']}"
yw "$R" spec/scenarios/SCN-0001.yaml "{'id':'SCN-0001','type':'scenario','title':'totals','status':'ACTIVE','feature':'F-0001','given':['g'],'when':['w'],'then':['t']}"
T=$(new_task "$R" implementation 'src/**,tests/**' --feature F-0001); echo "task: $T"
( cd "$R" && git add -A && git commit -qm spec ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "ok" task claim "$T"
printf '\npub fn rounding() {}\n' >> "$R/src/lib.rs"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/o4-rep4.json" passed src/lib.rs
printf 'close: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T" --report "$SCRATCH/o4-rep4.json"
( cd "$R" && git add -A && git commit -qm done ) >/dev/null 2>&1
AUDIT_PERSIST=1 audit_summary "$R" >/dev/null
note "upstream change: REQ-0001 acceptance criterion changed and superseding requirement semantics"
ye "$R" spec/requirements/REQ-0001.yaml "d['acceptance_criteria']=['totals rounded to whole units']; d['title']='totals rounded'"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "{'task_status':r.get('task_status'),'retest_required':r.get('retest_required'),'staleness':r.get('staleness')}" task show "$T"
gp "$R" "{'runnable':r['runnable'],'blocked':r['blocked'],'done':r['done']}" task dag
printf 'D021  : '; d021 "$R"
printf 'doctor: '; doctor_summary "$R"
printf 'audit : '; audit_summary "$R"
