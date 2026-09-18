"""D4 Component separation (Contract v3 lines 329-340): embedding model, embedding runtime, vector/index store, lexical
engine, graph engine, code intelligence, reranker, retrieval router, generative/query-planning model, context compiler
"are independently identifiable and replaceable where designed".

For each component: (a) where the product records its identity, (b) whether it can be replaced through a governed
mechanism, (c) INDEPENDENCE: replacing it leaves the derived state owned by the other components unchanged (a full
snapshot diff of chunks / FTS / vectors / edges / symbols before and after).
"""
import hashlib
import json
import shutil
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("d4")
g.ok("rebuild-memory")


def h(sql):
    return hashlib.sha256(json.dumps(sorted(q(root, sql)), default=str).encode()).hexdigest()[:16]


CONTENT = "artifact_id NOT LIKE 'file:governance/%' AND artifact_id NOT LIKE 'file:tools/%'"


def owned():
    """Derived state of the project CONTENT (configuration files the swap itself edits are excluded)."""
    return {"chunks": h(f"SELECT chunk_id, content_hash FROM chunks WHERE {CONTENT}"), "fts": h(f"SELECT chunk_id, text FROM chunks_fts WHERE {CONTENT}"),
            "vectors": h(f"SELECT chunk_id, embedder, dim, vec FROM vectors WHERE {CONTENT}"), "edges": h("SELECT src, type, dst FROM edges"),
            "symbols": h("SELECT symbol_id, kind, provider FROM symbols")}


def changed(a, b):
    return sorted(k for k in a if a[k] != b[k])


man = lambda: json.loads((root / "governance/generated/index-manifest.json").read_text())  # noqa
base = owned()

section("D4-b1 embedding model")
m0 = man()["embedder"]
install_plugin(root, "concept_embedder.py", "concept-embedder", "embed")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "concept-embedder", "MEMORY_POLICY.embedding.version": "1", "MEMORY_POLICY.embedding.dimensions": 256})
commit_all(root, "swap embedding model")
rb = g.ok("rebuild-memory")
after = owned()
r = g.ok("memory", "query", "why integer cents", "--route", "semantic", "--k", "3", show=False)
log("manifest embedder before/after:", m0, man()["embedder"], "| query embedder:", r["embedder"])
log("derived stores changed by the embedder swap:", changed(base, after))
(root / "governance/project/plugins/concept-embedder.yaml").unlink()
commit_all(root, "remove plugin while pinned")
fe = g.run("memory", "query", "why integer cents")
log("pinned embedder plugin removed -> query:", (fe.get("error") or {}).get("code"))
check("D4-b1", man()["embedder"]["id"] == "concept-embedder" and changed(base, after) == ["vectors"] and (fe.get("error") or {}).get("code") in ("EMBEDDER_UNAVAILABLE", "PLUGIN_NOT_FOUND"),
      "the embedding model is identified in the manifest, replaced through a governed pin + full rebuild, touches only the vector store, and fails closed when missing")
install_plugin(root, "concept_embedder.py", "concept-embedder", "embed")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "hashed-ngram", "MEMORY_POLICY.embedding.dimensions": 512})
commit_all(root, "back to builtin")
g.ok("rebuild-memory", show=False)

section("D4-b2 embedding runtime (separately identifiable from the model?)")
dst = root / "tools/probe-plugins"
dst.mkdir(parents=True, exist_ok=True)
shutil.copy(PLUGINS / "weights_embedder.py", dst / "weights_embedder.py")
shutil.copy(PLUGINS / "weights.json", dst / "weights.json")
desc = {"plugin_id": "weights-embedder", "capability": "embed", "version": "1", "command": ["python3", "tools/probe-plugins/weights_embedder.py"], "languages": []}
(BASE / "d4-weights-desc.yaml").write_text(yaml.safe_dump(desc))
reg = g.run("plugins", "register", "--descriptor", str(BASE / "d4-weights-desc.yaml"))
log("gov plugins register weights-embedder ->", reg.get("ok"), (reg.get("error") or {}).get("code"), json.dumps(reg.get("result", {}))[:300])
entry = g.ok("plugins", "registry", show=False)["plugins"].get("weights-embedder", {})
log("registry entry binds:", {k: entry.get(k) for k in ["version", "implementation_files", "implementation_sha256", "descriptor_sha256"]})
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "weights-embedder", "MEMORY_POLICY.embedding.version": "1", "MEMORY_POLICY.embedding.dimensions": 64})
commit_all(root, "pin weights-embedder")
g.ok("rebuild-memory")
m1 = man()["embedder"]
v1 = h("SELECT chunk_id, vec FROM vectors")
log("manifest embedder identity (the only component identity recorded):", m1)
# change the 'model weights / runtime' artefact behind the same plugin id + version + adapter script
(dst / "weights.json").write_text('{"salt": "B"}')
commit_all(root, "weights changed under the same plugin identity")
fr = g.ok("memory", "freshness", show=False)
d25 = [c for c in body_of(g.run("doctor")).get("checks", []) if c["id"] in ("D025", "D028")]
qx = g.run("memory", "query", "reconciliation procedure", "--route", "semantic", "--k", "3")
log("after changing weights.json: freshness pin_mismatch=", fr["pin_mismatch"], "stale=", [s for s in fr["stale"] if "probe-plugins" in s],
    "| doctor:", [(c["id"], c["ok"], c["message"][:100]) for c in d25], "| semantic query ->", qx.get("ok"), (qx.get("error") or {}).get("code"))
