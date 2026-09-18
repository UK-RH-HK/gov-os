#!/usr/bin/env bash
# P1 execution telemetry (Contract v3 lines 814-827; framework §65) and P2 organisational questions (lines 829-838;
# framework §66). Drive a representative workflow WITHOUT any explicit `telemetry emit`, then inventory what the
# product recorded by itself; then seed caller-supplied evidence and ask `telemetry summary` each §66 question.
source "$(dirname "$0")/lib.sh"
B=$(base_project)
R=$(clone "$B" p1)
EVF="$R/.governance-runtime/telemetry/events.jsonl"; : > "$EVF"
RF=$(readiness_full)
yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'Totals','status':'ACTIVE','readiness':$RF,'scenarios':['SCN-0001'],'acceptance_tests':['tests/ledger_test.rs']}"
yw "$R" spec/scenarios/SCN-0001.yaml "{'id':'SCN-0001','type':'scenario','title':'s','status':'ACTIVE','feature':'F-0001','given':['g'],'when':['w'],'then':['t']}"

say "workflow (no explicit telemetry emit): create, continue --claim, skills resolve, memory query, checkpoint, handoff create/return, gate create/present/decide, close, verify product"
T=$(new_task "$R" implementation 'src/**' --feature F-0001 --fields '{"required_skills":["SKL-BACKEND-IMPL"]}'); echo "task $T"
( cd "$R" && git add -A && git commit -qm spec ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
SESS=S-agent-1 ROLE=backend-engineer gp "$R" "{'status':r['status'],'packet_hash':r['context_packet']['packet_hash'][:16],'skills':r['skills']['resolved']}" continue --claim
SESS=S-agent-1 ROLE=backend-engineer gp "$R" "{'hits':len(r['hits'])}" memory query "ledger total cents"
SESS=S-agent-1 ROLE=backend-engineer gp "$R" "r['id']" checkpoint create --task "$T" --next-action "implement totals"
H=$(g "$R" handoff create --to-role backend-engineer --task "$T" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])"); echo "handoff $H"
python3 -c "import json; json.dump({'task':'$T','status':'success','work_completed':'w','files_changed':['src/lib.rs'],'evidence':[],'tests':{'status':'passed'},'discoveries':[],'risks':[],'lessons':['cache the ledger total'],'proposed_decisions':[],'unresolved':[],'recommended_next_action':'close'},open('$SCRATCH/p1-ret.json','w'))"
SESS=S-agent-1 ROLE=backend-engineer gp "$R" "r['lessons_created']" handoff return "$H" --file "$SCRATCH/p1-ret.json"
GT=$(g "$R" gate create --question "Ship totals?" --fields "{\"blocks_tasks\":[\"$T\"],\"options\":[{\"id\":\"A\",\"description\":\"a\"},{\"id\":\"B\",\"description\":\"b\"}]}" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
gp "$R" "ok" gate present "$GT" >/dev/null; ROLE=human gp "$R" "ok" decide "$GT" --option A --by owner
printf '\npub fn p1() {}\n' >> "$R/src/lib.rs"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/p1-rep.json" passed src/lib.rs
SESS=S-agent-1 ROLE=backend-engineer gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T" --report "$SCRATCH/p1-rep.json"
gp "$R" "r['status']" verify product

say "inventory of the telemetry log produced by that workflow"
python3 - "$EVF" <<'EOF'
import json,sys,collections
ev=[json.loads(l) for l in open(sys.argv[1])]
print("events:", len(ev))
keys=collections.OrderedDict()
for e in ev:
    keys.setdefault(e["name"], set()).update(e["attributes"].keys())
for n,k in keys.items(): print(f"  {n:22} attrs={sorted(k)}")
print("envelope keys:", sorted(ev[0].keys()), "| resource:", ev[0]["resource"])
allattr=set().union(*keys.values())
for f in ["model","provider","task","skill","skills","tool_versions","context_packet","packet_hash","query","hits","tokens_in","tokens_out","input_tokens","output_tokens","duration_ms","latency_ms","cost","files_read","files_written","files_changed","tests","status","retries","retry","error","handoff","decision","human"]:
    print(f"  attribute '{f}' present in any event: {f in allattr}")
EOF

say "field-by-field: where (if anywhere) each P1 item is recorded by the product for this run"
python3 - "$R" "$T" <<'EOF'
import json,sys,glob,yaml,sqlite3,os
R,T=sys.argv[1],sys.argv[2]
ev=[json.loads(l) for l in open(f"{R}/.governance-runtime/telemetry/events.jsonl")]
rep=yaml.safe_load(open(sorted(glob.glob(f"{R}/spec/reports/RPT-*.yaml"))[-1]))
ck=yaml.safe_load(open(sorted(glob.glob(f"{R}/spec/reports/checkpoints/CKPT-*.yaml"))[-1]))
db=sqlite3.connect(f"{R}/.governance-runtime/state.db")
rl=db.execute("select count(*), max(query) from retrieval_log").fetchone()
ho=yaml.safe_load(open(glob.glob(f"{R}/spec/**/HND-0001.yaml",recursive=True)[0]))
dec=[yaml.safe_load(open(p)) for p in glob.glob(f"{R}/spec/decisions/*.yaml")]
print("agent/session       : event.session =", sorted({e['session'] for e in ev}), "| report.session =", rep.get('session'))
print("model/provider      : in events:", any('model' in e['attributes'] or 'provider' in e['attributes'] for e in ev), "| report.model:", rep.get('model'))
print("role                : event.role =", sorted({e['role'] for e in ev}))
print("task                : events carrying a task id:", sum(1 for e in ev if 'task' in e['attributes']), "of", len(ev), "| report.task =", rep.get('task'))
print("skill/tool versions : events carrying skills/tools:", sum(1 for e in ev if any(k in e['attributes'] for k in ('skills','skill','tools','tool_versions'))), "| report.skills_used:", rep.get('skills_used'), "| report.tools_used:", rep.get('tools_used'), "| resource service.version:", ev[0]['resource']['service.version'])
print("context packet      : events carrying packet hash:", sum(1 for e in ev if 'packet_hash' in e['attributes']), "| checkpoint.context_packet_hash:", (ck.get('context_packet_hash') or '')[:16], "| report has packet:", 'context_packet' in rep)
print("retrieval q/hits    : retrieval events:", [(e['attributes'].get('hits'), e['attributes'].get('routes')) for e in ev if e['name']=='retrieval'], "| retrieval_log rows:", rl[0], "sample query:", rl[1])
print("token input/output  : any token attribute:", any('token' in k for e in ev for k in e['attributes']), "| report token fields:", [k for k in rep if 'token' in k])
print("latency/cost        : duration_ms on cli events:", all('duration_ms' in e['attributes'] for e in ev if e['name'].startswith('cli.')), "| any cost attribute:", any('cost' in e['attributes'] for e in ev), "| report.cost:", rep.get('cost'))
print("files read/written  : report.files_changed:", rep.get('files_changed'), "observed:", rep.get('observed_files_changed'), "| report.files_read:", rep.get('files_read'))
print("tests               : product.suite events:", [(e['attributes'].get('status'), e['attributes'].get('exit')) for e in ev if e['name']=='product.suite'], "| report.tests:", rep.get('tests'))
print("retries/failures    : failed cli events:", [(e['name'], e['attributes'].get('error')) for e in ev if e['attributes'].get('ok') is False], "| retry attribute anywhere:", any('retr' in k for e in ev for k in e['attributes']), "| report.repair_count:", rep.get('repair_count'))
print("handoffs            : handoff record", ho['id'], ho.get('handoff_status'), "returned_at" in ho, "| cli.handoff events:", sum(1 for e in ev if e['name']=='cli.handoff'))
print("decisions           : decision records:", [(d.get('id'), d.get('chosen_option'), d.get('approved_by')) for d in dec if d.get('type')=='decision'])
print("human interventions : gate answers:", [(d.get('id'), (d.get('answer') or {}).get('by')) for d in dec if d.get('type')=='human-gate'], "| cli.decide events:", sum(1 for e in ev if e['name']=='cli.decide'))
EOF
note "retrieval_log lives in the derived index: does it survive a full rebuild?"
g "$R" rebuild-memory >/dev/null 2>&1
python3 -c "import sqlite3; print('retrieval_log rows after gov rebuild-memory:', sqlite3.connect('$R/.governance-runtime/state.db').execute('select count(*) from retrieval_log').fetchone()[0])"
note "the only way to record tokens/model/cost/skills is caller-supplied, schema-free: telemetry emit accepts anything"
gp "$R" "r['attributes']" telemetry emit --name llm.call --attrs '{"tokens_in":"not-a-number","anything":{"nested":true}}'

say "P2 — seed caller-supplied evidence, then ask telemetry summary each §66 question"
R2=$(clone "$B" p2)
RF2=$(readiness_full)
yw "$R2" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'a','status':'ACTIVE','readiness':$RF2}"
yw "$R2" spec/features/F-0002.yaml "{'id':'F-0002','type':'feature','title':'b','status':'ACTIVE','readiness':$RF2}"
for i in 1 2 3; do yw "$R2" spec/tasks/TASK-000$i.yaml "{'id':'TASK-000$i','type':'task','title':'t$i','status':'ACTIVE','task_status':'DONE','class':'implementation','objective':'o','feature':'F-000$(( i<3 ? 1 : 2 ))','closed_by_report':'RPT-000$i'}"; done
yw "$R2" spec/reports/RPT-0001.yaml "{'id':'RPT-0001','type':'report','status':'ACTIVE','task':'TASK-0001','role':'backend-engineer','outcome':'success','repair_count':2,'cost':{'usd':3.0},'skills_used':[{'id':'SKL-BACKEND-IMPL','version':'1.0.0'}],'tokens':{'in':12000,'out':3000}}"
yw "$R2" spec/reports/RPT-0002.yaml "{'id':'RPT-0002','type':'report','status':'ACTIVE','task':'TASK-0002','role':'backend-engineer','outcome':'success','repair_count':0,'cost':{'usd':1.0},'skills_used':[{'id':'SKL-BACKEND-IMPL','version':'1.0.0'}],'tokens':{'in':4000,'out':900}}"
yw "$R2" spec/reports/RPT-0003.yaml "{'id':'RPT-0003','type':'report','status':'ACTIVE','task':'TASK-0003','role':'frontend-engineer','outcome':'success','repair_count':0,'cost':{'usd':0.5},'skills_used':[{'id':'SKL-API-CONTRACT-REVIEW','version':'1.0.0'}]}"
for g_ in 1 2 3; do yw "$R2" spec/decisions/HDG-000$g_.yaml "{'id':'HDG-000$g_','type':'human-gate','status':'ACTIVE','gate_status':'ANSWERED','question':'q$g_','blocks_tasks':['TASK-000$(( g_<3 ? 1 : 3 ))']}"; done
for m in "frontier-x T3 8.0 1" "light-y T1 0.2 1"; do set -- $m
python3 -c "import json; json.dump({'model':'$1','provider':'p','task_class':'documentation','reasoning_effort':'low','cost':$3,'latency_ms':100,'pass':True,'repair_count':0,'reviewer_findings':0,'tier':'$2'},open('$SCRATCH/p2-$1.json','w'))"
gp "$R2" "ok" route --record "$SCRATCH/p2-$1.json" >/dev/null; done
gp "$R2" "ok" memory query "ledger" >/dev/null
gp "$R2" "r" telemetry summary > "$SCRATCH/p2-summary.txt"; cat "$SCRATCH/p2-summary.txt" | cut -c1-2500
python3 - "$SCRATCH/p2-summary.txt" <<'EOF'
import json,sys
s=open(sys.argv[1]).read(); r=json.loads(s[s.index('{'):])
print("\nQ rework by role          :", r.get('rework_by_role'))
print("Q retrieval effect on tokens:", {k:v for k,v in r.items() if 'token' in k} or 'no token metric in summary', "| retrieval block:", r.get('retrieval'))
print("Q model over/under-power  :", r.get('model_routing'))
print("Q skill repair rate       :", {k:v for k,v in r.items() if 'skill' in k} or 'no skill metric in summary')
print("Q human-gate concentration:", r.get('human_gates_by_feature'))
print("Q retrieval misses        :", {k:v for k,v in r.items() if 'miss' in k} or 'no miss metric in summary')
print("Q cost by task/feature    :", r.get('cost_by_task_class'), "| by feature:", {k:v for k,v in r.items() if 'feature' in k and 'gate' not in k} or 'none')
print("Q first-pass completion   :", r.get('first_pass_completion_rate'))
EOF
note "retrieval misses of KNOWN knowledge by route: held-out evaluation (gov memory verify) with one injected miss"
R3=$(clone "$B" p2-miss)
ye "$R3" governance/tests/memory/heldout.yaml "d['queries'][6]['expected_refs']=['file:tests/ledger_test.rs']"
gp "$R3" "{'failed':[(x['id'],x['category'],x['routes'],x['expected'],x['got'][:2]) for x in (r or det)['results'] if not x['pass']],'by_category':(r or det)['by_category']}" memory verify
