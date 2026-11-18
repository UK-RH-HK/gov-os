"""``gov decisions basis`` as a command module (W2-198 S4, S5; EMERGENCY-2 10.1, A-8; the convention is in ``gov.cli.main``).

- ``basis [--range <A>..<B>] [--register <path>]``: for each decision entry the range adds to the register, whether it
  adds a rule and, if so, whether its basis line names an incident (the logic is ``gov.decisions.basis``). Exit 0 when
  every new entry passes; 1 (``BASIS_MISSING``) naming each failing entry's id and reason. A line an entry.
- ``basis --week [--since <YYYY-MM-DD>]``: the weekly review: every entry the register gained since the date (default 7
  days ago), each with its id, title, the date it was added, whether it adds a rule, its basis and its verdict. Exit 0
  whatever the verdicts.

The register is read from git objects, never the working tree. It prints its own output (the envelope under ``--json``)
and ends with its own code (``CHILD_EXIT_CODE``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HELP = "decision register checks: basis (a new rule needs a basis line that names an incident; --week for the review)"
CLASS = "read"
CHILD_EXIT_CODE = True
EXIT_CODES = {}


def _common(sub) -> None:
    """The command line's shared options, also after the action (absent, they keep the value given before it)."""
    sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    for flag in ("--root", "--session", "--role"):
        sub.add_argument(flag, default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def add_arguments(parser) -> None:
    parser.usage = "gov decisions basis [--range <A>..<B>] [--register <path>] | --week [--since <YYYY-MM-DD>]"
    actions = parser.add_subparsers(dest="action", metavar="{basis}", required=True)
    basis = actions.add_parser("basis", help="the new rule entries of a range and their basis lines")
    basis.add_argument("--range", dest="range_", metavar="<A>..<B>", help="the commits (default HEAD^..HEAD)")
    basis.add_argument("--register", default="docs/DECISION_REGISTER.md", metavar="<path>",
                       help="the register's path in the repository (default docs/DECISION_REGISTER.md)")
    basis.add_argument("--week", action="store_true", help="the weekly review: the entries gained in the last 7 days")
    basis.add_argument("--since", metavar="<YYYY-MM-DD>", help="with --week: the date the week starts (default 7 days ago)")
    _common(basis)


def _emit(args, ok: bool, result: dict, lines: list[str], code: str | None = None, message: str = "") -> None:
    if args.json:
        envelope = {"ok": ok, "command": "decisions", "result": result, "session": getattr(args, "session", "")}
        if code:
            envelope["error"] = {"code": code, "message": message, "details": {}}
        print(json.dumps(envelope))
        return
    for line in lines:
        print(line)
    if code:
        print(f"gov decisions: {code}: {message}", file=sys.stderr)


def _check_line(entry: dict) -> str:
    return f"{entry['id']} {entry['verdict']}: {entry['reason']}"


def _week_line(entry: dict) -> str:
    rule = "rule" if entry["rule"] else "no rule"
    basis = entry["basis"] if entry["basis"] is not None else "(no basis line)"
    return (f"{entry['id']} {entry['added'] or 'unknown date'} {rule} {entry['verdict']}: {entry['reason']}"
            f" | {entry['title']} | basis: {basis}")


def run(root: Path, args, config: dict) -> int:
    from gov.decisions import basis

    try:
        if args.week:
            if args.range_ is not None:
                raise basis.BasisError("BASIS_RANGE_INVALID", "--week takes no --range")
            result = basis.week(root, args.since, args.register)
            _emit(args, True, result, [_week_line(e) for e in result["entries"]]
                  or [f"no entry gained since {result['since']}"])
            return 0
        if args.since is not None:
            raise basis.BasisError("BASIS_RANGE_INVALID", "--since goes with --week")
        result = basis.check_range(root, args.range_, args.register)
    except basis.BasisError as error:
        _emit(args, False, {}, [], error.code, error.message)
        return 1
    entries = result["entries"]
    lines = [_check_line(e) for e in entries] or [f"no new decision entry in {result['range']}"]
    failing = [e for e in entries if e["verdict"] == "fail"]
    if failing:
        message = "; ".join(f"{e['id']}: {e['reason']}" for e in failing)
        _emit(args, False, result, lines, "BASIS_MISSING", f"a new rule needs a basis that names an incident: {message}")
        return 1
    _emit(args, True, result, lines)
    return 0
