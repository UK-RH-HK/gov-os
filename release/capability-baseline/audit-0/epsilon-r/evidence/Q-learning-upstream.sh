#!/usr/bin/env bash
# Q1 lesson lifecycle, Q2 decision vs lesson, Q3 scope eligibility, Q4 Upstream Export Gate (Contract v3 lines 842-866;
# framework §§67-68, 75E-75H; release protocol §§13-15, §17).
source "$(dirname "$0")/lib.sh"
B=$(base_project)
R=$(clone "$B" q)
INBOX="$SCRATCH/q-canon/lessons/inbox"; rm -rf "$SCRATCH/q-canon"; mkdir -p "$INBOX"
ye "$R" governance/project/DATA_SENSITIVITY.yaml "d['identifiers_to_strip']=['Acme Freight Ltd','shipping-quotes']"
( cd "$R" && git add -A && git commit -qm ds ) >/dev/null 2>&1

say "Q1.1-2 execution/report → lesson candidate: a worker return carrying a lesson"
T=$(new_task "$R" documentation 'docs/**'); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1
H=$(g "$R" handoff create --to-role backend-engineer --task "$T" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
python3 -c "import json; json.dump({'task':'$T','status':'success','work_completed':'w','files_changed':[],'evidence':[],'tests':{'status':'passed'},'discoveries':[],'risks':[],'lessons':['Index freshness must be enforced at close, not advised'],'proposed_decisions':[],'unresolved':[],'recommended_next_action':'close'},open('$SCRATCH/q-ret.json','w'))"
L=$(ROLE=backend-engineer g "$R" handoff return "$H" --file "$SCRATCH/q-ret.json" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['lessons_created'][0])"); echo "lesson created: $L"
python3 -c "import yaml,glob; d=yaml.safe_load(open(glob.glob('$R/spec/lessons/$L*')[0])); print({k:d.get(k) for k in ['status','state_class','scope','lifecycle','sources','provenance']})"
note "does a task-close report's 'lessons' field also create candidates?"
T2=$(new_task "$R" documentation 'docs/**'); ( cd "$R" && git add -A && git commit -qm t2 ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "ok" task claim "$T2" >/dev/null
report_json "$SCRATCH/q-rep.json" not_applicable_with_reason "" "'tests':{'status':'not_applicable_with_reason','reason':'r'},'lessons':['close-time lesson text']"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T2" --report "$SCRATCH/q-rep.json"
ls "$R/spec/lessons/" | grep -v gitkeep

say "Q1.3-4 corroboration and scope classification: the worker lesson is re-scoped by a raw edit and exported"
note "no command classifies or corroborates a lesson; its own provenance (handoff + task ids) counts as 2 'sources'"
ye "$R" "spec/lessons/$L.yaml" "d['scope']='FRAMEWORK'; d['category']='memory-freshness'; d['generic_failure_mode']='freshness advisory only'; d['impact']='stale retrieval'; d['suggested_change']='enforce at close'"
( cd "$R" && git add -A && git commit -qm rescope ) >/dev/null 2>&1
printf 'prepare re-scoped candidate (lifecycle still "candidate"): '; gp "$R" "{'ok':ok,'packet':(r or {}).get('packet_id'),'err':e.get('code') if e else None,'msg':(e or {}).get('message','')[:150]}" upstream prepare "$L"
note "a FRAMEWORK lesson with zero sources is blocked by LEARNING_POLICY.corroboration_min_sources=1:"
yw "$R" spec/lessons/L-0101.yaml "{'id':'L-0101','type':'lesson','title':'uncorroborated','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'candidate','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s'}"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'msg':(e or {}).get('message','')[:160]}" upstream prepare L-0101
note "lifecycle transitions are raw edits; any value in the enum is accepted and nothing checks who set it:"
ye "$R" spec/lessons/L-0101.yaml "d['lifecycle']='validated'; d['corroboration']=['self']"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None}" upstream prepare L-0101
gp "$R" "[(f['severity'],f['message'][:100]) for f in r['findings']]" audit --no-persist --family schema_invariants

