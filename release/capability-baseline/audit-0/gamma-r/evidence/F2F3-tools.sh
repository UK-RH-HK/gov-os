#!/usr/bin/env bash
# P2-AR-0010 — F2 Tool Capability Registry (Contract v3 lines 404-412) and F3 Missing-tool acquisition (414-423).
source "$(dirname "$0")/lib.sh"
R=$(mkproj f2f3)
echo "project: $R"

hdr "F2.0 the generated registry (governance/generated/tool-registry.json) — one entry per field group"
g "$R" orchestrator S0 tools registry > /tmp/f2reg.$$.json
python3 - /tmp/f2reg.$$.json <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))["result"]
print("  generated_from:", r["generated_from"])
print("  tools:", len(r["tools"]), " mcp_servers:", len(r["mcp_servers"]), " roles with exposure:", len(r["role_exposure"]))
keys = {
 "b1 identity/version":            ["tool_id","name","version"],
 "b2 executable/transport":        ["type","health_check","package","source"],
 "b3 permissions":                 ["permissions","required_permission_classes"],
 "b4 allowed roles/task classes":  ["approved_roles","task_classes","allowed_task_classes"],
 "b5 sensitivity/network/fs scope":["permissions","credential_scope","sensitivity","filesystem_scope","network_scope"],
 "b6 health status":               ["health_check","health","health_status"],
 "b7 provenance/hash pin":         ["provenance","pin","version_pin","sha256","hash"],
 "b8 installation/approval status":["status","installed_by","installed_at","approval","security_review","license_review"],
}
for b,ks in keys.items():
    present = {k: sum(1 for t in r["tools"] if k in t) for k in ks}
    print(f"  [{b}] entries carrying each key (of {len(r['tools'])}): {present}")
t=[x for x in r["tools"] if x["tool_id"]=="TOOL-GIT-001"][0]; print("  sample TOOL-GIT-001:", json.dumps(t))
m=r["mcp_servers"][0]; print("  sample MCP:", json.dumps(m))
print("  role_exposure[research-agent]:", r["role_exposure"]["research-agent"])
print("  role_exposure[independent-auditor]:", r["role_exposure"]["independent-auditor"])
PY

hdr "F2.b3/b4 exposure is computed from permissions + approved_roles (executable): resolve per role"
for role in research-agent orchestrator independent-auditor test-execution-agent; do
  printf '  %-22s run_tests -> ' "$role"; g "$R" "$role" S-$role tools resolve --capability run_tests | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print([t["tool_id"] for t in r["tools"]],"|",r["reason"])'
  printf '  %-22s git_commit -> ' "$role"; g "$R" "$role" S-$role tools resolve --capability git_commit | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print([t["tool_id"] for t in r["tools"]],"|",r["reason"])'
done
cmd "task-class scoping: is any tool restricted by task class? a task that requires a tool its class should not use"
g "$R" orchestrator S0 task create --id TASK-DOC --class documentation --objective "docs" --status READY --fields '{"required_tools":["TOOL-CARGO-002","TOOL-DOES-NOT-EXIST"]}' >/dev/null
g "$R" orchestrator S0 context compile TASK-DOC | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  context packet required_tools:",r["deterministic_authority"]["required_tools"])'
gq "$R" backend-engineer S-be task claim TASK-DOC
grep -n 'task_class' "$WT/runtime/src/tools.rs" | sed 's/^/  tools.rs: /'; echo "  (no match above = tool exposure never consults a task class)"

hdr "F2.b6 health status: executed per tool"
g "$R" orchestrator S0 tools health | python3 -c 'import json,sys;[print("  ",h) for h in json.load(sys.stdin)["result"]]'
cmd "is health status recorded in the registry?"; python3 -c 'import json,sys;r=json.load(open(sys.argv[1]))["result"];print("  any registry tool carrying a health result:",any(("health" in t and "ok" in json.dumps(t.get("health"))) for t in r["tools"]))' /tmp/f2reg.$$.json

hdr "F2.b7 provenance/hash pin: installed tools vs plugins"
python3 -c 'import json,sys;r=json.load(open(sys.argv[1]))["result"];[print("  %-18s version=%-8s version_pin=%-14s pin=%s" % (t["tool_id"],t.get("version"),t.get("version_pin"),t.get("pin"))) for t in r["tools"]]' /tmp/f2reg.$$.json

