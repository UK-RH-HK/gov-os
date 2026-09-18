"""C10 Capability memory (Contract v3 lines 294-301): tools, MCP servers, A2A agents, packages/dependencies, model
providers, permission/credential status, environment/tool versions.

Each facet is read back through the product surfaces an agent would use (`gov tools registry|resolve|health`,
`gov capabilities ecosystems|plugins`, `gov route`, `gov version`, runtime capability memory) after the probe changes
the environment (adds a tool, an MCP server, dependency manifests, a provider, a credential-scoped tool).
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

PYPROJECT = '[project]\nname = "orders-ledger"\nversion = "0.3.0"\ndependencies = ["flask>=3.0", "sqlalchemy==2.0.30", "httpx"]\n'
PKG = json.dumps({"name": "orders-web", "version": "0.1.0", "dependencies": {"express": "^4.19.2", "zod": "3.23.8"}}, indent=1)
root, g = build_rich("c10", extra_files={"pyproject.toml": PYPROJECT, "package.json": PKG})
g.ok("rebuild-memory")

section("C10-b1 tools")
write(root, "governance/project/tools/TOOL-RUFF-001.yaml", yaml.safe_dump({"tool_id": "TOOL-RUFF-001", "name": "ruff", "type": "CLI",
      "languages": ["python"], "capabilities": ["lint"], "status": "active", "version": "0.6.9", "version_pin": "ruff==0.6.9",
      "approved_roles": ["all"], "required_permission_classes": ["RUN_TESTS"], "health_check": {"kind": "command", "command": ["ruff", "--version"], "expect_exit": 0},
      "credential_scope": "none", "license": "MIT", "reversible": True}))
commit_all(root, "project tool")
reg = g.ok("tools", "registry")
log("registry tools:", [(t.get("tool_id"), t.get("type"), t.get("status"), t.get("version")) for t in reg["tools"]])
res = g.ok("tools", "resolve", "--capability", "lint")
log("tools resolve lint:", {k: res.get(k) for k in ["project_languages", "tools", "capability_gap", "reason"]})
res2 = g.ok("tools", "resolve", "--capability", "deploy_k8s")
log("tools resolve deploy_k8s:", {k: res2.get(k) for k in ["tools", "capability_gap", "reason"]})
check("C10-b1", any(t.get("tool_id") == "TOOL-RUFF-001" for t in reg["tools"]) and any(t["tool_id"] == "TOOL-RUFF-001" for t in res["tools"])
      and res2["capability_gap"], "tools are registered (kernel + project), resolved per role/language, and gaps reported")

section("C10-b2 MCP servers")
write(root, "governance/project/mcp/registry.yaml", yaml.safe_dump({"servers": [{"id": "MCP-DOCS-001", "name": "docs-search", "transport": "stdio",
      "command": ["docs-mcp"], "capabilities": ["doc_search"], "required_permission_classes": ["READ_REPO"], "approved_roles": ["all"],
      "credential_scope": "none", "status": "active", "health": {"kind": "none"}}]}))
commit_all(root, "mcp server")
reg = g.ok("tools", "registry")
log("registry mcp_servers:", [(s.get("id"), s.get("status")) for s in reg["mcp_servers"]])
log("role exposure (orchestrator) mcp:", reg["role_exposure"].get("orchestrator", {}).get("mcp_servers"))
res = g.ok("tools", "resolve", "--capability", "doc_search")
log("resolve doc_search -> mcp:", res.get("mcp_servers"))
m = g.run("mcp", "serve")
log("gov mcp serve ->", (m.get("error") or {}).get("code"))
check("C10-b2", any(s.get("id") == "MCP-DOCS-001" for s in reg["mcp_servers"]) and res.get("mcp_servers"),
      "MCP servers (kernel + project) are held in capability memory with status and per-role exposure")

section("C10-b3 A2A agents")
roles_doc = yaml.safe_load((root / "governance/kernel/roles/ROLES.yaml").read_text())
log("kernel role roster (id, level, tier):", [(r["id"], r["level"], r["minimum_tier"]) for r in roles_doc["roles"]][:8], "...")
a2a = {"tool_id": "A2A-RISK-001", "name": "external risk-scoring agent", "type": "A2A", "capabilities": ["risk_score"],
       "status": "active", "version": "1", "version_pin": "1", "approved_roles": ["all"], "health_check": {"kind": "none"}, "reversible": True}
(BASE / "c10-a2a.json").write_text(json.dumps(a2a))
inst = g.run("tools", "install", "--descriptor", str(BASE / "c10-a2a.json"))
log("register an A2A agent as a capability ->", inst.get("ok"), (inst.get("error") or {}).get("code"), (inst.get("error") or {}).get("message", "")[:200])
hits = [k for k in json.dumps(reg).split('"') if "a2a" in k.lower()]
log("any A2A entries in the tool/MCP registry:", hits)
h = g.run("handoff", "create", "--to-role", "external-risk-agent", "--task", "TASK-0001")
log("handoff to a non-kernel agent ->", (h.get("error") or {}).get("code"))
check("C10-b3", bool(hits) or inst.get("ok"), "available A2A agents (identity, endpoint/transport, capabilities, availability) are held in capability memory")

section("C10-b4 packages/dependencies")
eco = g.ok("capabilities", "ecosystems")
log("gov capabilities ecosystems:", [(e["id"], e["manifest"], e["available"]) for e in eco["ecosystems"]])
cm = q(root, "SELECT value FROM meta WHERE key='capability.ecosystems'")
log("runtime capability memory (ecosystems):", str(cm)[:400])
deps_known = any(d in json.dumps(eco) + json.dumps(cm) for d in ("sqlalchemy", "express", "flask"))
idx = q(root, "SELECT path, path_class FROM artifacts WHERE path IN ('pyproject.toml','package.json')")
log("dependency manifests in the index:", idx)
rq = g.ok("memory", "query", "which version of sqlalchemy do we depend on", "--k", "5")
log("query sqlalchemy dependency ->", [h["artifact_id"] for h in rq["hits"]])
check("C10-b4-ecosystems", len(eco["ecosystems"]) >= 2, "package ecosystems (manifests + native tool availability) are detected")
check("C10-b4-dependencies", deps_known or any(h["artifact_id"] in ("file:pyproject.toml", "file:package.json") for h in rq["hits"]),
      "declared packages/dependencies (flask, sqlalchemy==2.0.30, express, zod) are held in capability memory or retrievable")

section("C10-b5 model providers")
mr = root / "governance/project/MODEL_ROUTING_OVERRIDES.yaml"
mm = yaml.safe_load(mr.read_text())
mm["providers"] = [{"name": "prov-a", "models": [{"id": "big", "tier": "T3", "max_reasoning": "extra_high"}, {"id": "small", "tier": "T1", "max_reasoning": "low"}]},
                   {"name": "prov-b", "models": [{"id": "mid", "tier": "T2", "max_reasoning": "high"}]}]
mr.write_text(yaml.safe_dump(mm, sort_keys=False))
commit_all(root, "providers")
r = g.as_role("routine-documentation").ok("route", "--class", "documentation")
log("route documentation (acting role routine-documentation, tier T1) candidates:", [(c["provider"], c["model"], c["tier"]) for c in r["candidates"]], "chosen:", r["chosen"])
check("C10-b5", {c["provider"] for c in r["candidates"]} >= {"prov-a", "prov-b"}, "model providers and their models/tiers are held and used for routing")

section("C10-b6 permission / credential status")
reg = g.ok("tools", "registry")
log("role exposure backend-engineer permissions:", reg["role_exposure"].get("backend-engineer", {}).get("permissions"))
write(root, "governance/project/tools/TOOL-GW-001.yaml", yaml.safe_dump({"tool_id": "TOOL-GW-001", "name": "gateway-cli", "type": "CLI",
      "capabilities": ["gateway_call"], "status": "active", "version": "2.1.0", "approved_roles": ["all"], "required_permission_classes": ["NETWORK_READ"],
      "credential_scope": "env:GATEWAY_API_KEY", "health_check": {"kind": "builtin"}, "reversible": True, "license": "MIT"}))
commit_all(root, "credentialed tool")
reg = g.ok("tools", "registry")
gw = [t for t in reg["tools"] if t.get("tool_id") == "TOOL-GW-001"][0]
log("TOOL-GW-001 as recorded:", {k: gw.get(k) for k in ["credential_scope", "status", "required_permission_classes"]})
cred_status_keys = [k for k in json.dumps(reg).split('"') if "credential" in k.lower() and k != "credential_scope"]
log("credential-status fields anywhere in the registry:", sorted(set(cred_status_keys)))
res = g.ok("tools", "resolve", "--capability", "gateway_call", "--role", "backend-engineer")
log("resolve gateway_call for backend-engineer (no NETWORK_READ):", {k: res.get(k) for k in ["tools", "capability_gap", "reason"]})
check("C10-b6-permissions", res["capability_gap"] and "permission" in res["reason"], "permission status per role is held and enforced in resolution")
check("C10-b6-credentials", bool(cred_status_keys), "credential status (present/absent/expired for a declared credential scope) is held in capability memory")

section("C10-b7 environment / tool versions")
v = g.ok("version")
log("gov version:", v)
th = g.ok("tools", "health")
log("tools health sample:", th[:4])
vers = {t.get("tool_id"): t.get("version") for t in reg["tools"]}
log("registry versions (declared):", vers)
observed = [x for x in th if any(k in x for k in ("version", "observed_version", "stdout"))]
log("health results carrying an observed version string:", observed)
check("C10-b7-declared", v and all(vers.values()), "CLI/runtime and declared tool versions are recorded")
check("C10-b7-observed", bool(observed) or "version" in json.dumps(eco["ecosystems"]),
      "observed environment/tool versions (e.g. python3/cargo/node actually present) are captured")
summary()
