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

from pathlib import Path

from gov.config.loader import POOL_FLAGS, POOL_KEYS, RETRIEVAL_FILE, RETRIEVAL_SCHEMA, _load

FIRST = 10  # the head of the final order ``per_file_first10`` holds to
UNPOOLED = -10 ** 9  # the order key of a page's candidate the pool did not rerank: after the pool's, as given


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
