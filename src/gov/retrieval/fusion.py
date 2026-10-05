"""Reciprocal rank fusion of the retrieval routes, and the whole retrieval (W1-19; DEC-379, DEC-374).

``rrf`` merges the routes' ranked lists into one, each chunk once (deduplication by chunk hash: the ``chunk_id`` of
W1-17). ``search`` asks the lexical and the semantic route, fuses them and reranks the merged set once. A route
that is unavailable gives no hit and is reported in ``facets``; nothing raises for it.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from gov.retrieval import lexical, semantic
from gov.retrieval.rerank import rerank
from gov.store import STORE_REL

RRF_K = 60
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
    """Each fused hit as its chunk record, with the chunk's text for the reranker. Writes nothing."""
    if not fused:
        return []
    connection = sqlite3.connect((Path(root) / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        keys = ("path", "start_line", "end_line", "parent_id", "text")
        return [{**hit, **dict(zip(keys, connection.execute(_RECORD, (hit["chunk_id"],)).fetchone()))} for hit in fused]
    finally:
        connection.close()


def search(root: Path, query: str, limit: int | None, refresh: bool = True, reranker=None) -> dict:
    """Both routes, fused, and reranked in one pass over the merged set; ``limit`` cuts after the rerank.

    ``reranked`` is false when no reranker could be loaded: the fused order is kept (DEC-374).
    """
    answers = {lexical.FACET: lexical.search(root, query, refresh),
               semantic.FACET: semantic.search(root, query, refresh)}
    fused = rrf({name: answer["hits"] for name, answer in answers.items()})
    hits = rerank(query, _records(root, fused), reranker)
    return {"hits": hits[:limit],
            "facets": {name: {key: value for key, value in answer.items() if key != "hits"}
                       for name, answer in answers.items()},
            "reranked": any("rerank_score" in hit for hit in hits)}
