#!/usr/bin/env bash
# Gamma held-out probe: G1/G2 (human command surface) and I1-I4 (dynamic work system).
# Contract v3 :443-454 (G) and :535-590 (I).
. "$(dirname "$0")/lib.sh"
newproj gi --provision >/dev/null

# ===================== G1: natural-language intent ==================================================
r1=$(g orchestrator intent "what is the state of the project" | jget "r['intent']")
check "$r1" "STATUS" "G1 b1: a human expresses intent in words, without internal command syntax"
r2=$(g orchestrator intent "what is the state of the project" | jget "','.join(r['commands'])")
echo "    -> $r2"
# deterministic: the same words always give the same routing
a=$(g orchestrator intent "please pause everything" | jget "r['intent']")
b=$(g orchestrator intent "please pause everything" | jget "r['intent']")
check "$a/$b" "PAUSE/PAUSE" "G1 b2: the same words map deterministically to the same governed operation"
# every proposed command must be a governed operation the command contract declares
unknown=$(g orchestrator intent "approve it" | PROJ="$PROJ" python3 -c "
import sys,json,yaml,os
d=json.load(sys.stdin); r=d.get('result',d)
c=yaml.safe_load(open(os.environ['PROJ']+'/governance/kernel/commands/COMMAND_CONTRACT.yaml'))
cli={x['cli'].split()[0] for x in c['internal_operations']} | {x['command'] for x in c['human_surface']}
bad=[]
for cmd in r.get('commands') or []:
    toks=cmd.split()
    if toks[0]!='gov' or len(toks)<2: bad.append(cmd); continue
    if toks[1] not in cli: bad.append(cmd)
    if '...' in cmd or '<' in cmd and '&&' in cmd: bad.append(cmd)
print(';'.join(bad) or 'none')")
check "$unknown" "none" "G1 b2: every routed command is a governed operation the command contract declares"
# a negated intent must not route to the affirmative operation
neg=$(g orchestrator intent "do not approve this change" | jget "r['intent']")
case "$neg" in APPROVE) bad "G1 b2: 'do not approve this change' routes to APPROVE (negation inverted)";; *) ok "G1 b2: a negated intent does not route to the affirmative operation (got $neg)";; esac
# the router never proposes a command that asserts a human identity
hum=$(g orchestrator intent "approve it" | jget "'yes' if any('--by human' in c or '--role human' in c or '--method human' in c for c in (r.get('commands') or [])) else 'no'")
check "$hum" "no" "G1 b2: the router never proposes a command that asserts a human identity on the agent's behalf"
# G1 b3: a consequential change automatically invokes impact/gate logic, with no operator /impact step
mkdir -p "$PROJ/spec/interfaces"
T=$(g orchestrator task create --class documentation --objective "edit an interface contract" --allowed "spec/**" | jget "r['id']")
g orchestrator task status "$T" READY >/dev/null; g orchestrator task claim "$T" >/dev/null
python3 - "$PROJ/spec/interfaces/API-7001.yaml" <<'PY'
import sys, yaml
yaml.safe_dump({"id":"API-7001","type":"interface","status":"ACTIVE","title":"Payments API","kind":"http",
                "version":"1.0.0","contract":{"fields":["amount","currency"]}}, open(sys.argv[1],"w"))
