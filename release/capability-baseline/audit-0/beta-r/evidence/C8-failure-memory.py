"""C8 Failure memory (Contract v3 lines 276-283): structured records of bugs, failed approaches, wrong assumptions,
retrieval misses, regressions, migration failures, tool failures.

Each failure kind is produced by driving the product into (or recording) that failure, then the probe asks:
(1) is a STRUCTURED, DURABLE record created (tracked file, not only a transient error or derived runtime state)?
(2) is it distinguishable by kind? (3) can a later session recall it? Durability is tested by a full memory rebuild.
"""
import json
import shutil
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa
import brownfield  # noqa

root, g = build_rich("c8")
g.ok("rebuild-memory")


def tracked_new(before: set) -> list:
    now = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) | set(git(root, "ls-files", "-m").splitlines())
    return sorted(now - before)


section("C8-b1 bugs")
t = g.ok("task", "create", "--class", "repair", "--objective", "Fix reconciliation drift bug caused by float money", "--fields",
         json.dumps({"lessons": ["L-0101"], "decisions": ["D-0102"]}))
g.ok("rebuild-memory", "--incremental", show=False)
nb = g.ok("memory", "graph", "L-0101", "--depth", "1")
log("L-0101 (category=bug) graph:", [(n["via"], n["node"]) for n in nb])
rq = g.ok("memory", "query", "bug reconciliation drift float money", "--k", "5")
log("recall:", [(h["artifact_id"], h["record_type"]) for h in rq["hits"]])
check("C8-b1", any(n["via"] == "→FAILED_BECAUSE" for n in nb) and any(n["node"] == t["id"] for n in nb) and any(h["artifact_id"] == "L-0101" for h in rq["hits"]),
      "a bug is a structured lesson record (category) with a FAILED_BECAUSE cause edge, linked to its repair task, and recallable")

section("C8-b2 failed approaches (product-generated from a failed worker return)")
t2 = g.ok("task", "create", "--class", "implementation", "--objective", "Batch settlement import", "--status", "READY", "--allowed", "src/**")
h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", t2["id"])
ret = BASE / "c8-ret.json"
ret.write_text(json.dumps({"task": t2["id"], "status": "failed", "work_completed": "Tried streaming CSV parser; memory blow-up on 2GB exports",
                           "files_changed": [], "evidence": ["oom at 1.4GB"], "tests": {"status": "failed"}, "discoveries": [],
                           "risks": [], "lessons": ["Streaming the whole settlement CSV in one pass fails on 2GB exports; chunk it"],
                           "proposed_decisions": [], "unresolved": [], "recommended_next_action": "chunked import"}))
wr = g.as_role("backend-engineer").as_session("S-w").ok("handoff", "return", h["id"], "--file", str(ret))
lid = wr["lessons_created"][0] if wr["lessons_created"] else None
lrec = yaml.safe_load((root / f"spec/lessons/{lid}.yaml").read_text()) if lid else {}
log("lesson created:", lid, {k: lrec.get(k) for k in ["status", "category", "lifecycle", "provenance", "problem_statement"]})
check("C8-b2", lid and lrec.get("category") == "worker-return" and lrec.get("provenance", {}).get("from_handoff") == h["id"],
      "a failed approach reported through the worker-return contract becomes a durable PROVISIONAL lesson record with provenance")

section("C8-b3 wrong assumptions (authored; any product-generated form?)")
y(root, "spec/lessons/L-0150.yaml", {"id": "L-0150", "type": "lesson", "title": "Assumed settlement export is UTC", "status": "ACTIVE",
  "scope": "PROJECT", "category": "wrong-assumption", "problem_statement": "The reconciliation job assumed processor timestamps were UTC; they are local time.",
  "relations": [{"type": "FAILED_BECAUSE", "target": "RES-0101"}]})
commit_all(root, "wrong assumption")
g.ok("rebuild-memory", "--incremental", show=False)
aud = body_of(g.run("audit", "--no-persist", "--family", "schema_invariants"))
log("schema_invariants findings for L-0150:", [f["message"] for f in aud.get("findings", []) if "L-0150" in f["message"]])
rq = g.ok("memory", "query", "which assumption about timestamps was wrong", "--k", "5")
log("recall:", [(h["artifact_id"], h["record_type"]) for h in rq["hits"]])
kinds = sorted({r[0] for r in q(root, "SELECT json_extract(data_json,'$.category') FROM artifacts WHERE record_type='lesson'")})
log("failure kinds present (free-text lesson.category):", kinds)
check("C8-b3", any(h["artifact_id"] == "L-0150" for h in rq["hits"]),
      "a wrong assumption is representable as a structured lesson (free-text category) with a cause edge and is recallable")

