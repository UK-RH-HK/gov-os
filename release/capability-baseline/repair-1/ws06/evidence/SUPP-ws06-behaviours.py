"""P2-AR-0019 (WS-6 repair builder) supplementary behaviour probe — REGRESSION EVIDENCE ONLY (Contract v3 O3).

Situations the audit-of-record probes do not construct, run against target/release/gov through the beta-r harness
(imported read-only from release/capability-baseline/audit-0/beta-r/evidence/lib; nothing there is edited):

S1  BC-P2-29 registering / removing a code_intel adapter re-derives unchanged files (freshness says stale first) and
    the incremental index then equals a full build.
S2  BC-P2-32 a retrieval miss observed during `context compile` is recorded durably as a memory-quality event that is
    never indexed: the index stays fresh, a second compile yields the identical packet, a repeated miss reuses the
    record, a full memory rebuild does not touch it.
S3  BC-P2-32 while FREEZE_WRITES is active a miss is not written (the query itself still succeeds).
S4  BC-P2-32 a tool failure record is recalled through the fabric by a later query.
S5  BC-P2-26 identical content in two different records is returned once (duplicate reported).
S6  BC-P2-26 the lexical route admits before truncation (40 superseded near-duplicates cannot starve the ACTIVE one).
S7  BC-P2-27 Java entity/inheritance/route, Go package test, Kotlin supertypes; symbols never from strings/comments.
S8  BC-P2-29 a broken relative import stays visible as a dangling edge in incremental and full builds alike.
"""
import json
import shutil
import sys
import yaml
from pathlib import Path

HERE = Path(__file__).resolve()
LIB = HERE.parents[3] / "audit-0" / "beta-r" / "evidence" / "lib"
sys.path.insert(0, str(LIB))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa


def snapshot(root):
    return {
        "artifacts": sorted(q(root, "SELECT artifact_id, path, content_hash, status, state_class, namespace, path_class, default_retrieval FROM artifacts")),
        "chunks": sorted(q(root, "SELECT chunk_id, content_hash FROM chunks")),
        "symbols": sorted(q(root, "SELECT symbol_id, kind, lineno, end_lineno, provider FROM symbols")),
        "refs": sorted(q(root, "SELECT path, name, kind, target FROM symbol_refs")),
        "edges": sorted(q(root, "SELECT src, type, dst FROM edges")),
        "vectors": q(root, "SELECT COUNT(*) FROM vectors")[0][0],
    }


def diff(a, b):
    return {k: {"only_incremental": sorted(set(a[k]) - set(b[k]))[:5], "only_full": sorted(set(b[k]) - set(a[k]))[:5]}
            if isinstance(a[k], list) else {"incremental": a[k], "full": b[k]} for k in a if a[k] != b[k]}


def incr_vs_full(root, g):
    ri = g.ok("rebuild-memory", "--incremental", show=False)
    si = snapshot(root)
    g.ok("rebuild-memory", show=False)
    return ri, diff(si, snapshot(root))


root, g = build_rich("supp", extra_files={
    "src/java/Order.java": '@Entity\n@Table(name = "orders")\npublic class Order extends BaseEntity implements Serializable {\n  // class Phantom extends Nothing {}\n  @GetMapping("/orders/{id}")\n  public Order get(Long id) { return null; }\n}\n',
    "src/java/BaseEntity.java": "public abstract class BaseEntity {\n  protected Long id;\n}\n",
    "src/server/server_test.go": 'package server\n\nimport "testing"\n\nfunc TestPing(t *testing.T) {\n\ts := "func NotAFunc() {}"\n\t_ = s\n}\n',
    "src/kt/Repo.kt": "class SqlRepo(val url: String) : BaseRepo(url), Repo {\n}\n",
})
g.ok("rebuild-memory")

