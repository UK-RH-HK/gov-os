#!/usr/bin/env bash
# Gamma held-out probe: E1 (authority levels) and E2 (representative roles).
# Contract v3 E1 (:362-366): L0-L5 executable; role authority checked on every privileged/mutating path;
# lower roles cannot manufacture higher-trust facts; independent auditors/testers appropriately constrained.
# Contract v3 E2 (:368-375): the seven representative role classes, including governed extension.
. "$(dirname "$0")/lib.sh"
newproj e1auth --provision >/dev/null

# --- E1 b1: L0-L5 are executable (defined in the VERIFIED kernel and enforced, not merely listed) -----
levels=$(python3 -c "
import yaml,collections
d=yaml.safe_load(open('$PROJ/governance/kernel/roles/ROLES.yaml'))
ls=sorted({r['level'] for r in d['roles']})
print(','.join(ls))")
check "$levels" "L0,L1,L2,L3,L4,L5" "E1 b1: the kernel defines every authority level L0-L5"

# an L0 role is refused an L2 operation; an L2 role is allowed it; an L4-only operation refuses L2
a=$(g independent-auditor task create --class implementation --objective x | jget "d['error']['code']")
check "$a" "AUTHORITY_DENIED" "E1 b1: an L0 role is refused an L2 operation (create_task)"
b=$(g product-spec-agent task create --class implementation --objective x | jget "r['id'][:5]")
check "$b" "TASK-" "E1 b1: an L2 role performs the L2 operation"
c=$(g product-spec-agent resume | jget "d['error']['code']")
check "$c" "AUTHORITY_DENIED" "E1 b1: an L2 role is refused an L4 operation (resume_control)"

# --- E1 b2: authority is checked on privileged/mutating paths -----------------------------------------
# Every mutating command reachable without prior set-up, driven by the lowest role that exists (L0).
# Each entry is "<command> :: <authority operation it must be guarded by>"; the operation's required
# level comes from the VERIFIED kernel AUTHORITY_POLICY, and the probe drives the command with an
# L0 role, which is below every level except L0.
declare -a MUT=(
 "task create --class implementation --objective x::create_task"
 "task status TASK-0001 READY::mutate_task_status"
 "task replan::replan"
 "readiness plan FEAT-0001::readiness_plan"
 "handoff create --to-role backend-engineer --task TASK-0001::create_handoff"
 "checkpoint create --next-action x::checkpoint"
 "cit propose --proposal x --title x::propose_cit"
 "pause::emergency_control"
 "freeze-writes::emergency_control"
 "cancel-agents::emergency_control"
 "resume::resume_control"
 "gate create --question q --fields {}::create_gate"
 "gate revoke HDG-0001::revoke_gate"
 "tools install --descriptor /dev/null::install_tool"
 "plugins register --descriptor /dev/null::register_plugin"
 "update --apply::update_apply"
 "memory heldout-starter --force::memory_heldout_starter"
)
unguarded=0
for entry in "${MUT[@]}"; do
  cmd="${entry%%::*}"; op="${entry##*::}"
  req=$(python3 -c "
import yaml
d=yaml.safe_load(open('$PROJ/governance/kernel/policies/AUTHORITY_POLICY.yaml'))
print(d['authority_levels_required'].get('$op','(unmapped)'))")
  out=$(g independent-auditor $cmd)
  code=$(printf '%s' "$out" | python3 -c "
import sys,json
t=sys.stdin.read()
try: d=json.loads(t)
except Exception: print('NON_JSON'); raise SystemExit
print('OK' if d.get('ok') else d.get('error',{}).get('code','?'))")
  case "$code" in
    AUTHORITY_DENIED) ;;
    OK) echo "    NOTE unguarded: '$cmd' succeeded as an L0 role (declared authority $op=$req)"; unguarded=$((unguarded+1));;
    *)  echo "    (refused before the authority check: '$cmd' -> $code; declared $op=$req)";;
  esac
done
check "$unguarded" "0" "E1 b2: no command declared above L0 succeeds for an L0 role"

# undeclared invocation carries no privileged authority (BC-P2-08 / S0-E1-01)
u=$( cd "$PROJ" && env -u GOV_ROLE "$GOV" --json task create --class implementation --objective x 2>&1 | jget "d['error']['details']['cause']")
check "$u" "ROLE_UNDECLARED" "E1 b2: an invocation that declares no role receives no privileged authority"