section("C8-b4 retrieval misses")
before = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines())
miss = g.ok("memory", "query", "blue-green deployment rollback procedure for the settlement job", "--k", "5")
log("ad-hoc query with no relevant knowledge -> hits:", [h["artifact_id"] for h in miss["hits"]])
log("retrieval_log rows (derived state.db):", q(root, "SELECT COUNT(*) FROM retrieval_log")[0][0])
new_after_miss = tracked_new(before)
log("new tracked/untracked files after the miss:", new_after_miss)
hf = root / "governance/tests/memory/heldout.yaml"
held = yaml.safe_load(hf.read_text())
held["queries"].append({"id": "HQ-MISS", "category": "semantic_paraphrase", "query": "how do we keep cash exact without decimals",
                        "expected_refs": ["D-0102"], "forbidden": [], "k": 3})
hf.write_text(yaml.safe_dump(held, sort_keys=False))
mv = g.run("memory", "verify")
mvb = body_of(mv)
log("gov memory verify:", mv.get("ok"), (mv.get("error") or {}).get("code"), "status:", mvb.get("status"),
    "failed queries:", [r["id"] for r in mvb.get("results", []) if not r["pass"]])
au = g.run("audit")
aub = body_of(au)
aud_id = aub.get("audit")
log("gov audit ->", aub.get("verdict"), "record:", aud_id)
arec = yaml.safe_load((root / f"spec/audits/{aud_id}.yaml").read_text()) if aud_id else {}
mrr = arec.get("families", {}).get("memory_retrieval_regression", {})
log("persisted audit record memory_retrieval_regression:", mrr, "findings:", [f["message"] for f in arec.get("findings", []) if f.get("family") == "memory_retrieval_regression"])
g.ok("rebuild-memory")
log("retrieval_log rows after full rebuild:", q(root, "SELECT COUNT(*) FROM retrieval_log")[0][0])
check("C8-b4-heldout", bool(aud_id) and "HQ-MISS" in json.dumps(mrr.get("detail", {}).get("failed", [])),
      "a held-out retrieval miss is persisted (failed query id) in a governed audit record")
new_spec = [x for x in new_after_miss if x.startswith("spec/")]
log("new spec/ records created by the ad-hoc miss:", new_spec)
check("C8-b4-adhoc", bool(new_spec),
      "an ad-hoc retrieval miss creates a durable memory-quality/failure record (framework §18)")

section("C8-b5 regressions")
hf.write_text(yaml.safe_dump({**held, "queries": [q_ for q_ in held["queries"] if q_["id"] != "HQ-MISS"]}, sort_keys=False))
commit_all(root, "heldout restored")
g.ok("rebuild-memory", "--incremental", show=False)
commit_all(root, "pre-regression baseline")
a1 = body_of(g.run("audit"))
log("baseline audit findings:", [(f["severity"], f["family"], f["message"][:120]) for f in a1.get("findings", [])])
y(root, "spec/requirements/REQ-0501.yaml", {"id": "REQ-0501", "type": "requirement", "title": "bad", "status": "NOT_A_STATUS"})
a2 = body_of(g.run("audit"))
log("audit before regression:", a1.get("audit"), a1.get("verdict"), a1.get("green"), "| after:", a2.get("audit"), a2.get("verdict"), a2.get("green"))
recs = sorted(p.name for p in (root / "spec/audits").glob("AUD-*.yaml"))
log("audit records:", recs)
(root / "spec/requirements/REQ-0501.yaml").unlink()
check("C8-b5", a1.get("verdict") in ("HEALTHY", "DEGRADED") and a2.get("verdict") == "UNHEALTHY" and a1.get("audit") in [r[:-5] for r in recs]
      and a2.get("audit") in [r[:-5] for r in recs],
      "a governance regression (verdict worsens) is recorded as successive structured, persisted audit records")

