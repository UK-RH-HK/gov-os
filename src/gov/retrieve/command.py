"""``gov retrieve`` as a command module (W1-21, DEC-317, DEC-419). The convention is in ``gov.cli.main``.

``gov retrieve [--ticket <id>] [--id <id>]... [--radius <R>] [--batch-size <N>] [--bundle-budget <N>]
[--continue <token>] <query>`` prints the evidence bundle of ``gov.retrieval.retrieve``. It only reads (CAP-27).
The register's superseded and done entries are left out of it, and its ``left_out`` counts them (W2-55).
Exit code 1: ``STORE_MISSING``, no store was loaded; ``CONTINUATION_INVALID``, the token is none.

The stated gap (RETR-X-02; AR-9, DEC-900, W2-13): a question asked alone (no ``--ticket``, no ``--id``) whose
id-shaped tokens (``gov.retrieval.lexical.ids_in``) all exist nowhere, no record having one and no line of the index
holding one as a whole token, stops with ``UNRESOLVED_IDS``, each id a gap ``UNRESOLVED`` and no evidence: nothing
unrelated is offered in its place. When the lexical index cannot answer, or the record graph cannot be read, it is
not decided here and the question is retrieved as before.
"""

from __future__ import annotations

import re
from pathlib import Path


def add_arguments(parser) -> None:
    parser.add_argument("--ticket", metavar="<id>", help="a ticket to close over")
    parser.add_argument("--id", dest="ids", action="append", default=[], metavar="<id>",
                        help="a record id or a symbol name to close over; may be repeated")
    parser.add_argument("--radius", type=int, default=0, metavar="<R>", help="the impact radius (default 0)")
    parser.add_argument("--batch-size", type=int, metavar="<N>", help="candidates in a batch")
    parser.add_argument("--bundle-budget", type=int, metavar="<N>", help="tokens the bundle may hold after expansion")
    parser.add_argument("--continue", dest="continuation", metavar="<token>", help="the token of an earlier bundle")
    parser.add_argument("query", metavar="<query>", help="the question")


def _nowhere(root: Path, query: str) -> tuple[list[str], dict] | None:
    """The ids the question names, when it names some and none exists anywhere, with the lexical facet's state;
    None otherwise, or when that cannot be decided."""
    import sqlite3

    from gov import records
    from gov.cli.errors import GovError
    from gov.retrieval import lexical

    names = lexical.ids_in(query)
    if not names:
        return None
    try:
        if set(names) & {record["id"] for record in records.records(root)}:
            return None
    except (sqlite3.Error, GovError):
        return None  # no record graph: the retrieval says so itself
    for name in names:
        answer = lexical.search(root, name, refresh=False)
        if not answer["available"]:
            return None
        whole = re.compile(rf"(?<![\w-]){re.escape(name)}(?![\w]|-\w)")
        if any(whole.search(hit["text"]) for hit in answer["hits"]):
            return None
    return names, {"available": True, "reason": None}


def _stated_gap(root: Path, query: str, names: list[str], lexical_facet: dict, args) -> dict:
    """The bundle that states the gap: no evidence, each id a gap, ``UNRESOLVED_IDS``."""
    from gov import closure
    from gov.retrieval import retrieve, semantic

    answer = semantic.search(root, query, refresh=False)  # asked for its state only: its hits are not offered
    rounds = retrieve.ROUNDS_BY_RADIUS.get(args.radius, retrieve.ROUNDS_BY_RADIUS[4])
    return {"stopping_reason": closure.UNRESOLVED_ALONE, "evidence": [], "batches": [{"size": 0}],
            "merge": {"candidates": 0, "duplicates": 0, "dropped": [], "reranked": False},
            "expansions": [], "gaps": [{"id": name, "reason": closure.UNRESOLVED} for name in names],
            "facets": {"lexical": lexical_facet,
                       semantic.FACET: {"available": answer["available"], "reason": answer["reason"]}},
            "budget": {"bundle": {"limit": retrieve.BUNDLE_BUDGET if args.bundle_budget is None
                                  else args.bundle_budget, "used": 0},
                       "rounds": {"limit": rounds, "used": 0}},
            "continuation": None}


def run(root: Path, args, config: dict) -> dict:
    from gov.decisions.register import leave_out
    from gov.retrieval.retrieve import retrieve

    if args.ticket is None and not args.ids and args.continuation is None:
        nowhere = _nowhere(Path(root), args.query)
        if nowhere is not None:
            return _stated_gap(Path(root), args.query, *nowhere, args)
    bundle = retrieve(root, args.query, ids=args.ids, ticket=args.ticket, radius=args.radius,
                      batch_size=args.batch_size, bundle_budget=args.bundle_budget, continuation=args.continuation)
    # W2-55 (DEC-791 item 1): the register's superseded and done entries are left out, and counted
    bundle["evidence"], left_out = leave_out(root, bundle["evidence"])
    if left_out:
        bundle["left_out"] = left_out
    return bundle