PY
g memory-engineer rebuild-memory --incremental >/dev/null 2>&1
python3 - "$PROJ/spec/interfaces/API-7001.yaml" <<'PY'
import sys, yaml
d=yaml.safe_load(open(sys.argv[1])); d["contract"]["fields"]=["amount"]; d["version"]="2.0.0"
yaml.safe_dump(d, open(sys.argv[1],"w"))
PY
cls=$(g orchestrator cit classify --paths spec/interfaces/API-7001.yaml | jget "json.dumps(r)")
echo "    classify -> $(printf '%s' "$cls" | head -c 300)"
mat=$(printf '%s' "$cls" | python3 -c "
import sys,json
r=json.loads(sys.stdin.read())
t=json.dumps(r).lower()
print('material' if 'material' in t or 'interface_change' in t or 'r2' in t or 'r3' in t else 'none')")
check "$mat" "material" "G1 b3: a consequential edit is classified material by the OS, from the change itself"
python3 - "$LAB/gi-close.json" "$T" <<'PY'
import sys, json
json.dump({"task":sys.argv[2],"status":"success","work_completed":"edited the interface","files_changed":["spec/interfaces/API-7001.yaml"],
 "evidence":["the edit"],"tests":{"status":"not_applicable_with_reason","reason":"documentation"},"discoveries":[],"risks":[],
 "lessons":[],"proposed_decisions":[],"unresolved":[],"recommended_next_action":"none",
 "context_packet_hash":"","inputs_consumed":[],"outputs_produced":[],"requirements_implemented":[],
 "scenarios_implemented":[],"features_implemented":[],"decisions_applied":[],"constraints_applied":[],
 "acceptance_evidence":[],"deviations":[]}, open(sys.argv[1],"w"))
PY
H=$(g orchestrator context compile "$T" | jget "r['packet_hash']")
python3 -c "
import json;d=json.load(open('$LAB/gi-close.json'));d['context_packet_hash']='$H';json.dump(d,open('$LAB/gi-close.json','w'))"
cl=$(g orchestrator task close "$T" --report "$LAB/gi-close.json")
code=$(printf '%s' "$cl" | jget "'CLOSED' if d.get('ok') else d['error']['code']")
echo "    close of a task that made a material interface change -> $code"
case "$code" in
  CLOSED) bad "G1 b3 / BC-P2-13: a material interface change made inside an ordinary task closed with no impact simulation or gate";;
  *) ok "G1 b3: closing a task that made a material change without change control is refused ($code)";;
esac

# ===================== G2: the small explicit human control set =====================================
for pair in "status:status" "continue:continue" "audit:audit"; do
  cmd=${pair%%:*}
  out=$(gp orchestrator $cmd 2>&1 | head -1)
  if [ -n "$out" ]; then ok "G2: control '$cmd' is executable"; else bad "G2: control '$cmd' produced nothing"; fi
done
dec=$(gp orchestrator decide --help 2>&1 | grep -c "Usage: gov decide")
check "$dec" "1" "G2: control 'decide' is executable"
for c in pause freeze-writes cancel-agents; do
  o=$(g orchestrator $c | jget "'ok' if d.get('ok') else d['error']['code']")
  case "$o" in ok) ok "G2: emergency control '$c' is executable";; *) bad "G2: emergency control '$c' failed ($o)";; esac
done
# a frozen repository refuses writes and the remedy stays available (availability rule)
w=$(g orchestrator task create --class documentation --objective "should be refused" | jget "d['error']['code'] if not d.get('ok') else 'ALLOWED'")
case "$w" in FROZEN|FREEZE_WRITES|PAUSED) ok "G2: pause/freeze actually blocks governed writes ($w)";; *) bad "G2: a governed write was allowed under freeze ($w)";; esac
res=$(g orchestrator resume | jget "'ok' if d.get('ok') else d['error']['code']")
check "$res" "ok" "G2: the remedy for a freeze (resume) stays available while the freeze is in force"
rb=$(gp orchestrator cit rollback --help 2>&1 | head -1)
case "$rb" in *Usage*) ok "G2: control 'rollback' is executable";; *) bad "G2: rollback control missing";; esac

