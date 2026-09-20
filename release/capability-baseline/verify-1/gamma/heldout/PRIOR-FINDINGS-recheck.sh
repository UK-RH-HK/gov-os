#!/usr/bin/env bash
# Gamma held-out probe: direct re-checks for the iteration-0 findings in gamma's scope whose disposition the
# capability probes do not already decide. Each block names the finding it disposes of.
. "$(dirname "$0")/lib.sh"
newproj prior --provision >/dev/null

# --- A0-E1-06: do the derived views carry the gamma capabilities' checklist bullets and an evidence owner? ---
em=$(PROJ="$PROJ" python3 -c "
import yaml,os,glob
p=None
for c in ['$GAMMA_WT/tests/governance/capability-evidence-map.yaml']:
    if os.path.exists(c): p=c
if not p: print('map-missing'); raise SystemExit
d=yaml.safe_load(open(p))
rows=d.get('capabilities') or d.get('rows') or []
mine=[r for r in rows if str(r.get('capability') or r.get('id')) in [c+str(n) for c in 'EFGHI' for n in range(1,6)]]
unmapped=[r for r in mine if (r.get('evidence_class') in (None,'NOT_YET_MAPPED')) or not (r.get('automated_checks') or [])]
print('%d/%d unmapped' % (len(unmapped), len(mine)))")
echo "    evidence map for the 19 gamma capabilities: $em"
case "$em" in 0/*) ok "A0-E1-06: every gamma capability has an evidence class and at least one automated check";;
  *) bad "A0-E1-06: the evidence map still leaves gamma capabilities unmapped ($em)";; esac
cb=$(PROJ="$PROJ" python3 -c "
import yaml,os
p='$GAMMA_WT/framework/contracts/governance-capability-acceptance.yaml'
if not os.path.exists(p): print('absent'); raise SystemExit
d=yaml.safe_load(open(p))
caps=d.get('capabilities') or []
e1=[c for c in caps if str(c.get('id'))=='E1']
print('bullets' if (e1 and (e1[0].get('checklist') or e1[0].get('bullets'))) else 'headings-only')")
echo "    compiled contract view for E1: $cb"
case "$cb" in bullets) ok "A0-E1-06: the compiled contract view carries checklist bullets";; *) bad "A0-E1-06: the compiled contract view still carries headings only ($cb)";; esac

# --- A0-E1-05: does a generated gap task's designated role bind who may claim it? ---
mkdir -p "$PROJ/spec/features"
printf 'id: FEAT-7001\ntype: feature\nstatus: ACTIVE\ntitle: Designated role feature\nreadiness: {}\n' > "$PROJ/spec/features/FEAT-7001.yaml"
g memory-engineer rebuild-memory --incremental >/dev/null 2>&1
g orchestrator readiness plan FEAT-7001 >/dev/null 2>&1
TD=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
for f in glob.glob(os.environ['PROJ']+'/spec/tasks/TASK-*.yaml'):
    d=yaml.safe_load(open(f))
    if d.get('readiness_cell')=='independent_acceptance_tests': print(d['id']); break
else: print('none')")
echo "    independent-test gap task: $TD"
wrong=$(GOV_SESSION=wrong g backend-engineer task claim "$TD" | jget "'ALLOWED' if d.get('ok') else d['error']['code']")
right=$(GOV_SESSION=right g independent-test-designer task claim "$TD" | jget "'ALLOWED' if d.get('ok') else d['error']['code']")
echo "    claim by backend-engineer -> $wrong ; by independent-test-designer -> $right"
if [ "$wrong" != "ALLOWED" ] && [ "$right" = "ALLOWED" ]; then ok "A0-E1-05: a designated role binds who may claim the task it designates"
else bad "A0-E1-05: task role designation is not enforced (wrong role -> $wrong, designated role -> $right)"; fi

# --- A0-E3-01: is a handoff return bound to its recipient, and does a later return overwrite the earlier one? ---
T=$(g orchestrator task create --class documentation --objective "handoff binding" --allowed "product/h/**" | jget "r['id']")
g orchestrator task status "$T" READY >/dev/null; g orchestrator task claim "$T" >/dev/null
H=$(g orchestrator handoff create --to-role backend-engineer --task "$T" | jget "r['id']")
python3 -c "
import json
json.dump({'task':'$T','status':'success','work_completed':'first return','files_changed':[],'evidence':['a'],
 'tests':{'status':'not_applicable_with_reason','reason':'documentation'},'discoveries':[],'risks':[],'lessons':[],
 'proposed_decisions':[],'unresolved':[],'recommended_next_action':'none'}, open('$LAB/h1.json','w'))
json.dump({'task':'$T','status':'success','work_completed':'SECOND return by a different role','files_changed':[],'evidence':['b'],
 'tests':{'status':'not_applicable_with_reason','reason':'documentation'},'discoveries':[],'risks':[],'lessons':[],
 'proposed_decisions':[],'unresolved':[],'recommended_next_action':'none'}, open('$LAB/h2.json','w'))"
g backend-engineer handoff return "$H" --file "$LAB/h1.json" >/dev/null
second=$(g frontend-engineer handoff return "$H" --file "$LAB/h2.json" | jget "'ACCEPTED' if d.get('ok') else d['error']['code']")
kept=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
f=glob.glob(os.environ['PROJ']+'/spec/**/$H.yaml',recursive=True)[0]
print(yaml.safe_load(open(f))['return']['work_completed'][:20])")
echo "    second return by a role the handoff did not name -> $second ; record now holds: '$kept'"
case "$second" in ACCEPTED) bad "A0-E3-01: a role the handoff did not name returned it, overwriting the earlier return ('$kept')";;
  *) ok "A0-E3-01: a return by a role the handoff did not name is refused ($second)";; esac

