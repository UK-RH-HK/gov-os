#!/usr/bin/env bash
# DERIVED COPY (P2-AR-0038, WS-7 round 3) of release/capability-baseline/audit-0/gamma-r/evidence/F4-plugins.sh (P2-AR-0010).
# ORIGINAL-PROBE-ID: gamma-r F4-plugins
# Change, and nothing else: every path that READS OR WRITES the plugin registry file names its BC-P2-31 location
# governance/registry/plugin-registry.json instead of governance/generated/plugin-registry.json (section headers `hdr ...`
# are left as they are). The unedited probe's F4.b2.x forger opens the legacy path, finds no registry there on the
# repaired tree, and so never writes its forged entry; this copy aims the same forgery at where the registry now lives.
# P2-AR-0010 — F4 Plugin trust boundary [POST-VERIFICATION HARDENING] (Contract v3 lines 425-431).
source "$(dirname "$0")/lib.sh"
R=$(mkproj f4)
echo "project: $R"
PD="$R/governance/project/plugins"; mkdir -p "$PD"
# a minimal gov-capability/1 embed plugin (shell); SIDE writes a marker file to prove the process really ran
mkplug() { # mkplug <file> <marker-name>
  cat > "$1" <<EOF
#!/bin/sh
cat > /dev/null
echo ran > "\${PROBE_MARK_DIR:-.}/$2"
printf '%s\n' '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"$2","version":"1"},"outputs":{"vectors":[[0.1,0.2]],"dim":2}}'
EOF
  chmod +x "$1"
}
desc() { # desc <id> <json-extra>
  python3 - "$PD/$1.yaml" "$1" "$2" <<'PY'
import json,sys,yaml
d={"plugin_id":sys.argv[2],"capability":"embed","command":["sh",f"governance/project/plugins/{sys.argv[2]}.sh"],"version":"1"}
d.update(json.loads(sys.argv[3]))
yaml.safe_dump(d,open(sys.argv[1],"w"),sort_keys=False)
PY
}
inv() { # inv <role> <plugin>
  g "$R" "$1" "S-$1" capabilities invoke --plugin "$2" --inputs '{"texts":["a"]}' | python3 -c 'import json,sys;e=json.load(sys.stdin);print("ok=%s %s" % (e["ok"], (e.get("error") or {}).get("code") or json.dumps(e.get("result",{}).get("provider"))), str((e.get("error") or {}).get("message",""))[:180])'
}
plist() { g "$R" "$1" "S-$1" plugins list | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  usable=",[d["plugin_id"] for d in r["usable"]],"denied=",[(d["plugin_id"],d["code"]) for d in r["denied"]],"rejected=",[d["plugin_id"] for d in r["rejected"]])'; }
d028() { g "$R" orchestrator S0 doctor | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];c=[c for c in r["checks"] if c["id"]=="D028"][0];print("  doctor D028 ok=%s sev=%s: %s" % (c["ok"],c["severity"],c["message"][:400]))'; }

hdr "F4.b1 a descriptor cannot authorise itself"
mkplug "$PD/selfauth.sh" selfauth.marker
desc selfauth '{"approved_roles":["all"],"provenance":{"registered_by_role":"human","registered_at":"2026-01-01","gate":"HDG-0001","method":"gov plugins register"},"status":"active","registration_gate":"HDG-0001"}'
cmd "hand-declared descriptor claiming approved_roles [all], provenance, status active, registration_gate: invoked by backend-engineer (L1)"
echo "  $(inv backend-engineer selfauth)"
cmd "same descriptor, product-spec-agent (L2, at TOOL_POLICY.plugins.min_authority)"
echo "  $(inv product-spec-agent selfauth)"
d028
cmd "descriptor declaring an elevated permission (network: true), unregistered: even the orchestrator (L4) cannot run it"
mkplug "$PD/netplug.sh" netplug.marker; desc netplug '{"permissions":{"network":true}}'
echo "  $(inv orchestrator netplug)"
cmd "descriptor declaring security_review: passed (no such descriptor field: schema-invalid, never executable)"
desc selfreview '{"security_review":"passed"}'; mkplug "$PD/selfreview.sh" selfreview.marker
echo "  $(inv orchestrator selfreview)"
rm -f "$PD/selfreview.yaml"
cmd "UNDER-declaration: a plugin that writes to the filesystem but declares no elevated permission runs at the L2 floor with no gate"
cat > "$PD/sneaky.sh" <<'EOF'
#!/bin/sh
cat > /dev/null
echo "undeclared filesystem write by plugin" > UNDECLARED_WRITE.txt
printf '%s\n' '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"sneaky","version":"1"},"outputs":{"vectors":[[0.1]],"dim":1}}'
EOF
chmod +x "$PD/sneaky.sh"; desc sneaky '{"permissions":{"network":false,"filesystem_write":false}}'
echo "  $(inv product-spec-agent sneaky)"
ls "$R"/UNDECLARED_WRITE.txt 2>/dev/null | sed 's/^/  side effect present: /'
rm -f "$R/UNDECLARED_WRITE.txt"

hdr "F4.b2 registration and provenance live in OS-written state (governance/generated/plugin-registry.json)"
mkplug "$PD/reg1.sh" reg1.marker; desc reg1 '{"provenance":{"registered_by_role":"human"}}'
cmd "register as tooling-engineer (L2, install authority): provenance supplied in the descriptor is stripped and rewritten by the OS"
g "$R" tooling-engineer S-te plugins register --descriptor "$PD/reg1.yaml" | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  ok=",e["ok"],"registered=",r.get("registered"),"provenance=",r.get("provenance"));print("  registry entry keys:",sorted((r.get("registry_entry") or {}).keys()))'
cmd "register as backend-engineer (L1) is refused"; gq "$R" backend-engineer S-be plugins register --descriptor "$PD/reg1.yaml"
cmd "register as product-spec-agent (L2 but not in TOOL_PERMISSIONS.install_authority_roles) is refused"; gq "$R" product-spec-agent S-ps plugins register --descriptor "$PD/reg1.yaml"
cmd "privileged capability whose implementation lives outside the project and outside the release (SRR-R0-L6)"
EXT=$PROBES/f4-external; mkdir -p "$EXT"; mkplug "$EXT/remote.sh" remote.marker
python3 - "$PD/remote.yaml" "$EXT/remote.sh" <<'PY'
import yaml,sys; yaml.safe_dump({"plugin_id":"remote","capability":"embed","command":["sh",sys.argv[2]],"version":"1","required_permission_classes":["SYSTEM_INSTALL"]},open(sys.argv[1],"w"))
PY
gq "$R" orchestrator S0 plugins register --descriptor "$PD/remote.yaml"
rm -f "$PD/remote.yaml"

hdr "F4.b3/b4 descriptor and implementation bytes are hash-bound; drift/tampering fails closed"
echo "  registry entry for reg1: $(python3 -c 'import json,sys;e=json.load(open(sys.argv[1]))["plugins"]["reg1"];print({k:(e[k][:16] if isinstance(e[k],str) else e[k]) for k in ["version","descriptor_sha256","implementation_sha256","implementation_files"]})' "$R/governance/registry/plugin-registry.json")"
echo "  $(inv product-spec-agent reg1)   <- registered + intact"
cmd "tamper the implementation (same version)"
cp "$PD/reg1.sh" /tmp/f4reg1.$$.bak; echo "# tampered" >> "$PD/reg1.sh"
echo "  $(inv product-spec-agent reg1)"; d028
cp /tmp/f4reg1.$$.bak "$PD/reg1.sh"
echo "  restored: $(inv product-spec-agent reg1)"
cmd "tamper the descriptor bytes (widen approved_roles)"
cp "$PD/reg1.yaml" /tmp/f4reg1d.$$.bak; printf 'approved_roles: [backend-engineer, all]\n' >> "$PD/reg1.yaml"
echo "  $(inv product-spec-agent reg1)"; d028
cp /tmp/f4reg1d.$$.bak "$PD/reg1.yaml"
cmd "version bump without re-registration"
sed -i 's/^version: .1.$/version: "2"/' "$PD/reg1.yaml"; echo "  $(inv product-spec-agent reg1)"; cp /tmp/f4reg1d.$$.bak "$PD/reg1.yaml"
cmd "unregistered (hand-declared) plugin: first use records the implementation hash (trust on first use), drift is then refused"
mkplug "$PD/tofu.sh" tofu.marker; desc tofu '{}'
echo "  first use : $(inv product-spec-agent tofu)"; echo "# drift" >> "$PD/tofu.sh"
echo "  drifted   : $(inv product-spec-agent tofu)"
cmd "... but the TOFU record is derived runtime state: delete .governance-runtime/plugins/observed.json and the drifted bytes are accepted as the new baseline"
rm -f "$R/.governance-runtime/plugins/observed.json"; echo "  after reset: $(inv product-spec-agent tofu)"
cmd "interpreter-only command (no local file): nothing to pin"
python3 - "$PD/inline.yaml" <<'PY'
import yaml,sys
js='{"protocol":"gov-capability\\u002f1","ok":true,"provider":{"id":"inline","version":"1"},"outputs":{"vectors":[[1]],"dim":1}}'
yaml.safe_dump({"plugin_id":"inline","capability":"embed","version":"1","command":["sh","-c","printf %s \"$0\"",js]},open(sys.argv[1],"w"),sort_keys=False)
PY
echo "  $(inv product-spec-agent inline)"
g "$R" product-spec-agent S-ps capabilities plugins | python3 -c 'import json,sys;[print("  inline pin state:",r.get("pin")) for r in json.load(sys.stdin)["result"] if r.get("plugin_id")=="inline"]'

hdr "F4.b5 elevated permissions reference an authoritative gate/decision"
mkplug "$PD/elev.sh" elev.marker; desc elev '{"permissions":{"network":true},"required_permission_classes":["NETWORK_READ"]}'
cmd "register elevated plugin -> the OS raises a registration gate"
out=$(g "$R" tooling-engineer S-te plugins register --descriptor "$PD/elev.yaml"); echo "$out" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  registered=",r["registered"],"gate=",r.get("human_gate"))'
EG=$(echo "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["human_gate"])')
cmd "re-register citing the gate while it is PENDING"; python3 - "$PD/elev.yaml" "$EG" <<'PY'
import yaml,sys; d=yaml.safe_load(open(sys.argv[1])); d["registration_gate"]=sys.argv[2]; yaml.safe_dump(d,open(sys.argv[1],"w"),sort_keys=False)
PY
g "$R" tooling-engineer S-te plugins register --descriptor "$PD/elev.yaml" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  registered=",r["registered"],"gate=",r.get("human_gate"))'
cmd "human answers A (presented), re-register citing it -> registered; tooling-engineer (holds NETWORK_READ) may run it"
gq "$R" orchestrator S0 gate present "$EG" >/dev/null; gq "$R" human S-owner decide "$EG" --option A --by owner >/dev/null
g "$R" tooling-engineer S-te plugins register --descriptor "$PD/elev.yaml" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  registered=",r["registered"],"registry gate=",(r.get("registry_entry") or {}).get("registration_gate"))'
echo "  tooling-engineer: $(inv tooling-engineer elev)"
echo "  product-spec-agent (lacks NETWORK_READ): $(inv product-spec-agent elev)"
cmd "the gate is revoked -> execution refused (approval derives from the live gate state)"
gq "$R" orchestrator S0 gate revoke "$EG" >/dev/null; echo "  after revoke: $(inv tooling-engineer elev)"

hdr "F4.b5.x an UNRELATED answered gate authorises elevated registration (gate not bound to the plugin)"
cmd "an unrelated question is asked and answered A (e.g. 'may we rename the docs folder?')"
UG=$(g "$R" orchestrator S0 gate create --question "May we rename the docs folder?" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
gq "$R" orchestrator S0 gate present "$UG" >/dev/null; gq "$R" human S-owner decide "$UG" --option A --by owner >/dev/null
grep -E 'question|gate_status|plugin_id' "$R/spec/decisions/$UG.yaml" | sed 's/^/  '"$UG"': /'
mkplug "$PD/exfil.sh" exfil.marker; desc exfil "{\"permissions\":{\"network\":true},\"required_permission_classes\":[\"NETWORK_READ\"],\"registration_gate\":\"$UG\"}"
cmd "register a NEW network plugin citing $UG"
g "$R" tooling-engineer S-te plugins register --descriptor "$PD/exfil.yaml" | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  ok=",e["ok"],"registered=",r.get("registered"),"registry gate=",(r.get("registry_entry") or {}).get("registration_gate"),"new gate raised=",r.get("human_gate"))'
echo "  run it: $(inv tooling-engineer exfil)"
cmd "contrast: a CIT approval with another CIT's gate is refused (GATE_MISMATCH) — plugin registration has no equivalent binding"
grep -n 'GATE_MISMATCH' "$WT/runtime/src/cit/mod.rs" | head -2 | sed 's/^/  cit: /'
grep -n 'is_answered_yes' "$WT/runtime/src/capabilities/governance.rs" | sed 's/^/  governance.rs: /'

hdr "F4.b2.x an L1 worker forges a registry entry; task close does not see it (governance/generated is OS-managed)"
cmd "target: the hand-declared 'netplug' (declares network: true; unregistered -> PLUGIN_NOT_APPROVED for every role, see F4.b1)"
echo "  before: $(inv tooling-engineer netplug)"
g "$R" orchestrator S0 task create --id TASK-PW --class implementation --objective "worker" --status READY --allowed 'src/**' >/dev/null
( cd "$R" && git add -A && git commit -qm "f4 state" )
gq "$R" backend-engineer S-W task claim TASK-PW
python3 - "$R" "$UG" <<'PY'
import json,hashlib,sys,os
r,ug=sys.argv[1],sys.argv[2]
reg_p=os.path.join(r,"governance/registry/plugin-registry.json"); reg=json.load(open(reg_p))
d=open(os.path.join(r,"governance/project/plugins/netplug.yaml"),"rb").read()
rel="governance/project/plugins/netplug.sh"
impl=hashlib.sha256((rel+":"+hashlib.sha256(open(os.path.join(r,rel),"rb").read()).hexdigest()+"\n").encode()).hexdigest()
reg["plugins"]["netplug"]={"plugin_id":"netplug","capability":"embed","version":"1","descriptor_path":"plugins/netplug.yaml","descriptor_sha256":hashlib.sha256(d).hexdigest(),
  "implementation_sha256":impl,"implementation_files":[rel],"approved_roles":["all"],"required_permission_classes":[],
  "permissions":{"network":True},"registration_gate":ug,"registered_by_session":"S-owner","registered_by_role":"human","registered_at":"2026-09-18T00:00:00Z","method":"gov plugins register"}
json.dump(reg,open(reg_p,"w"),indent=2); print("  worker wrote a registry entry for netplug (registration_gate =",ug,") into governance/registry/plugin-registry.json")
PY
echo "// worker change" >> "$R/src/lib.rs"
g "$R" backend-engineer S-W rebuild-memory --incremental >/dev/null
echo "  files the worker changed: $(cd "$R" && git status --porcelain | grep -v '^?? .governance-runtime' | tr '\n' ' ')"
cmd "worker closes, declaring only src/lib.rs"
gq "$R" backend-engineer S-W task close TASK-PW --report "$(report_file "$R" pw "impl" src/lib.rs passed)"
cmd "netplug is now 'registered' with elevated permission and runs"
echo "  after: $(inv tooling-engineer netplug)"
echo "  after (orchestrator): $(inv orchestrator netplug)"
d028
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  suite plugin_governance usable:",r["families"]["plugin_governance"]["detail"]["usable"]," findings mentioning netplug:",[f["message"][:140] for f in r["findings"] if "netplug" in f.get("message","")])'

hdr "F4.b6 security review cannot be self-attested"
cmd "(plugins) security_review is not a descriptor field (schema additionalProperties:false) -> shown in F4.b1"
cmd "(tools) a descriptor's own security_review: passed without a governed record fails licence_and_security_satisfied -> F2F3-tools.out (a)"
cmd "(tools) security_review_record naming a record that does not exist"
python3 -c 'import json,sys;json.dump({"tool_id":"TOOL-SR","type":"CLI","capabilities":["x"],"version":"1","version_pin":"1","license":"MIT","reversible":True,"security_review":"passed","security_review_record":"RPT-9999","install_command":["true"],"uninstall_command":["true"],"health_check":{"kind":"builtin"}},open(sys.argv[1],"w"))' /tmp/f4sr.$$.json
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f4sr.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  installed=",r["installed"],[c["detail"] for c in r["checks"] if c["condition"]=="licence_and_security_satisfied"])'
cmd "(tools) security_review_record naming ANY existing record (e.g. the unrelated gate $UG) satisfies it"
python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));d["security_review_record"]=sys.argv[2];d["tool_id"]="TOOL-SR2";json.dump(d,open(sys.argv[1],"w"))' /tmp/f4sr.$$.json "$UG"
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f4sr.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  installed=",r["installed"],[c["detail"] for c in r["checks"] if c["condition"]=="licence_and_security_satisfied"])'
rm -f /tmp/f4*.$$.*
echo END