section("S7 structure beyond the audit fixtures: Java entity/inheritance/route, Go package test, Kotlin supertypes")
models = q(root, "SELECT path, name, signature FROM symbols WHERE kind='db_model' ORDER BY path")
routes = q(root, "SELECT path, name, parent FROM symbols WHERE kind='route' ORDER BY path, name")
rels = q(root, "SELECT path, name, kind, target FROM symbol_refs WHERE kind IN ('inherits','implements') ORDER BY path, name")
tests_e = q(root, "SELECT src, dst, provenance FROM edges WHERE type='TESTS' ORDER BY src, dst")
dep_e = q(root, "SELECT src, type, dst, provenance FROM edges WHERE provenance LIKE 'inherits:%' OR provenance LIKE 'implements:%'")
phantoms = q(root, "SELECT path, name FROM symbols WHERE name IN ('Phantom','NotAFunc')")
log("db models:", models)
log("routes:", routes)
log("supertype relations:", rels)
log("TESTS edges:", tests_e)
log("inheritance/implementation edges:", dep_e)
log("symbols read from comments/strings:", phantoms)
check("S7-java-model", any(m[0] == "src/java/Order.java" and "table=orders" in m[2] for m in models), "JPA @Entity/@Table class is a DB model with its table")
check("S7-java-route", any(r[0] == "src/java/Order.java" and r[1] == "/orders/{id}" for r in routes), "Spring @GetMapping is a route registration bound to its handler")
check("S7-java-inheritance-edge", ("file:src/java/Order.java", "DEPENDS_ON", "file:src/java/BaseEntity.java", "inherits:BaseEntity") in dep_e,
      "a cross-file superclass becomes a DEPENDS_ON edge to the defining file")
check("S7-kotlin", any(r[0] == "src/kt/Repo.kt" and r[1] == "BaseRepo" and r[2] == "inherits" for r in rels)
      and any(r[0] == "src/kt/Repo.kt" and r[1] == "Repo" and r[2] == "implements" for r in rels),
      "Kotlin supertypes after a primary constructor: superclass inherits, interface implements")
check("S7-go-package-test", any(e[0] == "file:src/server/server_test.go" and e[1] == "file:src/server/server.go" for e in tests_e),
      "a Go _test.go file tests the files of its package")
check("S7-no-phantoms", not phantoms, "no symbol is read from a comment or a string literal")

section("S1 registering / removing a code_intel adapter re-derives unchanged files; incremental equals full")
dst = root / "tools/pyplug"
shutil.copytree(WT / "capabilities/python/govos_capabilities", dst / "govos_capabilities")
write(root, "governance/project/plugins/python-ast.yaml", yaml.safe_dump({
    "plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "languages": ["python"],
    "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}, sort_keys=False))
commit_all(root, "register python-ast adapter")
fr = g.ok("memory", "freshness", show=False)
log("freshness after registering the adapter: fresh=", fr["fresh"], "reclassified=", fr.get("reclassified"))
ri, d = incr_vs_full(root, g)
prov = sorted({r[0] for r in q(root, "SELECT provider FROM symbols WHERE path LIKE '%.py'")})
log("incremental: rederived=", ri.get("rederived"), "| providers for .py after:", prov, "| incremental vs full:", json.dumps(d)[:600] if d else "identical")
check("S1-register-stale", not fr["fresh"] and "src/app/models.py" in (fr.get("reclassified") or []),
      "freshness reports the files the new adapter covers as stale (re-derivation pending)")
check("S1-register-equal", not d and "src/app/models.py" in (ri.get("rederived") or []) and prov == ["python-ast"],
      "the incremental build re-derives them with the adapter and equals a full build")
(root / "governance/project/plugins/python-ast.yaml").unlink()
shutil.rmtree(dst)
commit_all(root, "remove adapter")
fr2 = g.ok("memory", "freshness", show=False)
ri2, d2 = incr_vs_full(root, g)
log("after removal: freshness fresh=", fr2["fresh"], "| incremental vs full:", json.dumps(d2)[:600] if d2 else "identical")
check("S1-remove", not fr2["fresh"] and not d2, "removing the adapter is detected and re-derived the same way")

section("S2 a retrieval miss: durable, never indexed, index and compiled packets unchanged, deduplicated, rebuild-proof")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Implement nightly reconciliation of order totals",
         "--status", "READY", "--allowed", "src/**")
tid = t["id"]
g.ok("rebuild-memory", "--incremental", show=False)
m0 = json.loads((root / "governance/generated/index-manifest.json").read_text())["manifest_hash"]
p1 = g.ok("context", "compile", tid, show=False)
before = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines())
miss = g.ok("memory", "query", "quantum annealing scheduler for zebra stripe payouts", "--k", "5", show=False)
new = sorted(set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) - before)
fr = g.ok("memory", "freshness", show=False)
m1 = json.loads((root / "governance/generated/index-manifest.json").read_text())["manifest_hash"]
p2 = g.ok("context", "compile", tid, show=False)
mq = [x for x in new if x.startswith("spec/reports/memory-quality/")]
rec = yaml.safe_load((root / mq[0]).read_text()) if mq else {}
indexed = q(root, "SELECT COUNT(*) FROM artifacts WHERE path LIKE 'spec/reports/memory-quality/%'")[0][0]
log("query result: evidence_coverage=", miss.get("evidence_coverage"), "failure_record=", miss.get("failure_record"))
log("new files:", new, "| freshness fresh:", fr["fresh"], "| manifest hash unchanged:", m0 == m1)
log("packet hashes before/after the miss:", p1["packet_hash"][:16], p2["packet_hash"][:16])
log("record:", {k: rec.get(k) for k in ["id", "type", "failure_kind", "status", "state_class", "signature"]}, "| follow_up:", rec.get("follow_up"))
log("subject:", json.dumps(rec.get("subject"))[:700])
check("S2-recorded", bool(mq) and rec.get("type") == "failure" and rec.get("failure_kind") == "retrieval-miss"
      and rec.get("follow_up", {}).get("status") == "open", "the miss is a durable, kind-distinguishable failure record with an open follow-up")
