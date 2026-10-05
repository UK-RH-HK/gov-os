"""``gov launch <role> <ticket> [-- <CLI arguments>]`` as a command module (DEC-231, DEC-317).

A start command, not one of the twelve governance operations. It ends with the
exit code of the session it started. The convention is in ``gov.cli.main``.
"""

from __future__ import annotations

from pathlib import Path

HELP = "start a sandboxed worker session"
CLASS = "act"
PASSTHROUGH = True       # what follows "--" goes to the CLI unchanged
CHILD_EXIT_CODE = True   # the session's exit code is the command's


def add_arguments(parser) -> None:
    parser.usage = "gov launch <role> <ticket> [-- <CLI arguments>]"
    parser.add_argument("worker_role", metavar="<role>", help="engineer, independent-test-designer, "
                        "independent-auditor, research or product-spec")
    parser.add_argument("ticket", metavar="<ticket>", help="an in_progress ticket")


def run(root: Path, args, config: dict) -> int:
    from gov.launch.launcher import launch
    return launch(root, args.worker_role, args.ticket, args.passthrough or [])
