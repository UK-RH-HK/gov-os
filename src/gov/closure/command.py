"""``gov closure`` as a command module (W1-20, DEC-317, DEC-391). The convention is in ``gov.cli.main``.

``gov closure (--depth <N> | --radius <R>) <id>...`` prints the closure of the ids: every record and symbol at
most N hops away, the gaps with their reasons, and the stopping reason. ``--radius`` gives the depth of an impact
radius. It only reads (CAP-27). Exit code 1: ``STORE_MISSING``, no store was loaded.
"""

from __future__ import annotations

from pathlib import Path


def add_arguments(parser) -> None:
    how_far = parser.add_mutually_exclusive_group(required=True)
    how_far.add_argument("--depth", type=int, metavar="<N>", help="hops to follow from the ids")
    how_far.add_argument("--radius", type=int, metavar="<R>", help="the impact radius that gives the depth")
    parser.add_argument("ids", nargs="+", metavar="<id>", help="a record id or a symbol name")


def run(root: Path, args, config: dict) -> dict:
    from gov import closure

    depth = args.depth if args.depth is not None else closure.depth_of_radius(args.radius)
    return closure.closure(root, args.ids, depth)
