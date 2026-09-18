#!/usr/bin/env python3
"""A3 — security, sensitivity and permissions (six bullets), driven through the real `gov` binary.

[C1] paths / datasets / tools / namespaces carry sensitivity / access classification
[C2] secret / credential / restricted content excluded according to policy (seeded secrets)
[C3] restricted / confidential namespaces cannot be weakened by project overrides (every project-owned lever)
[C4] tool execution respects role / authority / permission boundaries (governed plugin execution, tool resolution)
[C5] destructive / elevated operations require correct gates
[C6] outbound / export controls default-deny (upstream export gate)
Run: PROBE_TMP=<scratch> python3 A3-security-sensitivity.py
"""
import os, sys, json, shutil, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

AWS = "AKIA" + "ABCDEFGHIJKLMNOP"   # synthetic, split so this file is not itself a hit
files = {
    "README.md": "# a3 probe\n",
    "product/app.py": "def run():\n    return 42\n",
    "product/settings.py": f"# config\nAWS_KEY = '{AWS}'\n",
    ".env": "DB_PASSWORD='hunter2hunter2'\n",
    "config/credentials.json": '{"token": "x"}\n',
    "product/secrets/key.pem": "-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n",
    "product/data/customers/list.csv": "name,email\nAlice Example,alice@example.invalid\n",
    "product/docs/pricing-confidential.md": "# Pricing\nConfidential margin model: zebra-quartz-17.\n",
}
sb = Sandbox("a3")
p = sb.new_repo("proj", files)
o = sb.gov("init", "--name", "a3", "--alias", "a3-a", "--skip-index", cwd=p, quiet=True)
DS = os.path.join(p, "governance/project/DATA_SENSITIVITY.yaml")
RC = os.path.join(p, "governance/project/REPOSITORY_CONTRACT.yaml")
ds = yaml.safe_load(open(DS)); ds["classifications"] = [
    {"pattern": "product/data/customers/**", "class": "restricted", "reason": "customer data"},
    {"pattern": "product/docs/*confidential*", "class": "confidential", "reason": "commercial"}]
open(DS, "w").write(yaml.safe_dump(ds, sort_keys=False))

def rebuild():
    r = sb.gov("rebuild-memory", cwd=p, quiet=True)
    return r.get("result") or {}
def artifacts():
    db = sqlite3.connect(os.path.join(p, ".governance-runtime/state.db"))
    rows = db.execute("SELECT path, namespace, sensitivity, path_class, semantic, lexical, default_retrieval FROM artifacts ORDER BY path").fetchall()
    ex = db.execute("SELECT path, reason FROM excluded ORDER BY path").fetchall()
    chunks = [r[0] for r in db.execute("SELECT text FROM chunks").fetchall()]
    db.close()
    return rows, ex, chunks

print("## [C1] classification carried by paths / datasets / namespaces / tools")
r = rebuild()
rows, ex, chunks = artifacts()
for row in rows:
    if row[0].startswith(("product/", "spec/", "README")):
        print("[C1] artifact", row)
print("[C1] excluded:", ex)
pol = sb.gov("policy", "effective", "MEMORY_POLICY", cwd=p, quiet=True)["result"]["effective"]["namespaces"]
print("[C1] namespace classification (MEMORY_POLICY.namespaces):", json.dumps({k: {x: v[x] for x in ("sensitivity", "roles", "export")} for k, v in pol.items()}))
tl = sb.gov("tools", "list", cwd=p, quiet=True)["result"]["tools"]
print("[C1] tools carry access classification:", [(t.get("tool_id"), t.get("approved_roles"), t.get("required_permission_classes"), (t.get("scope") or {}) if isinstance(t.get("scope"), dict) else t.get("scope")) for t in tl][:6])
print("[C1] tool fields present:", sorted({k for t in tl for k in t})[:40])

print("\n## [C2] seeded secrets / credentials / restricted content are excluded")
ctext = "\n".join(chunks)
for needle in [AWS, "hunter2hunter2", "BEGIN RSA PRIVATE KEY", "alice@example.invalid", "zebra-quartz-17"]:
    print(f"[C2] {needle[:24]!r:28} present in any indexed chunk: {needle in ctext}")