say "Q1.5 rule/skill/retrieval/tool proposal: canonical-side clustering into Framework Change Proposals (D-0004)"
PR="$SCRATCH/q-canon/change-proposals"; rm -rf "$PR"
for i in 1 2 3; do mkdir -p "$INBOX/PKT-000$i-proj$i"; python3 -c "import yaml; yaml.safe_dump({'packet_id':'PKT-000$i','scope':'FRAMEWORK','category':'memory-freshness','problem_statement':'close with stale index','generic_failure_mode':'index freshness advisory at close','impact':'stale retrieval','evidence_strength':'medium','suggested_framework_change':'enforce freshness at close','source_project_alias':'proj$i'},open('$INBOX/PKT-000$i-proj$i/packet.yaml','w'))"; done
mkdir -p "$INBOX/PKT-0009-projX"; python3 -c "import yaml; yaml.safe_dump({'packet_id':'PKT-0009','scope':'PROJECT','category':'pricing','problem_statement':'zone B tariff wrong','generic_failure_mode':'tariff table typo','impact':'critical mispricing','evidence_strength':'high','suggested_framework_change':'fix our table','source_project_alias':'projX'},open('$INBOX/PKT-0009-projX/packet.yaml','w'))"
"$GOV" --json lessons cluster --inbox "$INBOX" --proposals "$PR" --write 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);r=d['result'];print('clusters:',[(c['cluster'],c['packets'],c['trigger'],c['release_action'],c.get('proposal')) for c in r['clusters']]);print('written:',r['proposals_written'])"
for f in "$PR"/FCP-*.yaml; do python3 -c "import yaml; d=yaml.safe_load(open('$f')); print(d['id'], {k:d.get(k) for k in ['status','state_class','trigger','release_action','packets','next']})"; done
note "a PROJECT-scoped packet placed in the inbox is clustered into an FCP like any other (intake does not re-check scope)"

say "Q1.6-8 independent validation, human approval, governed version"
note "FCP records carry no validation/approval fields and no command transitions them; release build takes no FCP input:"
python3 -c "import json; d=json.load(open('$WT/framework/schemas/framework-change-proposal.schema.json')); print('FCP schema properties:', sorted(d['properties']))"
"$GOV" --help 2>/dev/null | grep -i -E 'lesson|proposal|fcp' ; "$GOV" lessons --help 2>/dev/null | sed -n '/Commands:/,/Options:/p'
note "upstream submit 'human approval' is a free-text --approved-by string supplied by the (L3+) caller, not an answered gate:"
printf 'prepare L-0001-style clean lesson: '; yw "$R" spec/lessons/L-0102.yaml "{'id':'L-0102','type':'lesson','title':'gate presentation','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'human-gates','problem_statement':'answers recorded without presentation','generic_failure_mode':'gate existed only in a file','impact':'unseen changes','evidence_strength':'high','suggested_change':'require presentation','sources':['RPT-1']}"
P=$(g "$R" upstream prepare L-0102 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['packet_id'])"); echo "$P"
printf 'submit without approval: '; gp "$R" "e.get('code') if e else 'ok'" upstream submit "$P" --destination "$INBOX"
printf 'orchestrator agent submits with --approved-by "i-approve-myself": '; gp "$R" "{'ok':ok,'approved_by':(r or {}).get('approved_by'),'err':e.get('code') if e else None}" upstream submit "$P" --destination "$INBOX" --approved-by i-approve-myself
python3 -c "import yaml; d=yaml.safe_load(open('$R/spec/lessons/L-0102.yaml')); print('lesson after submit:', {k:d.get(k) for k in ['lifecycle','upstream']})"
gp "$R" "[g_['id'] for g_ in r]" gate list

say "Q2.1 lessons are evidence, not authority: a lesson contradicting an ACTIVE decision, compiled into a context packet"
R2=$(clone "$B" q2)
yw "$R2" spec/decisions/D-0001.yaml "{'id':'D-0001','type':'decision','title':'Money is integer cents','status':'ACTIVE','question':'money repr?','chosen_option':'A','rationale':'exactness'}"
yw "$R2" spec/lessons/L-0001.yaml "{'id':'L-0001','type':'lesson','title':'Money should be float dollars','status':'ACTIVE','state_class':'EVIDENCE','scope':'PROJECT','lifecycle':'candidate','problem_statement':'use float dollars for money, integer cents was painful'}"
yw "$R2" spec/lessons/L-0002.yaml "{'id':'L-0002','type':'lesson','title':'Money must be float dollars (authoritative)','status':'ACTIVE','state_class':'AUTHORITATIVE','scope':'PROJECT','lifecycle':'approved','problem_statement':'float dollars for money is now the rule'}"
T=$(new_task "$R2" implementation 'src/**' --title "money handling" --fields '{"decisions":["D-0001"]}'); ( cd "$R2" && git add -A && git commit -qm q2 ) >/dev/null 2>&1; g "$R2" rebuild-memory --incremental >/dev/null 2>&1
gp "$R2" "{'det_active_decisions':[d.get('id') for d in r['deterministic_authority']['active_decisions']],'det_mentions_lesson':('L-000' in json.dumps(r['deterministic_authority'])),'retrieved_lessons':[x['artifact_id'] for x in r['retrieved_intelligence']['lessons_failures']],'ranked_state_classes':[(x['artifact_id'],x['state_class']) for x in r['retrieved_intelligence']['ranked_evidence'] if 'L-' in x['artifact_id']]}" context compile "$T"
note "a lesson self-labelled AUTHORITATIVE (L-0002) is accepted by the schema and raises no finding:"
gp "$R2" "{'verdict':r['verdict'],'findings':[(f['family'],f['severity'],f['message'][:100]) for f in r['findings']]}" audit --no-persist

