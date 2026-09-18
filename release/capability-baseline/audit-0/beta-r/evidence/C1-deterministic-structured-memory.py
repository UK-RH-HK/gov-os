"""C1 Deterministic structured memory — one section per record kind (Contract v3 lines 209-227).

For every kind: (a) the product holds a structured representation (tracked record/file or product store),
(b) the product reads it back as current truth through a CLI surface, (c) where the kind is mutable, an update is
reflected as the new current truth. Derived SQLite rows (artifacts table) are shown where the kind is indexed.
Run: python3 C1-deterministic-structured-memory.py   (PROBE_TMP optional)
"""
import json
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

root, g = build_rich("c1")
g.ok("rebuild-memory")


def art(aid):
    r = q(root, "SELECT artifact_id, record_type, status, state_class, path FROM artifacts WHERE artifact_id=?", (aid,))
    return r[0] if r else None


def section(t):
    log("")
    log("=" * 100)
    log(t)
    log("=" * 100)


def structured(aid):
    r = g.ok("memory", "query", aid, show=False)
    return r["routes"], [h["artifact_id"] for h in r["hits"]]


status = g.ok("status")

section("C1-b01 projects")
a = art("PRJ-0001")
log("artifacts row:", a)
log("gov status .project:", status["project"])
prj = yaml.safe_load((root / "spec/product/PRJ-0001.yaml").read_text())
log("spec/product/PRJ-0001.yaml:", {k: prj.get(k) for k in ["id", "type", "title", "status", "alias", "intent"] if k in prj})
rt, hits = structured("PRJ-0001")
log("memory query PRJ-0001 routes/hits:", rt, hits[:3], "(rank of PRJ-0001:", hits.index("PRJ-0001") + 1 if "PRJ-0001" in hits else None, ")")
check("C1-b01", a and a[1] == "project" and status["project"]["alias"] == "c1" and "structured" in rt and "PRJ-0001" in hits,
      "project record held (spec/product/PRJ-0001.yaml), in SQLite artifacts, returned by gov status and by structured ID lookup")

section("C1-b02 features")
a = art("F-0001")
log("artifacts row:", a)
rc = g.ok("readiness", "check", "F-0001")
log("gov readiness check F-0001 ->", {k: rc.get(k) for k in ["feature", "coverage", "pre_implementation_ok"]}, "gaps:", len(rc.get("gaps", [])))
feats = g.ok("status")["features"]
log("gov status .features:", feats)
check("C1-b02", a and a[1] == "feature" and any(f["id"] == "F-0001" for f in feats) and rc.get("feature") in ("F-0001", None),
      "feature record in SQLite, evaluated by gov readiness check, listed by gov status")

