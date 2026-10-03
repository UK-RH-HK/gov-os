"""The ``gov`` command line: command registry, API-0002 envelope and exit codes (W1-07).

Every command prints the envelope ``{ok, command, result, error?, session}``
under ``--json`` and ends with exit code 0 (success), 1 (governance error, a
GovError code in the JSON) or 2 (usage error). Codes 3 and 4 belong to
verification and control state, which later tickets build.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from gov.cli.errors import GovError

EXIT_OK, EXIT_GOV_ERROR, EXIT_USAGE = 0, 1, 2  # argparse ends a usage error with 2 itself


def _status(root: Path, args, config: dict) -> dict:
    return {"root": str(root), "config_files": sorted(config)}


def _check(root: Path, args, config: dict) -> dict:
    if not args.list:
        raise _not_implemented("check")  # running checks is W1-26 (DEC-186)
    from gov.cli.checks import load_declarations
    return {"checks": load_declarations(root)}


@dataclass(frozen=True)
class Command:
    name: str
    cls: str                          # "read" or "act"; internal until W1-26 (DEC-187)
    help: str
    handler: Callable | None = None   # None: reserved, not built yet
    act_paths: tuple = ()             # where an act command may write; a read command writes nowhere


# The Wave 1 governance operations (CAP-28.b). Read commands are those of CAP-27's acceptance line.
COMMANDS = (
    Command("status", "read", "tickets, gates, readiness, share, pause state", _status),
    Command("check", "read", "list the declared checks (--list); running them is not built yet", _check),
    Command("readiness", "read", "readiness of a ticket or a gate"),
    Command("doctor", "read", "health of the installation and the project"),
    Command("rebuild", "act", "rebuild derived state"),
    Command("context", "read", "the context for a ticket (--dry-run)"),
    Command("closure", "read", "the lineage of a feature and its missing links"),
    Command("retrieve", "read", "retrieve records"),
    Command("checkpoint", "act", "write a checkpoint"),
    Command("close", "act", "close a ticket"),
    Command("adopt", "act", "adopt a project"),
    Command("pause", "act", "pause or resume governed work"),
)
REGISTRY = {command.name: command for command in COMMANDS}


def _not_implemented(name: str) -> GovError:
    return GovError("NOT_IMPLEMENTED", f"gov {name} is reserved and not built yet", {"command": name})


def _parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    shared.add_argument("--json", action="store_true", help="structured output (the API-0002 envelope)")
    shared.add_argument("--root", metavar="<path>", help="the project (default: the working directory)")
    shared.add_argument("--session", metavar="<id>", default="", help="the session id the envelope carries")
    shared.add_argument("--role", metavar="<role>", help="the role of the caller")
    parser = argparse.ArgumentParser(prog="gov", description="Governance OS command line.", allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for command in COMMANDS:
        sub = commands.add_parser(command.name, help=command.help, parents=[shared], allow_abbrev=False)
        if command.name == "check":
            sub.add_argument("--list", action="store_true", help="list the declared checks, without running them")
    return parser


def _emit(args, ok: bool, result: dict, error: GovError | None) -> None:
    if args.json:
        envelope = {"ok": ok, "command": args.command, "result": result, "session": args.session}
        if error is not None:
            envelope["error"] = {"code": error.code, "message": error.message, "details": error.details}
        print(json.dumps(envelope))
    elif error is not None:
        print(f"gov {args.command}: {error.code}: {error.message}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args, extra = parser.parse_known_args(argv)
    command = REGISTRY[args.command]
    if extra and command.handler is not None:  # a command not built yet has no arguments to check against
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    root = Path(args.root) if args.root else Path.cwd()
    try:
        from gov.config.loader import load_config
        config = load_config(root)  # every command loads the configuration first (DEC-185)
        if command.handler is None:
            raise _not_implemented(command.name)
        result = command.handler(root, args, config)
    except GovError as error:
        _emit(args, False, {}, error)
        return EXIT_GOV_ERROR
    _emit(args, True, result, None)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
