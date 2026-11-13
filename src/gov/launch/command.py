"""``gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] [-- <CLI arguments>]`` as a
command module (DEC-231, DEC-317; W2-20 S19, P-1, P-2).

A start command, not one of the twelve governance operations. It ends with the
exit code of the session it started. The convention is in ``gov.cli.main``.
Every launch passes the machine-wide resource gate: shut, it refuses with exit 3
naming every limit and its reading, unless ``--gate-override`` names the decision
that starts it anyway (written to ``~/.gov-os/machine/launch.log`` and stderr).
``--plan`` (W2-60a; DEC-1167 (2)) prints the role file's default line, ``model <id>, effort <e>``,
and starts nothing: no session, no record, no gate; it refuses as a launch does (exit 1).
"""

from __future__ import annotations

from pathlib import Path

from gov.launch.gate import EXIT_GATE_SHUT

HELP = "start a sandboxed worker session"
CLASS = "act"
PASSTHROUGH = True       # what follows "--" goes to the CLI unchanged
CHILD_EXIT_CODE = True   # the session's exit code is the command's
EXIT_CODES = {EXIT_GATE_SHUT: "the resource gate is shut: no session starts"}


def add_arguments(parser) -> None:
    parser.usage = ("gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] "
                    "[-- <CLI arguments>]")
    parser.add_argument("worker_role", metavar="<role>", help="engineer, independent-test-designer, "
                        "independent-auditor, research or product-spec")
    parser.add_argument("ticket", metavar="<ticket>", help="an in_progress ticket")
    parser.add_argument("--gate-override", metavar="DEC-NNN", help="start the session while the resource gate is "
                        "shut, on this decision (logged)")
    parser.add_argument("--gpu-need-mib", metavar="<MiB>", type=int, help="the session's declared GPU need")
    parser.add_argument("--plan", action="store_true", help="print the role file's default line (model <id>, "
                        "effort <e>) and start nothing")


def run(root: Path, args, config: dict) -> int:
    from gov.launch import launcher
    if getattr(args, "plan", False):
        return launcher.plan(root, args.worker_role, args.ticket)
    return launcher.launch(root, args.worker_role, args.ticket, args.passthrough or [],
                  gate_override=getattr(args, "gate_override", None), gpu_need_mib=getattr(args, "gpu_need_mib", None))
