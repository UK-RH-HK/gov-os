"""``gov spend check | clear <ticket> [--projection-usd N] --note <text> | sum`` as a command module (W2-156).
The convention is in ``gov.cli.main``; the rule is in ``gov.spend.brake``.

- ``sum``: one line per ticket that has a counted session record: the running cost, ``N unknown`` when N sessions' cost
  is not measured, the projection (or ``no projection``) and the brake state (``braked`` or ``not braked``); exit 0.
- ``check``: brakes every ticket whose running cost is more than twice its latest projection and that has no marker:
  one brake record, one marker, one inbox item each; a ticket with no projection is named and never braked; exit 0
  whether or not it brakes. Usage stays record-only (DEC-1089 (3)): no session is stopped, nothing is sent.
- ``clear <ticket> [--projection-usd N] --note <text>``: removes the ticket's marker and restarts its count from now;
  the note and the new projection (if given) go into the brake record.

``--root <path>`` is the project (default: the working directory), before or after the subcommand. A record that cannot
be read is named on standard error and skipped. It writes only under ``.gov-runtime/spend/`` and, on a brake, the one
inbox item.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HELP = "the runaway brake: a ticket past twice its projection holds its next launch (check, clear, sum)"
CLASS = "act"
ACT_PATHS = (".gov-runtime/spend/**", ".gov-runtime/dispatch/inbox/**")
CHILD_EXIT_CODE = True   # the lines are printed here, as text; run returns the exit code


def _positive(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError(f"a number above 0, not {text!r}")
    return value


def _note(text: str) -> str:
    if not text.strip():
        raise argparse.ArgumentTypeError("the note is the reason, not an empty text")
    return text


def add_arguments(parser) -> None:
    # --root also after the subcommand: argparse hands a subparser's value up; SUPPRESS keeps the shared one when absent
    sub = parser.add_subparsers(dest="spend_command", metavar="<check|clear|sum>", required=True)
    for name, text in (("check", "brake every ticket past twice its projection (one record, marker and inbox item)"),
                       ("clear", "lift a ticket's brake and restart its count"),
                       ("sum", "each ticket's cost, projection and brake state, one line each")):
        each = sub.add_parser(name, help=text, allow_abbrev=False)
        each.add_argument("--root", metavar="<path>", default=argparse.SUPPRESS,
                          help="the project (default: the working directory)")
        if name == "clear":
            each.add_argument("ticket", metavar="<ticket>", help="the braked ticket")
            each.add_argument("--projection-usd", metavar="<N>", type=_positive, help="the ticket's new projection")
            each.add_argument("--note", metavar="<text>", type=_note, required=True, help="why the brake is lifted")


def run(root: Path, args, config: dict) -> int:
    from gov.spend import brake

    sub = args.spend_command
    if sub == "clear":
        at, had = brake.clear(root, args.ticket, args.note, getattr(args, "projection_usd", None))
        print(f"spend clear: {args.ticket} {'cleared' if had else 'had no marker'}; its cost counts afresh from {at}")
        return 0
    if sub == "check":
        lines, problems = brake.check(root)
    else:
        tickets, problems = brake.survey(root)
        lines = [brake.sum_line(item) for item in tickets]
    for problem in problems:
        print(f"gov spend: skipped: {problem}", file=sys.stderr)
    print("\n".join(lines))
    return 0
