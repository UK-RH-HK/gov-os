"""Routing by question type (W2-32 S8, DEC-1067 (a)): after the rerank, a question that names a symbol has the code
route's first hits ahead, and a question that names a record has that record's best chunks ahead.

Each half has its own setting in ``governance/project/retrieval.yaml`` (``gov.config.loader`` validates it):

    routing:
      code_first: 2    # a question naming a symbol: the code route's first 2 hits ahead
      named_first: 2   # a question naming a record: that record's 2 best chunks ahead

The settings are read before any search work, so an invalid file is refused first; a ``routing:`` block with no
keys is off (review S8-F4). Absent or 0, a half is off and the page is in today's order, nothing more asked
(DEC-1067: each half kept only if it holds at its measure, on the visible half alone). The measured form is the research harness's (``rx.py``,
variants r01 and s01):

- **code:** the code route's hits (the question names a symbol the code graph holds), ranked by their stored
  vectors' cosine to the question's (``semantic.distances``; with no vector to compare, the route's own order)
  before they enter the fusion, as r01's ``code: sem`` (review S8-F1); its first ``code_first``, those on the page,
  go first after the rerank.
- **named:** the closure's chunks of the records the question names (its ``--ticket``, its ``--id``s and the record
  route's start ids) that are on the page, ranked by the scores the page's rerank gave them (no request of its own,
  P-W2-32-9: the rerank stays one of the merged set in full requests of 16); the first ``named_first`` go first.
- Both on, for a question naming both: the code route's first, then the named record's, then the rest.

**The phrasings** (``routing.phrasings: true``; DEC-1067 order (4), measure 3's x5, the harness's ``phrasings``
variant): the lexical and the semantic route are each asked three deterministic phrasings (``phrasings``: the
question, its content words, the question with the record ids the record route resolves), and each route's lists are
fused by RRF (``fused``; the semantic route's cut to its ``TOP_K``); a phrasing a route cannot answer leaves that
route the question's own answer. The other routes, the fusion across routes, the one rerank of the merged pool (in
requests within ``rerank``'s bounds) and the two halves above then run as they do.
"""

from __future__ import annotations

from pathlib import Path

import re

from gov.config.loader import RETRIEVAL_FILE, RETRIEVAL_SCHEMA, ROUTING_FLAGS, ROUTING_KEYS, _load

CODE, NAMED = "code", "named"


def settings(root: Path) -> dict:
    """``code_first`` and ``named_first`` (0: off) and ``phrasings`` (False: off) at ``root``; raises CONFIG_INVALID
    for an invalid file."""
    routing = (_load(Path(root), RETRIEVAL_FILE, RETRIEVAL_SCHEMA) or {}).get("routing") or {}  # this file alone
    return {key: bool(routing.get(key, False)) if key in ROUTING_FLAGS else int(routing.get(key, 0))
            for key in ROUTING_KEYS}


# The phrasings (DEC-1067 order (4), measure 3's x5), in the research harness's measured form (``night/harness/rx.py``,
# variant ``phrasings``): no model call, the same words the harness drops.
STOPWORDS = frozenset("a an the of in on at to for by with from and or is are was were be been do does did which what "
                      "who whom whose where when why how may must can could should would will shall it its this that "
                      "these those there their they them as into about before after than then".split())
RRF_K = 60.0


def phrasings(query: str, named: list[str]) -> list[str]:
    """The question; its content words (no stopwords, no question mark); and the question with the record ids the
    record route resolves (``named``) appended, those it does not already hold. Each once, none empty."""
    words = [word for word in re.findall(r"[\w./-]+", query) if word.lower() not in STOPWORDS]
    extra = [record_id for record_id in named if record_id not in query]
    out = [query, " ".join(words), query + (" " + " ".join(extra) if extra else "")]
    return list(dict.fromkeys(phrasing for phrasing in out if phrasing.strip()))


def fused(lists: list[list[dict]], k: float = RRF_K) -> list[dict]:
    """The phrasings' lists of one route made one, as the harness does: reciprocal rank fusion, ``1 / (k + rank)``
    summed over the lists, each chunk once a list at its best rank, kept as first seen; ties in the order first met."""
    score: dict[str, float] = {}
    first: dict[str, dict] = {}
    for hits in lists:
        seen: set[str] = set()
        for rank, hit in enumerate(hits, 1):
            if hit["chunk_id"] in seen:
                continue
            seen.add(hit["chunk_id"])
            score[hit["chunk_id"]] = score.get(hit["chunk_id"], 0.0) + 1 / (k + rank)
            first.setdefault(hit["chunk_id"], hit)
    return [first[chunk_id] for chunk_id in sorted(score, key=lambda chunk_id: -score[chunk_id])]


def firsts(ordered_ids: list[str], count: int) -> list[str]:
    """The first ``count`` chunks of a route's order, each once."""
    return list(dict.fromkeys(ordered_ids))[:count] if count > 0 else []


def ahead(page: list[dict], lead: list[str]) -> tuple[list[dict], list[str]]:
    """``page`` with the chunks ``lead`` names, those on it, first in that order; and those moved."""
    on_page = {candidate["chunk_id"] for candidate in page}
    moved = [chunk_id for chunk_id in lead if chunk_id in on_page]
    by_id = {candidate["chunk_id"]: candidate for candidate in page}
    return [by_id[chunk_id] for chunk_id in moved] + [c for c in page if c["chunk_id"] not in moved], moved
