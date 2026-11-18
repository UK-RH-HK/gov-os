"""``gov memaudit scan`` as a command module (W2-198 S3, F2; EMERGENCY-2 2.7, A-12; the convention is in ``gov.cli.main``).

``gov memaudit scan --set <path> --since <ISO> [--until <ISO>] [--id <id>]... [--allow-session <id>]... [--projects <dir>]``:
every transcript written in the window that names the set's path or one of its question ids (the logic is
``gov.memaudit.scan``). Exit 0 when none; 1 when any (``MEASURE_VOID``: the measure is void); 3 when none is found but
a transcript could not be read (``SCAN_INCOMPLETE``). It prints its own output (the envelope under ``--json``), never a
transcript line's text and never a set file's contents. ``python3 -m gov.memaudit`` is a separate entry and is unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HELP = "memory audit tools: scan transcripts for a hidden set's path or question ids (exit 1 void, 3 incomplete)"
CLASS = "read"
CHILD_EXIT_CODE = True
EXIT_INCOMPLETE = 3
EXIT_CODES = {EXIT_INCOMPLETE: "scan: nothing found but a transcript in the window could not be read"}


def _moment(text: str) -> datetime:
    try:
        at = datetime.fromisoformat(text.strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not an ISO-8601 time") from None
    return at if at.tzinfo else at.replace(tzinfo=timezone.utc)


def _common(sub) -> None:
    """The command line's shared options, also after the action (absent, they keep the value given before it)."""
    sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    for flag in ("--root", "--session", "--role"):
        sub.add_argument(flag, default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def add_arguments(parser) -> None:
    parser.usage = "gov memaudit scan --set <path> --since <ISO> [options]"
    actions = parser.add_subparsers(dest="action", metavar="{scan}", required=True)
    scan = actions.add_parser("scan", help="the transcripts of a window that name a set's path or ids")
    scan.add_argument("--set", required=True, metavar="<path>", help="the set's folder (its *.yaml names are the ids)")
    scan.add_argument("--since", required=True, type=_moment, metavar="<ISO>", help="the window's start")
    scan.add_argument("--until", type=_moment, metavar="<ISO>", help="the window's end (default now)")
    scan.add_argument("--id", action="append", default=[], dest="ids", metavar="<id>",
                      help="a question id; given, these are the ids, not the set's")
    scan.add_argument("--allow-session", action="append", default=[], dest="allow", metavar="<id>",
                      help="a session allowed to name the set (the writer's, the checker's)")
    scan.add_argument("--projects", metavar="<dir>", help="the transcripts' root (default ~/.claude/projects)")
    _common(scan)


def _emit(args, ok: bool, result: dict, lines: list[str], code: str | None = None, message: str = "") -> None:
    if args.json:
        envelope = {"ok": ok, "command": "memaudit", "result": result, "session": getattr(args, "session", "")}
        if code:
            envelope["error"] = {"code": code, "message": message, "details": {}}
        print(json.dumps(envelope))
        return
    for line in lines:
        print(line)
    if code:
        print(f"gov memaudit: {code}: {message}", file=sys.stderr)


def _finding_line(found: dict) -> str:
    return (f"{found['file']}:{found['line']} session={found['session']} role={found['role'] or '-'} "
            f"kind={found['kind']} match={found['match']}")


def run(root: Path, args, config: dict) -> int:
    import os

    from gov.memaudit.scan import scan

    if not Path(args.set).exists():
        _emit(args, False, {}, [], "SCAN_SET_MISSING", f"the set {args.set} does not exist")
        return 1
    until = args.until or datetime.now(timezone.utc)
    projects = args.projects or os.path.join(os.path.expanduser("~"), ".claude", "projects")
    result = scan(args.set, args.since, until, args.ids, args.allow, projects)
    found, problems = result["findings"], result["problems"]
    allowed = sorted({one["session"] for one in result["allowed"]})
    tail = f"; allowed: {', '.join(allowed)}" if allowed else ""
    read = f"{result['transcripts_read']} transcripts read"
    problem_lines = [f"problem: {one['file']}: {one['error']}" for one in problems]
    if found:
        message = f"the measure is void: {len(found)} finding(s) in the window"
        _emit(args, False, result, [f"MEASURE VOID: {len(found)} finding(s), {read}{tail}",
                                    *map(_finding_line, found), *problem_lines], "MEASURE_VOID", message)
        return 1
    if problems:
        message = f"{len(problems)} transcript(s) in the window could not be read; nothing found in the rest"
        _emit(args, False, result, [f"SCAN INCOMPLETE: {message}", *problem_lines], "SCAN_INCOMPLETE", message)
        return EXIT_INCOMPLETE
    _emit(args, True, result, [f"no transcript in the window names the set: {read}, {result['ids_count']} ids{tail}"])
    return 0
