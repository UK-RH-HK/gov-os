"""``gov check`` command module (W1-26): runs governance checks or lists declarations.

``gov check --structural [<base>] [--timeout <s>]`` (W2-158) is one cheap, bounded pass over the declared check
families and the new links on a head: plain lines on standard output, exit 0 whatever it finds, 2 only when it cannot
run (``gov.check.structural``). It is a notice, never a refusal; the command ends with that code and prints no envelope.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gov.cli.errors import GovError

EXIT_CODES = {3: "checks failed"}
CHILD_EXIT_CODE = True  # --structural: run returns the pass's own exit code, 0 or 2; gov prints no envelope


def _seconds(text: str) -> float:
    import argparse
    import math
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid number of seconds: {text!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError(f"must be a number of seconds above 0, not {text!r}")
    return value


def add_arguments(parser) -> None:
    parser.add_argument("--list", action="store_true", help="list the declared checks, without running them")
    parser.add_argument("--structural", action="store_true",
                        help="one bounded notice-only pass over the declared check families and the new links")
    parser.add_argument("--timeout", type=_seconds, metavar="<s>",
                        help="--structural: the bound of each check, in seconds (default 50)")
    parser.add_argument("base", nargs="?", metavar="<base>",
                        help="--structural: the revision the change is read from (portability and links need it)")


def _usage(message: str) -> int:
    print(f"gov check: error: {message}", file=sys.stderr)
    return 2


def run(root: Path, args, config: dict) -> dict | int:
    if args.structural:
        if args.list:
            return _usage("--structural cannot be combined with --list")
        from gov.check.structural import DEFAULT_TIMEOUT, run_structural
        return run_structural(Path(root), args.base, DEFAULT_TIMEOUT if args.timeout is None else args.timeout,
                              sys.stdout)
    if args.base is not None or args.timeout is not None:
        return _usage("<base> and --timeout belong to --structural")
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

    for name in sorted(result.get("families", {})):
        fam = result["families"][name]
        status = fam.get("status", "?")
        reason = fam.get("reason", "")
        line = f"  {name}: {status}"
        if reason:
            line += f" ({reason})"
        print(line, file=sys.stderr)

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
