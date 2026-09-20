#!/usr/bin/env bash
# Gamma held-out probe: F4 plugin trust boundary, bullet by bullet (Contract v3 :425-431), plus
# D-0010 (hand-declared descriptors) and registration inside a claimed task (round-4 INT3-O1).
#   b1 Descriptor cannot authorise itself
#   b2 Registration/provenance live in trusted OS state
#   b3 Descriptor/implementation bytes are hash-bound
#   b4 Drift/tampering fails closed
#   b5 Elevated permissions reference authoritative gate/decision
#   b6 Security review cannot be self-attested
. "$(dirname "$0")/lib.sh"
newproj f4plug --provision >/dev/null
mkdir -p "$PROJ/governance/project/plugins" "$PROJ/product/plug"
cat > "$PROJ/product/plug/impl.py" <<'PY'
import sys, json
for line in sys.stdin:
    r = json.loads(line)
    print(json.dumps({"protocol": "gov-capability/1", "ok": True,
                      "request_id": r.get("request_id"), "outputs": {"echo": r.get("inputs")}}))
    sys.stdout.flush()
PY
writedesc() { python3 - "$1" "$2" <<'PY'
import sys, json, yaml
out, patch = sys.argv[1], json.loads(sys.argv[2])
d = {"plugin_id":"plg-echo","capability":"embed","version":"1.0.0",
     "command":["python3","product/plug/impl.py"],"approved_roles":["all"],
     "required_permission_classes":[],"permissions":{"network":False,"filesystem_write":False},
     "provenance":{"origin":"trusted vendor","signed":True,"security_review":"passed"},
     "status":"active","health_check":{"kind":"command","command":["python3","-c","print(1)"]}}
d.update(patch); yaml.safe_dump(d, open(out,"w"))
PY
}
DESC="$PROJ/governance/project/plugins/plg-echo.yaml"

# --- b1: a descriptor cannot authorise itself ------------------------------------------------------
# It declares approved_roles: all, provenance signed, a passed security review and status active.
writedesc "$DESC" '{}'
inv=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null \
      | jget "d['error']['code'] if not d.get('ok') else 'RAN'")
case "$inv" in
  PLUGIN_NOT_APPROVED|PLUGIN_REGISTRATION_UNBOUND|PLUGIN_NOT_AUTHORIZED)
     ok "F4 b1: a hand-declared, self-attested executable plugin does not run ($inv)";;
  RAN) bad "F4 b1: a hand-declared descriptor authorised its own execution";;
  *)   bad "F4 b1: unexpected outcome '$inv'";;
esac
st=$(g orchestrator tools registry | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
e=[t for t in r.get('tools',[]) if t.get('tool_id')=='plg-echo' or t.get('plugin_id')=='plg-echo']
print(e[0].get('status') if e else 'absent')")
check "$st" "unregistered" "F4 b1: the tool-registry view reports the self-declared plugin as unregistered, not active/approved"
ign=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
cl=[]
def walk(x):
    if isinstance(x,dict):
        cl.extend(x.get('descriptor_claims_ignored') or [])
        cl.extend(x.get('ignored_descriptor_claims') or [])
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(d.get('error'))
print(' | '.join(sorted(set(cl))) or 'none')")
echo "    descriptor claims the OS records as ignored: $ign"

# --- b2: registration and provenance live in trusted OS state --------------------------------------
reg=$(g orchestrator plugins registry | jget "r.get('read_from') or r.get('location')")
case "$reg" in
  *governance/registry/plugin-registry.json) ok "F4 b2: the registry is OS state at $reg (not a generated view)";;
  *) bad "F4 b2: unexpected registry location '$reg'";;
esac
# a hand-written registry entry is a request, not a registration
mkdir -p "$PROJ/governance/registry"
python3 - "$PROJ/governance/registry/plugin-registry.json" <<'PY'
import json, os, sys, hashlib
p = sys.argv[1]
doc = json.load(open(p)) if os.path.exists(p) else {"schema_version": 1, "plugins": {}}
doc.setdefault("plugins", {})["plg-echo"] = {
  "plugin_id":"plg-echo","version":"1.0.0","status":"REGISTERED","approved_roles":["all"],
  "required_permission_classes":[],"descriptor_sha256":"0"*64,"implementation_sha256":"0"*64,
  "registration_subject_sha256":"0"*64,"registration_gate":"HDG-9999"}
