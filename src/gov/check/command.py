"""``gov check`` command module (W1-26): runs governance checks or lists declarations."""

from __future__ import annotations

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
