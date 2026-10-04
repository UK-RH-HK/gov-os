"""``gov check`` (W1-07): a read command. The convention of a command module is in ``gov.cli.main``."""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import not_implemented


def add_arguments(parser) -> None:
    parser.add_argument("--list", action="store_true", help="list the declared checks, without running them")


def run(root: Path, args, config: dict) -> dict:
    if not args.list:
        raise not_implemented("check")  # running checks is W1-26 (DEC-186)
    from gov.cli.checks import load_declarations
    return {"checks": load_declarations(root)}