check("S2-not-indexed-fresh", indexed == 0 and fr["fresh"] and m0 == m1, "the memory-quality record is never indexed: index manifest unchanged and fresh")
check("S2-packet-stable", p1["packet_hash"] == p2["packet_hash"], "recording the miss does not change a compiled packet")
again = g.ok("memory", "query", "Quantum  annealing scheduler for ZEBRA stripe payouts", "--k", "5", show=False)
new2 = sorted(set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) - before)
log("repeat:", again.get("failure_record"))
check("S2-dedup", new2 == new and (again.get("failure_record") or {}).get("status") == "existing", "a repeated miss reuses its record (one record per signature)")
g.ok("rebuild-memory", show=False)
check("S2-survives-rebuild", all((root / x).exists() for x in mq) and g.ok("memory", "freshness", show=False)["fresh"],
      "a full memory rebuild leaves the record and a fresh index")

section("S3 FREEZE_WRITES: a miss is not written, the query still answers")
g.run("freeze-writes", "--reason", "probe")
ctl = json.loads((root / ".governance-runtime/control.json").read_text()) if (root / ".governance-runtime/control.json").exists() else {}
b3 = set(git(root, "ls-files", "-o", "--exclude-standard").splitlines())
rq = g.run("memory", "query", "platypus lighthouse telemetry for submarine invoices", "--k", "3")
a3 = sorted(set(git(root, "ls-files", "-o", "--exclude-standard").splitlines()) - b3)
log("control:", {k: ctl.get(k) for k in ["mode", "writes_frozen"]}, "| query ok:", rq.get("ok"), "| failure_record:", (rq.get("result") or {}).get("failure_record"), "| new files:", a3)
check("S3-frozen", ctl.get("writes_frozen") and rq.get("ok") and not a3 and ((rq.get("result") or {}).get("failure_record") or {}).get("status") == "not_recorded",
      "under FREEZE_WRITES the miss is reported as not recorded and nothing is written")
g.run("resume")

