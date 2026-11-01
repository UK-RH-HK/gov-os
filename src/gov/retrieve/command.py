"""``gov retrieve`` as a command module (W1-21, DEC-317, DEC-419). The convention is in ``gov.cli.main``.

``gov retrieve [--ticket <id>] [--id <id>]... [--radius <R>] [--batch-size <N>] [--bundle-budget <N>]
[--continue <token>] <query>`` prints the evidence bundle of ``gov.retrieval.retrieve``. It only reads (CAP-27).
The register's superseded and done entries are left out of it, and its ``left_out`` counts them (W2-55).
Exit code 1: ``STORE_MISSING``, no store was loaded; ``STORE_UNREADABLE``, the store is no database that can be read
(W2-13: never a traceback); ``CONTINUATION_INVALID``, the token is none.

The stated gap (RETR-X-02; AR-9, DEC-900, W2-13). The ids a request names are the question's id-shaped tokens
(``gov.retrieval.lexical.ids_in``), each ``--id`` and the ``--ticket``. When it names some, every one is id-shaped,
and every one exists nowhere (no record has it and no line of the index holds it as a whole token), the request
stops with ``UNRESOLVED_IDS``, each id a gap ``UNRESOLVED``, no evidence and no continuation: nothing unrelated is
offered in its place. The line is drawn at "every": when one named id exists, the request is retrieved as before
(the closure names the missing ones as gaps beside the answer); when one is no id (an ``--id`` that is a symbol name,
for the code index), or a ``--continue`` is given, it is retrieved as before too. When the lexical index cannot
answer, or the record graph cannot be read, nothing is decided here and the request is retrieved as before.
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


def _nowhere(root: Path, query: str, named: list[str] = ()) -> tuple[list[str], dict] | None:
    """The ids the question and ``named`` (the ``--id`` values and the ticket) name, when they name some, all are
    ids and none exists anywhere, with the lexical facet's state; None otherwise, or when that cannot be decided."""
    import sqlite3

    from gov import records
    from gov.cli.errors import GovError
    from gov.retrieval import lexical

    if any(lexical.ids_in(name) != [name] for name in named):
        return None  # a symbol name, or no id: the closure asks the code index for it
    names = list(dict.fromkeys([*lexical.ids_in(query), *named]))
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
    import sqlite3

    from gov.cli.errors import GovError
    from gov.decisions.register import leave_out
    from gov.retrieval.retrieve import retrieve

    if args.continuation is None:
        nowhere = _nowhere(Path(root), args.query, [*args.ids, *([args.ticket] if args.ticket else [])])
        if nowhere is not None:
            return _stated_gap(Path(root), args.query, *nowhere, args)
    try:
        bundle = retrieve(root, args.query, ids=args.ids, ticket=args.ticket, radius=args.radius,
                          batch_size=args.batch_size, bundle_budget=args.bundle_budget,
                          continuation=args.continuation)
    except sqlite3.DatabaseError as error:  # no bundle was made: the store itself cannot be read (W2-M071)
        raise GovError("STORE_UNREADABLE", f"the store at {root} cannot be read: {error}",
                       {"root": str(root), "error": str(error)}) from None
    # W2-55 (DEC-791 item 1): the register's superseded and done entries are left out, and counted
    bundle["evidence"], left_out = leave_out(root, bundle["evidence"])
    if left_out:
        bundle["left_out"] = left_out
    return bundle