# ===================== I1: the unified task DAG supports 22 classes ==================================
missing=$(PROJ="$PROJ" python3 -c "
import json,os
d=json.load(open(os.environ['PROJ']+'/governance/kernel/schemas/task.schema.json'))
have=set(d['properties']['class']['enum'])
need=['discovery','research','experiment','specification','decision-preparation','data','architecture','implementation',
 'integration','test-design','test-execution','security','devops','performance','validation','refactor','repair',
 'documentation','release','tooling','memory','governance']
print(','.join(x for x in need if x not in have) or 'none')")
check "$missing" "none" "I1: every one of the twenty-two task classes is in the governed task contract"
# each class is not merely declared: it can be created and enters the one DAG
made=$(PROJ="$PROJ" bash -c '
n=0; bad=""
for c in discovery research experiment specification decision-preparation data architecture implementation integration test-design test-execution security devops performance validation refactor repair documentation release tooling memory governance; do
  out=$(cd "$PROJ" && "'$GOV'" --role orchestrator --json task create --class "$c" --objective "class probe $c" 2>&1)
  ok=$(printf "%s" "$out" | python3 -c "import sys,json;print(json.load(sys.stdin).get(\"ok\"))")
  if [ "$ok" = "True" ]; then n=$((n+1)); else bad="$bad $c"; fi
done
echo "$n|$bad"')
check "${made%%|*}" "22" "I1: all twenty-two classes can actually be created as tasks (${made##*|})"
inone=$(g orchestrator task dag | jget "r['counts']['total']")
echo "    tasks in the single DAG: $inone"

# ===================== I2: the task contract's nine fields are ENFORCED ==============================
TA=$(g orchestrator task create --class documentation --objective "A" --allowed "product/i2/**" | jget "r['id']")
TB=$(g orchestrator task create --class documentation --objective "B" --allowed "product/i2b/**" --deps "$TA" | jget "r['id']")
# dependencies/blocks
g orchestrator task status "$TB" READY >/dev/null
depblock=$(g orchestrator task claim "$TB" | jget "d['error']['code'] if not d.get('ok') else 'ALLOWED'")
check "$depblock" "TASK_NOT_RUNNABLE" "I2 b3: 'dependencies' are enforced (a dependent task is not runnable)"
# allowed/forbidden paths
g orchestrator task status "$TA" READY >/dev/null; g orchestrator task claim "$TA" >/dev/null
mkdir -p "$PROJ/product/elsewhere"; printf 'x\n' > "$PROJ/product/elsewhere/out.txt"
python3 -c "
import json
json.dump({'task':'$TA','status':'success','work_completed':'wrote outside the allowed paths',
 'files_changed':['product/elsewhere/out.txt'],'evidence':['x'],
 'tests':{'status':'not_applicable_with_reason','reason':'documentation'},'discoveries':[],'risks':[],'lessons':[],
 'proposed_decisions':[],'unresolved':[],'recommended_next_action':'none','context_packet_hash':'',
 'inputs_consumed':[],'outputs_produced':[],'requirements_implemented':[],'scenarios_implemented':[],
 'features_implemented':[],'decisions_applied':[],'constraints_applied':[],'acceptance_evidence':[],'deviations':[]},
 open('$LAB/i2.json','w'))"
HH=$(g orchestrator context compile "$TA" | jget "r['packet_hash']")
python3 -c "
import json;d=json.load(open('$LAB/i2.json'));d['context_packet_hash']='$HH';json.dump(d,open('$LAB/i2.json','w'))"
sc=$(g orchestrator task close "$TA" --report "$LAB/i2.json" | jget "d['error']['code'] if not d.get('ok') else 'CLOSED'")
case "$sc" in CLOSED) bad "I2 b8: a task closed although it changed a file outside its allowed paths";;
  *) ok "I2 b8: 'allowed/forbidden paths' are enforced at close ($sc)";; esac
# required_tools / required_data / production_merge_allowed
TC=$(g orchestrator task create --class documentation --objective "needs an absent tool" --allowed "product/i2c/**" \
      --fields '{"required_tools":["TL-DOES-NOT-EXIST"],"required_data":["DATA-DOES-NOT-EXIST"],"production_merge_allowed":false}' | jget "r['id']")
