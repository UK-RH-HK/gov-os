"""``gov retrieve``: one cited evidence bundle with one stopping reason (W1-21; DEC-080, DEC-419).

``retrieve`` asks the lexical and the semantic route, closes over a ticket or ids with ``gov.closure``, merges the
three by chunk hash, drops what the store says is superseded (DEC-329, G-19), reranks the rest once (DP-9) and
expands a child hit to its parent within the bundle budget (DEC-091, DP-3). It only reads (DEC-322).

Not decided yet, and so not built (DEC-419): batches beyond the first, rounds and a continuation token (DP-2); a
must-not-cite marking and a file the store did not load (DP-4); failure and lesson records ahead (DP-5). One batch
is gathered. When it does not hold everything, the rest is listed as gaps, the bundle has no ``continuation`` key
and never says that nothing is left.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from gov import closure as closures
from gov import records
from gov.cli.errors import GovError
from gov.retrieval import lexical, semantic
from gov.retrieval.fusion import RERANK_CHARS, rrf
from gov.retrieval.rerank import rerank

CLOSURE = "closure"
SATURATED, BUDGET_EXHAUSTED = "SATURATED", "BUDGET_EXHAUSTED_WITH_GAPS"
SUPERSEDED, NOT_GATHERED = "SUPERSEDED", "NOT_GATHERED"
BUNDLE_BUDGET = 6000  # tokens: DEC-004's packet ceiling, until a decision gives another number (DP-3)
TOKEN_CHARS = 4
NO_CODE_INDEX = "the code index did not answer for an id that is no record"


def _graph(root: Path) -> tuple[dict[str, str], set[str]]:
    """``path -> id`` of every record of the store, and the ids that are superseded: a status of ``SUPERSEDED`` or
    the target of a ``SUPERSEDES`` edge. Without a record graph nothing can be told current: ``STORE_MISSING``."""
    try:
        known = records.records(root)
        superseded = {edge["target"] for edge in records.edges(root, type="SUPERSEDES")}
    except sqlite3.OperationalError:
        raise GovError("STORE_MISSING", f"no record graph in the store at {root}; load it first",
                       {"root": str(root)}) from None
    return ({record["path"]: record["id"] for record in known},
            superseded | {record["id"] for record in known if record["status"] == SUPERSEDED})


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None, bundle_budget=None, continuation=None,
             reranker=None) -> dict:
    """The evidence bundle for ``query``; ``ticket`` and ``ids`` are closed over to the depth of ``radius``."""
    if continuation is not None:  # DP-2 is open: no token exists yet, so none is valid
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle")
    root = Path(root)
    record_of, superseded = _graph(root)
    answers = {lexical.FACET: lexical.search(root, query, refresh=False),
               semantic.FACET: semantic.search(root, query, refresh=False)}
    facets = {name: {"available": answer["available"], "reason": answer["reason"]} for name, answer in answers.items()}
    routes = {name: answer["hits"] for name, answer in answers.items()}
    # A stale index holds lines the files no longer have: without the lexical route nothing is cited.
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)} if facets[lexical.FACET]["available"] else {}
    gaps, start = [], [*([ticket] if ticket else []), *ids]
    if start:
        closed = closures.closure(root, start, closures.depth_of_radius(radius))
        reached = {item["id"] for item in closed["closure"]}
        routes[CLOSURE] = [chunk for chunk in chunks.values() if record_of.get(chunk["path"]) in reached]
        answered = closed["facets"]["code"] != "unavailable"
        facets[CLOSURE] = {"available": answered, "reason": None if answered else NO_CODE_INDEX}
        gaps += closed["gaps"]

    fused = rrf(routes)  # each chunk once, naming every route that returned it
    batch, rest = (fused, []) if batch_size is None else (fused[:batch_size], fused[batch_size:])
    gaps += [{"path": hit["path"], "chunk_id": hit["chunk_id"], "reason": NOT_GATHERED} for hit in rest]
    files: dict[str, list[bytes]] = {}

    def span(rel: str, first: int, last: int) -> bytes:
        if rel not in files:
            files[rel] = (root / rel).read_bytes().splitlines(keepends=True)
        return b"".join(files[rel][first - 1:last])

    dropped, candidates = {}, []
    for hit in batch:
        chunk = chunks[hit["chunk_id"]]
        if record_of.get(chunk["path"]) in superseded:
            dropped[chunk["path"]] = {"path": chunk["path"], "id": record_of[chunk["path"]], "reason": SUPERSEDED}
            continue
        body = span(chunk["path"], chunk["start_line"], chunk["end_line"])
        candidates.append({**chunk, "routes": hit["routes"], "body": body,
                           "text": f"[path: {chunk['path']}]\n{body.decode('utf-8', 'replace')[:RERANK_CHARS]}"})
    try:
        ranked = rerank(query, candidates, reranker)
    except (OSError, RuntimeError, ValueError):  # a reranker that dies after loading ends nothing (DP-6)
        ranked = candidates

    limit = BUNDLE_BUDGET if bundle_budget is None else bundle_budget
    used = sum(_tokens(candidate["body"].decode("utf-8", "replace")) for candidate in ranked)
    evidence, expansions, expanded = [], [], set()
    for candidate in ranked:
        rel, first, last, body = candidate["path"], candidate["start_line"], candidate["end_line"], candidate["body"]
        parent = lexical.parent(root, candidate["parent_id"])
        if parent and (parent["start_line"], parent["end_line"]) != (first, last) and parent["parent_id"] not in expanded:
            wider = span(rel, parent["start_line"], parent["end_line"])
            cost = _tokens(wider.decode("utf-8", "replace")) - _tokens(body.decode("utf-8", "replace"))
            if used + cost <= limit:  # the budget bounds expansion only: the child stands when its parent does not fit
                used, first, last, body = used + cost, parent["start_line"], parent["end_line"], wider
                expanded.add(parent["parent_id"])
                expansions.append({"chunk_id": candidate["chunk_id"], "parent_id": parent["parent_id"], "path": rel,
                                   "start_line": first, "end_line": last})
        evidence.append({"id": record_of.get(rel, candidate["chunk_id"]), "sha256": hashlib.sha256(body).hexdigest(),
                         "path": rel, "start_line": first, "end_line": last, "text": body.decode("utf-8", "replace"),
                         "chunk_id": candidate["chunk_id"], "routes": candidate["routes"], "batch": 1})

    reasons = {gap["reason"] for gap in gaps}
    if not all(facet["available"] for facet in facets.values()):
        stopping = closures.FACET_UNAVAILABLE
    elif rest:  # a batch-size limit is never reported as completeness
        stopping = BUDGET_EXHAUSTED
    elif closures.DEPTH_LIMIT in reasons:
        stopping = closures.DEPTH_LIMIT
    elif closures.UNRESOLVED in reasons:
        stopping = closures.UNRESOLVED_ALONE
    else:
        stopping = closures.COMPLETE if start else SATURATED
    bundle = {"stopping_reason": stopping, "evidence": evidence, "batches": [{"size": len(batch)}],
              "merge": {"candidates": len(batch), "duplicates": sum(map(len, routes.values())) - len(fused),
                        "dropped": [dropped[rel] for rel in sorted(dropped)],
                        "reranked": any("rerank_score" in candidate for candidate in ranked)},
              "expansions": expansions, "gaps": gaps, "facets": facets, "budget": {"bundle": {"limit": limit, "used": used}}}
    if not rest:
        bundle["continuation"] = None  # nothing more exists; otherwise the key is absent until DP-2 defines a token
    return bundle