for q in [AWS, "hunter2hunter2", "alice@example.invalid", "zebra-quartz-17"]:
    h = sb.gov("memory", "query", q, cwd=p, quiet=True)["result"]["hits"]
    print(f"[C2] memory query {q[:24]!r:28} -> {[x['path'] for x in h][:4]}")
print("[C2] secret_blocked (content scan):", r.get("secret_blocked"))
d = sb.gov("doctor", cwd=p, quiet=True); res = d.get("result") or (d.get("error") or {}).get("details") or {}
print("[C2] doctor D011/D012:", [(c["id"], c["ok"], c["severity"], c["message"][:120]) for c in res.get("checks", []) if c["id"] in ("D011", "D012")])
pd = sb.gov("policy", "effective", "SECURITY_POLICY", cwd=p, quiet=True)["result"]["effective"]
print("[C2] never_index_classes =", pd["never_index_classes"], "| confidential is indexable but never exported:", "confidential" not in pd["never_index_classes"] and "confidential" in pd["never_export_classes"])

print("\n## [C3] project-owned levers cannot weaken restricted / confidential / secret classification")
rc = yaml.safe_load(open(RC))
orig_rc = json.loads(json.dumps(rc))
rc["paths"].append({"pattern": "**/.env*", "class": "source", "semantic_index": True, "lexical_index": True, "namespace": "product"})
rc["paths"].append({"pattern": "product/data/customers/**", "class": "source", "sensitivity": "public", "semantic_index": True, "lexical_index": True, "export": "allowed"})
rc["paths"].append({"pattern": "product/docs/**", "class": "source", "sensitivity": "public", "export": "allowed"})
open(RC, "w").write(yaml.safe_dump(rc, sort_keys=False))
rebuild(); rows, ex, chunks = artifacts()
print("[C3a] contract rules re-classifying .env as source / customers as public: excluded =", ex)
print("[C3a] customers list indexed:", any(r_[0].startswith("product/data/customers") for r_ in rows), "| .env indexed:", any(r_[0] == ".env" for r_ in rows))
conf = [r_ for r_ in rows if "pricing" in r_[0]]
print("[C3a] confidential doc row (sensitivity kept?):", conf)
rc2 = json.loads(json.dumps(orig_rc)); rc2["paths"] = [x for x in rc2["paths"] if x.get("class") != "secret"]
open(RC, "w").write(yaml.safe_dump(rc2, sort_keys=False))
rebuild(); rows, ex, chunks = artifacts()
print("[C3b] ALL secret rules removed from the project contract: excluded =", ex)
print("[C3b] .env / credentials / key.pem indexed:", [r_[0] for r_ in rows if r_[0] in (".env", "config/credentials.json", "product/secrets/key.pem")])
open(RC, "w").write(yaml.safe_dump(orig_rc, sort_keys=False))
ds2 = yaml.safe_load(open(DS)); saved = ds2["classifications"]; ds2["classifications"] = []
open(DS, "w").write(yaml.safe_dump(ds2, sort_keys=False))
rebuild(); rows, ex, chunks = artifacts()
print("[C3c] the project DELETES its own restricted classification: customers list now indexed =", any(r_[0].startswith("product/data/customers") for r_ in rows), "(the restricted class was project-declared; no higher layer declares it)")
ds2["classifications"] = saved; open(DS, "w").write(yaml.safe_dump(ds2, sort_keys=False)); rebuild()
PP = os.path.join(p, "governance/project/PROJECT_POLICY.yaml")
y = yaml.safe_load(open(PP)); y["policy_overrides"] = {"SECURITY_POLICY.never_index_classes": ["secret"], "SECURITY_POLICY.never_export_classes": [], "MEMORY_POLICY.namespaces.secret.default_retrieval": True, "MEMORY_POLICY.namespaces.secret.roles": ["all"], "MEMORY_POLICY.namespaces.product.export": "allowed", "SECURITY_POLICY.secret_path_patterns": []}
open(PP, "w").write(yaml.safe_dump(y, sort_keys=False))
ov = sb.gov("policy", "overrides", cwd=p, quiet=True)["result"]
print("[C3d] policy-override weakening attempts: applied =", [(a["policy"], a["key"]) for a in ov["applied"]], "| refused =", [(r_["policy"], r_["key"]) for r_ in ov["refused"]])
y["policy_overrides"] = {}; open(PP, "w").write(yaml.safe_dump(y, sort_keys=False))