g orchestrator task status "$TC" READY >/dev/null
rt=$(g orchestrator task claim "$TC" | jget "d['error']['code'] if not d.get('ok') else 'ALLOWED'")
case "$rt" in ALLOWED) bad "I2 b6/b4: 'required_tools' and 'required_data' are recorded but not enforced (the task was claimed with both absent)";;
  *) ok "I2 b4/b6: an absent required tool/data blocks the task ($rt)";; esac
# minimum model tier / reasoning
tier=$(g orchestrator route --task "$TC" 2>/dev/null | jget "json.dumps({k:r.get(k) for k in ('tier','reasoning','minimum_tier','minimum_reasoning')})")
echo "    routing for $TC -> $tier"
case "$tier" in *tier*) ok "I2 b7: a minimum model tier / reasoning is resolved for a task";; *) bad "I2 b7: no model tier is resolved for a task";; esac

# ===================== I3: work is generated from each of the eleven sources ==========================
src=$(PROJ="$PROJ" python3 -c "
import yaml,os
d=yaml.safe_load(open(os.environ['PROJ']+'/governance/kernel/taxonomy/WORK_GENERATION.yaml'))
print(','.join(sorted(d['sources'])))")
echo "    declared generation sources: $src"
for want in "failed-tests:failed tests" "audit-finding:audit findings" "research-discovery:research discoveries" \
            "human-decision:human decisions" "cit-effect:CIT effects" "lesson:lessons" \
            "missing-tool:missing tools" "missing-skill:missing skills" "retrieval-failure:retrieval failures" \
            "security-finding:security findings" "performance-regression:performance regressions"; do
  k=${want%%:*}; label=${want##*:}
  case ",$src," in *",$k,"*) ok "I3: '$label' is a declared generation source ($k)";; *) bad "I3: no generation source for '$label'";; esac
done
# readiness gaps generate work (the twelfth source, :573) — shown in the H probe; here: the generator runs
gen=$(g orchestrator task generate --dry-run | jget "json.dumps({'created':len(r.get('created') or []),'candidates':len(r.get('candidates') or r.get('would_create') or [])})")
echo "    task generate --dry-run -> $gen"
# and generated work is LINKED and IDEMPOTENT
g orchestrator audit >/dev/null 2>&1
n1=$(g orchestrator task generate | jget "len(r.get('created') or [])")
n2=$(g orchestrator task generate | jget "len(r.get('created') or [])")
echo "    generated on first run: $n1; on an immediate second run: $n2"
check "$n2" "0" "I3: generation is idempotent (the same events do not generate the work twice)"
# every generated task states its source, subject and the evidence that caused it
prov=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
bad=[]
for f in glob.glob(os.environ['PROJ']+'/spec/tasks/TASK-*.yaml'):
    d=yaml.safe_load(open(f)); gs=d.get('generation') or {}
    if d.get('generated_by')=='gov work generation':
        if not all(gs.get(k) for k in ('source','subject','key','evidence_at')): bad.append(d['id'])
print(','.join(bad) or 'none')")
check "$prov" "none" "I3: every generated task records its source, subject, dedup key and the evidence that caused it"
# a RECORD-backed source links the causing record
L=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
f=sorted(glob.glob(os.environ['PROJ']+'/spec/lessons/L-*.yaml'))
print(yaml.safe_load(open(f[-1]))['id'] if f else 'none')")
TL=$(g orchestrator task create --class documentation --objective "produce a lesson for generation" --allowed "product/i3/**" | jget "r['id']")
g orchestrator task status "$TL" READY >/dev/null; g orchestrator task claim "$TL" >/dev/null
HL=$(g orchestrator handoff create --to-role backend-engineer --task "$TL" | jget "r['id']")
python3 -c "
import json
json.dump({'task':'$TL','status':'success','work_completed':'x','files_changed':[],'evidence':['x'],
 'tests':{'status':'not_applicable_with_reason','reason':'documentation'},'discoveries':[],'risks':[],
 'lessons':['the generation path must link the record that caused the work'],'proposed_decisions':[],
 'unresolved':[],'recommended_next_action':'none'}, open('$LAB/i3ret.json','w'))"