json.dump(doc, open(p,"w"), indent=1)
PY
forged=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null | jget "d['error']['code'] if not d.get('ok') else 'RAN'")
case "$forged" in
  PLUGIN_REGISTRATION_UNBOUND|PLUGIN_REGISTRY_MISMATCH|PLUGIN_NOT_APPROVED|PLUGIN_PIN_MISMATCH)
     ok "F4 b2: a hand-written registry entry is refused ($forged)";;
  RAN) bad "F4 b2: a forged registry entry ran an unapproved plugin";;
  *) bad "F4 b2: unexpected outcome '$forged'";;
esac
mv "$PROJ/governance/registry/plugin-registry.json" "$LAB/forged-registry.json"

# --- register it properly, inside a CLAIMED task (round-4 INT3-O1) ---------------------------------
TASK=$(g orchestrator task create --class tooling --objective "register the echo capability plugin" --allowed "governance/registry/**,governance/project/plugins/**,governance/generated/**" | jget "r['id']")
g orchestrator task status "$TASK" READY >/dev/null
g orchestrator task claim "$TASK" >/dev/null
reg1=$(g tooling-engineer plugins register --descriptor "$DESC")
GATE=$(printf '%s' "$reg1" | jget "r.get('human_gate') or (r.get('registration') or {}).get('human_gate') or 'none'")
CIT=$(printf '%s' "$reg1" | jget "(r.get('change_transaction') or {}).get('cit') or 'none'")
if [ "$GATE" != "none" ]; then ok "F4 b5: registering an executable plugin raises a Human Decision Gate ($GATE) and a change transaction ($CIT)"
else bad "F4 b5: registration raised no gate (result: $(printf '%s' "$reg1" | head -c 300))"; fi
# the registration gate and the change transaction's gate are separate answers
CGATE=$(printf '%s' "$reg1" | jget "(r.get('change_transaction') or {}).get('human_gate') or 'none'")
echo "    registration gate=$GATE change-transaction gate=$CGATE"
answer_gate orchestrator "$GATE" A >/dev/null 2>&1
[ "$CGATE" != "none" ] && answer_gate orchestrator "$CGATE" A >/dev/null 2>&1
reg2=$(g tooling-engineer plugins register --descriptor "$DESC")
registered=$(printf '%s' "$reg2" | jget "str(r.get('registered'))")
echo "    second register -> registered=$registered"
inv2=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null \
       | jget "'RAN' if d.get('ok') else d['error']['code']")
check "$inv2" "RAN" "F4 b5: after the owner answered the gate raised for exactly this registration, the plugin runs"

# K3 impact simulation and the F4 gate both hold for a registration made inside a claimed task
closed=$(g orchestrator task show "$TASK" | jget "r.get('task_status')")
echo "    task $TASK status after registration: $closed"

# --- b3/b4: implementation bytes are hash-bound and drift fails closed ------------------------------
e=$(python3 -c "
import json;d=json.load(open('$PROJ/governance/registry/plugin-registry.json'))['plugins']['plg-echo']
print('%s|%s|%s|%s' % (d.get('descriptor_sha256','')[:8], d.get('implementation_sha256','')[:8],
                       d.get('registration_subject_sha256','')[:8], d.get('registration_gate')))")
case "$e" in
  *"|"*"|"*"|HDG-"*) ok "F4 b3: the registration binds descriptor, implementation, subject and gate ($e)";;
  *) bad "F4 b3: the registration does not bind every required element ($e)";;
esac
imp=$(python3 -c "
import json;print(json.load(open('$PROJ/governance/registry/plugin-registry.json'))['plugins']['plg-echo'].get('implementation_sha256') or 'NULL')")
case "$imp" in NULL|"") bad "F4 b3: the implementation hash is null (BC-P2-40)";; *) ok "F4 b3: implementation_sha256 is bound (${imp:0:12}…)";; esac