print("\n## [C4] tool / plugin execution respects role / authority / permission boundaries")
os.makedirs(os.path.join(p, "tools"), exist_ok=True)
shutil.copy(os.path.join(REPO, "capabilities/shell/echo_embedder.sh"), os.path.join(p, "tools/echo.sh"))
os.chmod(os.path.join(p, "tools/echo.sh"), 0o755)
os.makedirs(os.path.join(p, "governance/project/plugins"), exist_ok=True)
open(os.path.join(p, "governance/project/plugins/echo.yaml"), "w").write(yaml.safe_dump({"plugin_id": "echo", "capability": "embed", "version": "1", "command": ["tools/echo.sh"], "languages": [], "approved_roles": ["all"]}))
inp = json.dumps({"texts": ["hello"], "dimensions": 4})
for role in ["independent-auditor", "backend-engineer", "product-spec-agent", "orchestrator", "not-a-role"]:
    x = sb.gov("capabilities", "invoke", "--plugin", "echo", "--inputs", inp, role=role, cwd=p, quiet=True)
    print(f"[C4] invoke echo as {role:22s} ->", "ok" if x["ok"] else f"REFUSED {err(x)}: {str(x['error']['message'])[:110]}")
open(os.path.join(p, "governance/project/plugins/echo.yaml"), "w").write(yaml.safe_dump({"plugin_id": "echo", "capability": "embed", "version": "1", "command": ["tools/echo.sh"], "languages": [], "approved_roles": ["orchestrator"]}))
x = sb.gov("capabilities", "invoke", "--plugin", "echo", "--inputs", inp, role="product-spec-agent", cwd=p, quiet=True)
print("[C4] descriptor narrows approved_roles to [orchestrator]; product-spec-agent (L2) ->", "ok" if x["ok"] else f"REFUSED {err(x)}")
open(os.path.join(p, "governance/project/plugins/echo.yaml"), "w").write(yaml.safe_dump({"plugin_id": "echo", "capability": "embed", "version": "1", "command": ["tools/echo.sh"], "languages": [], "approved_roles": ["all"], "required_permission_classes": ["SECRET_READ"]}))
x = sb.gov("capabilities", "invoke", "--plugin", "echo", "--inputs", inp, role="orchestrator", cwd=p, quiet=True)
print("[C4] descriptor self-declares elevated SECRET_READ, unregistered; orchestrator ->", "ok" if x["ok"] else f"REFUSED {err(x)}: {str(x['error']['message'])[:140]}")
x = sb.gov("tools", "resolve", "--capability", "secret_scan", role="independent-auditor", cwd=p, quiet=True)
print("[C4] tools resolve secret_scan for independent-auditor:", json.dumps({k: x["result"][k] for k in ("tools", "capability_gap", "reason")} if x["ok"] else x.get("error"))[:300])
TP = os.path.join(p, "governance/project/TOOL_PERMISSIONS.yaml")
tp = yaml.safe_load(open(TP)); tp["roles"]["independent-auditor"] = ["READ_REPO", "RUN_TESTS", "SECRET_READ", "DEPLOY_PRODUCTION", "NETWORK_WRITE"]
open(TP, "w").write(yaml.safe_dump(tp, sort_keys=False))
x = sb.gov("tools", "resolve", "--capability", "secret_scan", role="independent-auditor", cwd=p, quiet=True)
print("[C4] after the project overlay grants independent-auditor SECRET_READ/DEPLOY_PRODUCTION/NETWORK_WRITE:", json.dumps({k: x["result"][k] for k in ("tools", "capability_gap")} if x["ok"] else x.get("error"))[:300])
print("[C4b] the same overlay grant for orchestrator + a descriptor self-declaring SECRET_READ (still UNREGISTERED): does it now execute?")
tp["roles"]["orchestrator"] = tp["roles"]["orchestrator"] + ["SECRET_READ"]; open(TP, "w").write(yaml.safe_dump(tp, sort_keys=False))
x = sb.gov("capabilities", "invoke", "--plugin", "echo", "--inputs", inp, role="orchestrator", cwd=p, quiet=True)
print("[C4b] invoke echo (requires SECRET_READ, unregistered) as orchestrator ->", "ok (EXECUTED)" if x["ok"] else f"REFUSED {err(x)}: {str(x['error']['message'])[:160]}")
pl = sb.gov("plugins", "list", role="orchestrator", cwd=p, quiet=True)
print("[C4b] plugins list:", json.dumps({k: [(d.get('plugin_id'), d.get('code') or d.get('status')) for d in pl['result'][k]] for k in ('usable', 'denied', 'rejected')} if pl["ok"] else pl.get("error"))[:300])
dd = sb.gov("doctor", cwd=p, quiet=True); res = dd.get("result") or (dd.get("error") or {}).get("details") or {}
print("[C4] doctor/audit reaction to the elevated grant:", [(c["id"], c["ok"], c["message"][:100]) for c in res.get("checks", []) if not c["ok"]][:6])
au = sb.gov("audit", "--no-persist", cwd=p, quiet=True); ares = au.get("result") or (au.get("error") or {}).get("details") or {}
print("[C4] audit findings mentioning TOOL_PERMISSIONS / elevated:", [f["message"][:120] for f in ares.get("findings", []) if "TOOL_PERMISSIONS" in f["message"] or "elevat" in f["message"].lower()][:4])