section("C1-b03 requirements")
a = art("REQ-0001")
log("artifacts row:", a)
t = g.ok("task", "create", "--class", "implementation", "--objective", "Implement exact order totals", "--feature", "F-0001",
         "--status", "READY", "--allowed", "src/**,tests/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}))
tid = t["id"]
g.ok("rebuild-memory", "--incremental", show=False)
pk = g.ok("context", "compile", tid)
reqs = [r["id"] for r in pk["deterministic_authority"]["governing_requirements"]]
log("context packet governing_requirements:", reqs)
check("C1-b03", a and a[1] == "requirement" and "REQ-0001" in reqs,
      "requirement record in SQLite and delivered as current governing requirement in the deterministic authority block")

section("C1-b04 decisions (current truth under supersession)")
log("D-0101 row:", art("D-0101"))
log("D-0102 row:", art("D-0102"))
sup = q(root, "SELECT superseded_by FROM artifacts WHERE artifact_id='D-0101'")[0][0]
ad = [d["id"] for d in pk["deterministic_authority"]["active_decisions"]]
log("context packet active_decisions:", ad, "conflicting:", [d["id"] for d in pk["deterministic_authority"]["conflicting_decisions"]])
r_def = g.ok("memory", "query", "How is money represented in the ledger?", show=False)
r_hist = g.ok("memory", "query", "How is money represented in the ledger?", "--include-historical", show=False)
log("default query hits:", [(h["artifact_id"], h["status"]) for h in r_def["hits"]])
log("--include-historical hits:", [(h["artifact_id"], h["status"], h["flags"]) for h in r_hist["hits"]])
check("C1-b04", sup == "D-0102" and "D-0102" in ad and "D-0101" not in ad
      and "D-0101" not in [h["artifact_id"] for h in r_def["hits"]]
      and any(h["artifact_id"] == "D-0101" for h in r_hist["hits"]),
      "decision current truth = D-0102; superseded D-0101 recorded superseded_by, excluded from authority and default retrieval, visible only on explicit historical request")

section("C1-b05 tasks (current truth follows status change)")
show1 = g.ok("task", "show", tid)
log("task show before:", {k: show1.get(k) for k in ["id", "class", "task_status", "feature"]})
g.ok("task", "status", tid, "IN_PROGRESS", "--note", "probe")
show2 = g.ok("task", "show", tid)
log("task show after status change:", {k: show2.get(k) for k in ["id", "task_status"]})
dag = g.ok("task", "dag")
in_dag = tid in json.dumps(dag)
log("task present in DAG:", in_dag)
check("C1-b05", show1.get("task_status") == "READY" and show2.get("task_status") == "IN_PROGRESS" and in_dag,
      "task record created via gov task create; status change is the new current truth (task show, task dag)")

section("C1-b06 scenarios")
a = art("SCN-0001")
scn = [s["id"] for s in pk["deterministic_authority"]["scenarios"]]
acc = pk["deterministic_authority"]["acceptance_criteria"]
log("artifacts row:", a, "packet scenarios:", scn, "acceptance criteria:", acc)
check("C1-b06", a and a[1] == "scenario" and "SCN-0001" in scn and any(x.get("scenario") == "SCN-0001" for x in acc),
      "scenario record in SQLite; delivered with its then/success criteria as acceptance criteria")

section("C1-b07 tests (test obligations + test artefacts + TESTS relationships)")
a = art("TST-0001")
tests_edges = q(root, "SELECT src, type, dst FROM edges WHERE type='TESTS'")
tf = q(root, "SELECT artifact_id, path_class FROM artifacts WHERE path_class='test'")
log("TST-0001 row:", a)
log("TESTS edges:", tests_edges)
log("test-class file artefacts:", tf)
check("C1-b07", a and a[1] == "test-obligation" and ("TST-0001", "TESTS", "REQ-0001") in tests_edges and tf,
      "test obligations are typed records with TESTS edges; test files are classified path_class=test in structured memory")

section("C1-b08 interfaces")
a = art("API-0101")
ifs = [i["id"] for i in pk["deterministic_authority"]["interfaces"]]
log("artifacts row:", a, "packet interfaces:", ifs)
check("C1-b08", a and a[1] == "interface" and "API-0101" in ifs, "interface record in SQLite and delivered in the authority block")

section("C1-b09 experiments")
a = art("EXP-0001")
data = json.loads(q(root, "SELECT data_json FROM artifacts WHERE artifact_id='EXP-0001'")[0][0])
log("artifacts row:", a, "production_merge_allowed:", data.get("production_merge_allowed"))
rt, hits = structured("EXP-0001")
log("structured lookup:", rt, hits[:2])
check("C1-b09", a and a[1] == "experiment" and data.get("production_merge_allowed") is False and "EXP-0001" in hits,
      "experiment record (hypothesis/method/result, production_merge_allowed=false) held and retrievable by ID")

section("C1-b10 releases")
lock = yaml.safe_load((root / "governance/framework.lock").read_text())
log("framework.lock:", {k: lock.get(k) for k in ["framework", "version", "release_hash", "installed_at"]})
log("gov status .framework:", status["framework"])
# a product release record: the product has no 'release' record type (records.rs TYPE_DIR/TYPE_PREFIX)
y(root, "spec/releases/REL-0001.yaml", {"id": "REL-0001", "type": "release", "title": "orders-ledger 1.0.0",
  "status": "ACTIVE", "version": "1.0.0", "includes": ["F-0001"]})
commit_all(root, "product release record")
rb = g.ok("rebuild-memory", "--incremental", show=False)
a = art("REL-0001")
log("generic REL-0001 row after incremental rebuild:", a)
aud = g.run("audit", "--family", "schema_invariants", "--no-persist")
body = aud.get("result") or (aud.get("error") or {}).get("details") or {}
log("schema_invariants verdict:", body.get("verdict"), "findings mentioning REL-0001:", [f["message"] for f in body.get("findings", []) if "REL-0001" in json.dumps(f)])
check("C1-b10", lock.get("version") and lock.get("release_hash") and status["framework"]["version"] == lock.get("version"),
      "installed Governance OS release is current truth in framework.lock and gov status")
check("C1-b10-note", a is not None and a[1] == "release",
      "a governed product's own release can only be an untyped generic record (no release type/dir/prefix); indexed generically")

section("C1-b11 claims")
g.ok("task", "status", tid, "READY")
c1 = g.ok("task", "claim", tid)
cl = g.ok("claims", "list")
log("claims list:", cl)
other = g.as_session("S-other").run("task", "claim", tid)
log("second session claim ->", other.get("error", {}).get("code"))
check("C1-b11", any(c["task_id"] == tid for c in cl) and other.get("error", {}).get("code") == "TASK_CLAIMED",
      "claims held in the claims store (.governance-runtime/claims.db); current holder enforced against a second session")

section("C1-b12 transactions (CIT records)")
c = g.ok("cit", "propose", "--proposal", "Rename the settlement window key", "--trigger", "behaviour_change", "--targets", "REQ-0001")
cid = c["id"]
lst = g.ok("cit", "list")
st = g.ok("status")
log("cit list:", [(x.get("id"), x.get("cit_status")) for x in lst])
log("gov status open_transactions:", st["open_transactions"])
g.ok("cit", "reject", cid, "--by", "orchestrator", "--reason", "probe")
st2 = g.ok("status")
lst2 = g.ok("cit", "list")
log("after reject: cit list:", [(x.get("id"), x.get("cit_status")) for x in lst2], "open_transactions:", st2["open_transactions"])
check("C1-b12", any(o["id"] == cid for o in st["open_transactions"]) and not any(o["id"] == cid for o in st2["open_transactions"]),
      "change transactions are CIT records whose status is current truth (open -> REJECTED removes it from open_transactions)")

section("C1-b13 statuses (lifecycle statuses are policy-bounded current truth)")
y(root, "spec/requirements/REQ-0099.yaml", {"id": "REQ-0099", "type": "requirement", "title": "Bogus status", "status": "WHATEVER"})
aud = g.run("audit", "--family", "schema_invariants", "--no-persist")
body = aud.get("result") or (aud.get("error") or {}).get("details") or {}
msgs = [f["message"] for f in body.get("findings", []) if "REQ-0099" in f.get("message", "")]
log("schema_invariants on invalid status:", msgs)
(root / "spec/requirements/REQ-0099.yaml").unlink()
counts = g.ok("status")["tasks"]["counts"]
log("gov status task counts:", counts)
check("C1-b13", any("outside AUTHORITY_POLICY.lifecycle_statuses" in m for m in msgs) and counts,
      "status values are validated against AUTHORITY_POLICY.lifecycle_statuses; task status counts are current truth in gov status")

section("C1-b14 skill versions")
sk = g.ok("skills", "list")
log("skills (id, version, source):", [(s.get("id"), s.get("version"), s.get("_source")) for s in sk][:20])
t2 = g.ok("task", "create", "--class", "test-design", "--objective", "Design acceptance tests", "--feature", "F-0001",
          "--fields", json.dumps({"required_skills": ["SKL-TEST-DESIGN"]}))
pk2 = g.ok("context", "compile", t2["id"])
log("context packet required_skills:", pk2["deterministic_authority"]["required_skills"])
check("C1-b14", sk and all(s.get("version") for s in sk) and pk2["deterministic_authority"]["required_skills"][0].get("version"),
      "skills carry versions; task context resolves the required skill's current version")

section("C1-b15 tool versions")
reg = g.ok("tools", "registry")
tv = [(t.get("tool_id"), t.get("version"), t.get("version_pin")) for t in reg["tools"]]
log("tool registry (tool_id, version, version_pin):", tv)
log("governance/generated/tool-registry.json present:", (root / "governance/generated/tool-registry.json").exists())
check("C1-b15", tv and all(v[1] for v in tv) and (root / "governance/generated/tool-registry.json").exists(),
      "tool registry records every tool's version (and version_pin where declared) in a generated manifest")

section("C1-b16 model-routing records")
mr = root / "governance/project/MODEL_ROUTING_OVERRIDES.yaml"
m = yaml.safe_load(mr.read_text())
m["providers"] = [{"name": "prov-a", "models": [{"id": "big", "tier": "T3", "max_reasoning": "extra_high", "cost_per_1k_in": 3.0, "cost_per_1k_out": 6.0},
                                                {"id": "mid", "tier": "T2", "max_reasoning": "high", "cost_per_1k_in": 1.0, "cost_per_1k_out": 2.0}]}]
mr.write_text(yaml.safe_dump(m, sort_keys=False))
r1 = g.ok("route", "--class", "implementation")
log("route implementation:", {k: r1.get(k) for k in ["minimum_tier", "reasoning", "chosen"]})
ev = BASE / "c1-routing-ev.json"
ev.write_text(json.dumps({"task": tid, "provider": "prov-a", "model": "mid", "task_class": "implementation", "reasoning_effort": "high",
                          "cost": 0.4, "latency_ms": 900, "pass": True, "repair_count": 0, "reviewer_findings": 0}))
g.ok("route", "--record", str(ev))
rep = g.ok("route", "--report")
log("route report rows:", rep["rows"])
check("C1-b16", r1.get("chosen", {}) and r1["chosen"].get("model") in ("mid", "big") and rep["rows"] and rep["rows"][0]["model"] == "mid",
      "model routing mapping (overlay) resolves the current route; routing evidence records are kept and reported")
log("NOTE: routing evidence lives in", str((root / ".governance-runtime/routing/evidence.jsonl").relative_to(root)),
    "exists:", (root / ".governance-runtime/routing/evidence.jsonl").exists(), "(untracked runtime directory)")

section("C1-b17 index manifests")
im = json.loads((root / "governance/generated/index-manifest.json").read_text())
mm = json.loads((root / "governance/generated/memory-manifest.json").read_text())
log("index-manifest keys:", sorted(im.keys()))
log("index-manifest embedder/lexical/chunking/index_version:", im["embedder"], im["lexical"], im["chunking"], im["index_version"])
log("index-manifest artifacts:", len(im["artifacts"]), "manifest_hash:", im["manifest_hash"])
log("memory-manifest keys:", sorted(mm.keys()))
fr = g.ok("memory", "freshness")
log("gov memory freshness:", {k: fr[k] for k in ["fresh", "manifest_present", "checked", "stale", "added", "removed", "pin_mismatch"]})
h0 = im["manifest_hash"]
write(root, "docs/runbook.md", (root / "docs/runbook.md").read_text() + "\nAppendix: escalate to finance.\n")
fr2 = g.ok("memory", "freshness")
g.ok("rebuild-memory", "--incremental", show=False)
im2 = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("after editing docs/runbook.md: freshness stale=", fr2["stale"], "; after incremental rebuild manifest_hash changed:", im2["manifest_hash"] != h0,
    "; entry content_hash updated:", im2["artifacts"]["docs/runbook.md"]["content_hash"] != im["artifacts"]["docs/runbook.md"]["content_hash"])
check("C1-b17", im["manifest_hash"] and im["artifacts"] and fr["manifest_present"] and "docs/runbook.md" in fr2["stale"] and im2["manifest_hash"] != h0,
      "tracked index manifest records component identity + per-artefact content hashes; it is read as current truth and updated on change")

section("C1 derived SQLite deterministic store: record kinds present")
for row in q(root, "SELECT record_type, COUNT(*) FROM artifacts GROUP BY record_type ORDER BY record_type"):
    log("  ", row)
summary()
