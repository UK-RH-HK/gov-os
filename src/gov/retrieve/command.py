"""``gov retrieve`` as a command module (W1-21, DEC-317, DEC-419). The convention is in ``gov.cli.main``.

``gov retrieve [--ticket <id>] [--id <id>]... [--radius <R>] [--batch-size <N>] [--bundle-budget <N>]
[--continue <token>] <query>`` prints the evidence bundle of ``gov.retrieval.retrieve``. It only reads (CAP-27).
Exit code 1: ``STORE_MISSING``, no store was loaded; ``CONTINUATION_INVALID``, the token is none.
"""

from __future__ import annotations

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


def run(root: Path, args, config: dict) -> dict:
    from gov.retrieval.retrieve import retrieve

    return retrieve(root, args.query, ids=args.ids, ticket=args.ticket, radius=args.radius,
                    batch_size=args.batch_size, bundle_budget=args.bundle_budget, continuation=args.continuation)
