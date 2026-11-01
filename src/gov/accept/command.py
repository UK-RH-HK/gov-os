"""``gov accept <ticket> [--timeout <seconds>]`` as a command module (DEC-959 item 6, DEC-317).

A read command: it runs the ticket's acceptance tests in a child process and reports only pass or fail per
KPI line of the folder's README map, with counts; never a test's name, source, message or output. The
convention is in ``gov.cli.main``; the runner is ``gov.accept.runner``.
"""

from __future__ import annotations

from pathlib import Path

HELP = "run a ticket's acceptance tests, reporting only pass or fail per KPI line"
CLASS = "read"
EXIT_CODES = {3: "a mapped KPI line fails, or any test failed",4: "the run errored (collection, timeout or crash)"}


def add_arguments(parser) -> None:
    parser.usage = "gov accept <ticket> [--timeout <seconds>] [--json] [--root <path>]"
    parser.add_argument("ticket", metavar="<ticket>", help="a ticket id or its WBS id")
    parser.add_argument("--timeout", type=float, default=1800.0, metavar="<seconds>",
                        help="kill the run after this many seconds (default 1800)")


def run(root: Path, args, config: dict):
    from gov.accept.runner import accept
    return accept(root, args.ticket, args.timeout)