section("C8-b6 migration failures (brownfield A7 on a sabotaged migration)")
broot = brownfield.prepare("c8-brown")
brownfield.run_stages(broot, "A6G", show=False)
shutil.copy(WT / "fixtures/brownfield/project/.cursorrules", broot / ".cursorrules")  # legacy rules reappear in the active tree
v = brownfield.roles(broot)["verifier"].ok("adopt", "verify-migration")
bl = yaml.safe_load((broot / "spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml").read_text())
ev = (broot / "spec/audits/GOVERNANCE-ADOPTION/08-INDEPENDENT-MIGRATION-VERIFICATION.md")
log("A7 verdict:", v["verdict"], "legacy_in_active_tree:", v["legacy_in_active_tree"])
log("baseline verdict A7:", bl.get("verdicts", {}).get("A7"), "; evidence file present:", ev.exists())
log("evidence excerpt:", ev.read_text()[:400] if ev.exists() else None)
ex8 = brownfield.roles(broot)["executor"].run("adopt", "extract-legacy")
log("A8 after rejected A7 ->", (ex8.get("error") or {}).get("code"))
check("C8-b6", v["verdict"] == "MIGRATION_REJECTED_NEEDS_REPAIR" and ev.exists() and ".cursorrules" in ev.read_text(),
      "a migration failure is recorded durably (baseline verdict + independent verification evidence) and blocks the next stage")

section("C8-b7 tool failures")
# (i) code_intel adapter failure -> degradation
dst = root / "tools/pyplug"
shutil.copytree(WT / "capabilities/python/govos_capabilities", dst / "govos_capabilities")
(dst / "govos_capabilities/code_intel_python_ast.py").write_text("import sys\nsys.exit(4)\n")
write(root, "governance/project/plugins/python-ast.yaml", yaml.safe_dump({"plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0",
      "languages": ["python"], "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}))
commit_all(root, "broken adapter")
before = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) | set(git(root, "ls-files").splitlines())
rb = g.ok("rebuild-memory")
deg = q(root, "SELECT value FROM meta WHERE key='capability.degradations'")
log("rebuild degradations:", rb["degradations"][:3], "| runtime meta capability.degradations:", str(deg)[:300])
im = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("index-manifest carries degradations?:", "degradations" in json.dumps(im))
after = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) | set(git(root, "ls-files", "-m").splitlines())
log("tracked/untracked files written by the failing run (excluding manifests):", sorted(x for x in after - before if "generated" not in x))
(root / "governance/project/plugins/python-ast.yaml").unlink()
shutil.rmtree(dst)
commit_all(root, "adapter removed")
g.ok("rebuild-memory", show=False)
deg2 = q(root, "SELECT value FROM meta WHERE key='capability.degradations'")
log("after next rebuild, capability.degradations:", deg2)
# (ii) embed plugin failure
install_plugin(root, "bad_dim_embedder.py", "bad-dim", "embed")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "bad-dim", "MEMORY_POLICY.embedding.dimensions": 64})
commit_all(root, "bad embedder pinned")
be = g.run("rebuild-memory")
log("rebuild with failing embedder ->", (be.get("error") or {}).get("code"), (be.get("error") or {}).get("message", "")[:160])
# (iii) tool health failure
write(root, "governance/project/tools/TOOL-BROKEN.yaml", yaml.safe_dump({"tool_id": "TOOL-BROKEN-001", "name": "broken", "type": "CLI",
      "capabilities": ["lint"], "status": "active", "version": "1", "approved_roles": ["all"],
      "health_check": {"kind": "command", "command": ["false"], "expect_exit": 0}, "required_permission_classes": []}))
th = g.ok("tools", "health")
log("tools health for TOOL-BROKEN-001:", [x for x in th if x.get("tool_id") == "TOOL-BROKEN-001"])
spec_fail = [p for p in (root / "spec").rglob("*.yaml") if any(w in p.read_text() for w in ("bad-dim", "TOOL-BROKEN", "python-ast"))]
log("spec/ records mentioning any of the three tool failures:", spec_fail)
check("C8-b7", bool(spec_fail) or (bool(deg2) and "python-ast" in str(deg2)),
      "tool failures (adapter crash, embedder bad output, failing health check) leave a durable structured failure record")
summary()
