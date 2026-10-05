"""The one rerank over the merged candidate set (W1-19; DEC-379, DEC-374; ADR-0002 §2).

A reranker is given as its loader: a function without arguments that returns ``score(query, texts)``, one number
per text, higher is better. The loader is called at the first rerank and not before, so nothing of a model is
loaded by importing this module or by a retrieval that has nothing to rerank. A loader that returns None says the
reranker cannot be loaded: the order given is kept and no candidate carries a score.
"""

from __future__ import annotations

# The pins of ADR-0002 §2; the index manifest records them.
MODEL = "Qwen/Qwen3-Reranker-0.6B"
REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"


def default_reranker():
    """The loader of the pinned reranker, which runs as a separate, pinned process (ADR-0002 §2).

    How that process is started (which interpreter, which command) is not decided (DEC-384), so there is none to
    load today and the answer is None. The decision changes this function and nothing else.
    """
    return None


def rerank(query: str, candidates: list[dict], reranker=None) -> list[dict]:
    """``candidates`` in the order of the reranker's scores, each with ``rerank_score``; equal scores keep the order
    given. One call of ``score``, with the ``text`` of every candidate. Without a reranker the candidates are returned
    as given."""
    candidates = [dict(candidate) for candidate in candidates]
    score = (reranker or default_reranker)() if candidates else None
    if score is None:
        return candidates
    scores = [float(value) for value in score(query, [candidate["text"] for candidate in candidates])]
    ranked = sorted(zip(scores, candidates, strict=True), key=lambda pair: -pair[0])
    return [{**candidate, "rerank_score": value} for value, candidate in ranked]
