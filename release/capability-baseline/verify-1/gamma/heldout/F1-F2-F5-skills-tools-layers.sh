#!/usr/bin/env bash
# Gamma held-out probe: F1 (skill lifecycle), F2 (Tool Capability Registry fields), F5 (MCP/A2A/Knowledge-Fabric
# separation), and the OD-P2-03 envelope-source question: is the AUTHORISED side of the tool-installation trust
# envelope actually trusted OS state?
. "$(dirname "$0")/lib.sh"
newproj f125 --provision >/dev/null

# --- F1 b1: skills are versioned methods, not authority -------------------------------------------
v=$(python3 -c "
import yaml,glob,re
bad=[]; n=0
for f in glob.glob('$PROJ/governance/kernel/skills/*.yaml'):
    d=yaml.safe_load(open(f)); n+=1
    if not re.match(r'^\d+\.\d+\.\d+', str(d.get('version',''))): bad.append(d.get('id'))
print('%d/%s' % (n, ','.join(x for x in bad if x) or 'none'))")
check "${v#*/}" "none" "F1 b1: every kernel skill carries a semantic version ($v skills)"
auth=$(python3 -c "
import yaml,glob
grant=[]
for f in glob.glob('$PROJ/governance/kernel/skills/*.yaml'):
    d=yaml.safe_load(open(f))
    for k in ('authority','authority_level','grants','level'):
        if k in d: grant.append('%s.%s' % (d.get('id'),k))
print(','.join(grant) or 'none')")
check "$auth" "none" "F1 b1: no skill document carries or grants authority"
# a skill cannot lend authority: resolving one under an L0 role confers nothing
sk=$(g independent-auditor skills resolve --task-class validation | jget "'ok' if d.get('ok') else d['error']['code']")
echo "    skills resolve as an L0 role -> $sk"

# --- F1 b2: applicability / inputs / outputs / evidence are defined --------------------------------
f1b2=$(python3 -c "
import yaml,glob
need=['roles','task_classes','inputs','outputs','validation_scenarios']
miss={}
for f in glob.glob('$PROJ/governance/kernel/skills/*.yaml'):
    d=yaml.safe_load(open(f))
    m=[k for k in need if not d.get(k)]
    if m: miss[d.get('id')]=m
print(';'.join('%s:%s'%(k,','.join(v)) for k,v in miss.items()) or 'none')")
check "$f1b2" "none" "F1 b2: every skill defines applicability (roles, task classes), inputs, outputs and evidence scenarios"

# --- F1 b3: skill regression is testable — scenarios are EXECUTED, not merely declared --------------
sr=$(g orchestrator health skills | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
sk=r.get('detail',{}).get('skills',[])
executed=sum(1 for s in sk for sc in (s.get('scenarios') or []) if sc.get('status') in ('passed','failed'))
declared=sum(len(s.get('scenarios') or []) for s in sk)
deferred=sum(1 for s in sk for sc in (s.get('scenarios') or []) if sc.get('status') not in ('passed','failed'))
print('%d/%d/%d' % (executed, declared, deferred))")
ex=${sr%%/*}
if [ "$ex" -gt 0 ]; then ok "F1 b3: skill validation scenarios are actually executed ($sr executed/declared/deferred)"
else bad "F1 b3: no skill validation scenario is executed ($sr)"; fi
# a deferred scenario must say why (no silent N/A)
silent=$(g orchestrator health skills | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
n=0
for s in r.get('detail',{}).get('skills',[]):
    for sc in (s.get('scenarios') or []):
        if sc.get('status') not in ('passed','failed') and not (sc.get('reason') or sc.get('detail') or sc.get('deferred_reason') or sc.get('why')): n+=1
print(n)")
check "$silent" "0" "F1 b3: a scenario the suite does not execute states why (no silent N/A)"
# version/content binding: an edited skill no longer matches its recorded version
bind=$(g orchestrator health skills | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
print('present' if any('content_sha256' in s for s in r.get('detail',{}).get('skills',[])) else 'absent')")
check "$bind" "present" "F1 b3: a skill's version is bound to its content (content_sha256 recorded)"

# --- F1 b4: lessons can propose skill updates through governed promotion ----------------------------
# a project lesson (the only kind ordinary work produces) reaching a skill update through governed promotion
T=$(g orchestrator task create --class documentation --objective "produce a lesson" --allowed "product/**" | jget "r['id']")
g orchestrator task status "$T" READY >/dev/null; g orchestrator task claim "$T" >/dev/null
H=$(g orchestrator handoff create --to-role backend-engineer --task "$T" | jget "r['id']")
python3 - "$T" "$LAB/f1ret.json" <<'PY2'
import json,sys
json.dump({"task":sys.argv[1],"status":"success","work_completed":"x","files_changed":[],"evidence":["x"],
 "tests":{"status":"not_applicable_with_reason","reason":"documentation"},"discoveries":[],"risks":[],
 "lessons":["SKL-TASK-CLOSE should also require the consumption receipt"],"proposed_decisions":[],
 "unresolved":[],"recommended_next_action":"promote the lesson"}, open(sys.argv[2],"w"))
PY2
g backend-engineer handoff return "$H" --file "$LAB/f1ret.json" >/dev/null
L=$(python3 -c "
import glob,os
f=sorted(glob.glob('$PROJ/spec/lessons/L-*.yaml'))
print(os.path.basename(f[-1])[:-5] if f else 'none')")
up=$(g orchestrator upstream prepare "$L" | jget "'ok' if d.get('ok') else d['error']['code']")
skillprop=$(python3 -c "
import json
d=json.load(open('$PROJ/governance/kernel/schemas/framework-change-proposal.schema.json'))['properties']
print('skill-target' if any('skill' in k.lower() for k in d) else 'no-skill-target')")
if [ "$up" = "ok" ] && [ "$skillprop" = "skill-target" ]; then
  ok "F1 b4: a lesson from ordinary work reaches a governed promotion that can target a skill"
else
  bad "F1 b4: a lesson from ordinary work cannot propose a skill update through governed promotion (upstream prepare -> $up; framework-change-proposal -> $skillprop; no skill-promotion operation exists)"
fi

# --- F2: the Tool Capability Registry's eight fields -------------------------------------------------
f2=$(python3 -c "
import json
d=json.load(open('$PROJ/governance/generated/tool-registry.json'))
t=[x for x in d['tools'] if x.get('tool_id')=='TOOL-GIT-001'][0]
sch=json.load(open('$PROJ/governance/kernel/schemas/tool.schema.json'))['properties']
def has(*ks): return all(k in t or k in sch for k in ks)
rows=[('identity/version', has('tool_id','version')),
      ('executable/transport', has('type')),
      ('permissions', has('permissions')),
      ('allowed roles', has('approved_roles')),
      ('allowed task classes', 'task_classes' in sch or 'task_classes' in t),
      ('sensitivity', 'sensitivity' in sch or 'credential_scope' in sch),
      ('network scope', 'permissions' in sch),
      ('filesystem scope', 'filesystem_scope' in sch or 'path_scope' in sch),
      ('health status', has('health_check')),
      ('provenance', 'source' in sch or 'package' in sch),
      ('hash pin', 'installation_sha256' in sch or 'pin_sha256' in sch),
      ('installation/approval status', 'approval' in sch and 'status' in sch)]
print(';'.join('%s=%s'%(k,'yes' if v else 'NO') for k,v in rows))")
echo "    F2 registry fields: $f2"
for field in "identity/version" "executable/transport" "permissions" "allowed roles" "health status" "provenance" "hash pin" "installation/approval status"; do
  case "$f2" in *"$field=yes"*) ok "F2: the registry records $field";; *) bad "F2: the registry does not record $field";; esac
done
case "$f2" in *"allowed task classes=yes"*) ok "F2 b4: the registry scopes a tool to task classes";;
  *) bad "F2 b4: the registry records allowed ROLES but no task-class scoping, although TOOL_POLICY.mcp.scope declares role_and_task";; esac
case "$f2" in *"filesystem scope=yes"*) ok "F2 b5: the registry records a filesystem scope";;
  *) bad "F2 b5: the registry records no filesystem scope for a tool (only a repo_write boolean)";; esac
# health status is live, not declared
hl=$(g orchestrator tools health | jget "str(len(r))")
echo "    tools health rows: $hl"

# --- F5: MCP/tools = action, A2A = communication, Knowledge Fabric = knowing -------------------------
mcp=$(g orchestrator tools registry | python3 -c "
import sys,json; d=json.load(sys.stdin); r=d.get('result',d)
s=r.get('mcp_servers') or []
print(','.join('%s:%s'%(x.get('id'),x.get('status')) for x in s) or 'none')")
echo "    MCP registry: $mcp"
case "$mcp" in *":planned"*) ok "F5 b1/b4: the deferred MCP transport is registered as 'planned', never silently substituted (D-0004)";;
  *) bad "F5: the MCP layer's state is not explicit ($mcp)";; esac
gap=$(g orchestrator doctor | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
txt=json.dumps(r)
print('reported' if 'MCP' in txt or 'mcp' in txt else 'silent')")
check "$gap" "reported" "F5 b4: doctor reports the deferred MCP layer rather than passing over it"
# A2A carries communication only: a handoff's authority cannot exceed its task's
au=$(python3 -c "
import json
d=json.load(open('$PROJ/governance/kernel/schemas/handoff.schema.json'))
print('present' if 'authority' in (d.get('required') or []) else 'absent')")
check "$au" "present" "F5 b2: an A2A handoff always carries an explicit authority envelope"
kf=$(g orchestrator context compile "$T" 2>/dev/null | jget "'separate' if 'retrieved_intelligence' in r and 'deterministic_authority' in r else 'merged'")
check "$kf" "separate" "F5 b3/b4: the Knowledge Fabric's retrieved material is kept separate from deterministic authority in a context packet"

# --- OD-P2-03 requirement 2: is the AUTHORISED side of the envelope trusted OS state? ---------------
RPT=$(security_review TL-ENV 2.0.0)
descriptor "$LAB/env.yaml" "$RPT" '{"tool_id":"TL-ENV","version_pin":"2.0.0","required_permission_classes":["READ_REPO","DB_WRITE"]}'
envverdict() { GOV_SESSION="env-$RANDOM" g tooling-engineer tools install --descriptor "$LAB/env.yaml" | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d); cc=r.get('change_class',{}); e=cc.get('authority_envelope',{})
print('%s|%s|%s' % (e.get('expands_authority'), ','.join(e.get('triggers_fired') or []) or '-', cc.get('branch')))"; }
before=$(envverdict)
check "${before%%|*}" "True" "OD-P2-03: an installation demanding a class the role does not hold expands authority ($before)"
# now widen the envelope by writing the project overlay directly — no gov command, no change transaction
python3 - "$PROJ/governance/project/TOOL_PERMISSIONS.yaml" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["roles"]["tooling-engineer"] = sorted(set(d["roles"]["tooling-engineer"]) | {"DB_WRITE"})
yaml.safe_dump(d, open(p, "w"))
PY
after=$(envverdict)
echo "    envelope verdict before=$before after=$after"
if [ "${after%%|*}" = "False" ]; then
  bad "OD-P2-03 req 2: a hand edit of governance/project/TOOL_PERMISSIONS.yaml (no gov command, no change transaction, no gate) enlarged the authorised envelope: the same installation stopped being an authority expansion ($before -> $after)"
else
  ok "OD-P2-03 req 2: a hand edit of the envelope source does not enlarge the authorised envelope ($after)"
fi
det=$(g orchestrator audit | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
t=json.dumps(r.get('findings',[]))
print('detected' if 'TOOL_PERMISSIONS' in t else 'silent')")
check "$det" "detected" "OD-P2-03 req 2: the governance suite reports an out-of-band edit of an envelope source"
summary
