"""``gov decisions basis`` and ``gov decisions in-force`` as a command module (W2-198 S4, S5; EMERGENCY-2 10.1, A-8;
W2-200 S2; the convention is in ``gov.cli.main``).

- ``basis [--range <A>..<B>] [--register <path>]``: for each decision entry the range adds to the register, whether it
  adds a rule and, if so, whether its basis line names an incident (the logic is ``gov.decisions.basis``), and whether
  its ``Decided-by`` is at or above the level its stated facts compute (``gov.decisions.level``; an entry with no stated
  facts is listed ``unstated``). Exit 0 when every new entry passes; 1 naming each failing entry's id and reason:
  ``DECISION_BELOW_LEVEL`` for a decision below its level, else ``BASIS_MISSING``. A line an entry.
- ``basis --week [--since <YYYY-MM-DD>]``: the weekly review: every entry the register gained since the date (default 7
  days ago), each with its id, title, the date it was added, whether it adds a rule, its basis and its verdict. Exit 0
  whatever the verdicts.
- ``in-force``: the digest of the decisions in force (``gov.util.register.in_force``; W2-200 S2, DEC-1214 M1): one line
  ``DEC-n — title`` per register entry neither superseded nor tagged done, in the register's order, a changed entry
  naming what changed it; then the left-out count and the register's path. Exit 0, also without a register.

- ``level [<package>] [--touches a,b --reversible yes|no --inside worktree|repository|outside] [--spends] [--rounds n]
  [--emergency]``: the level the facts compute and the facts that set it (W2-211 EL-1); ``LEVEL_FACT_INVALID`` (1) for a
  missing fact or an unknown word.
- ``page [--batches <dir>] [--register <path>] [--max n]``: puts every open page-ready package into a batch manifest and
  names, for each other open package, the field that is missing, too long or false (PG-1); the page itself is slice b.
- ``answer <sheet|-> [--batches <dir>] [--register <path>] [--dry-run]``: the owner's answer sheet becomes one register
  entry per pick, in one commit; run by the orchestrator (W2-211 PG-4 to PG-6).

The register is read from git objects, never the working tree. It prints its own output (the envelope under ``--json``)
and ends with its own code (``CHILD_EXIT_CODE``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HELP = ("decision register: basis (a new rule needs a basis line that names an incident; a record below its level is "
        "refused; --week for the review), in-force (the digest of the decisions in force), level (the level of "
        "stated facts), page (the batch of page-ready packages), answer (an owner's answer sheet into the register)")
CLASS = "read"
CHILD_EXIT_CODE = True
EXIT_CODES = {}


def _common(sub) -> None:
    """The command line's shared options, also after the action (absent, they keep the value given before it)."""
    sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    for flag in ("--root", "--session", "--role"):
        sub.add_argument(flag, default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def add_arguments(parser) -> None:
    parser.usage = ("gov decisions basis [--range <A>..<B>] [--register <path>] | --week [--since <YYYY-MM-DD>]\n"
                    "       gov decisions in-force\n"
                    "       gov decisions level [<package>] [--touches a,b --reversible yes|no --inside "
                    "worktree|repository|outside] [--spends] [--rounds n] [--emergency]\n"
                    "       gov decisions page [--batches <dir>] [--register <path>] [--max n]\n"
                    "       gov decisions answer <sheet|-> [--batches <dir>] [--register <path>] [--dry-run]")
    actions = parser.add_subparsers(dest="action", metavar="{basis,in-force,level,page,answer}", required=True)
    basis = actions.add_parser("basis", help="the new rule entries of a range and their basis lines")
    basis.add_argument("--range", dest="range_", metavar="<A>..<B>", help="the commits (default HEAD^..HEAD)")
    basis.add_argument("--register", default="docs/DECISION_REGISTER.md", metavar="<path>",
                       help="the register's path in the repository (default docs/DECISION_REGISTER.md)")
    basis.add_argument("--week", action="store_true", help="the weekly review: the entries gained in the last 7 days")
    basis.add_argument("--since", metavar="<YYYY-MM-DD>", help="with --week: the date the week starts (default 7 days ago)")
    _common(basis)
    in_force = actions.add_parser("in-force", help="the digest of the register's decisions in force, read from HEAD")
    _common(in_force)
    level = actions.add_parser("level", help="the level of the facts a decision record states")
    level.add_argument("package", nargs="?", help="a package file whose frontmatter states the facts")
    level.add_argument("--touches", metavar="a,b", help="what the decision changes (words of the escalation table)")
    level.add_argument("--reversible", metavar="yes|no")
    level.add_argument("--inside", metavar="worktree|repository|outside")
    level.add_argument("--spends", action="store_true", default=None, help="it spends money (a paid service)")
    level.add_argument("--rounds", metavar="n", help="the review rounds so far")
    level.add_argument("--emergency", action="store_true", default=None)
    _common(level)
    page = actions.add_parser("page", help="a batch of the open page-ready packages; names what keeps the others off")
    answer = actions.add_parser("answer", help="the owner's answer sheet into the register, in one commit")
    answer.add_argument("sheet", metavar="<sheet|->", help="the sheet's file, or - for standard input")
    answer.add_argument("--dry-run", action="store_true", help="print what would be written and write nothing")
    for sub in (page, answer):
        sub.add_argument("--batches", default="docs/decisions/batches", metavar="<dir>",
                         help="the batches' folder (default docs/decisions/batches)")
        sub.add_argument("--register", default="docs/DECISION_REGISTER.md", metavar="<path>",
                         help="the register's path (default docs/DECISION_REGISTER.md)")
        _common(sub)
    page.add_argument("--max", type=int, default=12, metavar="n", help="cards on one page at most (default 12)")


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


def _in_force(root: Path, args) -> int:
    """``in-force``: the digest's lines, then what was left out and the register's path (W2-200 S2)."""
    from gov.util.register import in_force

    result = in_force(root)
    left = result["left_out"]
    _emit(args, True, result, result["lines"] + [
        f"left out: {left['count']} (superseded: {', '.join(left['superseded']) or 'none'}; "
        f"done: {', '.join(left['done']) or 'none'})",
        f"register: {result['register'] or 'none'}"])
    return 0


def _level(root: Path, args) -> int:
    from gov.decisions import level, package

    try:
        facts = {}
        if args.package:
            front, _text = package.read(Path(args.package) if Path(args.package).is_absolute() else root / args.package)
            facts = {k: front.get(k) for k in ("touches", "reversible", "inside", "spends", "rounds", "emergency")}
        given = {"touches": args.touches, "reversible": args.reversible, "inside": args.inside,
                 "spends": "yes" if args.spends else None, "rounds": args.rounds,
                 "emergency": "yes" if args.emergency else None}
        facts.update({k: v for k, v in given.items() if v is not None})
        result = level.compute_level(facts, level.load_table(root))
    except (level.LevelError, OSError, ValueError) as error:
        _emit(args, False, {}, [], getattr(error, "code", "LEVEL_FACT_INVALID"), getattr(error, "message", str(error)))
        return 1
    _emit(args, True, result, [level.level_line(result)])
    return 0


def _page(root: Path, args) -> int:
    from gov.decisions import page

    built = page.build(root, args.batches, args.register, args.max)
    lines = [f"{pid} {'; '.join(f'{field}: {why}' for field, why in problems)}" for pid, problems in built["refused"]]
    if built["manifest"] is None:
        _emit(args, False, {"refused": built["refused"]}, lines, "PAGE_EMPTY", "no open package is page-ready")
        return 1
    path = page.publish(root, args.batches, built["manifest"])
    lines += [f"{pid} on the page" for pid in built["taken"]]
    lines.append(f"batch {built['batch']}: {len(built['taken'])} cards, {path}")
    _emit(args, True, {"batch": built["batch"], "cards": built["taken"], "manifest": str(path),
                       "refused": built["refused"]}, lines)
    return 0


def _answer(root: Path, args) -> int:
    import os

    from gov.decisions import answer as answering

    role = os.environ.get("GOV_ROLE") or getattr(args, "role", None)
    try:
        if args.sheet == "-":
            text = sys.stdin.buffer.read().decode("utf-8", "replace")
        else:
            try:
                text = Path(args.sheet).read_text(encoding="utf-8", errors="replace")
            except OSError as error:
                raise answering.AnswerError("ANSWER_FORMAT", f"the sheet {args.sheet} cannot be read: {error.strerror}")
        result = answering.answer(root, text, batches=args.batches, register=args.register, role=role,
                                  dry_run=args.dry_run)
    except answering.AnswerError as error:
        _emit(args, False, {}, [], error.code, error.message)
        return 1
    lines = list(result["lines"])
    if result["skipped"]:
        lines.append(f"skipped: {', '.join(result['skipped'])}")
    if result["notes"]:
        lines.append("notes for the CTO:")
        lines += [f"  {pid}: {note}" for pid, note in result["notes"]]
    lines.append(f"still open in this batch: {', '.join(result['still_open']) or 'none'}")
    if args.dry_run:
        lines.append("dry run: nothing written")
    _emit(args, True, {k: v for k, v in result.items() if k != "lines"}, lines)
    return 0


def run(root: Path, args, config: dict) -> int:
    if args.action == "in-force":
        return _in_force(root, args)
    if args.action in ("level", "page", "answer"):
        return {"level": _level, "page": _page, "answer": _answer}[args.action](root, args)
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
    lines = []
    for e in entries:
        line = _check_line(e)
        judged = e.get("level") or {}
        if judged.get("verdict") in ("unstated", "invalid"):
            line += f" | level {judged['verdict']}: {judged['reason']}"
        lines.append(line)
        if judged.get("verdict") == "fail":
            lines.append(f"{e['id']} DECISION_BELOW_LEVEL: {judged['reason']}")
    lines = lines or [f"no new decision entry in {result['range']}"]
    below = [e for e in entries if (e.get("level") or {}).get("verdict") == "fail"]
    failing = [e for e in entries if e["verdict"] == "fail"]
    if below:
        message = "; ".join(f"{e['id']}: {e['level']['reason']}" for e in below)
        _emit(args, False, result, lines, "DECISION_BELOW_LEVEL", f"a decision below its level: {message}")
        return 1
    if failing:
        message = "; ".join(f"{e['id']}: {e['reason']}" for e in failing)
        _emit(args, False, result, lines, "BASIS_MISSING", f"a new rule needs a basis that names an incident: {message}")
        return 1
    _emit(args, True, result, lines)
    return 0