hdr "F3.b1 capability gap -> candidate discovery"
for cap in web_search code_intel quantum_compile; do printf '  resolve %-16s ' "$cap"; g "$R" tooling-engineer S-te tools resolve --capability $cap | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("gap=",r["capability_gap"],"reason=",r["reason"],"| candidates returned:",r["tools"],r["mcp_servers"],"| next:",r["next"][:60])'; done
cmd "does a gap create any governed record (task, gate, capability-memory entry)?"
before=$(ls "$R/spec/tasks" "$R/spec/decisions" 2>/dev/null | wc -l); g "$R" tooling-engineer S-te tools resolve --capability quantum_compile >/dev/null; after=$(ls "$R/spec/tasks" "$R/spec/decisions" 2>/dev/null | wc -l); echo "  governed record count before=$before after=$after"

hdr "F3.b2..b8 acquisition: auto-install conditions, approval, install, pin, register, health"
mkd() { python3 - "$@" <<'PY'
import json,sys
d={"tool_id":sys.argv[2],"name":sys.argv[2].lower(),"type":"CLI","capabilities":["quantum_compile"],"version":"1.0","version_pin":"1.0.0",
   "permissions":{"repo_write":False,"network":False},"required_permission_classes":["READ_REPO"],"license":"MIT","reversible":True,
   "security_review":"passed","cost_usd":0,"install_command":["true"],"uninstall_command":["true"],
   "health_check":{"kind":"command","command":["true"],"expect_exit":0}}
for kv in sys.argv[3:]:
    k,v=kv.split("=",1); d[k]=json.loads(v)
json.dump(d,open(sys.argv[1],"w"))
PY
}
cmd "(a) all conditions except the security evidence record: descriptor claims security_review: passed with no governed record"
mkd /tmp/f3a.$$.json TOOL-QC-A
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3a.$$.json > /tmp/f3a.out.$$.json
python3 -c 'import json,sys;r=json.load(open(sys.argv[1]))["result"];print("  installed=",r["installed"],"gate=",r.get("human_gate"));[print("    ",c["condition"],c["ok"],c["detail"][:90]) for c in r["checks"]]' /tmp/f3a.out.$$.json
GA=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result"]["human_gate"])' /tmp/f3a.out.$$.json)
cmd "(b) the human approves the install gate ($GA): present, decide A; then re-run the same install"
gq "$R" orchestrator S0 gate present "$GA"; gq "$R" human S-owner decide "$GA" --option A --by owner
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3a.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  after approval: installed=",r["installed"],"new gate=",r.get("human_gate"))'
python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));d["human_gate"]=sys.argv[2];d["registration_gate"]=sys.argv[2];json.dump(d,open(sys.argv[1],"w"))' /tmp/f3a.$$.json "$GA"
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3a.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  citing the answered gate in the descriptor: installed=",r["installed"],"new gate=",r.get("human_gate"))'
grep -n 'human_gate\|registration_gate\|is_answered\|answered_option' "$WT/runtime/src/tools.rs" | sed 's/^/  tools.rs: /'
echo "  (tools::install never reads an answered gate; an approved install can only proceed if the descriptor itself meets every automatic condition)"
cmd "(c) security evidence resolved through a governed record + all conditions -> autonomous install"
mkdir -p "$R/spec/reports"; printf '{"id":"RPT-0901","type":"report","title":"security review of qc tool","status":"ACTIVE","state_class":"EVIDENCE","task":"TASK-DOC","work_completed":"reviewed","outcome":"success"}\n' > "$R/spec/reports/RPT-0901.yaml"
mkd /tmp/f3c.$$.json TOOL-QC-C 'security_review_record="RPT-0901"'
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3c.$$.json --execute | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  installed=",r.get("installed"),"executed=",r.get("executed"),"exec=",r.get("exec_result"),"health=",r.get("health"),"registered_at=",r.get("registered_at"),(e.get("error") or {}).get("code"))'
g "$R" tooling-engineer S-te tools resolve --capability quantum_compile | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  resolve after install: tools=",[t["tool_id"] for t in r["tools"]],"gap=",r["capability_gap"])'
grep -E 'status|installed_by|installed_at|version_pin|approved_roles' "$R/governance/project/tools/TOOL-QC-C.yaml" | sed 's/^/  record: /'
cmd "(d) cost over budget / licence not approved / irreversible / privilege escalation / no version pin -> each fails its condition and raises a gate"
for kv in 'cost_usd=500' 'license="GPL-3.0"' 'reversible=false' 'required_permission_classes=["SECRET_READ"]' 'version_pin=""' 'uninstall_command=[]'; do
  mkd /tmp/f3d.$$.json TOOL-QC-D 'security_review_record="RPT-0901"' "$kv"
  printf '  %-40s ' "$kv"; g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3d.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("installed=",r["installed"],"gate=",r.get("human_gate"),"failed=",[c["condition"] for c in r["checks"] if not c["ok"]])'