print("\n## [C5] destructive / elevated operations require the correct gates")
os.makedirs(os.path.join(p, "spec/decisions"), exist_ok=True)
open(os.path.join(p, "spec/decisions/D-0300.yaml"), "w").write(yaml.safe_dump({"id": "D-0300", "type": "decision", "title": "security architecture", "status": "ACTIVE"}))
man = os.path.join(sb.dir, "man.json"); json.dump([{"op": "delete_file", "path": "spec/decisions/D-0300.yaml"}], open(man, "w"))
c = sb.gov("cit", "propose", "--proposal", "delete the security architecture decision", "--trigger", "security_change", "--targets", "D-0300", "--manifest", man, cwd=p, quiet=True)
cid = c["result"]["id"] if c["ok"] else None
print("[C5] cit propose:", c["ok"], cid, "| status =", (c.get("result") or {}).get("cit_status"), "| error =", (c.get("error") or {}).get("message"))
s = sb.gov("cit", "simulate", cid, cwd=p, quiet=True)
sr = s.get("result") or {}
print("[C5] simulate:", json.dumps({k: sr.get(k) for k in ("impact_radius", "radius", "human_gate_required", "human_gate", "cit_status")} if s["ok"] else s.get("error"))[:300], "| keys:", sorted(sr)[:25])
a = sb.gov("cit", "approve", cid, "--by", "human", cwd=p, quiet=True)
print("[C5] cit approve without an answered gate ->", "ok" if a["ok"] else f"REFUSED {err(a)}")
e = sb.gov("cit", "execute", cid, cwd=p, quiet=True)
print("[C5] cit execute before approval ->", "ok" if e["ok"] else f"REFUSED {err(e)}", "| D-0300 still present:", os.path.exists(os.path.join(p, "spec/decisions/D-0300.yaml")))
kf = os.path.join(p, "governance/kernel/policies/CONTEXT_POLICY.yaml"); korig = open(kf).read(); open(kf, "w").write(korig + "# local edit\n")
k = sb.gov("kernel", "override", "--reason", "probe", role="change-controller", cwd=p, quiet=True)
print("[C5] (kernel now tampered) kernel override as change-controller (L3) ->", "ok " + json.dumps(k["result"])[:160] if k["ok"] else f"REFUSED {err(k)}")
k = sb.gov("kernel", "override", "--reason", "probe", role="orchestrator", cwd=p, quiet=True)
print("[C5] (kernel now tampered) kernel override as orchestrator (L4) ->", "ok " + json.dumps({x: k["result"].get(x) for x in ("override_active", "human_gate")}) if k["ok"] else f"REFUSED {err(k)}")
t = sb.gov("task", "create", "--objective", "work on a tampered kernel", role="orchestrator", cwd=p, quiet=True)
print("[C5] mutating op while the override gate is unanswered ->", "ok" if t["ok"] else f"REFUSED {err(t)}")
open(kf, "w").write(korig)
open(os.path.join(p, "governance/project/plugins/net.yaml"), "w").write(yaml.safe_dump({"plugin_id": "net", "capability": "embed", "version": "1", "command": ["tools/echo.sh"], "languages": [], "approved_roles": ["all"], "required_permission_classes": ["NETWORK_WRITE"]}))
rg = sb.gov("plugins", "register", "--descriptor", os.path.join(p, "governance/project/plugins/net.yaml"), cwd=p, quiet=True)
print("[C5] plugins register with elevated NETWORK_WRITE ->", json.dumps(rg.get("result") or rg.get("error"))[:300])