printf '\n# drift\n' >> "$PROJ/product/plug/impl.py"
drift=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null \
        | jget "'RAN' if d.get('ok') else d['error']['code']")
check "$drift" "PLUGIN_PIN_MISMATCH" "F4 b4: a changed implementation byte fails closed"
git -C "$PROJ" checkout -- product/plug/impl.py 2>/dev/null || python3 -c "
s=open('$PROJ/product/plug/impl.py').read().replace('\n# drift\n','');open('$PROJ/product/plug/impl.py','w').write(s)"
# descriptor drift
python3 - "$DESC" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1])); d["approved_roles"] = ["all", "independent-auditor"]
yaml.safe_dump(d, open(sys.argv[1], "w"))
PY
ddrift=$(g orchestrator capabilities invoke --plugin plg-echo --inputs '{}' 2>/dev/null | jget "'RAN' if d.get('ok') else d['error']['code']")
case "$ddrift" in
  PLUGIN_REGISTRY_MISMATCH|PLUGIN_NOT_APPROVED|PLUGIN_PIN_MISMATCH) ok "F4 b4: an edited descriptor no longer matches its registration ($ddrift)";;
  RAN) bad "F4 b4: an edited descriptor still ran under the old approval";;
  *) bad "F4 b4: unexpected outcome '$ddrift'";;
esac

# --- b3 (module form): the BC-P2-40 case — an interpreter/module command --------------------------
writedesc "$LAB/mod.yaml" '{"plugin_id":"plg-mod","command":["python3","-m","plugmod"],"cwd":"product"}'
mkdir -p "$PROJ/product/plugmod"
printf 'import sys,json\nfor l in sys.stdin:\n  r=json.loads(l); print(json.dumps({"protocol":"gov-capability/1","ok":True,"request_id":r.get("request_id"),"outputs":{}})); sys.stdout.flush()\n' > "$PROJ/product/plugmod/__main__.py"
cp "$LAB/mod.yaml" "$PROJ/governance/project/plugins/plg-mod.yaml"
rm3=$(g tooling-engineer plugins register --descriptor "$PROJ/governance/project/plugins/plg-mod.yaml")
G3=$(printf '%s' "$rm3" | jget "r.get('human_gate') or 'none'")
C3=$(printf '%s' "$rm3" | jget "(r.get('change_transaction') or {}).get('human_gate') or 'none'")
[ "$G3" != "none" ] && answer_gate orchestrator "$G3" A >/dev/null 2>&1
[ "$C3" != "none" ] && answer_gate orchestrator "$C3" A >/dev/null 2>&1
g tooling-engineer plugins register --descriptor "$PROJ/governance/project/plugins/plg-mod.yaml" >/dev/null 2>&1
mimp=$(python3 -c "
import json,os
p='$PROJ/governance/registry/plugin-registry.json'
d=json.load(open(p))['plugins'].get('plg-mod') if os.path.exists(p) else None
print((d or {}).get('implementation_sha256') or 'NULL')")
case "$mimp" in
  NULL|"") bad "F4 b3 / BC-P2-40: a registered module-form plugin has NO implementation pin";;
  *) ok "F4 b3 / BC-P2-40: a module-form plugin's implementation is pinned (${mimp:0:12}…)";;
esac

# --- b6: a security review cannot be self-attested (plugin side) ------------------------------------
# The descriptor declares provenance.security_review: passed and provenance.signed: true. Those claims
# must never make the plugin approved; the OS must record that it ignored them.
case "$ign" in
  *security_review*|*provenance*|*approved_roles*) ok "F4 b6: the descriptor's own provenance / security-review claim is recorded as ignored ($ign)";;
  none) bad "F4 b6: the OS records no ignored descriptor claim for a descriptor that self-attests provenance and a passed security review";;
  *) bad "F4 b6: unexpected ignored-claims list ($ign)";;
esac
summary
