"""D2 Retrieval router (Contract v3 lines 315-321).

For each route: a set of agent-style questions, the routes the router classifies them into (`routes`), whether the
expected artefact is returned, and its rank. Exact-ID lookups are also graded on rank 1 (a structured lookup should put
the known record first).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("d2")
g.ok("rebuild-memory")
g.ok("audit", show=False)   # an AUD record mentioning many IDs (realistic noise for ID lookups)
g.ok("rebuild-memory", "--incremental", show=False)


def ask(query, k=8):
    r = g.ok("memory", "query", query, "--k", str(k), show=False)
    return r


def row(bid, query, expected, want_route):
    r = ask(query)
    got = [h["artifact_id"] for h in r["hits"]]
    rank = got.index(expected) + 1 if expected in got else None
    log(f"{bid}: {query!r:<62} routes={r['routes']!s:<40} strategy={r['strategy']:<14} expected={expected} rank={rank} top3={got[:3]}")
    return r, rank


section("D2-b1 structured lookup for known IDs / paths")
ranks = []
for q_, e in [("REQ-0001", "REQ-0001"), ("D-0102", "D-0102"), ("PRJ-0001", "PRJ-0001"), ("SCN-0001", "SCN-0001"), ("API-0101", "API-0101"), ("EXP-0001", "EXP-0001")]:
    r, rank = row("D2-b1", q_, e, "structured")
    ranks.append((q_, "structured" in r["routes"], rank))
for q_, e in [("spec/requirements/REQ-0001.yaml", "REQ-0001"), ("src/core/ledger.rs", "file:src/core/ledger.rs")]:
    r, rank = row("D2-b1p", q_, e, "path")
    ranks.append((q_, "path" in r["routes"], rank))
log("structured/path lookups (query, route taken, rank of the known record):", ranks)
check("D2-b1", all(rt and rk is not None for _, rt, rk in ranks), "known IDs and paths are routed to structured/path lookup and the record is returned")
check("D2-b1-rank1", all(rk == 1 for _, _, rk in ranks), "the known record is ranked first for an exact ID/path lookup")

section("D2-b2 code / symbol route")
sym = []
for q_, e in [("compute_total", "file:src/app/models.py"), ("def compute_total", "file:src/app/models.py"), ("Order.total_cents", "file:src/app/models.py"),
              ("symbol:MemoryLedger", "file:src/core/ledger.rs"), ("fn sum_entries", "file:src/core/ledger.rs")]:
    r, rank = row("D2-b2", q_, e, "symbol")
    sym.append(("symbol" in r["routes"], rank))
check("D2-b2", all(rt and rk for rt, rk in sym), "symbol/definition queries are routed to the code-symbol route and return the defining file")

section("D2-b3 lexical route")
lex = []
for q_, e in [('"append-only ledger"', "file:docs/runbook.md"), ("ERR_LEDGER_DRIFT_4711", "file:docs/runbook.md"), ("max_retries_per_gateway", "file:config/settings.yaml")]:
    r, rank = row("D2-b3", q_, e, "lexical")
    lex.append((any(x.startswith("lexical") for x in r["routes"]), rank))
r, rank = row("D2-b3f", "runbook.md", "file:docs/runbook.md", "lexical")
lex_fn = (any(x.startswith("lexical") for x in r["routes"]), rank)
check("D2-b3", all(rt and rk for rt, rk in lex), "exact text / error / config-key queries are routed to the lexical route")
check("D2-b3-filename", lex_fn[0] and lex_fn[1], "a bare filename query reaches a route that can answer it")

section("D2-b4 graph / impact route")
r, rank = row("D2-b4", "what depends on REQ-0001", "F-0001", "graph")
g1 = ("graph" in r["routes"], rank)
r2, rank2 = row("D2-b4", "impact of changing F-0001", "SCN-0001", "graph")
g2 = ("graph" in r2["routes"], rank2)
r3, rank3 = row("D2-b4c", "what breaks if compute_total changes", "file:src/app/api.py", "graph")
g3 = ("graph" in r3["routes"], rank3)
deep = g.ok("memory", "query", "what depends on REQ-0001", "--k", "30", show=False)
dl = [h["artifact_id"] for h in deep["hits"]]
log("default router, k=30, 'what depends on REQ-0001': first graph-route hit at rank",
    next((i + 1 for i, h in enumerate(deep["hits"]) if "graph" in h["routes"]), None), "; F-0001 rank:", dl.index("F-0001") + 1 if "F-0001" in dl else None,
    "; hits carrying only lexical/semantic routes before it:", sum(1 for h in deep["hits"][:27] if set(h["routes"]) <= {"lexical", "semantic"}))
log("   first 10:", [(h["artifact_id"], h["routes"]) for h in deep["hits"][:10]])
go = g.ok("memory", "query", "what depends on REQ-0001", "--route", "graph", "--k", "10", show=False)
log("same question, --route graph only:", [h["artifact_id"] for h in go["hits"]])
imp = g.ok("memory", "impact", "file:src/app/models.py", show=False)
log("for comparison, gov memory impact file:src/app/models.py ->", [x["node"] for x in imp])
check("D2-b4", g1[0] and g1[1] and g2[0] and g2[1], "dependency/impact questions about governed records are routed to graph traversal AND the graph answer is delivered within k (not buried by fused lexical/semantic noise)")
check("D2-b4-code", g3[0], "dependency/impact questions about code symbols/files reach the graph route")

section("D2-b5 semantic route")
r, rank = row("D2-b5", "why did we move away from floating point money", "D-0102", "semantic")
check("D2-b5", "semantic" in r["routes"] and rank, "concept/rationale questions are routed to semantic retrieval")

section("D2-b6 multi-route fusion for complex questions")
r = ask("why does REQ-0001 require compute_total to use integer cents and what depends on it")
log("routes:", r["routes"], "strategy:", r["strategy"])
multi = [(h["artifact_id"], h["routes"]) for h in r["hits"]]
log("hits with contributing routes:", multi)
fused_from_several = any(len(h["routes"]) > 1 for h in r["hits"])
check("D2-b6", len(r["routes"]) >= 3 and r["strategy"] == "fusion" and fused_from_several,
      "a complex question runs several routes and fuses them (reciprocal-rank fusion), with per-hit route provenance")
summary()