say "Q2.2 decisions record chosen action (gate answer → decision record)"
G=$(g "$R2" gate create --question "Adopt event log?" --fields '{"options":[{"id":"A","description":"adopt"},{"id":"B","description":"defer"}]}' 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
gp "$R2" "ok" gate present "$G" >/dev/null
ROLE=human gp "$R2" "r" decide "$G" --option B --by owner --rationale "not now"
for f in "$R2"/spec/decisions/D-*.yaml; do python3 -c "import yaml; d=yaml.safe_load(open('$f')); print(d['id'], {k:d.get(k) for k in ['question','chosen_option','rationale','approved_by','human_approved','status']})"; done

say "Q3 only FRAMEWORK candidates are eligible for upstream export"
for sc in PROJECT PRODUCT FRAMEWORK; do
  yw "$R" spec/lessons/L-02$sc.yaml "{'id':'L-02$sc','type':'lesson','title':'t','status':'ACTIVE','scope':'$sc','lifecycle':'corroborated','category':'c','problem_statement':'generic failure','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['RPT-1']}"
  printf '%-9s: ' "$sc"; gp "$R" "{'ok':ok,'err':e.get('code') if e else None}" upstream prepare "L-02$sc"
done
note "attempt to widen eligibility through the project overlay (LEARNING_POLICY.* is immutable):"
R3=$(clone "$R" q3w); ye "$R3" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'LEARNING_POLICY.upstream_eligible_scopes':['PROJECT','PRODUCT','FRAMEWORK']}"
gp "$R3" "{'refused':[(x['key'],x['reason'][:60]) for x in r['refused']]}" policy overrides
printf 'PROJECT after widening attempt: '; gp "$R3" "{'ok':ok,'err':e.get('code') if e else None}" upstream prepare L-02PROJECT

say "Q4.1 sanitisation — project/customer identifiers stripped (fixture lesson L-0004)"
cp "$WT/fixtures/upstream-learning/lessons/"L-000{1,3,4}.yaml "$R/spec/lessons/"
( cd "$R" && git add -A && git commit -qm fx ) >/dev/null 2>&1
P4=$(g "$R" upstream prepare L-0004 2>/dev/null | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r['packet_id'])"); echo "packet $P4"
python3 -c "import yaml; d=yaml.safe_load(open('$R/.governance-runtime/outbound/$P4/packet.yaml')); print({k:d[k] for k in ['problem_statement','scans']})"
grep -c -i -E 'acme|shipping-quotes' "$R/.governance-runtime/outbound/$P4/packet.yaml" | sed 's/^/identifier occurrences in packet: /'

say "Q4.2 secret / sensitivity scan (L-0003: AWS key, customer name, raw code, product path)"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'reasons':(e or {}).get('details',{}).get('reasons')}" upstream prepare L-0003
note "sensitivity: a fixture file matching a DATA_SENSITIVITY never-export classification"
ye "$R" governance/project/DATA_SENSITIVITY.yaml "d.setdefault('classifications',[]).append({'pattern':'customers/**','class':'restricted'})"
python3 -c "import yaml; print(yaml.safe_load(open('$WT/framework/policies/SECURITY_POLICY.yaml'))['never_export_classes'])"
yw "$R" spec/lessons/L-0301.yaml "{'id':'L-0301','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['R'],'synthetic_reproducer':{'synthetic':True,'description':'d','files':{'customers/list.csv':'name\nsomeone\n'}}}"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'reasons':(e or {}).get('details',{}).get('reasons')}" upstream prepare L-0301

