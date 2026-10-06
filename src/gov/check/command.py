"""``gov check`` command module (W1-26): runs governance checks or lists declarations."""

from __future__ import annotations

import sys
from pathlib import Path

from gov.cli.errors import GovError

EXIT_CODES = {3: "checks failed"}


def add_arguments(parser) -> None:
    parser.add_argument("--list", action="store_true", help="list the declared checks, without running them")


def run(root: Path, args, config: dict) -> dict:
    if args.list:
        from gov.cli.checks import load_declarations
        return {"checks": load_declarations(root)}

    from gov.check.runner import run_checks
    result, has_hard_block_red = run_checks(root)

    uncovered = [
        name for name, fam in result.get("families", {}).items()
        if fam.get("reason") == "no registered check"
    ]
    if uncovered:
        print("families with no registered check: " + ", ".join(uncovered), file=sys.stderr)

    if has_hard_block_red:
        red_families = [
            name for name, fam in result.get("families", {}).items()
            if fam.get("status") == "RED"
        ]
        msg = "one or more hard-block checks failed"
        if red_families:
            msg += ": " + ", ".join(red_families)
        raise GovError("CHECK_FAILED", msg,
                        details=result, exit_code=3)
    return result