section("S4 a tool failure is recalled by a later query")
dst = root / "tools/pyplug"
shutil.copytree(WT / "capabilities/python/govos_capabilities", dst / "govos_capabilities")
(dst / "govos_capabilities/code_intel_python_ast.py").write_text("import sys\nsys.exit(5)\n")
write(root, "governance/project/plugins/python-ast.yaml", yaml.safe_dump({
    "plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "languages": ["python"],
    "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}, sort_keys=False))
commit_all(root, "broken adapter")
rb = g.ok("rebuild-memory", show=False)
log("rebuild failures:", rb.get("failures"))
fr = g.ok("memory", "freshness", show=False)
rq = g.ok("memory", "query", "code_intel python-ast tool failure", "--k", "5", show=False)
log("freshness after the failing build:", fr["fresh"], "| query hits:", [(h["artifact_id"], h["record_type"]) for h in rq["hits"]])
check("S4-recall", fr["fresh"] and any(h["record_type"] == "failure" for h in rq["hits"]),
      "the tool-failure record is indexed by the same build (index fresh) and recalled by a query")
(root / "governance/project/plugins/python-ast.yaml").unlink()
shutil.rmtree(dst)
commit_all(root, "adapter removed")
g.ok("rebuild-memory", show=False)

section("S5 identical content in two records is returned once")
R = "Settlement files are archived for eleven years in the cold vault because the regulator demands retrievable originals."
y(root, "spec/decisions/D-0401.yaml", {"id": "D-0401", "type": "decision", "title": "Settlement archive retention", "status": "ACTIVE",
  "question": "How long are settlement files archived?", "rationale": R})
y(root, "spec/research/RES-0401.yaml", {"id": "RES-0401", "type": "research", "title": "Regulator archive rules", "status": "ACTIVE",
  "question": "What does the regulator require?", "rationale": R})
commit_all(root, "duplicate rationale")
g.ok("rebuild-memory", "--incremental", show=False)
rq = g.ok("memory", "query", "settlement files archived eleven years cold vault regulator originals", "--k", "8", show=False)
ex = [h["excerpt"] for h in rq["hits"] if R[:40] in h["excerpt"]]
log("hits:", [(h["artifact_id"], h["section"]) for h in rq["hits"]], "| duplicates_suppressed:", rq.get("duplicates_suppressed"))
check("S5-slice-dedup", len(ex) == 1 and any(d.get("kind") == "slice_content" for d in rq.get("duplicates_suppressed", [])),
      "the identical rationale slice is returned once and the suppression is reported")

section("S6 lexical route: admission before truncation")
TARGET = "Quarterly ledger freeze windows block postings for two business days before the audit snapshot"
y(root, "spec/decisions/D-0500.yaml", {"id": "D-0500", "type": "decision", "title": "Ledger freeze window", "status": "ACTIVE",
  "question": "When are postings frozen?", "rationale": TARGET + " and reopen after sign-off."})
for i in range(40):
    y(root, f"spec/decisions/D-05{i + 10:02d}.yaml", {"id": f"D-05{i + 10:02d}", "type": "decision", "title": "Ledger freeze window (withdrawn)",
      "status": "SUPERSEDED", "superseded_by": "D-0500", "question": "When are postings frozen?", "rationale": TARGET})
commit_all(root, "40 superseded near duplicates")
g.ok("rebuild-memory", "--incremental", show=False)
rl = g.ok("memory", "query", TARGET, "--route", "lexical", "--k", "3", show=False)
log("lexical k=3:", [h["artifact_id"] for h in rl["hits"]], "excluded_by_authority:", rl["excluded_by_authority"])
check("S6-lexical-admission", "D-0500" in [h["artifact_id"] for h in rl["hits"]] and rl["excluded_by_authority"] > 0,
      "the ACTIVE record is returned at k=3 on the lexical route alone; exclusions are counted")

section("S8 a broken relative import is a dangling edge in incremental and full builds alike")
(root / "src/web/format.ts").rename(root / "src/web/money.ts")
commit_all(root, "rename format.ts -> money.ts (importer unchanged)")
g.ok("rebuild-memory", "--incremental", show=False)
inc = q(root, "SELECT src, type, dst FROM edges WHERE dst='file:src/web/format.ts'")
g.ok("rebuild-memory", show=False)
full = q(root, "SELECT src, type, dst FROM edges WHERE dst='file:src/web/format.ts'")
au = body_of(g.run("audit", "--no-persist", "--family", "graph_integrity"))
log("incremental:", inc, "| full:", full, "| findings:", [f["message"] for f in au.get("findings", [])])
check("S8-dangling", inc == full and bool(full) and any("dangling" in f["message"] for f in au.get("findings", [])),
      "the broken import is the same dangling edge after incremental and full builds and graph integrity reports it")
summary()
