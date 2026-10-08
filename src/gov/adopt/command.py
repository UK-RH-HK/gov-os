"""``gov adopt --lite`` as a command module (W1-41, DEC-090, DEC-517). The convention is in ``gov.cli.main``.

``gov adopt --lite --stage <A0|A1|A2|A3|A4|A5|A6|A8> [--map <file>] [--verdict <path>]`` runs one stage of the
adoption of the project, which commits its evidence record under ``governance/adoption/`` and refuses without the
record of the stage before it. ``gov adopt`` without ``--lite`` stays reserved: the full transaction is Wave 3.
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = ("**",)  # A6 moves and A8 retires what the audited path map names, wherever it lies in the project
STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
_parser = None  # the command's own parser, kept for the usage error of --lite without --stage


def add_arguments(parser) -> None:
    global _parser
    _parser = parser
    parser.add_argument("--lite", action="store_true", help="the Wave 1 adoption: one stage per call")
    parser.add_argument("--stage", choices=STAGES, help="the stage to run")
    parser.add_argument("--map", metavar="<file>", help="A3: the proposal, a YAML file outside the project")
    parser.add_argument("--verdict", metavar="<path>", help="A5: the auditor's committed verdict record")


def run(root: Path, args, config: dict) -> dict:
    if not args.lite:
        from gov.cli.errors import not_implemented
        raise not_implemented("adopt")
    if not args.stage:
        _parser.error("--lite needs --stage, one of " + ", ".join(STAGES))
    from gov.adopt import stages
    return stages.run(Path(root).resolve(), args, config)
