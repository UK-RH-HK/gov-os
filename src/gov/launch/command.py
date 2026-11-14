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
                    "[--reason <text>] [--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]")
    parser.add_argument("worker_role", metavar="<role>", help="engineer, independent-test-designer, "
                        "independent-auditor, research or product-spec")
    parser.add_argument("ticket", metavar="<ticket>", help="an in_progress ticket")
    parser.add_argument("--gate-override", metavar="DEC-NNN", help="start the session while the resource gate is "
                        "shut, on this decision (logged)")
    parser.add_argument("--gpu-need-mib", metavar="<MiB>", type=int, help="the session's declared GPU need")
    parser.add_argument("--plan", action="store_true", help="print the role file's default line (model <id>, "
                        "effort <e>) and start nothing")
    # W2-184 (interface 7.2a, the CTO's P-W2-184-2 (a)): RUBRIC-2's options, before "--"; the launcher judges them.
    parser.add_argument("--reason", metavar="<text>", help="why the launch chooses effort max itself (recorded)")
    parser.add_argument("--trial", metavar="<id>", help="the trial (governance/project/trials/<id>.yaml) that "
                        "admits the launch's model and effort")
    parser.add_argument("--owner-named", metavar="<DEC-id>", help="the owner's decision that admits a review "
                        "repeating a recorded setting, or a third review")


def run(root: Path, args, config: dict) -> int:
    from gov.launch import launcher
    if getattr(args, "plan", False):
        return launcher.plan(root, args.worker_role, args.ticket)
    # a given option only (an empty one too, for the launcher to refuse); absent, the launcher's default is None
    options = {key: value for key in ("reason", "trial", "owner_named")
               if (value := getattr(args, key, None)) is not None}
    return launcher.launch(root, args.worker_role, args.ticket, args.passthrough or [],
                  gate_override=getattr(args, "gate_override", None), gpu_need_mib=getattr(args, "gpu_need_mib", None),
                  **options)