# --- E1 b3: lower roles cannot manufacture higher-trust facts ------------------------------------------
h=$(g human task create --class implementation --objective x | jget "d['error']['details']['cause']")
check "$h" "HUMAN_ROLE_CLAIM" "E1 b3: --role human manufactures no human authority"
h2=$( cd "$PROJ" && GOV_ROLE=human "$GOV" --json task create --class implementation --objective x 2>&1 | jget "d['error']['details']['cause']")
check "$h2" "HUMAN_ROLE_CLAIM" "E1 b3: GOV_ROLE=human manufactures no human authority"
h3=$(g not-a-kernel-role task create --class implementation --objective x | jget "d['error']['code']")
check "$h3" "UNKNOWN_ROLE" "E1 b3: an invented role id is refused, not honoured"

# a hand-written gate answer (a repository file) must not approve anything
GFIELDS='{"why_now":"probe","current_state":"none","options":[{"id":"A","description":"approve"},{"id":"B","description":"reject"}],"impact":"none","reversibility":"reversible","cost_rework":"low","recommendation":"B","confidence":0.5}'
g product-spec-agent gate create --question "gamma forge probe" --fields "$GFIELDS" >/dev/null 2>&1 || true
GATE=$(python3 -c "
import os,glob,yaml
gs=sorted(glob.glob('$PROJ/spec/decisions/HDG-*.yaml'))
print(os.path.basename(gs[-1])[:-5] if gs else '')")
if [ -n "$GATE" ]; then
  python3 - "$PROJ/spec/decisions/$GATE.yaml" <<'PY'
import sys,yaml
p=sys.argv[1]; d=yaml.safe_load(open(p))
d['gate_status']='ANSWERED'; d['answer']={'option':'A','answered_by':'human','by_kind':'human'}
d['answered_by']='human'; d['answered_by_kind']='human'; d['option']='A'
yaml.safe_dump(d,open(p,'w'))
PY
  sh=$(gp orchestrator gate show "$GATE" 2>&1)
  t2=$(printf '%s' "$sh" | python3 -c "
import sys,yaml
d=yaml.safe_load(sys.stdin)
print('%s/%s/%s' % (d.get('t2',{}).get('binding'), d.get('authorisation',{}).get('state'), d.get('answer',{}).get('verified')))")
  check "$t2" "BROKEN/UNVERIFIED/False" "E1 b3: a hand-edited gate answer is T2-unbound, unverified and not honoured"
else
  echo "    (no gate available to forge)"
fi

# --- E1 b4: independent auditors/testers are appropriately constrained ---------------------------------
lvl=$(python3 -c "
import yaml
d=yaml.safe_load(open('$PROJ/governance/kernel/roles/ROLES.yaml'))
m={r['id']:r['level'] for r in d['roles']}
print(','.join(m.get(x,'-') for x in ['independent-auditor','independent-test-designer','migration-reviewer','migration-verifier','memory-verifier']))")
check "$lvl" "L0,L1,L0,L0,L0" "E1 b4: the independent audit/verification roles sit at read-only authority"
perms=$(python3 -c "
import yaml
d=yaml.safe_load(open('$PROJ/governance/project/TOOL_PERMISSIONS.yaml'))['roles']
bad=[r for r in ['independent-auditor','migration-reviewer','memory-verifier'] if 'WRITE_REPO_SCOPED' in d.get(r,[])]
print(','.join(bad) or 'none')")
check "$perms" "none" "E1 b4: the independent roles hold no repository-write permission class"

# --- E2: the seven representative role classes, and governed extension ---------------------------------
missing=$(python3 -c "
import yaml
d=yaml.safe_load(open('$PROJ/governance/kernel/roles/ROLES.yaml'))
ids={r['id'] for r in d['roles']}
need={'orchestrator/CTO':['orchestrator'],
 'architecture/research/data/implementation':['architecture-agent','research-agent','data-engineer','backend-engineer'],
 'memory engineer':['memory-engineer'],'independent test author':['independent-test-designer'],
 'independent verifier/auditor':['independent-auditor'],'security/release':['security-engineer','release-agent']}
miss=[k for k,v in need.items() if not all(x in ids for x in v)]
print(';'.join(miss) or 'none')")
check "$missing" "none" "E2 b1-b6: every representative role class the contract lists exists in the kernel"

ext=$(python3 -c "
import yaml,os
p='$PROJ/governance/kernel/roles/ROLES.yaml'
d=yaml.safe_load(open(p))
print('declared' if d.get('project_roles') or d.get('extension') or d.get('project_role_extension') else 'absent')")
# a project-specific role must be usable through a governed extension point
cp "$PROJ/governance/project/CAPABILITY_PROFILE.yaml" "$LAB/cp.bak" 2>/dev/null
pr=$(g orchestrator policy show 2>/dev/null | jget "'x'" 2>/dev/null)
newrole=$(g my-project-role task create --class implementation --objective x | jget "d['error']['code']")
check "$newrole/$ext" "UNKNOWN_ROLE/absent" "E2 b7: a project-specific role is refused and no governed role-extension point exists (gap)"
summary
