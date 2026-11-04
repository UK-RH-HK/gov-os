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
"""

from __future__ import annotations

from pathlib import Path

from gov.config.loader import RETRIEVAL_FILE, RETRIEVAL_SCHEMA, ROUTING_KEYS, _load

CODE, NAMED = "code", "named"


def settings(root: Path) -> dict[str, int]:
    """``code_first`` and ``named_first`` at ``root`` (0: off); raises CONFIG_INVALID for an invalid file."""
    routing = (_load(Path(root), RETRIEVAL_FILE, RETRIEVAL_SCHEMA) or {}).get("routing") or {}  # this file alone
    return {key: int(routing.get(key, 0)) for key in ROUTING_KEYS}


def firsts(ordered_ids: list[str], count: int) -> list[str]:
    """The first ``count`` chunks of a route's order, each once."""
    return list(dict.fromkeys(ordered_ids))[:count] if count > 0 else []


def ahead(page: list[dict], lead: list[str]) -> tuple[list[dict], list[str]]:
    """``page`` with the chunks ``lead`` names, those on it, first in that order; and those moved."""
    on_page = {candidate["chunk_id"] for candidate in page}
    moved = [chunk_id for chunk_id in lead if chunk_id in on_page]
    by_id = {candidate["chunk_id"]: candidate for candidate in page}
    return [by_id[chunk_id] for chunk_id in moved] + [c for c in page if c["chunk_id"] not in moved], moved
