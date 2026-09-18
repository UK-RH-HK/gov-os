"""C3 Semantic memory (Contract v3 lines 234-241).

b1..b6: each content class is embedded (vectors exist for its chunks) and is returned by the SEMANTIC route alone
        (`--route semantic`) for a concept query, with the kernel-default embedder (hashed-ngram).
b6 also shows "selected" code units: the path map's semantic_index flag controls which code is embedded.
b7: namespace/authority filters — (i) role namespace filter, (ii) authority (superseded) filter, (iii) ORDER: are the
    filters applied before/during candidate generation or only after the candidate pool is truncated? (candidate
    starvation), (iv) does namespace-excluded content reach a pinned reranker plugin?
Paraphrase note: token-overlap-free paraphrase with the baseline embedder vs an auditor-authored concept embedder.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

root, g = build_rich("c3")
y(root, "spec/reports/RPT-0101.yaml", {"id": "RPT-0101", "type": "report", "title": "Nightly reconciliation incident report",
  "status": "ACTIVE", "summary": "The nightly reconciliation job failed twice because the settlement export arrived late; operators reran it manually."})
commit_all(root, "report")
g.ok("rebuild-memory")


def vec_count(aid):
    return q(root, "SELECT COUNT(*) FROM vectors WHERE artifact_id=?", (aid,))[0][0]


def sem(query, gg=None, k=8, extra=()):
    r = (gg or g).ok("memory", "query", query, "--route", "semantic", "--k", str(k), *extra, show=False)
    return r


def facet(bid, query, expected, label):
    section(f"{bid} {label}")
    vc = {e: vec_count(e) for e in expected}
    r = sem(query)
    got = [h["artifact_id"] for h in r["hits"]]
    log(f"query={query!r} routes={r['routes']} embedder={r['embedder']}")
    log("vectors per expected artefact:", vc)
    log("semantic hits:", [(h["artifact_id"], h["section"], round(h["score"], 5)) for h in r["hits"]])
    ok = all(vc[e] > 0 for e in expected) and all(e in got for e in expected) and r["routes"] == ["semantic"]
    check(bid, ok, f"{label}: embedded and returned by the semantic route alone")
    return r


facet("C3-b1", "why did we decide to keep money as integer cents rationale", ["D-0102"], "decisions/rationale")
facet("C3-b2", "lesson about floating point money failure drift", ["L-0101"], "lessons/failures")
facet("C3-b3", "research settlement export format refunds conclusion", ["RES-0101"], "research")
facet("C3-b3r", "reconciliation incident report settlement export late", ["RPT-0101"], "reports")
facet("C3-b4", "experiment caching order lookups latency hypothesis", ["EXP-0001"], "experiments")
facet("C3-b5", "requirement order totals exact integer cents", ["REQ-0001"], "requirements")
facet("C3-b5s", "reconciliation procedure after the settlement window", ["file:docs/runbook.md"], "specifications/narrative spec documents")
section("C3-b5-lists list-valued specification content (scenario given/when/then, acceptance criteria)")
for aid, needle in [("SCN-0001", "two orders are appended"), ("SCN-0001", "the total is 750 cents"), ("REQ-0001", "total_cents equals quantity")]:
    log(f"chunks of {aid} containing {needle!r}:", q(root, "SELECT COUNT(*) FROM chunks WHERE artifact_id=? AND text LIKE ?", (aid, f"%{needle}%"))[0][0])
log("all chunks of SCN-0001:", q(root, "SELECT chunk_id, level, section, text FROM chunks WHERE artifact_id='SCN-0001'"))
rs = sem("given an empty ledger when two orders are appended then the total is 750 cents", k=8)
log("semantic hits for the scenario's own steps:", [(h["artifact_id"], h["section"]) for h in rs["hits"]])
check("C3-b5-lists", "SCN-0001" in [h["artifact_id"] for h in rs["hits"]] and
      q(root, "SELECT COUNT(*) FROM chunks WHERE artifact_id='SCN-0001' AND text LIKE '%two orders are appended%'")[0][0] > 0,
      "scenario steps / acceptance criteria (list-valued record fields) are embedded and retrievable by content")
r6 = facet("C3-b6", "compute total quantity unit cents non-negative", ["file:src/app/models.py"], "selected code units")
log("code unit sections returned:", [(h["artifact_id"], h["level"], h["section"]) for h in r6["hits"] if h["artifact_id"].startswith("file:src/")])
# "selected": path map decides which code is embedded
cp = root / "governance/project/REPOSITORY_CONTRACT.yaml"
c = yaml.safe_load(cp.read_text())
c["paths"].insert(1, {"pattern": "src/web/**", "class": "source", "owner_role": "frontend-engineer", "semantic_index": False,
                      "lexical_index": True, "graph_index": True, "code_index": True, "namespace": "product"})
cp.write_text(yaml.safe_dump(c, sort_keys=False))
commit_all(root, "src/web not embedded")
g.ok("rebuild-memory")
vw = q(root, "SELECT COUNT(*) FROM vectors WHERE artifact_id LIKE 'file:src/web/%'")[0][0]
cw = q(root, "SELECT COUNT(*) FROM chunks_fts WHERE artifact_id LIKE 'file:src/web/%'")[0][0]
va = q(root, "SELECT COUNT(*) FROM vectors WHERE artifact_id LIKE 'file:src/app/%'")[0][0]
log(f"after path-map selection: vectors src/web={vw} (lexical rows {cw}); vectors src/app={va}")
check("C3-b6-selected", vw == 0 and cw > 0 and va > 0, "path map selects which code units are embedded (semantic_index flag) without dropping lexical")

section("C3-b7(i) namespace filter by role (product namespace roles=[engineering])")
r_eng = sem("compute total quantity unit cents", k=5)
spec_agent = g.as_role("product-spec-agent")
r_ps = sem("compute total quantity unit cents", gg=spec_agent, k=5)
log("orchestrator hits:", [h["artifact_id"] for h in r_eng["hits"]], "excluded_by_namespace:", r_eng["excluded_by_namespace"])
log("product-spec-agent hits:", [h["artifact_id"] for h in r_ps["hits"]], "excluded_by_namespace:", r_ps["excluded_by_namespace"])
check("C3-b7-role-filter", any(h["artifact_id"].startswith("file:src/") for h in r_eng["hits"])
      and not any(h["artifact_id"].startswith("file:src/") for h in r_ps["hits"]) and r_ps["excluded_by_namespace"] > 0,
      "namespace role filter removes product-namespace code for a role outside the namespace")

section("C3-b7(ii) authority filter (superseded excluded by default)")
r_a = sem("store money as floating point dollars display formatting")
log("hits:", [(h["artifact_id"], h["status"]) for h in r_a["hits"]], "excluded_by_authority:", r_a["excluded_by_authority"])
check("C3-b7-authority-filter", "D-0101" not in [h["artifact_id"] for h in r_a["hits"]] and r_a["excluded_by_authority"] >= 1,
      "superseded decision is filtered from semantic results by default")

section("C3-b7(iii) filter ORDER: candidate starvation by excluded near-duplicates")
TARGET = "Cold storage archival policy keeps monthly ledger snapshots for seven years in the vault"
y(root, "spec/decisions/D-0300.yaml", {"id": "D-0300", "type": "decision", "title": "Ledger snapshot retention",
  "status": "ACTIVE", "question": "How long are snapshots retained?", "rationale": TARGET + " as required by audit."})
for i in range(40):
    y(root, f"spec/decisions/D-03{i + 10:02d}.yaml", {"id": f"D-03{i + 10:02d}", "type": "decision",
      "title": "Ledger snapshot retention (withdrawn draft)", "status": "SUPERSEDED", "superseded_by": "D-0300",
      "question": "How long are snapshots retained?", "rationale": TARGET})
commit_all(root, "40 superseded near duplicates")
g.ok("rebuild-memory")
for k in (3, 5, 8):
    r = sem(TARGET, k=k)
    got = [h["artifact_id"] for h in r["hits"]]
    log(f"k={k}: hits={got} excluded_by_authority={r['excluded_by_authority']}")
r_hist = g.ok("memory", "query", TARGET, "--route", "semantic", "--k", "60", "--include-historical", show=False)
rank = [h["artifact_id"] for h in r_hist["hits"]].index("D-0300") + 1 if "D-0300" in [h["artifact_id"] for h in r_hist["hits"]] else None
log("rank of the ACTIVE D-0300 among all (historical included, k=60):", rank)
r5 = sem(TARGET, k=5)
starved = "D-0300" not in [h["artifact_id"] for h in r5["hits"]]
log("ACTIVE D-0300 returned at k=5 (default filters):", not starved)
check("C3-b7-filter-before-truncation", not starved,
      "the relevant ACTIVE record is still returned when excluded (superseded) near-duplicates outrank it in the candidate pool")
# lexical route shows the same ordering
rl = g.ok("memory", "query", TARGET, "--route", "lexical", "--k", "5", show=False)
log("lexical route k=5 hits:", [h["artifact_id"] for h in rl["hits"]], "excluded_by_authority:", rl["excluded_by_authority"])

section("C3-b7(iv) does namespace-excluded content reach a pinned reranker plugin?")
install_plugin(root, "logging_reranker.py", "logging-reranker", "rerank")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "logging-reranker"})
commit_all(root, "pin logging reranker")
g.ok("rebuild-memory")
logf = root / ".probe-rerank-log.jsonl"
if logf.exists():
    logf.unlink()
ps_env = spec_agent.run("memory", "query", "compute total quantity unit cents", "--k", "5")
log("product-spec-agent query with reranker:", "ok" if ps_env.get("ok") else ps_env.get("error"))
seen = [json.loads(l) for l in logf.read_text().splitlines()] if logf.exists() else []
leaked = [s for s in seen if s["id"].startswith("file:src/")]
log("candidates received by the reranker plugin:", len(seen), "of which product-namespace (role-excluded) chunks:", len(leaked))
for s in leaked[:6]:
    log("   ", s)
if ps_env.get("ok"):
    log("hits returned to the role:", [h["artifact_id"] for h in ps_env["result"]["hits"]], "excluded_by_namespace:", ps_env["result"]["excluded_by_namespace"])
check("C3-b7-no-excluded-text-to-plugin", not leaked,
      "chunks the acting role may not retrieve are not sent to the reranker plugin (filter before/during retrieval)")

section("NOTE (AC-7 / D5 context): token-overlap-free paraphrase — baseline vs auditor concept embedder")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "none"})
commit_all(root, "unpin reranker")
g.ok("rebuild-memory")
PARA = "why do we keep cash as whole units instead of imprecise decimals"
rb = sem(PARA, k=5)
log("baseline hashed-ngram:", [h["artifact_id"] for h in rb["hits"]])
install_plugin(root, "concept_embedder.py", "concept-embedder", "embed")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "concept-embedder", "MEMORY_POLICY.embedding.version": "1",
                     "MEMORY_POLICY.embedding.dimensions": 256})
commit_all(root, "pin concept embedder")
g.ok("rebuild-memory")
rc = sem(PARA, k=5)
log("concept-embedder (plugin):", [h["artifact_id"] for h in rc["hits"]], "embedder:", rc["embedder"])
log("D-0102 in baseline top5:", "D-0102" in [h["artifact_id"] for h in rb["hits"]], "; in concept-embedder top5:", "D-0102" in [h["artifact_id"] for h in rc["hits"]])
summary()
