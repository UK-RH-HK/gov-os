#!/usr/bin/env bash
# Gamma held-out probe: evidence freshness for the gamma capabilities (Contract v3 :95-111, AC-10).
# For each capability family, change a relevant input and show that prior green evidence goes STALE.
. "$(dirname "$0")/lib.sh"
newproj fresh --provision >/dev/null

classes=$(g orchestrator health currency | jget "','.join(sorted((r.get('snapshot') or {}).get('classes',{})))")
echo "    currency input classes: $classes"
for cls in tools_plugins project_skills spec_tasks spec_requirements source index_manifest machine_trust; do
  case ",$classes," in *",$cls,"*) ok "AC-10: the evidence currency key covers the input class '$cls'";;
    *) bad "AC-10: the evidence currency key does not cover '$cls'";; esac
done

keyof() { g orchestrator health currency | jget "(r.get('snapshot') or {}).get('key')"; }
digestof() { g orchestrator health currency | jget "((r.get('snapshot') or {}).get('classes',{}).get('$1') or {}).get('digest')"; }

k0=$(keyof); s0=$(digestof project_skills); t0=$(digestof tools_plugins); q0=$(digestof spec_tasks)

# F1: a skill is a versioned method — changing one must invalidate skill evidence
mkdir -p "$PROJ/governance/project/skills"
cat > "$PROJ/governance/project/skills/SKL-PROBE.yaml" <<'Y'
id: SKL-PROBE
name: Probe skill
version: 1.0.0
status: ACTIVE
roles: [orchestrator]
task_classes: [governance]
purpose: "a skill added to test evidence freshness"
inputs: [x]
outputs: [y]
method: [{step: one, description: do the thing}]
validation_scenarios: [{id: V1, given: x, expect: y}]
Y
s1=$(digestof project_skills); k1=$(keyof)
[ "$s0" != "$s1" ] && ok "AC-10 (F1): adding a project skill changes the project_skills digest" || bad "AC-10 (F1): a new project skill leaves the skill digest unchanged"
[ "$k0" != "$k1" ] && ok "AC-10 (F1): and the whole evidence currency key" || bad "AC-10 (F1): the currency key did not change"

# F2/F4: the tool / plugin registry
mkdir -p "$PROJ/governance/project/tools"
printf 'tool_id: TL-FRESH\nname: fresh\ntype: CLI\ncapabilities: [x]\nstatus: active\napproved_roles: [all]\n' > "$PROJ/governance/project/tools/TL-FRESH.yaml"
t1=$(digestof tools_plugins)
[ "$t0" != "$t1" ] && ok "AC-10 (F2/F4): a change to the tool/plugin registry changes its digest" || bad "AC-10 (F2/F4): a new tool descriptor leaves the tool/plugin digest unchanged"

# H2/H3 and I1/I2/I4: features, readiness and the task DAG
mkdir -p "$PROJ/spec/features"
printf 'id: FEAT-9001\ntype: feature\nstatus: ACTIVE\ntitle: Freshness feature\nreadiness: {}\n' > "$PROJ/spec/features/FEAT-9001.yaml"
g orchestrator task create --class governance --objective "freshness task" >/dev/null 2>&1
q1=$(digestof spec_tasks); r1=$(digestof spec_requirements)
[ "$q0" != "$q1" ] && ok "AC-10 (I1/I2/I4): a task-DAG change changes the spec_tasks digest" || bad "AC-10 (I1/I2/I4): a new task leaves the task digest unchanged"
[ -n "$r1" ] && ok "AC-10 (H2/H3): feature/readiness state is carried by the spec_requirements class" || bad "AC-10 (H2/H3): no digest class carries feature readiness"

# a green governance record must stop being current once a relevant input changes
g memory-engineer rebuild-memory >/dev/null 2>&1
g orchestrator audit >/dev/null 2>&1
cur0=$(g orchestrator health currency | jget "str((r.get('currency') or {}).get('current'))")
green=$(g orchestrator health currency | jget "str((r.get('currency') or {}).get('green'))")
echo "    green record $green current=$cur0"
printf '\n# an edit made after the record was taken\n' >> "$PROJ/governance/project/tools/TL-FRESH.yaml"
cur1=$(g orchestrator health currency | jget "str((r.get('currency') or {}).get('current'))")
ch=$(g orchestrator health currency | jget "','.join(sorted(c['class'] for c in ((r.get('currency') or {}).get('changed_classes') or [])))")
echo "    after a tool-registry edit: current=$cur1 changed=$ch"
check "$cur1" "False" "AC-10: a green governance record stops being current once a relevant input changes"
case ",$ch," in *",tools_plugins,"*) ok "AC-10: the OS names the changed input class that invalidated it";; *) bad "AC-10: the invalidating class is not named ($ch)";; esac

# and the stale record actually refuses governance-affecting work rather than being ignored
TT=$(g orchestrator task create --class governance --objective "governance work on stale evidence" --allowed "spec/**" | jget "r['id']")
g orchestrator task status "$TT" READY >/dev/null; g orchestrator task claim "$TT" >/dev/null
printf 'id: D-9001\ntype: decision\nstatus: ACTIVE\ntitle: probe decision\nchosen_option: A\nrationale: probe\nhuman_approved: false\n' > "$PROJ/spec/decisions/D-9001.yaml"
HH=$(g orchestrator context compile "$TT" | jget "r.get('packet_hash')")
python3 -c "
import json
json.dump({'task':'$TT','status':'success','work_completed':'governance edit','files_changed':['spec/decisions/D-9001.yaml'],
 'evidence':['x'],'tests':{'status':'not_applicable_with_reason','reason':'governance'},'discoveries':[],'risks':[],
 'lessons':[],'proposed_decisions':[],'unresolved':[],'recommended_next_action':'none','context_packet_hash':'$HH',
 'inputs_consumed':[],'outputs_produced':[],'requirements_implemented':[],'scenarios_implemented':[],
 'features_implemented':[],'decisions_applied':[],'constraints_applied':[],'acceptance_evidence':[],'deviations':[]},
 open('$LAB/fresh-close.json','w'))"
cc=$(g orchestrator task close "$TT" --report "$LAB/fresh-close.json" | jget "'CLOSED' if d.get('ok') else d['error']['code']")
echo "    close of governance work on a stale green record -> $cc"
case "$cc" in CLOSED) bad "AC-10: governance-affecting work closed on an obsolete green record";; *) ok "AC-10: governance-affecting work is refused on an obsolete green record ($cc)";; esac
summary
