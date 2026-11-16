"""``gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] [--reason <text>]
[--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]`` as a command module (DEC-231, DEC-317; W2-20 S19,
P-1, P-2; W2-184 interface 7.2a).

A start command, not one of the twelve governance operations. It ends with the
exit code of the session it started. The convention is in ``gov.cli.main``.
Every launch passes the machine-wide resource gate: shut, it refuses with exit 3
naming every limit and its reading, unless ``--gate-override`` names the decision
that starts it anyway (written to ``~/.gov-os/machine/launch.log`` and stderr).
``--plan`` (W2-60a; DEC-1167 (2)) prints the role file's default line, ``model <id>, effort <e>``,
and starts nothing: no session, no record, no gate; it refuses as a launch does (exit 1).
``--reason``, ``--trial`` and ``--owner-named`` (W2-184, RUBRIC-2, DEC-1120) go to ``launcher.launch`` as the keywords
``reason``, ``trial`` and ``owner_named``; ``--plan`` does not read them, and written after ``--`` they are CLI arguments.
A lead (``orchestrator``, ``lead``) given any of them is refused here with exit 2, before the launcher (W2-184 R1).
"""

from __future__ import annotations

import sys
from pathlib import Path

from gov.launch.gate import EXIT_GATE_SHUT

HELP = "start a sandboxed worker session"
CLASS = "act"
PASSTHROUGH = True       # what follows "--" goes to the CLI unchanged
CHILD_EXIT_CODE = True   # the session's exit code is the command's
EXIT_CODES = {EXIT_GATE_SHUT: "the resource gate is shut: no session starts"}


def _positive(text: str) -> float:
    """``--projection-usd``: a finite number above 0; anything else is argparse's usage error (exit 2)."""
    import argparse
    import math

    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError(f"a number above 0, not {text!r}")
    return value


def add_arguments(parser) -> None:
    parser.usage = ("gov launch <role> <ticket> [--plan] [--tests-worktree] [--gate-override DEC-NNN] "
                    "[--gpu-need-mib N] [--reason <text>] [--trial <id>] [--owner-named <DEC-id>] "
                    "[--projection-usd N] [-- <CLI arguments>]")
    parser.add_argument("worker_role", metavar="<role>", help="engineer, independent-test-designer, "
                        "independent-auditor, research or product-spec")
    parser.add_argument("ticket", metavar="<ticket>", help="an in_progress ticket")
    parser.add_argument("--gate-override", metavar="DEC-NNN", help="start the session while the resource gate is "
                        "shut, on this decision (logged)")
    parser.add_argument("--gpu-need-mib", metavar="<MiB>", type=int, help="the session's declared GPU need")
    parser.add_argument("--plan", action="store_true", help="print the role file's default line (model <id>, "
                        "effort <e>) and start nothing")
    # W2-60b S10 (DEC-847, DEC-963, DEC-982): the test designer's own tree, made from the ticket's worktree.
    parser.add_argument("--tests-worktree", action="store_true", help="make the ticket's tests worktree "
                        "(<tree>-tests, on <branch>-tests at HEAD), print its path and start nothing")
    # W2-184 (interface 7.2a, the CTO's P-W2-184-2 (a)): RUBRIC-2's options, before "--"; the launcher judges them.
    parser.add_argument("--reason", metavar="<text>", help="why the launch chooses effort max itself (recorded)")
    parser.add_argument("--trial", metavar="<id>", help="the trial (governance/project/trials/<id>.yaml) that "
                        "admits the launch's model and effort")
    parser.add_argument("--owner-named", metavar="<DEC-id>", help="the owner's decision that admits a review "
                        "repeating a recorded setting, or a third review")
    # W2-156 (DEC-1091 (2), DEC-1126 (4)): the projection the runaway brake counts against, on the launch record.
    parser.add_argument("--projection-usd", metavar="<N>", type=_positive, help="the session's projected cost in USD "
                        "(a number above 0; recorded on the launch record; `gov spend` brakes at twice it)")


OPTIONS = (("reason", "--reason"), ("trial", "--trial"), ("owner_named", "--owner-named"))
EXIT_USAGE = 2  # the command line's own usage code (gov.cli.main), as argparse ends a usage error


def run(root: Path, args, config: dict) -> int:
    from gov.launch import launcher
    if getattr(args, "plan", False):
        return launcher.plan(root, args.worker_role, args.ticket)
    if getattr(args, "tests_worktree", False):
        return launcher.tests_worktree(root, args.worker_role, args.ticket)
    # a given option only (an empty one too, for the launcher to refuse); absent, the launcher's default is None
    options = {key: value for key, _ in OPTIONS if (value := getattr(args, key, None)) is not None}
    if args.worker_role in launcher.LEAD_ROLES and options:
        # W2-184 R1 (interface 10.1, DEC-1180 (4)): a usage error, before the launcher: nothing starts or is recorded,
        # the gate is not asked and no plan override is logged. Written after "--" they stay CLI arguments.
        given = ", ".join(flag for key, flag in OPTIONS if key in options)
        print(f"gov launch: error: a lead launch ({args.worker_role}) takes none of --reason, --trial and "
              f"--owner-named; given: {given}", file=sys.stderr)
        return EXIT_USAGE
    projection = getattr(args, "projection_usd", None)
    if args.worker_role in launcher.LEAD_ROLES and projection is not None:
        # W2-156: as the three above: a lead writes no launch record, so it takes no projection
        print(f"gov launch: error: a lead launch ({args.worker_role}) takes no --projection-usd: it writes no "
              f"launch record to hold one", file=sys.stderr)
        return EXIT_USAGE
    return launcher.launch(root, args.worker_role, args.ticket, args.passthrough or [],
                  gate_override=getattr(args, "gate_override", None), gpu_need_mib=getattr(args, "gpu_need_mib", None),
                  **options, **({} if projection is None else {"projection_usd": projection}))
