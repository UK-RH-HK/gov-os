"""The candidate pool (W2-32 S11; DEC-1071 (2), DEC-1074 (5)): five query-time settings in
``governance/project/retrieval.yaml``, each absent or 0 meaning today's behaviour exactly (``gov.config.loader``
validates them, ``CONFIG_INVALID`` naming ``pool.<key>``):

    pool:
      meaning_uncut: true     # the meaning route's phrasings fused and not cut back to its depth
      route_depth: 60         # the keyword and meaning routes' depth (``lexical.TOP_K``, ``semantic.TOP_K``: 30)
      rerank_depth: 40        # the first 40 fused candidates reranked once; the pages cut from that one order
      per_file_first10: 2     # at most 2 chunks of one file in the first 10 of the final order, the rest after
      drop_nested: true       # an item whose lines lie inside an earlier item's of the same file left out

The measured form is the research harness's v456 (``night/harness/rx.py``: ``sem_uncut``, ``sem_k``/``lex_k``,
``depth``, ``perfile``, ``dedup``); ``retrieve`` builds the same behaviour into its own path. The depth is passed to
each search (``top_k``), never set on a module: one search's setting never reaches another's.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import POOL_FLAGS, POOL_KEYS, RETRIEVAL_FILE, RETRIEVAL_SCHEMA, _load

FIRST = 10  # the head of the final order ``per_file_first10`` holds to
UNPOOLED = -10 ** 9  # the order key of a page's candidate the pool did not rerank: after the pool's, as given
DIGEST_CHARS = 16  # the token's digest of the pool's candidates (their chunk ids, in fused order)


def settings(root: Path) -> dict:
    """The five settings at ``root``: the flags True or False, the others whole numbers (0: off); raises
    CONFIG_INVALID for an invalid file."""
    pool = (_load(Path(root), RETRIEVAL_FILE, RETRIEVAL_SCHEMA) or {}).get("pool") or {}
    return {key: bool(pool.get(key, False)) if key in POOL_FLAGS else int(pool.get(key, 0)) for key in POOL_KEYS}


def capped(ordered: list[dict], cap: int, first: int = FIRST) -> list[dict]:
    """``ordered`` with at most ``cap`` items of one file (``path``) in its first ``first``: each item in order goes
    to the head while the head has room and its file is under the cap, else after the head, in order. None lost."""
    if cap <= 0:
        return list(ordered)
    head, rest, per = [], [], {}
    for item in ordered:
        if len(head) < first and per.get(item["path"], 0) < cap:
            head.append(item)
            per[item["path"]] = per.get(item["path"], 0) + 1
        else:
            rest.append(item)
    return head + rest


def digest(chunk_ids) -> str:
    """The pool's candidates named in a continuation token: a digest of their chunk ids in fused order."""
    return hashlib.sha256("\n".join(chunk_ids).encode()).hexdigest()[:DIGEST_CHARS]


def carried(head: list[dict], order: list[dict] | None, outcome: dict) -> dict:
    """What a continuation token carries of the pool (round 2): ``h`` the candidates' digest, ``o`` the pool's
    order as positions in ``head`` (None: the pool's rerank was not scored, so the question ranks page by page),
    ``b`` and ``d`` who scored and on which device. At most ``rerank_depth`` small numbers: bounded."""
    at = {hit["chunk_id"]: position for position, hit in enumerate(head)}
    return {"h": digest(hit["chunk_id"] for hit in head),
            "o": None if order is None else [at[candidate["chunk_id"]] for candidate in order],
            "b": outcome.get("by"), "d": outcome.get("device")}


def well_formed(value) -> bool:
    """A token's pool part as ``carried`` writes it (its positions checked against the candidates by ``reorder``)."""
    return (isinstance(value, dict) and set(value) == {"h", "o", "b", "d"}
            and isinstance(value["h"], str) and len(value["h"]) == DIGEST_CHARS
            and (value["o"] is None or (isinstance(value["o"], list)
                                        and all(type(n) is int for n in value["o"])))
            and isinstance(value["b"], str) and (value["d"] is None or isinstance(value["d"], str)))


def reorder(head: list[dict], token_pool: dict) -> list[dict] | None:
    """``head`` in the order the earlier call's pool gave (``token_pool``, from ``carried``); None when that pool was
    not scored. A token whose candidates are not this call's (the store or the settings changed) or whose order is no
    order of them is refused: ``CONTINUATION_INVALID``."""
    if token_pool["h"] != digest(hit["chunk_id"] for hit in head):
        raise GovError("CONTINUATION_INVALID",
                       "the continuation's candidate pool is not this question's: the store or the pool settings "
                       "changed since the earlier call") from None
    positions = token_pool["o"]
    if positions is None:
        return None
    if sorted(positions) != list(range(len(head))):
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    return [head[position] for position in positions]


def without_nested(evidence: list[dict]) -> tuple[list[dict], list[dict]]:
    """``evidence`` without each item whose lines lie inside a kept earlier item's of the same file (an equal span
    included), and the items left out."""
    kept, nested = [], []
    for item in evidence:
        if any(other["path"] == item["path"] and other["start_line"] <= item["start_line"]
               and item["end_line"] <= other["end_line"] for other in kept):
            nested.append(item)
        else:
            kept.append(item)
    return kept, nested
