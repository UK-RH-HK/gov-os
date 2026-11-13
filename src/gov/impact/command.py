"""``gov impact`` as a command module (W2-37; CAP-33.b, CAP-33.g, DEC-167). The convention is in ``gov.cli.main``.

``gov impact [--out <path>] <change>...`` prints the impact assessment of a stated change (record ids, symbol names,
or one question "What's the impact of X?") and its CIT-P; ``--out`` also writes the CIT-P as a record file, the one
file the command writes. ``gov impact --compare <CIT-E path>`` checks a change-execution record against the
change-impact proposal it names. It only reads otherwise. A refusal is exit code 1.
"""

from __future__ import annotations

from pathlib import Path

HELP = "the impact of a change over the record and code graphs (a CIT-P), or a CIT-E checked against its CIT-P"
CLASS = "read"


def add_arguments(parser) -> None:
    parser.add_argument("--out", metavar="<path>", help="also write the CIT-P as a record file at <path>")
    parser.add_argument("--compare", metavar="<CIT-E path>",
                        help="check a change-execution record against the change-impact proposal it names")
    parser.add_argument("changes", nargs="*", metavar="<change>",
                        help="a record id, a symbol name, or one question: \"What's the impact of X?\"")


def run(root: Path, args, config: dict) -> dict:
    from gov import impact
    from gov.cli.errors import GovError

    if args.compare is not None:
        if args.changes or args.out is not None:
            raise GovError("IMPACT_USAGE", "--compare takes a CIT-E path alone: no stated change and no --out")
        return impact.compare(root, args.compare)
    return impact.assess(root, args.changes, config, out=args.out)