print("\n## [C6] outbound / export default-deny (upstream export gate)")
os.makedirs(os.path.join(p, "spec/lessons"), exist_ok=True)
def lesson(i, scope, text):
    open(os.path.join(p, f"spec/lessons/{i}.yaml"), "w").write(yaml.safe_dump({"id": i, "type": "lesson", "title": f"lesson {i}", "status": "ACTIVE", "scope": scope,
        "problem_statement": text, "generic_failure_mode": "stale index hides current spec", "impact": "wrong work", "suggested_framework_change": "check freshness at task close",
        "category": "retrieval", "sources": ["R-1", "R-2", "R-3"], "lifecycle": "candidate", "evidence_strength": "medium"}))
lesson("L-0901", "PROJECT", "project-only lesson")
lesson("L-0902", "FRAMEWORK", f"freshness bug; key was {AWS}")
lesson("L-0903", "FRAMEWORK", "a stale index can hide the current specification")
for lid in ("L-0901", "L-0902", "L-0903"):
    x = sb.gov("upstream", "prepare", lid, cwd=p, quiet=True)
    print(f"[C6] prepare {lid} ->", "ok " + json.dumps({k: x['result'].get(k) for k in ('packet_id', 'blocked', 'blocked_reasons')})[:220] if x["ok"] else f"REFUSED {err(x)}: {str(x['error']['message'])[:140]}")
    if lid == "L-0903" and x["ok"]:
        pid = x["result"].get("packet_id")
inbox = os.path.join(sb.dir, "canon/lessons/inbox"); os.makedirs(inbox)
for args, label in [(["--destination", inbox], "no --approved-by"), (["--destination", "https://example.invalid/inbox", "--approved-by", "human"], "remote URL"),
                    (["--destination", sb.dir, "--approved-by", "human"], "not an inbox dir"), (["--destination", inbox, "--approved-by", "human"], "approved, local inbox")]:
    x = sb.gov("upstream", "submit", pid, *args, cwd=p, quiet=True)
    print(f"[C6] submit ({label:22s}) ->", "ok files=" + json.dumps(x["result"].get("files")) if x["ok"] else f"REFUSED {err(x)}")
print("[C6] what reached the inbox:", [os.path.relpath(os.path.join(dp, f), inbox) for dp, _, fs in os.walk(inbox) for f in fs])
print("[C6] path-level export decision: customers list export =", [r_ for r_ in artifacts()[0] if r_[0].startswith("product/data/customers")] or "excluded (never indexed)")
print("\nDONE")
