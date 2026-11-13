"""``gov plan [--open | --tickets <id> ...] [--json] [--ready <file>]`` (W2-136, DEC-1088).

Prints the plan itself and ends with its own exit code: 0 a plan, 1 a plan with findings, 2 cannot run. Under
``--json`` the shared envelope ``{ok, command, result, error?, session}``. Nothing is written without ``--ready``.
The convention is in ``gov.cli.main``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HELP = "the dependency map and the launch batches it proposes (read-only; --ready writes the ready list)"
CLASS = "act"            # --ready writes the file it names; nothing else is written
CHILD_EXIT_CODE = True   # the plan's own exit codes: 0 a plan, 1 a plan with findings, 2 cannot run
EXIT_PLAN, EXIT_FINDINGS, EXIT_CANNOT_RUN = 0, 1, 2
CANNOT_RUN = "PLAN_CANNOT_RUN"


def add_arguments(parser) -> None:
    parser.usage = "gov plan [--open | --tickets <id> ...] [--json] [--ready <file>]"
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--open", action="store_true", help="every open and in-progress ticket (the default)")
    which.add_argument("--tickets", nargs="+", metavar="<id>", help="these tickets only (ids or WBS ids)")
    parser.add_argument("--ready", metavar="<file>", help="write the batches in the dispatcher's ready-list form")


def _envelope(args, ok: bool, result: dict, error: dict | None = None) -> str:
    envelope = {"ok": ok, "command": "plan", "result": result, "session": getattr(args, "session", "")}
    if error is not None:
        envelope["error"] = error
    return json.dumps(envelope)


def run(root: Path, args, config: dict) -> int:
    from gov.plan import render
    from gov.plan.derive import make_plan
    from gov.plan.tickets import PlanError

    try:
        plan = make_plan(Path(root), selected=args.tickets or None)
        if args.ready:
            render.write_ready(plan, Path(args.ready))
    except (PlanError, OSError) as error:
        message = str(error) if isinstance(error, PlanError) else f"--ready {args.ready}: {error}"
        if args.json:
            print(_envelope(args, False, {}, {"code": CANNOT_RUN, "message": message, "details": {}}))
        else:
            print(f"gov plan: {CANNOT_RUN}: {message}", file=sys.stderr)
        return EXIT_CANNOT_RUN
    if args.json:
        result = render.result(plan)
        if args.ready:
            result["ready"] = str(args.ready)
        print(_envelope(args, True, result))
    else:
        print("\n".join(render.lines(plan)))
    return EXIT_FINDINGS if render.has_findings(plan) else EXIT_PLAN