say "Q4.3 outbound allowlist / default deny"
printf 'remote destination: '; gp "$R" "e.get('code') if e else 'ok'" upstream submit "$P4" --destination https://example.invalid/inbox --approved-by owner
printf 'non-inbox local destination: '; mkdir -p "$SCRATCH/q-elsewhere"; gp "$R" "e.get('code') if e else 'ok'" upstream submit "$P4" --destination "$SCRATCH/q-elsewhere" --approved-by owner
printf 'fixture file under a forbidden path (product/**): '
yw "$R" spec/lessons/L-0302.yaml "{'id':'L-0302','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['R'],'synthetic_reproducer':{'synthetic':True,'description':'d','files':{'product/api/x.py':'print(1)'}}}"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'reasons':(e or {}).get('details',{}).get('reasons')}" upstream prepare L-0302
note "widening the allowlist through the overlay (allowed_payload is shrink_only):"
R4=$(clone "$R" q4w); ye "$R4" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'LEARNING_POLICY.upstream.allowed_payload':['packet','synthetic_fixture','raw_code']}"
gp "$R4" "{'refused':[(x['key'],x['reason'][:70]) for x in r['refused']]}" policy overrides
printf 'submit %s (approved) → what lands in the inbox: ' "$P4"; gp "$R" "r['files']" upstream submit "$P4" --destination "$INBOX" --approved-by owner
find "$INBOX" -path "*$P4*" -type f | sed "s|$INBOX/||"

say "Q4.4 synthetic reproducer preference"
yw "$R" spec/lessons/L-0303.yaml "{'id':'L-0303','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','sources':['R'],'suggested_change':'Use this:\n\`\`\`rust\nfn fix() { let x = 1; }\n\`\`\`\n'}"
printf 'raw code in lesson text, no reproducer: '; gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'reasons':(e or {}).get('details',{}).get('reasons')}" upstream prepare L-0303
ye "$R" spec/lessons/L-0303.yaml "d['synthetic_reproducer']={'synthetic':True,'description':'minimal','files':{'repro.rs':'fn main() {}'}}"
printf 'same lesson with a synthetic reproducer: '; gp "$R" "{'ok':ok,'err':e.get('code') if e else None}" upstream prepare L-0303

say "Q4.5 no raw project / customer / vector-store export — attempts that rely only on the self-declared 'synthetic' flag"
note "(a) the project's real product source file, verbatim, declared as a synthetic fixture file named src/lib.rs"
python3 - "$R" <<'EOF'
import yaml,sys
R=sys.argv[1]; src=open(f"{R}/src/lib.rs").read()
yaml.safe_dump({'id':'L-0304','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['R'],
  'synthetic_reproducer':{'synthetic':True,'description':'repro','files':{'src/lib.rs':src}}},open(f"{R}/spec/lessons/L-0304.yaml","w"),sort_keys=False)
EOF
P5=$(g "$R" upstream prepare L-0304 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print((d.get('result') or {}).get('packet_id') or 'BLOCKED '+json.dumps((d.get('error') or {}).get('details',{}).get('reasons')))"); echo "prepare: $P5"
case "$P5" in PKT-*) gp "$R" "r['files']" upstream submit "$P5" --destination "$INBOX" --approved-by owner; f=$(find "$INBOX" -path "*$P5*/fixture/src/lib.rs"); cmp "$f" "$R/src/lib.rs" && echo "inbox received a byte-identical copy of the project's src/lib.rs";; esac
note "(b) vector rows from the project's derived index dumped into a fixture file named embeddings.json"
python3 - "$R" <<'EOF'
import yaml,sys,sqlite3,json
R=sys.argv[1]; db=sqlite3.connect(f"{R}/.governance-runtime/state.db")
cols=[r[1] for r in db.execute("PRAGMA table_info(vectors)")]
rows=db.execute("SELECT * FROM vectors LIMIT 3").fetchall()
dump=json.dumps([{c:(v if not isinstance(v,bytes) else v.hex()[:200]) for c,v in zip(cols,r)} for r in rows])
yaml.safe_dump({'id':'L-0305','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['R'],
  'synthetic_reproducer':{'synthetic':True,'description':'repro','files':{'embeddings.json':dump}}},open(f"{R}/spec/lessons/L-0305.yaml","w"),sort_keys=False)
print("vector columns:", cols, "rows dumped:", len(rows))
EOF
gp "$R" "{'ok':ok,'packet':(r or {}).get('packet_id'),'err':e.get('code') if e else None}" upstream prepare L-0305
note "(c) filename-based controls do work: a fixture named index.sqlite or state.db"
yw "$R" spec/lessons/L-0306.yaml "{'id':'L-0306','type':'lesson','title':'t','status':'ACTIVE','scope':'FRAMEWORK','lifecycle':'corroborated','category':'c','problem_statement':'p','generic_failure_mode':'g','impact':'i','suggested_change':'s','sources':['R'],'synthetic_reproducer':{'synthetic':True,'description':'d','files':{'index.sqlite':'x','state.db':'y'}}}"
gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'reasons':(e or {}).get('details',{}).get('reasons')}" upstream prepare L-0306

say "Q4 ledger / payload hash"
tail -3 "$R/spec/reports/upstream-ledger.jsonl" | python3 -c "import json,sys; [print({k:json.loads(l)[k] for k in ['packet_id','payload_hash','approved_by','files']}) for l in sys.stdin]"