g.ok("rebuild-memory", "--incremental", show=False)
v2 = h("SELECT chunk_id, vec FROM vectors")
log("incremental rebuild after the weights change: vectors re-embedded?", v1 != v2, "| manifest embedder identity unchanged:", man()["embedder"] == m1)
(dst / "weights_embedder.py").write_text((dst / "weights_embedder.py").read_text() + "\n# adapter edit\n")
commit_all(root, "adapter script edited")
qy = g.run("memory", "query", "reconciliation procedure", "--route", "semantic", "--k", "3")
log("after editing the adapter script (registered pin covers it): query ->", qy.get("ok"), (qy.get("error") or {}).get("code"))
check("D4-b2-identified", "runtime" in json.dumps(m1).lower() or "weights.json" in json.dumps(entry.get("implementation_files", [])),
      "the embedding runtime / model artefact is recorded as its own identity (separate from the embed adapter)")
check("D4-b2-drift", not qx.get("ok") or fr["pin_mismatch"] or v1 != v2,
      "a change of the runtime/model artefact behind an unchanged plugin identity is detected (fail closed or forced re-embed)")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "hashed-ngram", "MEMORY_POLICY.embedding.dimensions": 512})
commit_all(root, "back to builtin (2)")
g.ok("rebuild-memory", show=False)
base = owned()

section("D4-b3 vector / index store")
mm = json.loads((root / "governance/generated/memory-manifest.json").read_text())
log("memory-manifest stores:", mm.get("stores"), "| index-manifest index_version:", man()["index_version"])
import sqlite3
con = sqlite3.connect(str(root / ".governance-runtime/state.db"))
con.execute("UPDATE meta SET value=? WHERE key='index_version'", (json.dumps("4.1.5-idx2"),))
con.commit()
con.close()
im = man()
im["index_version"] = "4.1.5-idx2"
(root / "governance/generated/index-manifest.json").write_text(json.dumps(im))
fr = g.ok("memory", "freshness", show=False)
log("live store + tracked manifest carry an older store format (4.1.5-idx2) -> freshness pin_mismatch:", fr["pin_mismatch"])
rb = g.ok("rebuild-memory", "--incremental")
log("incremental rebuild -> mode:", rb["mode"], "escalated:", rb["escalated_to_full"])
check("D4-b3", mm.get("stores", {}).get("state_db") and fr["pin_mismatch"] and rb["mode"] == "full",
      "the derived store is identified (runtime path, tables, index format version); a store-format change is a governed full rebuild")
log("replaceability: no plugin capability exists for vector storage (API-0001 capabilities: embed, rerank, code_intel)")

section("D4-b4 lexical engine")
log("manifest lexical:", man()["lexical"])
base = owned()
set_overrides(root, {"MEMORY_POLICY.lexical.tokenizer": "unicode61"})
commit_all(root, "tokenizer change")
fr = g.ok("memory", "freshness", show=False)
rb = g.ok("rebuild-memory", "--incremental")
after = owned()
stem_before = "porter" in json.dumps(base)
r = g.ok("memory", "query", "reconciles", "--route", "lexical", "--k", "5", show=False)
log("tokenizer porter unicode61 -> unicode61: freshness pin_mismatch=", fr["pin_mismatch"], "| rebuild mode:", rb["mode"], "| stores changed:", changed(base, after),
    "| 'reconciles' (no stemming now) lexical hits:", [x["artifact_id"] for x in r["hits"]])
check("D4-b4", fr["pin_mismatch"] and rb["mode"] == "full" and man()["lexical"]["tokenizer"] == "unicode61" and "vectors" not in changed(base, after) and "edges" not in changed(base, after),
      "the lexical engine/tokenizer is identified, replaceable by pin with a forced rebuild, and independent of vectors/graph")
set_overrides(root, {"MEMORY_POLICY.lexical.tokenizer": "porter unicode61"})
commit_all(root, "tokenizer back")
g.ok("rebuild-memory", show=False)
base = owned()

section("D4-b5 graph engine")
log("edge store rows:", q(root, "SELECT COUNT(*) FROM edges")[0][0], "| graph queries run without any embedder/reranker:",
    [n["node"] for n in g.ok("memory", "graph", "F-0001", show=False)][:6])
log("graph identity recorded in the manifest?:", [k for k in man().keys() if "graph" in k.lower()], "(only via index_version)")
check("D4-b5", q(root, "SELECT COUNT(*) FROM edges")[0][0] > 0, "the graph store/engine is a distinct component (edges table + deterministic traversal), independent of vectors/lexical (shown in b1/b4)")

