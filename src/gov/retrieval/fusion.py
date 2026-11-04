"""Reciprocal rank fusion of the retrieval routes, and the whole retrieval (W1-19; DEC-379, DEC-374).

``rrf`` merges the routes' ranked lists into one, each chunk once (deduplication by chunk hash: the ``chunk_id`` of
W1-17). ``search`` asks the lexical and the semantic route, fuses them and reranks the head of the merged set once,
as S0b2's R1 does (DEC-406): the first ``RERANK_TOP`` chunks, each scored on its path and its whole text (W2-32 S7). A
route that is unavailable gives no hit and is reported in ``facets``; nothing raises for it. The lexical route's
list is its ``ranked`` chunks: the exact string's first, then the BM25-ranked words' (W2-13, DEC-725).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from gov.retrieval import lexical, semantic
from gov.retrieval.rerank import MAX_REQUEST_CHARS, last_outcome, rerank
from gov.store import STORE_REL

RRF_K = 60
RERANK_TOP = 30  # the fused chunks that are reranked and returned: the first ones, as S0b2's R1 takes them (DEC-406)
# The reranker reads a chunk's path and the whole chunk up to this many characters (W2-32 S7, DEC-1067; was 500):
# the size bound of one request (``rerank.MAX_REQUEST_CHARS``, 24,000), so one chunk can always be sent. The service
# sets no length of its own; its memory is bounded by a request's 16 texts and 24,000 characters, and a pair still
# above the bound (the path and the question added) is read up to it by ``rerank.requests``.
RERANK_LIMIT_CHARS = MAX_REQUEST_CHARS
RERANK_CHARS = RERANK_LIMIT_CHARS
_RECORD = "SELECT c.path, c.start_line, c.end_line, c.parent_id, f.text FROM lexical_chunk c " \
          "JOIN lexical_fts f ON f.rowid = c.id WHERE c.chunk_id = ?"


def rrf(routes: dict[str, list[dict]], k: int = RRF_K) -> list[dict]:
    """One list, best first: each chunk once, with the fields it came with, ``score`` (the sum of ``1 / (k + rank)``
    over the routes that returned it) and ``routes``. Several hits of one route in one chunk count once, at the
    best rank; chunks that score alike keep the order they were first named in."""
    fused: dict[str, dict] = {}
    for name, hits in routes.items():
        chunks: dict[str, dict] = {}
        for hit in hits:
            chunks.setdefault(hit["chunk_id"], hit)
        for rank, (chunk_id, hit) in enumerate(chunks.items(), 1):
            entry = fused.setdefault(chunk_id, {**hit, "score": 0.0, "routes": []})
            entry["score"] += 1 / (k + rank)
            entry["routes"].append(name)
    return sorted(fused.values(), key=lambda entry: -entry["score"])


def _records(root: Path, fused: list[dict]) -> list[dict]:
    """Each fused hit as its chunk record, with the chunk's text. Writes nothing."""
    if not fused:
        return []
    connection = sqlite3.connect((Path(root) / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        keys = ("path", "start_line", "end_line", "parent_id", "text")
        return [{**hit, **dict(zip(keys, connection.execute(_RECORD, (hit["chunk_id"],)).fetchone()))} for hit in fused]
    finally:
        connection.close()


def search(root: Path, query: str, limit: int | None, refresh: bool = True, reranker=None) -> dict:
    """Both routes, fused, and the first ``RERANK_TOP`` fused chunks reranked in one pass; ``hits`` are those
    chunks and ``limit`` cuts after the rerank.

    The reranker scores ``[path: …]`` and the whole chunk (up to ``RERANK_CHARS``, W2-32 S7); a hit keeps the
    chunk's own text. ``reranked`` is false when no reranker could be loaded, or it failed once loaded: the fused
    order is kept (DEC-374), and ``rerank`` names who scored or why none did (W2-32 S4).

    The limit is honoured or refused (W2-32 S5, W2-M103): ``None`` gives the reranked head; a limit up to the cap,
    ``RERANK_TOP``, gives exactly that many distinct chunks, or all there are if fewer. A limit above the cap is
    refused with ``ValueError`` naming the limit and the cap: the routes give at most ``TOP_K`` ranked chunks each
    (W2-13's words, the semantic route's nearest), so more could not be honoured. So is a limit that is not a whole
    number of 0 or more.
    """
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 0):
        raise ValueError(f"fusion.search: the limit must be a whole number of 0 or more, not {limit!r}")
    if limit is not None and limit > RERANK_TOP:
        raise ValueError(f"fusion.search: the limit {limit} is above its cap of {RERANK_TOP} hits (the reranked "
                         f"head); ask for {RERANK_TOP} or fewer")
    answers = {lexical.FACET: lexical.search(root, query, refresh),
               semantic.FACET: semantic.search(root, query, refresh)}
    fused = rrf({name: answer.get("ranked", answer["hits"]) for name, answer in answers.items()})
    records = {record["chunk_id"]: record for record in _records(root, fused[:RERANK_TOP])}
    scored = [{**record, "text": f"[path: {record['path']}]\n{record['text'][:RERANK_CHARS]}"}
              for record in records.values()]
    hits = [{**hit, "text": records[hit["chunk_id"]]["text"]} for hit in rerank(query, scored, reranker)]
    outcome, reranked = last_outcome(), any("rerank_score" in hit for hit in hits)
    return {"hits": hits[:limit],
            "facets": {name: {key: value for key, value in answer.items() if key not in ("hits", "ranked")}
                       for name, answer in answers.items()},
            "reranked": reranked, "rerank": outcome}