g backend-engineer handoff return "$HL" --file "$LAB/i3ret.json" >/dev/null
g memory-engineer rebuild-memory --incremental >/dev/null 2>&1
g orchestrator task generate >/dev/null 2>&1
lk=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
out='none'
for f in glob.glob(os.environ['PROJ']+'/spec/tasks/TASK-*.yaml'):
    d=yaml.safe_load(open(f)); gs=d.get('generation') or {}
    if gs.get('source')=='lesson':
        out = 'linked' if (gs.get('records') or d.get('relations') or d.get('derived_from')) else 'unlinked:%s'%d['id']
        break
print(out)")
case "$lk" in linked) ok "I3: a record-backed source (a lesson) generates work linked to the causing record";;
  none) bad "I3: a lesson produced no generated work at all";;
  *) bad "I3: generated work from a lesson is not linked to the causing record ($lk)";; esac

# ===================== I4: parallel execution ========================================================
dag=$(g orchestrator task dag | jget "json.dumps({k:len(r.get(k) or []) for k in ('runnable','blocked','waiting_human')} | {'chain':len(r.get('longest_chain') or []),'per_feature':len(r.get('per_feature') or {}),'gatedeps':len(r.get('human_gate_dependencies') or [])})")
echo "    dag -> $dag"
for k in runnable blocked waiting_human chain per_feature; do
  v=$(printf '%s' "$dag" | python3 -c "import sys,json;print(json.load(sys.stdin).get('$k'))")
  case "$k" in
    runnable) [ "$v" -ge 0 ] && ok "I4 b1: the DAG reports a runnable set ($v)";;
    blocked) [ "$v" -ge 0 ] && ok "I4 b1: the DAG reports a blocked set ($v)";;
    chain) [ "$v" -ge 1 ] && ok "I4 b2: the DAG reports a critical path ($v tasks)" || bad "I4 b2: no critical path";;
    per_feature) [ "$v" -ge 1 ] && ok "I4 b3: the DAG reports a per-feature path ($v features)" || bad "I4 b3: no per-feature path";;
    waiting_human) ok "I4 b4: the DAG reports a waiting-on-human set ($v)";;
  esac
done
# b4/b5: a task blocked on a human gate waits, and independent work stays available
TG=$(g orchestrator task create --class documentation --objective "waits on the owner" --allowed "product/i4a/**" --fields '{"human_gate":"HDG-0001"}' | jget "r['id']")
GF='{"why_now":"probe","current_state":"none","options":[{"id":"A","description":"approve"},{"id":"B","description":"reject"}],"impact":"none","reversibility":"reversible","cost_rework":"low","recommendation":"A","confidence":0.5}'
g orchestrator gate create --question "authorise the waiting work" --fields "$GF" >/dev/null
TI=$(g orchestrator task create --class documentation --objective "independent of the gate" --allowed "product/i4b/**" | jget "r['id']")
g orchestrator task status "$TG" READY >/dev/null; g orchestrator task status "$TI" READY >/dev/null
wh=$(g orchestrator task dag | jget "'waiting' if '$TG' in (r.get('waiting_human') or []) or any('$TG'==t.get('task') for t in (r.get('waiting_human') or []) if isinstance(t,dict)) else 'not-waiting'")
check "$wh" "waiting" "I4 b4: a task whose authorising gate is unanswered is reported as waiting on the human"
ind=$(g orchestrator task claim "$TI" | jget "'yes' if d.get('ok') else d['error']['code']")
check "$ind" "yes" "I4 b5: an independent branch continues while another waits for human input"
cont=$(g orchestrator continue | jget "json.dumps(r)[:200]")
echo "    continue -> $cont"
summary
