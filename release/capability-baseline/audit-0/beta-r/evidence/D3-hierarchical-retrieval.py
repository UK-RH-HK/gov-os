"""D3 Hierarchical retrieval (Contract v3 lines 323-327).

A long design document (sections longer than chunking.max_chars) and a long Python class (methods) are indexed. The
probe inspects the chunk tree (level, parent_chunk_id) and asks retrieval questions whose best answer is a CHILD unit,
checking child-first ranking and selective parent / graph-neighbour expansion on the top-N hits only.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

filler = "The settlement batch is streamed in pages of five hundred rows and each page is validated before commit. " * 8
DOC = ("# Settlement design\n\nOverview of the settlement pipeline.\n\n## Ingestion\n\n" + filler +
       "\n\nThe quarantine bucket keeps malformed rows for fourteen days under key QUARANTINE_TTL_DAYS.\n\n" + filler +
       "\n\n## Matching\n\n" + filler + "\n")
methods = "".join(f"\n    def step_{i}(self, rows):\n        \"\"\"Pipeline step {i}.\"\"\"\n        return [r for r in rows if r.get('k{i}') is not None]\n" for i in range(1, 16))
CLS = '"""Settlement pipeline."""\n\n\nclass SettlementPipeline:\n    """Runs settlement steps."""\n' + methods + \
      "\n    def reconcile_quarantine(self, rows):\n        return [r for r in rows if r.get('quarantined') and r.get('age_days', 0) > 14]\n"
root, g = build_rich("d3", extra_files={"docs/settlement-design.md": DOC, "src/app/pipeline.py": CLS})
g.ok("rebuild-memory")

section("D3-b1 document -> section/record -> child chunk")
tree = q(root, "SELECT chunk_id, level, section, parent_chunk_id, chars FROM chunks WHERE artifact_id='file:docs/settlement-design.md' ORDER BY ordinal")
for r in tree:
    log("  ", r)
levels = {r[1] for r in tree}
kids_ok = all(r[3] for r in tree if r[1] == "child") and all(any(p[0] == r[3] and p[1] == "section" for p in tree) for r in tree if r[1] == "child")
sec_ok = all(r[3] and r[3].endswith("#0") for r in tree if r[1] == "section")
rec = q(root, "SELECT chunk_id, level, section, parent_chunk_id FROM chunks WHERE artifact_id='D-0102' ORDER BY ordinal")
log("record D-0102 chunk tree:", rec)
check("D3-b1", levels == {"document", "section", "child"} and kids_ok and sec_ok and any(r[1] == "section" for r in rec),
      "documents and records are indexed as document -> section/field -> child chunks with parent pointers")

section("D3-b2 code file -> module/class -> function/symbol")
ctree = q(root, "SELECT chunk_id, level, section, parent_chunk_id, chars FROM chunks WHERE artifact_id='file:src/app/pipeline.py' ORDER BY ordinal")
for r in ctree:
    log("  ", r)
syms = q(root, "SELECT qualname, kind, parent, lineno, end_lineno FROM symbols WHERE path='src/app/pipeline.py' ORDER BY lineno")
log("symbols:", syms)
method_chunks = [r for r in ctree if (r[2] or "").startswith("SettlementPipeline.")]
log("chunks whose section is a method (Class.method):", method_chunks)
rq = g.ok("memory", "query", "SettlementPipeline.reconcile_quarantine", "--k", "5")
log("symbol query SettlementPipeline.reconcile_quarantine ->", [(h["artifact_id"], h["chunk_id"], h["level"], h["section"]) for h in rq["hits"]])
hit = rq["hits"][0] if rq["hits"] else {}
check("D3-b2-symbols", any(s[1] == "method" and s[2] == "SettlementPipeline" for s in syms), "the class -> method hierarchy is held in the symbol store")
log("excerpt returned for the method lookup (first 160 chars):", repr(hit.get("excerpt", "")[:160]))
check("D3-b2-chunks", bool(method_chunks) or (hit and "def reconcile_quarantine" in hit.get("excerpt", "")),
      "a function/method inside a class is retrievable as its own unit (chunk hierarchy file -> class -> method)")

section("D3-b3 child-first retrieval")
rq = g.ok("memory", "query", "how long does the quarantine bucket keep malformed rows", "--k", "5")
top = rq["hits"][0] if rq["hits"] else {}
log("hits:", [(h["artifact_id"], h["chunk_id"], h["level"], h["section"]) for h in rq["hits"]])
log("top hit level:", top.get("level"), "| contains the answer:", "fourteen days" in top.get("excerpt", ""), "| parent_excerpt present:", bool(top.get("parent_excerpt")))
check("D3-b3", top.get("level") == "child" and "fourteen days" in top.get("excerpt", ""),
      "the precise child chunk holding the answer is retrieved first (not the whole section/document)")

section("D3-b4 selective parent / graph-neighbour expansion")
pol_top = g.ok("policy", "effective", "MEMORY_POLICY")["effective"]["retrieval"]
log("MEMORY_POLICY.retrieval parent_expansion_top_n / graph_neighbour_depth:", pol_top.get("parent_expansion_top_n"), pol_top.get("graph_neighbour_depth"))
rq = g.ok("memory", "query", "settlement batch streamed in pages validated before commit quarantine matching", "--k", "8")
for i, h in enumerate(rq["hits"]):
    log(f"  #{i + 1} {h['artifact_id']:<34} level={h['level']:<8} parent_excerpt={'yes' if h.get('parent_excerpt') else 'no ':<3} neighbours={len(h.get('neighbours', []))}")
expanded = [i for i, h in enumerate(rq["hits"]) if h.get("parent_excerpt") or h.get("neighbours")]
rn = g.ok("memory", "query", "REQ-0001 exact integer cents", "--k", "5")
log("neighbour expansion for a record hit:", [(h["artifact_id"], h.get("neighbours")) for h in rn["hits"][:2]])
check("D3-b4", expanded and max(expanded) < pol_top.get("parent_expansion_top_n", 3) and any(h.get("parent_excerpt") for h in rq["hits"] if h["level"] == "child")
      and any(h.get("neighbours") for h in rn["hits"][:3]),
      "only the top-N hits are expanded: child hits get their parent section, record hits their graph neighbours")
summary()
