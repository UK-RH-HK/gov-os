"""The ``gov`` command line: reserved commands, command modules, API-0002 envelope and exit codes (W1-07, DEC-317).

Every command prints the envelope ``{ok, command, result, error?, session}``
under ``--json``. This file knows the twelve reserved names (CAP-28.b), their
class and their help line. Everything else about a command comes from its own
module, so a command ticket does not change this file.

The convention of a command module
----------------------------------

**Where.** ``gov <command>`` is built by the file ``src/gov/<command>/command.py``
(module ``gov.<command>.command``; the directory is a package, with an
``__init__.py``). ``gov checkpoint`` is ``src/gov/checkpoint/command.py``. A
reserved command with no such file answers ``NOT_IMPLEMENTED`` (exit code 1).
A file for a name that is not reserved adds that command (``gov launch``).
(``status`` and ``check`` alone live in ``src/gov/cli/commands/<command>.py``.)

**What the module exposes.** Only ``run`` is required.

- ``run(root, args, config)``: the handler. ``root`` is the project as a
  ``pathlib.Path``, ``config`` the loaded configuration (a dict), ``args`` the
  ``argparse.Namespace``: the module's own arguments, plus ``json`` (bool),
  ``root``, ``session`` (str), ``role``, ``command`` and ``passthrough``.
- ``add_arguments(parser)``: adds the command's own arguments to its
  ``argparse`` parser (``parser.add_argument("--watch", ...)``). ``--json``,
  ``--root``, ``--session``, ``--role`` and ``-h`` are there already.
- ``ACT_PATHS``: a tuple of path patterns, relative to the project, where an
  act command may write. A read command declares none.
- ``EXIT_CODES``: a dict ``{code: meaning}`` of the command's own exit codes,
  each an int from 3 to 255. **0, 1 and 2 are reserved** to the command line
  (success, governance error, usage error) and may not be declared.
- ``PASSTHROUGH = True``: the command takes what follows ``--`` on the command
  line, unparsed, as the list ``args.passthrough`` (``None`` without ``--``).
  Without it, ``--`` is a usage error.
- ``CHILD_EXIT_CODE = True``: ``run`` may return an int, the exit code of a
  process it ran; ``gov`` ends with it and prints no envelope.
- ``HELP`` (a line for ``gov --help``) and ``CLASS`` (``"read"`` or ``"act"``,
  default ``"act"``): read only for a name that is not reserved.

**What ``run`` returns or raises.**

- a dict: the envelope's ``result``, ``ok: true``, exit code 0;
- a tuple ``(result, code)``, ``code`` declared in ``EXIT_CODES``: the same
  envelope, and ``gov`` ends with ``code``;
- ``raise GovError(code, message, details)`` (``gov.cli.errors``): ``ok:
  false`` with the error, exit code 1; with ``exit_code=<a declared code>``,
  that exit code. An exit code that is not declared ends as 1;
- a usage error is argparse's (exit code 2), from the declared arguments.

Keep the module's top level light and import the rest inside ``run``: the
module is imported for ``gov --help``.

**A faulty module.** A module that fails to import, has no ``run``, or declares
something it may not (a reserved exit code, act paths on a read command, a
return value outside the list above) makes its own command answer
``COMMAND_MODULE_INVALID`` (exit code 1) and nothing else: when a command is
named, only that command's module is imported.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

from gov.cli.errors import GovError, not_implemented

EXIT_OK, EXIT_GOV_ERROR, EXIT_USAGE = 0, 1, 2  # argparse ends a usage error with 2 itself
RESERVED_EXIT_CODES = (EXIT_OK, EXIT_GOV_ERROR, EXIT_USAGE)
PACKAGE = Path(__file__).resolve().parents[1]  # src/gov
MODULE_INVALID = "COMMAND_MODULE_INVALID"


@dataclass(frozen=True)
class Command:
    name: str
    cls: str                               # "read" or "act"; internal until W1-26 (DEC-187)
    help: str
    handler: Callable | None = None        # None: reserved and not built yet, or a faulty module
    act_paths: tuple = ()                  # where an act command may write; a read command writes nowhere
    add_arguments: Callable | None = None
    exit_codes: tuple = ()                 # the command's own exit codes, beyond 0, 1 and 2
    passthrough: bool = False
    child_exit_code: bool = False
    fault: str | None = None               # why the command's module cannot be used


# The Wave 1 governance operations (CAP-28.b). Read commands are those of CAP-27's acceptance line.
COMMANDS = (
    Command("status", "read", "tickets, gates, readiness, share, pause state"),
    Command("check", "read", "list the declared checks (--list); running them is not built yet"),
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


def _known() -> dict[str, Command]:
    """The reserved commands, then every other name with a command module, none of them loaded."""
    known = {command.name: command for command in COMMANDS}
    for path in sorted(PACKAGE.glob("*/command.py")):
        known.setdefault(path.parent.name, Command(path.parent.name, "act", ""))
    return known


def _module_name(name: str) -> str | None:
    if (PACKAGE / name / "command.py").is_file():
        return f"gov.{name}.command"
    if (PACKAGE / "cli" / "commands" / f"{name}.py").is_file():
        return f"gov.cli.commands.{name}"
    return None


def _shared() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    shared.add_argument("--json", action="store_true", help="structured output (the API-0002 envelope)")
    shared.add_argument("--root", metavar="<path>", help="the project (default: the working directory)")
    shared.add_argument("--session", metavar="<id>", default="", help="the session id the envelope carries")
    shared.add_argument("--role", metavar="<role>", help="the role of the caller")
    return shared


def _declared(module, command: Command, reserved: bool) -> dict:
    """What a command module declares, checked; ``ValueError`` names what it may not declare."""
    run, add_arguments = getattr(module, "run", None), getattr(module, "add_arguments", None)
    if not callable(run) or not (add_arguments is None or callable(add_arguments)):
        raise ValueError("run (and add_arguments, when present) must be a function")
    cls = command.cls if reserved else getattr(module, "CLASS", "act")
    act_paths = getattr(module, "ACT_PATHS", ())
    if cls not in ("read", "act") or not isinstance(act_paths, (tuple, list)) \
            or not all(isinstance(path, str) and path for path in act_paths) or (cls == "read" and act_paths):
        raise ValueError("CLASS is read or act, and ACT_PATHS a tuple of paths, empty for a read command")
    exit_codes = getattr(module, "EXIT_CODES", {})
    if not isinstance(exit_codes, dict) or not all(
            type(code) is int and 0 <= code <= 255 and code not in RESERVED_EXIT_CODES for code in exit_codes):
        raise ValueError("EXIT_CODES is a dict of codes from 3 to 255: 0, 1 and 2 are the command line's")
    if add_arguments is not None:  # a trial run: an argument the parser refuses is a fault of the module
        add_arguments(argparse.ArgumentParser(parents=[_shared()], allow_abbrev=False))
    return {"handler": run, "add_arguments": add_arguments, "cls": cls, "act_paths": tuple(act_paths),
            "exit_codes": tuple(exit_codes), "passthrough": getattr(module, "PASSTHROUGH", False) is True,
            "child_exit_code": getattr(module, "CHILD_EXIT_CODE", False) is True,
            "help": command.help if reserved else str(getattr(module, "HELP", ""))}


def _load(command: Command, reserved: bool) -> Command:
    """The command with what its module declares; unchanged without a module; with ``fault`` set for a faulty one."""
    module_name = _module_name(command.name)
    if module_name is None:
        return command
    try:
        return replace(command, **_declared(importlib.import_module(module_name), command, reserved))
    except (Exception, SystemExit) as error:  # nothing a module does at import ends another command
        return replace(command, fault=f"{module_name}: {type(error).__name__}: {error}")


def _parser(commands: dict[str, Command]) -> argparse.ArgumentParser:
    shared = _shared()
    parser = argparse.ArgumentParser(prog="gov", description="Governance OS command line.", allow_abbrev=False)
    subparsers = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for command in commands.values():
        sub = subparsers.add_parser(command.name, help=command.help, parents=[shared], allow_abbrev=False)
        if command.add_arguments is not None:
            command.add_arguments(sub)
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
    argv = list(sys.argv[1:] if argv is None else argv)
    passed = None  # what follows "--" goes to a command that takes it, unparsed
    if "--" in argv:
        argv, passed = argv[:argv.index("--")], argv[argv.index("--") + 1:]
    known = _known()
    reserved = {command.name for command in COMMANDS}
    wanted = argv[:1] if argv and argv[0] in known else list(known)  # no command named: every module, for the help
    commands = {name: _load(command, name in reserved) if name in wanted else command
                for name, command in known.items()}
    parser = _parser(commands)
    args, extra = parser.parse_known_args(argv)
    command = commands[args.command]
    args.passthrough = passed if command.passthrough else None
    if passed is not None and not command.passthrough:
        extra += ["--", *passed]
    if extra and command.handler is not None:  # a command not built yet has no arguments to check against
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    root = Path(args.root) if args.root else Path.cwd()
    try:
        from gov.config.loader import load_config
        config = load_config(root)  # every command loads the configuration first (DEC-185)
        if command.fault is not None:
            raise GovError(MODULE_INVALID, f"gov {command.name} cannot be used: {command.fault}",
                           {"command": command.name})
        if command.handler is None:
            raise not_implemented(command.name)
        outcome = command.handler(root, args, config)
        if command.child_exit_code and type(outcome) is int:
            return outcome
        result, code = outcome if isinstance(outcome, tuple) and len(outcome) == 2 else (outcome, EXIT_OK)
        if not isinstance(result, dict) or type(code) is not int or code not in (EXIT_OK, *command.exit_codes):
            raise GovError(MODULE_INVALID, f"gov {command.name} returned something its module does not declare",
                           {"command": command.name})
    except GovError as error:
        _emit(args, False, {}, error)
        return error.exit_code if error.exit_code in command.exit_codes else EXIT_GOV_ERROR
    _emit(args, True, result, None)
    return code


if __name__ == "__main__":
    sys.exit(main())