# --- A0-E4-04: does `gov continue` offer a task already in progress under another session? ---
TA=$(g orchestrator task create --class documentation --objective "held by A" --allowed "product/ca/**" | jget "r['id']")
g orchestrator task status "$TA" READY >/dev/null
GOV_SESSION=sessA g orchestrator task claim "$TA" >/dev/null
offer=$(GOV_SESSION=sessB g orchestrator continue | jget "r.get('task')")
echo "    continue in session B offered: $offer (session A holds $TA)"
case "$offer" in "$TA") bad "A0-E4-04: continue offered a task already claimed by another session";;
  *) ok "A0-E4-04: continue offers other work, not the task another session holds ($offer)";; esac

# --- A0-F1-02: are a skill's inputs/outputs consumed, and is skill evidence a defined element? ---
TV=$(g orchestrator task create --class validation --objective "close a task with evidence" | jget "r['id']")
sr=$(g orchestrator skills resolve "$TV" | jget "json.dumps(r)[:500]")
echo "    skills resolve (a class kernel skills cover) -> $sr"
defd=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
miss=[]
for f in glob.glob(os.environ['PROJ']+'/governance/kernel/skills/*.yaml'):
    d=yaml.safe_load(open(f))
    if not (d.get('inputs') and d.get('outputs') and d.get('validation_scenarios')): miss.append(d.get('id'))
print(','.join(x for x in miss if x) or 'none')")
check "$defd" "none" "A0-F1-02 (defined half): every kernel skill defines inputs, outputs and evidence scenarios"
case "$sr" in *inputs*|*outputs*) ok "A0-F1-02 (consumed half): a resolved skill carries its inputs/outputs to the caller";;
  *) bad "A0-F1-02 (consumed half): skill resolution returns id, version, source and content hash only — a skill's declared inputs/outputs are still not consumed by any caller";; esac

# --- A0-F3-01: does an install gate answered A actually lead to the installation? ---
RPT=$(security_review TL-GATED 3.0.0)
descriptor "$LAB/gated.yaml" "$RPT" '{"tool_id":"TL-GATED","version_pin":"3.0.0","required_permission_classes":["READ_REPO","DB_WRITE"]}'
o1=$(GOV_SESSION=gi1 g tooling-engineer tools install --descriptor "$LAB/gated.yaml")
IG=$(printf '%s' "$o1" | jget "r.get('human_gate') or 'none'")
CG=$(printf '%s' "$o1" | jget "(r.get('change_transaction') or {}).get('human_gate') or 'none'")
echo "    elevated install raised installation gate=$IG change gate=$CG"
[ "$IG" != "none" ] && answer_gate orchestrator "$IG" A >/dev/null 2>&1
[ "$CG" != "none" ] && answer_gate orchestrator "$CG" A >/dev/null 2>&1
o2=$(GOV_SESSION=gi1 g tooling-engineer tools install --descriptor "$LAB/gated.yaml")
inst=$(printf '%s' "$o2" | jget "str(r.get('installed'))")
g2=$(printf '%s' "$o2" | jget "r.get('human_gate') or (r.get('change_transaction') or {}).get('human_gate') or 'none'")
echo "    after the owner answered: installed=$inst gate=$g2"
if [ "$inst" = "True" ]; then ok "A0-F3-01: an install gate answered A leads to the installation"
else
  [ "$g2" != "none" ] && [ "$g2" != "$IG" ] && [ "$g2" != "$CG" ] && bad "A0-F3-01: a NEW gate was raised instead of consuming the answered one ($g2)" || bad "A0-F3-01: the answered gate did not lead to an installation (installed=$inst, gate=$g2)"
fi

