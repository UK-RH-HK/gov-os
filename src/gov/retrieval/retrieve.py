"""``gov retrieve``: one cited evidence bundle with one stopping reason (W1-21; DEC-080, DEC-419, DEC-422–425).

``retrieve`` asks the lexical and the semantic route, closes over a ticket or ids with ``gov.closure``, merges the
three by chunk hash, drops what the store says is superseded or must-not-cite (DEC-329, G-19, DEC-423), reranks
the rest once (DP-9) and expands a child hit to its parent within the bundle budget (DEC-091, DP-3). It only
reads (DEC-322).

Paging (DEC-422): batches beyond the first, rounds scaled by radius, a stateless continuation token.
Must-not-cite (DEC-423): DEPRECATED, REJECTED, WITHDRAWN; frontmatter check for files not in the store.
Failure/lesson ahead (DEC-424): failure and lesson records in the ticket's closure come ahead of other evidence.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from pathlib import Path

import yaml

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

ROUNDS_BY_RADIUS = {0: 1, 1: 1, 2: 3, 3: 8, 4: 8}
DEFAULT_BATCH_SIZE = 10
MUST_NOT_CITE_STATUSES = frozenset({"DEPRECATED", "REJECTED", "WITHDRAWN"})
AHEAD_TYPES = frozenset({"failure", "lesson"})


def _graph(root: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """``path -> id`` of every record, ``id -> reason`` for not-current records (superseded or must-not-cite),
    and ``id -> type`` for every record."""
    try:
        known = records.records(root)
        superseded_edges = {edge["target"] for edge in records.edges(root, type="SUPERSEDES")}
    except sqlite3.OperationalError:
        raise GovError("STORE_MISSING", f"no record graph in the store at {root}; load it first",
                       {"root": str(root)}) from None
    record_of = {record["path"]: record["id"] for record in known}
    not_current: dict[str, str] = {}
    for record in known:
        if record["status"] == SUPERSEDED or record["id"] in superseded_edges:
            not_current[record["id"]] = SUPERSEDED
        elif record["status"] in MUST_NOT_CITE_STATUSES:
            not_current[record["id"]] = record["status"]
    record_types = {record["id"]: record["type"] for record in known}
    return record_of, not_current, record_types


def _frontmatter_status(root: Path, rel: str) -> tuple[str | None, str | None]:
    """The (id, status) from a file's YAML frontmatter, or (None, None)."""
    try:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, None
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None, None
    try:
        front = yaml.safe_load(text[4:text.index("\n---\n", 4)])
    except Exception:
        return None, None
    if not isinstance(front, dict):
        return None, None
    return front.get("id"), front.get("status")


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def _encode_continuation(query, ids, ticket, radius, batch_size, bundle_budget, offset):
    payload = json.dumps({"q": query, "i": sorted(ids), "t": ticket, "r": radius,
                          "bs": batch_size, "bb": bundle_budget, "o": offset},
                         separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _decode_continuation(token, query, ids, ticket, radius, batch_size, bundle_budget):
    try:
        payload = json.loads(base64.urlsafe_b64decode(token))
    except Exception:
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    expected = {"q": query, "i": sorted(ids), "t": ticket, "r": radius, "bs": batch_size, "bb": bundle_budget}
    for key in expected:
        if payload.get(key) != expected[key]:
            raise GovError("CONTINUATION_INVALID",
                           "the continuation belongs to a different question or arguments") from None
    offset = payload.get("o")
    if not isinstance(offset, int) or offset < 0:
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    return offset


def retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None, bundle_budget=None, continuation=None,
             reranker=None) -> dict:
    """The evidence bundle for ``query``; ``ticket`` and ``ids`` are closed over to the depth of ``radius``."""
    if batch_size is None:
        batch_size = DEFAULT_BATCH_SIZE
    limit = BUNDLE_BUDGET if bundle_budget is None else bundle_budget

    offset = 0
    if continuation is not None:
        offset = _decode_continuation(continuation, query, tuple(ids), ticket, radius, batch_size, bundle_budget)

    root = Path(root)
    record_of, not_current, record_types = _graph(root)
    answers = {lexical.FACET: lexical.search(root, query, refresh=False),
               semantic.FACET: semantic.search(root, query, refresh=False)}
    facets = {name: {"available": answer["available"], "reason": answer["reason"]} for name, answer in answers.items()}
    routes = {name: answer["hits"] for name, answer in answers.items()}
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)} if facets[lexical.FACET]["available"] else {}
    closure_gaps, start = [], [*([ticket] if ticket else []), *ids]
    reached = set()
    if start:
        closed = closures.closure(root, start, closures.depth_of_radius(radius))
        reached = {item["id"] for item in closed["closure"]}
        routes[CLOSURE] = [chunk for chunk in chunks.values() if record_of.get(chunk["path"]) in reached]
        answered = closed["facets"]["code"] != "unavailable"
        facets[CLOSURE] = {"available": answered, "reason": None if answered else NO_CODE_INDEX}
        closure_gaps += closed["gaps"]

    fused = rrf(routes)

    # DEC-424: move failure/lesson records ahead so they're gathered even in small batches
    ahead_paths: set[str] = set()
    if ticket and reached:
        ahead_ids = {rid for rid in reached if record_types.get(rid) in AHEAD_TYPES and rid not in not_current}
        ahead_paths = {path for path, rid in record_of.items() if rid in ahead_ids}
        if ahead_paths:
            ahead_fused = [hit for hit in fused if hit["path"] in ahead_paths]
            rest_fused = [hit for hit in fused if hit["path"] not in ahead_paths]
            fused = ahead_fused + rest_fused

    # DEC-422: paging with rounds budget
    rounds_limit = ROUNDS_BY_RADIUS.get(radius, ROUNDS_BY_RADIUS[4])
    total_slots = (rounds_limit + 1) * batch_size
    gathering = fused[offset:offset + total_slots]
    remaining = fused[offset + total_slots:]

    batches_list: list[dict] = []
    batch_assignments: dict[str, int] = {}
    for i in range(rounds_limit + 1):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, len(gathering))
        batch_chunk = gathering[start_idx:end_idx]
        if not batch_chunk and i > 0:
            break
        batches_list.append({"size": len(batch_chunk)})
        for hit in batch_chunk:
            batch_assignments[hit["chunk_id"]] = i + 1

    rounds_used = min(rounds_limit, max(0, len(batches_list) - 1))

    gaps = list(closure_gaps)
    gaps += [{"path": hit["path"], "chunk_id": hit["chunk_id"], "reason": NOT_GATHERED} for hit in remaining]

    files: dict[str, list[bytes]] = {}

    def span(rel: str, first: int, last: int) -> bytes:
        if rel not in files:
            files[rel] = (root / rel).read_bytes().splitlines(keepends=True)
        return b"".join(files[rel][first - 1:last])

    dropped: dict[str, dict] = {}
    candidates = []
    frontmatter_cache: dict[str, tuple[str | None, str | None]] = {}

    for hit in gathering:
        chunk = chunks[hit["chunk_id"]]
        record_id = record_of.get(chunk["path"])

        # DEC-329, G-19: superseded records
        if record_id is not None and record_id in not_current:
            if chunk["path"] not in dropped:
                dropped[chunk["path"]] = {"path": chunk["path"], "id": record_id, "reason": not_current[record_id]}
            continue

        # DEC-423: files the store could not load — read frontmatter
        if record_id is None:
            rel = chunk["path"]
            if rel not in frontmatter_cache:
                frontmatter_cache[rel] = _frontmatter_status(root, rel)
            fm_id, fm_status = frontmatter_cache[rel]
            if fm_status in ({SUPERSEDED} | MUST_NOT_CITE_STATUSES):
                if rel not in dropped:
                    dropped[rel] = {"path": rel, "id": fm_id or rel, "reason": fm_status}
                continue

        body = span(chunk["path"], chunk["start_line"], chunk["end_line"])
        candidates.append({**chunk, "routes": hit["routes"], "body": body,
                           "text": f"[path: {chunk['path']}]\n{body.decode('utf-8', 'replace')[:RERANK_CHARS]}",
                           "_batch": batch_assignments[hit["chunk_id"]]})

    try:
        ranked = rerank(query, candidates, reranker)
    except (OSError, RuntimeError, ValueError):
        ranked = candidates

    # DEC-424: sort failure/lesson records ahead of other evidence after reranking
    if ahead_paths:
        ahead_ranked = [c for c in ranked if c["path"] in ahead_paths]
        rest_ranked = [c for c in ranked if c["path"] not in ahead_paths]
        ranked = ahead_ranked + rest_ranked

    used = sum(_tokens(candidate["body"].decode("utf-8", "replace")) for candidate in ranked)
    evidence, expansions, expanded = [], [], set()
    for candidate in ranked:
        rel, first, last, body = candidate["path"], candidate["start_line"], candidate["end_line"], candidate["body"]
        parent = lexical.parent(root, candidate["parent_id"])
        if parent and (parent["start_line"], parent["end_line"]) != (first, last) and parent["parent_id"] not in expanded:
            wider = span(rel, parent["start_line"], parent["end_line"])
            cost = _tokens(wider.decode("utf-8", "replace")) - _tokens(body.decode("utf-8", "replace"))
            if used + cost <= limit:
                used, first, last, body = used + cost, parent["start_line"], parent["end_line"], wider
                expanded.add(parent["parent_id"])
                expansions.append({"chunk_id": candidate["chunk_id"], "parent_id": parent["parent_id"], "path": rel,
                                   "start_line": first, "end_line": last})
        evidence.append({"id": record_of.get(rel, candidate["chunk_id"]), "sha256": hashlib.sha256(body).hexdigest(),
                         "path": rel, "start_line": first, "end_line": last, "text": body.decode("utf-8", "replace"),
                         "chunk_id": candidate["chunk_id"], "routes": candidate["routes"],
                         "batch": candidate["_batch"]})

    reasons = {gap["reason"] for gap in gaps}
    if not all(facet["available"] for facet in facets.values()):
        stopping = closures.FACET_UNAVAILABLE
    elif remaining:
        stopping = BUDGET_EXHAUSTED
    elif closures.DEPTH_LIMIT in reasons:
        stopping = closures.DEPTH_LIMIT
    elif closures.UNRESOLVED in reasons:
        stopping = closures.UNRESOLVED_ALONE
    else:
        stopping = closures.COMPLETE if start else SATURATED

    new_offset = offset + len(gathering)
    if remaining:
        token = _encode_continuation(query, tuple(ids), ticket, radius, batch_size, bundle_budget, new_offset)
    else:
        token = None

    bundle = {"stopping_reason": stopping, "evidence": evidence, "batches": batches_list,
              "merge": {"candidates": len(gathering), "duplicates": sum(map(len, routes.values())) - len(fused),
                        "dropped": [dropped[rel] for rel in sorted(dropped)],
                        "reranked": any("rerank_score" in candidate for candidate in ranked)},
              "expansions": expansions, "gaps": gaps, "facets": facets,
              "budget": {"bundle": {"limit": limit, "used": used},
                         "rounds": {"limit": rounds_limit, "used": rounds_used}},
              "continuation": token}
    return bundle