done
cmd "is 'maintenance' reviewed anywhere? (conditions evaluated)"; python3 -c 'import json,sys;print("  ",[c["condition"] for c in json.load(open(sys.argv[1]))["result"]["checks"]])' /tmp/f3a.out.$$.json
cmd "(e) health test after install: a tool whose health check FAILS"
mkd /tmp/f3e.$$.json TOOL-QC-E 'security_review_record="RPT-0901"' 'health_check={"kind":"command","command":["false"],"expect_exit":0}'
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3e.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  installed=",r["installed"],"health=",r.get("health"))'
g "$R" tooling-engineer S-te tools resolve --capability quantum_compile | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  resolve still offers:",[t["tool_id"] for t in r["tools"]])'
grep -E '^status' "$R/governance/project/tools/TOOL-QC-E.yaml" | sed 's/^/  TOOL-QC-E record /'
cmd "(f) install command fails -> nothing registered"
mkd /tmp/f3f.$$.json TOOL-QC-F 'security_review_record="RPT-0901"' 'install_command=["false"]'
gq "$R" tooling-engineer S-te tools install --descriptor /tmp/f3f.$$.json --execute; ls "$R/governance/project/tools/" | sed 's/^/  tools dir: /'
cmd "(g) install without --execute: registered as active although install_command never ran"
mkd /tmp/f3g.$$.json TOOL-QC-G 'security_review_record="RPT-0901"' 'install_command=["sh","-c","exit 9"]'
g "$R" tooling-engineer S-te tools install --descriptor /tmp/f3g.$$.json | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  installed=",r["installed"],"executed=",r["executed"])'
cmd "(h) continue task: the missing-tool gap is not linked to any task (required_tools is never checked)"
g "$R" orchestrator S0 task create --id TASK-NEEDS-TOOL --class tooling --objective "needs TOOL-NOPE" --status READY --fields '{"required_tools":["TOOL-NOPE"]}' >/dev/null
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  TASK-NEEDS-TOOL runnable:", "TASK-NEEDS-TOOL" in r["runnable"])'
g "$R" orchestrator S0 continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  continue ->",r.get("task"),"skills gap:",r.get("skills",{}).get("capability_gap"))'
hdr "F2.b8.x approval standing shown by the generated registry for a HAND-DECLARED plugin that claims provenance in its own descriptor"
PD="$R/governance/project/plugins"; mkdir -p "$PD"
printf '#!/bin/sh\ncat >/dev/null\nprintf %%s\\\\n '"'"'{"protocol":"gov-capability/1","ok":true,"provider":{"id":"claimsreg","version":"1"},"outputs":{"vectors":[[1]],"dim":1}}'"'"'\n' > "$PD/claimsreg.sh"; chmod +x "$PD/claimsreg.sh"
printf 'plugin_id: claimsreg\ncapability: embed\ncommand: [sh, governance/project/plugins/claimsreg.sh]\nversion: "1"\nprovenance: {registered_at: "2026-01-01T00:00:00Z", registered_by_role: human, method: gov plugins register}\n' > "$PD/claimsreg.yaml"
g "$R" orchestrator S0 plugins registry | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  OS plugin registry has claimsreg:", "claimsreg" in r.get("plugins",{}))'
g "$R" orchestrator S0 tools registry | python3 -c '
import json,sys; r=json.load(sys.stdin)["result"]
e=[t for t in r["tools"] if t["tool_id"]=="claimsreg"][0]
print("  generated tool-registry entry: status=%s approved_roles=%s provenance=%s denied_for_acting_role=%s" % (e["status"],e["approved_roles"],e.get("provenance"),str(e.get("denied_for_acting_role"))[:60]))
print("  role_exposure lists claimsreg for:", sorted(k for k,v in r["role_exposure"].items() if "claimsreg" in v["tools"]))'
printf '  tools resolve --capability embed as backend-engineer (L1): '; g "$R" backend-engineer S-be tools resolve --capability embed | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print([t["tool_id"] for t in r["tools"]])'
printf '  capabilities invoke claimsreg as backend-engineer (L1): '; gq "$R" backend-engineer S-be capabilities invoke --plugin claimsreg --inputs '{"texts":["a"]}' | cut -c1-140
rm -f /tmp/f2reg.$$.json /tmp/f3*.$$.json
echo END
