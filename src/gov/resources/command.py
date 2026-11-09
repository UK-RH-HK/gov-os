"""``gov resources`` as a command module (W2-20). The convention is in ``gov.cli.main``.

- ``gov resources``: the reading (memory, load, busy cores, the servers' CPU p95, the disk, every live Gov OS
  session of the machine-wide registry, the slots, the GPU) and the gate with its named reasons; exit 0, open or shut.
- ``--check [--gpu-need-mib N] [--gpu-kind embedder|reranker|other]``: the start check of one new session; exit 3 and
  ``RESOURCE_GATE_SHUT`` when shut. Without a GPU need it never runs ``nvidia-smi``.
- ``--register PID --ticket ID --session-role ROLE``: enter a session in the registry.
- ``--slot test|rebuild [--tree T] [--workers N] -- CMD...``: run a heavy job in a slot; ``CMD``'s exit code.
- ``--sample`` / ``--remeasure``: one sample; write the measured figures into the configuration file (S9).
- ``--init-config``: write this machine's dated, sourced configuration file, never over an existing one (P-3).
- ``--trip-wire``: one pass of the out-of-memory trip-wire (S11).

It writes only under ``~/.gov-os/machine/``, never the project.
"""

from __future__ import annotations

from pathlib import Path

from gov.launch.gate import EXIT_GATE_SHUT

CLASS = "act"
HELP = "the machine-wide resource gate: memory, load, CPU, disk, the GPU and every live Gov OS session"
ACT_PATHS = ()  # everything it writes is under ~/.gov-os/machine/, outside the project
EXIT_CODES = {EXIT_GATE_SHUT: "the resource gate is shut: no session starts"}
PASSTHROUGH = True       # --slot's command follows "--"
CHILD_EXIT_CODE = True   # --slot ends with its job's exit code
GPU_KINDS = ("embedder", "reranker", "other")


def add_arguments(parser) -> None:
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="the start check: exit 3 when the gate is shut")
    mode.add_argument("--register", metavar="<pid>", type=int, help="enter a session in the machine-wide registry")
    mode.add_argument("--slot", metavar="<kind>", choices=("test", "rebuild"),
                      help="run the command after -- as a heavy job in a slot")
    mode.add_argument("--sample", action="store_true", help="take one memory sample for the re-measure")
    mode.add_argument("--remeasure", action="store_true", help="write the measured figures into the configuration")
    mode.add_argument("--init-config", action="store_true", help="write this machine's configuration file (never "
                      "over an existing one)")
    mode.add_argument("--trip-wire", action="store_true", help="one pass of the out-of-memory trip-wire")
    parser.add_argument("--gpu-need-mib", metavar="<MiB>", type=int, help="the start's declared GPU need")
    parser.add_argument("--gpu-kind", metavar="<kind>", choices=GPU_KINDS, default="other",
                        help="the GPU work's kind for its share (embedder, reranker, other; default other)")
    parser.add_argument("--tree", metavar="<path>", help="a rebuild's tree (default: the root)")
    parser.add_argument("--workers", metavar="<n>", type=int, help="the heavy job's workers (its thread budget)")
    parser.add_argument("--ticket", metavar="<id>", help="the registered session's ticket")
    parser.add_argument("--session-role", metavar="<role>", help="the registered session's role")


def run(root: Path, args, config: dict):
    from gov.cli.errors import GovError

    invalid = lambda message: GovError("RESOURCE_ARGUMENTS_INVALID", message)  # noqa: E731
    if args.slot is None and args.passthrough:
        raise invalid("a command after -- goes with --slot")
    if (args.tree or args.workers is not None) and args.slot is None:
        raise invalid("--tree and --workers go with --slot")
    if (args.ticket or args.session_role) and args.register is None:
        raise invalid("--ticket and --session-role go with --register")
    if args.gpu_need_mib is not None and (args.gpu_need_mib < 1 or not (args.check or _plain(args))):
        raise invalid("--gpu-need-mib is a positive number of MiB, with --check or the reading")
    if args.register is not None:
        from gov.resources.registry import folder, register
        if not (args.ticket and args.session_role):
            raise invalid("--register needs --ticket and --session-role")
        return {"registered": register(args.register, root, args.ticket, args.session_role),
                "registry": str(folder())}
    if args.init_config:
        from gov.resources.config import init
        return init()
    if args.sample:
        from gov.resources.measure import sample
        return sample()
    if args.remeasure:
        from gov.resources.measure import remeasure
        return remeasure()
    if args.trip_wire:
        from gov.resources import config as configuration
        from gov.resources.slots import tripwire
        conf = configuration.load()
        if "oom_floor_bytes" not in conf["values"]:
            named = "; ".join(f["why"] for f in conf["faults"] if f["key"] in ("oom_floor_bytes", configuration.FILE))
            raise GovError("RESOURCE_CONFIG_INVALID", f"the trip-wire needs oom_floor_bytes: {named}",
                           {"faults": conf["faults"]})
        return tripwire(conf["values"])
    if args.slot is not None:
        from gov.resources.slots import run as run_slot
        return run_slot(args.slot, args.passthrough or [], workers=args.workers, tree=args.tree or str(root))
    if args.check:
        from gov.launch.gate import check_start
        return check_start(gpu_need_mib=args.gpu_need_mib, gpu_kind=args.gpu_kind)
    from gov.resources.gate import read
    return read(False, gpu_need_mib=args.gpu_need_mib, gpu_kind=args.gpu_kind)


def _plain(args) -> bool:
    return not any((args.check, args.register is not None, args.init_config, args.sample, args.remeasure,
                    args.trip_wire, args.slot))
