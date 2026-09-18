"""D1 Incremental indexing / freshness (Contract v3 lines 307-313), plus the Contract v3 lines 97-109 invalidation
inputs that touch the index (project path map, security/sensitivity policy, model/retrieval profile, relevant source).

Every incremental result is compared against a FULL rebuild of the same tree (the reference): an incremental build
that leaves the index different from a fresh full build has failed to invalidate something.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

root, g = build_rich("d1")
g.ok("rebuild-memory")


def snapshot():
    return {
        "artifacts": sorted(q(root, "SELECT artifact_id, path, content_hash, status, state_class, namespace, path_class, sensitivity, default_retrieval, semantic, lexical FROM artifacts")),
        "chunks": sorted(q(root, "SELECT chunk_id, content_hash FROM chunks")),
        "symbols": sorted(q(root, "SELECT symbol_id, kind, lineno, end_lineno FROM symbols")),
        "refs": sorted(q(root, "SELECT path, name, kind, target FROM symbol_refs")),
        "edges": sorted(q(root, "SELECT src, type, dst FROM edges")),
        "vectors": q(root, "SELECT COUNT(*) FROM vectors")[0][0],
    }


def diff(a, b):
    out = {}
    for k in a:
        if a[k] != b[k]:
            if isinstance(a[k], list):
                sa, sb = set(a[k]), set(b[k])
                out[k] = {"only_incremental": sorted(sa - sb)[:10], "only_full": sorted(sb - sa)[:10]}
            else:
                out[k] = {"incremental": a[k], "full": b[k]}
    return out


def incr_vs_full(label):
    ri = g.ok("rebuild-memory", "--incremental", show=False)
    si = snapshot()
    rf = g.ok("rebuild-memory", show=False)
    sf = snapshot()
    d = diff(si, sf)
    log(f"[{label}] incremental: mode={ri['mode']} indexed={ri['indexed']} unchanged={ri['unchanged']} removed={ri['removed']} moved={ri['moved']} "
        f"escalated={ri.get('escalated_to_full')}")
    log(f"[{label}] incremental vs full differences:", json.dumps(d)[:1500] if d else "none")
    return ri, d


section("D1-b1 content-hash / repo-commit invalidation")
fr0 = g.ok("memory", "freshness", show=False)
write(root, "docs/runbook.md", (root / "docs/runbook.md").read_text() + "\n## Escalation\n\nPage the finance on-call.\n")
fr1 = g.ok("memory", "freshness", show=False)
(root / "config/settings.yaml").touch()
fr1b = g.ok("memory", "freshness", show=False)
log("fresh before:", fr0["fresh"], "| after content edit: stale=", fr1["stale"], "| after mtime-only touch of config: stale=", fr1b["stale"])
commit_all(root, "edit runbook")
ri, d = incr_vs_full("content edit")
man = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("manifest repo_commit:", man.get("repo_commit"), "HEAD:", git(root, "rev-parse", "HEAD"))
check("D1-b1", fr0["fresh"] and fr1["stale"] == ["docs/runbook.md"] and "config/settings.yaml" not in fr1b["stale"] and ri["indexed"] == 1 and not d
      and man.get("repo_commit") == git(root, "rev-parse", "HEAD"),
      "content-hash change (not mtime) marks exactly the edited artefact stale; incremental re-indexes only it; manifest pins the repo commit")

section("D1-b2 changed artefacts invalidate affected chunks / nodes / symbols (including dependants)")
src = (root / "src/app/models.py").read_text()
write(root, "src/app/models.py", src.replace("def compute_total(", "def compute_total_cents(").replace("return compute_total(", "return compute_total_cents("))
commit_all(root, "rename compute_total -> compute_total_cents in models.py only (callers not edited)")
ri, d = incr_vs_full("callee rename")
log("symbols named compute_total after full rebuild:", q(root, "SELECT path, qualname FROM symbols WHERE name LIKE 'compute_total%'"))
check("D1-b2-own", "symbols" not in d and "chunks" not in d, "the changed file's own chunks and symbols are replaced incrementally")
check("D1-b2-dependants", not d, "dependent nodes/edges derived from OTHER files (callers' CALLS edges/refs) are invalidated so incremental == full")
write(root, "src/app/models.py", src)
commit_all(root, "restore")
g.ok("rebuild-memory", show=False)

section("D1-b3 rename / move / delete+add")
# plain file rename
git(root, "mv", "docs/runbook.md", "docs/operations-runbook.md")
commit_all(root, "rename runbook")
ri, d = incr_vs_full("file rename")
dup = q(root, "SELECT artifact_id FROM artifacts WHERE path LIKE 'docs/%runbook%'")
log("docs artefacts after rename:", dup)
ok_rename = not d and dup == [("file:docs/operations-runbook.md",)]
# record move keeps identity
git(root, "mv", "spec/requirements/REQ-0001.yaml", "spec/requirements/REQ-0001-order-totals.yaml")
commit_all(root, "move record")
ri2, d2 = incr_vs_full("record move")
log("REQ-0001 path after move:", q(root, "SELECT artifact_id, path FROM artifacts WHERE artifact_id='REQ-0001'"))
# delete + add with identical content under a new name (delete+add, not a git rename)
txt = (root / "docs/operations-runbook.md").read_text()
(root / "docs/operations-runbook.md").unlink()
write(root, "docs/ops/runbook-v2.md", txt)
commit_all(root, "delete + add")
ri3, d3 = incr_vs_full("delete+add")
log("docs artefacts after delete+add:", q(root, "SELECT artifact_id FROM artifacts WHERE path LIKE 'docs/%'"))
# plain delete
(root / "config/settings.yaml").unlink()
commit_all(root, "delete config")
ri4, d4 = incr_vs_full("delete")
check("D1-b3", ok_rename and not d2 and any(m["artifact_id"] == "REQ-0001" for m in ri2["moved"]) and not d3 and not d4 and ri4["removed"] >= 1,
      "rename, record move (identity kept), delete+add and delete leave the incremental index identical to a full rebuild with no duplicates")

section("D1-b4 model / embedder / dimension change invalidates incompatible semantic state")
set_overrides(root, {"MEMORY_POLICY.embedding.dimensions": 256})
commit_all(root, "dimension change")
fr = g.ok("memory", "freshness", show=False)
qe = g.run("memory", "query", "reconciliation procedure")
log("after pin change: freshness.fresh=", fr["fresh"], "pin_mismatch=", fr["pin_mismatch"], "| query ->", (qe.get("error") or {}).get("code"))
doc = body_of(g.run("doctor"))
d25 = [c for c in doc.get("checks", []) if c["id"] in ("D010", "D025")]
log("doctor D010/D025:", [(c["id"], c["ok"], c["message"][:140]) for c in d25])
ri = g.ok("rebuild-memory", "--incremental")
dims = q(root, "SELECT DISTINCT dim FROM vectors")
log("incremental after pin change: mode=", ri["mode"], "escalated=", ri["escalated_to_full"], "| vector dims now:", dims)
qe2 = g.run("memory", "query", "reconciliation procedure")
check("D1-b4", not fr["fresh"] and fr["pin_mismatch"] and (qe.get("error") or {}).get("code") == "EMBEDDER_MISMATCH" and ri["mode"] == "full"
      and dims == [(256,)] and qe2.get("ok"), "an embedder/dimension pin change marks the index incompatible, blocks semantic queries, and forces a full re-embed (no mixed index)")

section("D1-b5 index manifest records compatible component identity")
man = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("manifest component identity:", {k: man.get(k) for k in ["index_version", "embedder", "reranker", "chunking", "lexical", "repo_commit", "manifest_hash"]})
install_plugin(root, "logging_reranker.py", "logging-reranker", "rerank")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "logging-reranker"})
commit_all(root, "pin a reranker")
fr = g.ok("memory", "freshness", show=False)
qr = g.run("memory", "query", "reconciliation procedure")
log("after reranker pin change (no rebuild): freshness.fresh=", fr["fresh"], "pin_mismatch=", fr["pin_mismatch"], "| query ->", (qr.get("error") or {}).get("code"))
g.ok("rebuild-memory", "--incremental", show=False)
man2 = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("manifest reranker after rebuild:", man2.get("reranker"))
check("D1-b5", all(man.get(k) for k in ["index_version", "embedder", "chunking", "lexical"]) and man["embedder"].get("dimensions") == 256
      and man2.get("reranker", {}).get("provider") == "logging-reranker",
      "manifest pins embedder id/version/dims/source, reranker, chunking, lexical engine and index format")
log("OBSERVATION: freshness.pin_mismatch excludes the reranker (indexer.rs pin_differences compares embedder/chunking/lexical/index_version);"
    " freshness was stale here only because PROJECT_POLICY.yaml itself is an indexed file; the reranker pin is enforced at query time"
    " (RERANKER_MISMATCH) and by doctor D025. Stored vectors do not depend on the reranker, so no re-index is required.")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "none"})
commit_all(root, "unpin reranker")
g.ok("rebuild-memory", show=False)

section("D1-b6 required stale indexes degrade/block task close according to policy")
t = g.ok("task", "create", "--class", "documentation", "--objective", "Document escalation", "--status", "READY", "--allowed", "docs/**")
g.ok("task", "claim", t["id"])
write(root, "docs/ops/runbook-v2.md", (root / "docs/ops/runbook-v2.md").read_text() + "\nMore escalation detail.\n")
rep = BASE / "d1-rep.json"
rep.write_text(json.dumps({"task": t["id"], "work_completed": "doc", "files_changed": ["docs/ops/runbook-v2.md"], "tests": {"status": "not_applicable_with_reason", "reason": "docs"}}))
c1 = g.run("task", "close", t["id"], "--report", str(rep))
log("close with stale index (on_stale_close=fail):", (c1.get("error") or {}).get("code"))
set_overrides(root, {"MEMORY_POLICY.freshness.on_stale_close": "degrade"})
ov = g.ok("policy", "overrides", show=False)
log("override on_stale_close applied?:", [o for o in ov["applied"] if o["key"] == "freshness.on_stale_close"], "refused:", [o for o in ov["refused"] if o["key"] == "freshness.on_stale_close"])
refused = [o for o in ov["refused"] if o["key"] == "freshness.on_stale_close"]
git(root, "checkout", "--", "governance/project/PROJECT_POLICY.yaml")
g.ok("rebuild-memory", "--incremental", show=False)
c2 = g.run("task", "close", t["id"], "--report", str(rep))
log("after incremental rebuild, close:", c2.get("ok"), (c2.get("error") or {}).get("code"), (c2.get("result") or {}).get("degraded"))
check("D1-b6", (c1.get("error") or {}).get("code") == "INDEX_STALE" and refused and c2.get("ok"),
      "a stale required index blocks task close per MEMORY_POLICY.freshness.on_stale_close=fail (a project cannot weaken it to degrade); close succeeds once fresh")

section("FRESHNESS INPUT: project path map change (class/namespace/default_retrieval) — archive indexed as current?")
root2, g2 = build_rich("d1-pathmap")
g2.ok("rebuild-memory", show=False)
r0 = g2.ok("memory", "query", "reconciliation procedure settlement window", "--k", "5", show=False)
log("before: runbook returned:", "file:docs/runbook.md" in [h["artifact_id"] for h in r0["hits"]],
    "row:", q(root2, "SELECT path_class, status, default_retrieval, namespace FROM artifacts WHERE path='docs/runbook.md'"))
cp = root2 / "governance/project/REPOSITORY_CONTRACT.yaml"
c = yaml.safe_load(cp.read_text())
for r in c["paths"]:
    if r["pattern"] == "docs/**":
        r.update({"class": "historical", "default_retrieval": False, "namespace": "archive"})
cp.write_text(yaml.safe_dump(c, sort_keys=False))
commit_all(root2, "path map: docs/** is now historical (archived)")
fr = g2.ok("memory", "freshness", show=False)
log("freshness after path-map reclassification:", {k: fr[k] for k in ["fresh", "stale", "added", "removed", "pin_mismatch"]})
g2.ok("rebuild-memory", "--incremental", show=False)
row_i = q(root2, "SELECT path_class, status, default_retrieval, namespace FROM artifacts WHERE path='docs/runbook.md'")
r1 = g2.ok("memory", "query", "reconciliation procedure settlement window", "--k", "5", show=False)
log("after INCREMENTAL rebuild: row=", row_i, "| runbook returned as current:", "file:docs/runbook.md" in [h["artifact_id"] for h in r1["hits"]])
g2.ok("rebuild-memory", show=False)
row_f = q(root2, "SELECT path_class, status, default_retrieval, namespace FROM artifacts WHERE path='docs/runbook.md'")
r2 = g2.ok("memory", "query", "reconciliation procedure settlement window", "--k", "5", show=False)
log("after FULL rebuild: row=", row_f, "| runbook returned as current:", "file:docs/runbook.md" in [h["artifact_id"] for h in r2["hits"]])
fr_after = g2.ok("memory", "freshness", show=False)
log("freshness after the incremental rebuild:", {k: fr_after[k] for k in ["fresh", "stale", "added", "removed"]})
check("D1-pathmap-freshness", "docs/runbook.md" in fr["stale"] or not fr_after["fresh"] or row_i == row_f,
      "a path-map reclassification marks the affected entries stale (not merely the contract file); freshness is not green while entries keep the old classification")
check("D1-pathmap-incremental", row_i == row_f, "an incremental rebuild applies the path-map reclassification (no archive-as-current)")

section("FRESHNESS INPUT: security/sensitivity policy change — newly restricted content")
root3, g3 = build_rich("d1-sensitivity")
g3.ok("rebuild-memory", show=False)
ds = root3 / "governance/project/DATA_SENSITIVITY.yaml"
dsv = yaml.safe_load(ds.read_text())
dsv["classifications"] = [{"pattern": "config/**", "class": "restricted", "reason": "gateway settings are restricted"}]
ds.write_text(yaml.safe_dump(dsv, sort_keys=False))
commit_all(root3, "config/** is now restricted")
fr = g3.ok("memory", "freshness", show=False)
still = q(root3, "SELECT COUNT(*) FROM chunks WHERE artifact_id='file:config/settings.yaml'")[0][0]
rq = g3.ok("memory", "query", "max_retries_per_gateway", "--k", "5", show=False)
log("after reclassifying config/** as restricted (no rebuild): freshness.fresh=", fr["fresh"], "| restricted chunks still in index:", still,
    "| query returns it:", "file:config/settings.yaml" in [h["artifact_id"] for h in rq["hits"]])
dd = body_of(g3.run("doctor"))
log("doctor D010/D012:", [(c["id"], c["ok"], c["message"][:120]) for c in dd.get("checks", []) if c["id"] in ("D010", "D012")])
g3.ok("rebuild-memory", "--incremental", show=False)
after = q(root3, "SELECT COUNT(*) FROM chunks WHERE artifact_id='file:config/settings.yaml'")[0][0]
log("after incremental rebuild: restricted chunks in index:", after, "| excluded:", q(root3, "SELECT path, reason FROM excluded WHERE path='config/settings.yaml'"))
log("NOTE: the index is flagged stale because DATA_SENSITIVITY.yaml is itself an indexed file (stale list:", fr["stale"], "); the restricted entry is not itself listed")
check("D1-sensitivity-freshness", not fr["fresh"], "a sensitivity-policy change leaves the index flagged stale until it is rebuilt")
check("D1-sensitivity-incremental", after == 0, "an incremental rebuild removes newly restricted content")
summary()
