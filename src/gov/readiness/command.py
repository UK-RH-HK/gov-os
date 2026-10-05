"""``gov readiness`` as a command module (W1-13, DEC-317). The convention is in ``gov.cli.main``.

- ``gov readiness --specification <record id>`` judges one specification from its readiness rows (DEC-348).
- ``gov readiness --ticket <ticket id>`` judges the specification the ticket names (DEC-307).
- ``gov readiness`` judges every specification, and passes only when each of them does.

It only reads (CAP-27). Exit code 0: no required row is open; 3: ``SPEC_NOT_CLOSED``, the report in
``error.details``; 1: ``READINESS_INVALID``, or no such specification (DEC-351).
"""

from __future__ import annotations

from pathlib import Path

EXIT_OPEN = 3
EXIT_CODES = {EXIT_OPEN: "a readiness row the profile requires is open"}


def add_arguments(parser) -> None:
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--specification", metavar="<record id>", help="the specification to judge")
    which.add_argument("--ticket", metavar="<ticket id>", help="judge the specification this ticket names")


def run(root: Path, args, config: dict) -> dict:
    from gov.readiness import checker

    if args.ticket is not None:
        return checker.check(root, checker.of_ticket(root, args.ticket))
    if args.specification is not None:
        return checker.check(root, args.specification)
    return checker.check_all(root)