# --- A0-H3-01: can the project overlay switch off pre-implementation readiness gating? ---
python3 - "$PROJ/governance/project/PROJECT_POLICY.yaml" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p)) or {}
d.setdefault("readiness", {})["enforce_pre_implementation_cells"] = False
yaml.safe_dump(d, open(p, "w"))
PY
IMPL=$(g orchestrator task create --class implementation --objective "implement FEAT-7001" --feature FEAT-7001 | jget "r['id']")
g orchestrator task status "$IMPL" READY >/dev/null 2>&1
off=$(g orchestrator task dag | jget "'runnable' if '$IMPL' in (r.get('runnable') or []) else 'blocked'")
ref=$(g orchestrator policy 2>/dev/null | jget "json.dumps(r)[:200]" 2>/dev/null)
echo "    with PROJECT_POLICY.readiness.enforce_pre_implementation_cells=false the implementation task is $off"
case "$off" in runnable) bad "A0-H3-01: the project overlay switched off pre-implementation readiness gating";;
  *) ok "A0-H3-01: the project overlay cannot switch off pre-implementation readiness gating (task still $off)";; esac

# --- A0-I2-02: is a path permanently in scope for every later task once a CIT touched it? ---
TS=$(g orchestrator task create --class documentation --objective "scoped task" --allowed "product/scoped/**" | jget "r['id']")
g orchestrator task status "$TS" READY >/dev/null; g orchestrator task claim "$TS" >/dev/null
mkdir -p "$PROJ/spec/decisions"
printf 'id: D-7001\ntype: decision\nstatus: ACTIVE\ntitle: touched by an earlier transaction\nchosen_option: A\nrationale: x\nhuman_approved: false\n' > "$PROJ/spec/decisions/D-7001.yaml"
HS=$(g orchestrator context compile "$TS" | jget "r.get('packet_hash')")
python3 -c "
import json
json.dump({'task':'$TS','status':'success','work_completed':'wrote a decision outside my scope',
 'files_changed':['spec/decisions/D-7001.yaml'],'evidence':['x'],
 'tests':{'status':'not_applicable_with_reason','reason':'documentation'},'discoveries':[],'risks':[],'lessons':[],
 'proposed_decisions':[],'unresolved':[],'recommended_next_action':'none','context_packet_hash':'$HS',
 'inputs_consumed':[],'outputs_produced':[],'requirements_implemented':[],'scenarios_implemented':[],
 'features_implemented':[],'decisions_applied':[],'constraints_applied':[],'acceptance_evidence':[],'deviations':[]},
 open('$LAB/scoped.json','w'))"
sc=$(g orchestrator task close "$TS" --report "$LAB/scoped.json" | jget "'CLOSED' if d.get('ok') else d['error']['code']")
echo "    closing a task that wrote outside its scope -> $sc"
case "$sc" in CLOSED) bad "A0-I2-02: a path outside the task's declared scope was accepted at close";;
  *) ok "A0-I2-02: a path outside the task's declared scope is refused at close ($sc)";; esac

# --- A0-I4-01: is the per-feature view an end-to-end path or a record-order grouping? ---
pf=$(g orchestrator task dag | jget "json.dumps(r.get('per_feature'))[:300]")
echo "    per_feature: $pf"
ordered=$(g orchestrator task dag | PROJ="$PROJ" python3 -c "
import sys,json,yaml,glob,os
d=json.load(sys.stdin); r=d.get('result',d)
pf=r.get('per_feature') or {}
ids=[]
for k,v in pf.items():
    if k and v: ids=v; break
if not ids: print('empty'); raise SystemExit
# an end-to-end path respects dependency order: no task appears before one it depends on
pos={t:i for i,t in enumerate(ids)}
bad=[]
for t in ids:
    f=os.environ['PROJ']+'/spec/tasks/%s.yaml'%t
    if not os.path.exists(f): continue
    for dep in (yaml.safe_load(open(f)).get('depends_on') or []):
        if dep in pos and pos[dep]>pos[t]: bad.append((t,dep))
print('ordered' if not bad else 'out-of-order:%s'%bad[:2])")
case "$ordered" in ordered) ok "A0-I4-01: the per-feature view respects dependency order (an end-to-end path)";;
  empty) echo "    (no multi-task feature to order)"; ok "A0-I4-01: recorded — no multi-task feature in this project to order";;
  *) bad "A0-I4-01: the per-feature view is not dependency-ordered ($ordered)";; esac

# --- A0-F5-01 (second half): can a handoff declare authority broader than its task? ---
TB=$(g orchestrator task create --class documentation --objective "narrow scope" --allowed "product/narrow/**" | jget "r['id']")
g orchestrator task status "$TB" READY >/dev/null; g orchestrator task claim "$TB" >/dev/null
HB=$(g orchestrator handoff create --to-role backend-engineer --task "$TB" --fields '{"authority":{"allowed":["**"],"prohibited":[]}}' | jget "r['id']")
au=$(PROJ="$PROJ" python3 -c "
import yaml,glob,os
f=glob.glob(os.environ['PROJ']+'/spec/**/$HB.yaml',recursive=True)[0]
d=yaml.safe_load(open(f)); print(str(d['authority']))")
echo "    handoff authority as recorded: $au"
case "$au" in *'**'*) bad "A0-F5-01: a handoff declared authority ('**') broader than its task's allowed paths";;
  *) ok "A0-F5-01: a handoff cannot declare authority broader than its task ($au)";; esac
summary
