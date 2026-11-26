"""``gov memaudit scan`` as a command module (W2-198 S3, F2; EMERGENCY-2 2.7, A-12; the convention is in ``gov.cli.main``).

``gov memaudit scan --set <path> --since <ISO> [--until <ISO>] [--id <id>]... [--allow-session <id>]... [--projects <dir>]``:
every transcript written in the window that names the set's path, holds a question's text, or names one of its question
ids beside the set's audit name or tag (the logic is ``gov.memaudit.scan``; every transcript of the window is read, a bare
id is no finding, F-033). Exit 0 when none; 1 when any (``MEASURE_VOID``: the measure is void); 3 when none is found but
a transcript could not be read (``SCAN_INCOMPLETE``). It prints its own output (the envelope under ``--json``), never a
transcript line's text and never a set file's contents.

``gov memaudit preflight|void|declare|measure|judge|figures|brief|deliver|check|fresh ...`` (W2-204 S11, I3): each
takes the flags of ``python3 -m gov.memaudit <step>`` and is handed to that entry unparsed; ``gov`` ends with its exit
code (0 ok, 1 refused, 2 void or stopped, 3 used, 4 usage, 5 waiting) and its lines are that entry's own (``say``).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HELP = ("memory audit tools: the measure's steps (preflight, void, declare, measure, judge, figures, brief, deliver, "
        "check, fresh, writer-check, writer-run) and the transcript scan for a hidden set's path, question text or ids")
STEPS = {
    "preflight": "the checks of a delivered half before any search",
    "void": "the drop and void rule after the checker's last pass",
    "declare": "the declaration and the use-once marker",
    "measure": "the declaration, the control, the attempts and the retrieval figures",
    "judge": "the judged reader run, the verdict and FIGURES.json",
    "figures": "one JSON line of an audit's figures",
    "brief": "a writer's or checker's brief, filled from the repository's configuration",
    "deliver": "take a writer's set or a checker's notes into the sets root",
    "check": "the repository's memory-audit configuration: ok, or its first fault",
    "fresh": "a whole fresh pair of halves on a pinned snapshot it builds",
    "writer-check": "the Stop hook of a writer's session: the pre-flight's checks on out/set, blocking the stop on a refusal",
    "writer-run": "a writer's session run with its check in the loop: a refusal resumes the same session, up to 3 returns",
    "forbidden-reach": "whether an audit's cited forbidden sources are now outside default memory: counts only",
}
CLASS = "read"
CHILD_EXIT_CODE = True
EXIT_INCOMPLETE = 3
EXIT_CODES = {EXIT_INCOMPLETE: "scan: nothing found but a transcript in the window could not be read; a step: used",
              4: "a step: usage (a flag or value refused, or an unexpected error)",
              5: "fresh: waiting for a delivery"}


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
    parser.usage = "gov memaudit <step> [the step's flags] | gov memaudit scan --set <path> --since <ISO> [options]"
    actions = parser.add_subparsers(dest="action", metavar="{" + ",".join([*STEPS, "scan"]) + "}", required=True)
    for name, line in STEPS.items():  # the step's own flags are parsed by ``python3 -m gov.memaudit``'s parser
        step = actions.add_parser(name, help=line, add_help=False, prefix_chars="\x00")
        step.add_argument("rest", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    scan = actions.add_parser("scan", help="the transcripts of a window that name a set's path, hold a question's text or name its ids")
    scan.add_argument("--set", required=True, metavar="<path>", help="the set's folder (its *.yaml names are the ids)")
    scan.add_argument("--since", required=True, type=_moment, metavar="<ISO>", help="the window's start")
    scan.add_argument("--until", type=_moment, metavar="<ISO>", help="the window's end (default now)")
    scan.add_argument("--id", action="append", default=[], dest="ids", metavar="<id>",
                      help="a question id (counts beside the set's name or tag); given, these are the ids, not the set's; "
                           "the questions' text is still read")
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

    if args.action in STEPS:
        from gov.memaudit.__main__ import main
        return main([args.action, *args.rest])
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
