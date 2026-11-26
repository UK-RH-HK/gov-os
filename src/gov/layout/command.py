"""``gov layout check <plan> [--moved] [--root <path>] [--json]`` (W2-213, DEC-1256).

Prints the result itself and ends with its own exit code: 0 clean, 1 findings or stoppers, 2 cannot run. It writes
nothing in the repository. The convention is in ``gov.cli.main``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HELP = "check a repository's layout plan against the standard in the kit (read-only)"
CLASS = "read"
CHILD_EXIT_CODE = True  # 0 clean, 1 findings or stoppers, 2 cannot run
EXIT_CLEAN, EXIT_FINDINGS, EXIT_CANNOT_RUN = 0, 1, 2
CANNOT_RUN = "LAYOUT_CANNOT_RUN"


def add_arguments(parser) -> None:
    parser.usage = "gov layout check <plan> [--moved] [--root <path>] [--json]"
    parser.add_argument("action", choices=["check"], help="check: judge the plan, changing nothing")
    parser.add_argument("plan", metavar="<plan>", help="the plan file, one JSON object a line")
    parser.add_argument("--moved", action="store_true", help="the repository is moved: check it against the plan")


def _envelope(args, ok: bool, result: dict, error: dict | None = None) -> str:
    envelope = {"ok": ok, "command": "layout", "result": result, "session": getattr(args, "session", "")}
    if error is not None:
        envelope["error"] = error
    return json.dumps(envelope)


def run(root: Path, args, config: dict) -> int:
    from gov.cli.errors import GovError
    from gov.layout import CannotRun, engine, render

    try:
        result = engine.run(Path(root), Path(args.plan), after_moves=args.moved)
    except (CannotRun, GovError, OSError) as error:
        message = error.message if isinstance(error, GovError) else str(error)
        if args.json:
            print(_envelope(args, False, {}, {"code": CANNOT_RUN, "message": message, "details": {}}))
        else:
            print(f"gov layout check: {CANNOT_RUN}: {message}", file=sys.stderr)
        return EXIT_CANNOT_RUN
    print(_envelope(args, True, result) if args.json else "\n".join(render.lines(result)))
    return EXIT_FINDINGS if result["findings"] or result["stoppers"] else EXIT_CLEAN