section("D4-b6 code intelligence")
prov0 = q(root, "SELECT DISTINCT provider FROM symbols")
shutil.copytree(WT / "capabilities/python/govos_capabilities", root / "tools/pyplug/govos_capabilities")
write(root, "governance/project/plugins/python-ast.yaml", yaml.safe_dump({"plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0",
      "languages": ["python"], "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}))
commit_all(root, "python-ast adapter")
g.ok("rebuild-memory")
prov1 = q(root, "SELECT path, provider FROM symbols WHERE path LIKE 'src/%' GROUP BY path, provider")
after = owned()
log("providers before:", prov0, "| after:", prov1, "| stores changed:", changed(base, after))
check("D4-b6", any(p == "python-ast" for _, p in prov1) and "symbols" in changed(base, after),
      "code intelligence is identified per symbol (provider) and replaceable per language through the plugin registry")
(root / "governance/project/plugins/python-ast.yaml").unlink()
shutil.rmtree(root / "tools/pyplug")
commit_all(root, "remove adapter")
g.ok("rebuild-memory", show=False)
base = owned()

section("D4-b7 reranker")
install_plugin(root, "logging_reranker.py", "logging-reranker", "rerank")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "logging-reranker"})
commit_all(root, "pin reranker")
g.ok("rebuild-memory")
after = owned()
r = g.ok("memory", "query", "reconciliation procedure settlement", "--k", "3", show=False)
log("manifest reranker:", man()["reranker"], "| query reranker:", r["reranker"], "| rerank scores:", [x["rerank_score"] for x in r["hits"]], "| stores changed:", changed(base, after))
(root / "governance/project/plugins/logging-reranker.yaml").unlink()
commit_all(root, "remove reranker plugin while pinned")
rr = g.run("memory", "query", "reconciliation procedure", "--k", "3")
log("pinned reranker removed -> query:", (rr.get("error") or {}).get("code"))
check("D4-b7", man()["reranker"]["provider"] == "logging-reranker" and r["reranker"]["provider"] == "logging-reranker" and not changed(base, after)
      and (rr.get("error") or {}).get("code") in ("RERANKER_UNAVAILABLE", "PLUGIN_NOT_FOUND"),
      "the reranker is identified, replaceable by pin, changes no stored index state, and fails closed when missing")
set_overrides(root, {"MEMORY_POLICY.reranker.provider": "none"})
commit_all(root, "unpin reranker")
g.ok("rebuild-memory", show=False)

section("D4-b8 retrieval router")
r = g.ok("memory", "query", "REQ-0001", "--k", "3", show=False)
r2 = g.ok("memory", "query", "REQ-0001", "--route", "lexical", "--k", "3", show=False)
log("router decision recorded per query: routes=", r["routes"], "strategy=", r["strategy"], "| explicit route override:", r2["routes"])
log("router identity/version recorded in manifest or result?:", [k for k in list(r.keys()) + list(man().keys()) if "router" in k.lower()])
check("D4-b8", r["routes"] and r2["routes"] == ["lexical"], "the router is a distinct component whose decision is recorded per query and can be overridden per query")

section("D4-b9 generative / query-planning model")
schema = json.loads((WT / "framework/schemas/plugin-descriptor.schema.json").read_text())
log("plugin-descriptor capability enum:", schema.get("properties", {}).get("capability"))
log("retrieval result component fields:", sorted(k for k in r.keys()))
check("D4-b9", "planner" not in json.dumps(r) and "llm" not in json.dumps(r).lower(),
      "no generative model participates in retrieval (nothing can substitute for deterministic authority resolution)")

section("D4-b10 context compiler")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Totals", "--feature", "F-0001", "--fields", json.dumps({"requirements": ["REQ-0001"]}))
g.ok("rebuild-memory", "--incremental", show=False)
p1 = g.ok("context", "compile", t["id"])
install_plugin(root, "concept_embedder.py", "concept-embedder", "embed")
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "concept-embedder", "MEMORY_POLICY.embedding.dimensions": 256})
commit_all(root, "swap embedder under the compiler")
g.ok("rebuild-memory", show=False)
p2 = g.ok("context", "compile", t["id"])
det_same = {k: v for k, v in p1["deterministic_authority"].items() if k != "authority_layers"} == {k: v for k, v in p2["deterministic_authority"].items() if k != "authority_layers"}
log("packet identity fields:", {k: p1.get(k) for k in ["packet_id", "index_version", "deterministic_hash", "packet_hash"]})
log("embedder swapped: mandatory authority content unchanged:", det_same, "| retrieved index snapshot changed:", p1["retrieved_intelligence"]["index_snapshot"] != p2["retrieved_intelligence"]["index_snapshot"])
check("D4-b10", det_same and p1["retrieved_intelligence"]["index_snapshot"] != p2["retrieved_intelligence"]["index_snapshot"],
      "the context compiler is a distinct component: retrieval-component swaps change only the retrieved block, never the deterministic authority content")
summary()
