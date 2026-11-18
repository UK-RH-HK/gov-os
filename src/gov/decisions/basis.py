"""The basis line checked by code: a new rule needs a basis that names an incident (W2-198 S4, S5; EMERGENCY-2 10.1, A-8).

For each decision entry (a ``### DEC-<n> — <title>`` heading; a hyphen or an en dash is read too) present at a range's
end and absent at its start, ``judge`` decides whether the entry adds a rule: its title or body, outside its
``**Basis:**`` and ``**Governing sources:**`` fields, holds ``rule``, ``gate``, ``check``, ``practice`` or ``standing`` as a
word (plural and ``-ed`` forms, any case), unless it has an ``- **Adds:** no rule`` line. A rule entry passes only when
its basis (the ``**Basis:**`` field with its continuation lines) names an incident: a date ``YYYY-MM-DD`` and at least
five more words, or a path that exists in the tree at the range's end. The register is read from git objects at the
range's two ends, never from the working tree. ``week`` lists what the register gained since a date, for the weekly review.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from gov.util.gitenv import git_env

REGISTER_DEFAULT = "docs/DECISION_REGISTER.md"
RANGE_DEFAULT = "HEAD^..HEAD"
_GIT = ("git", "--no-replace-objects", "-c", "core.commitGraph=false", "-c", "protocol.allow=never")
_HEADING = re.compile(r"^###[ \t]+(DEC-\d+)[ \t]+[—–-]+[ \t]*(.*?)[ \t]*$")
_ANY_HEADING = re.compile(r"^#{1,3}[ \t]")
_FIELD = re.compile(r"(?:^-[ \t]+|[ \t]·[ \t])\*\*([^*:\n]+):\*\*")
_RULE_WORD = re.compile(r"\b(?:rule|gate|check|practice|standing)(?:s|d|ed)?\b", re.IGNORECASE)
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_NO_RULE = re.compile(r"no[ \t]+rule\b", re.IGNORECASE)
_PATHISH = re.compile(r"[^\s`'\"()<>\[\]{},;|]+")
_MORE_WORDS = 5
_EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


class BasisError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


# --- the register's text -------------------------------------------------------------------------------------------

def parse_entries(text: str) -> list[dict]:
    """The decision entries of a register: ``{id, title, lines}``, each ending at the next heading of level 1 to 3
    (a line inside a code fence is not a heading)."""
    entries, current, fenced = [], None, False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        found = None if fenced else _HEADING.match(line)
        if found:
            current = {"id": found.group(1), "title": found.group(2), "lines": []}
            entries.append(current)
        elif current is not None and not fenced and _ANY_HEADING.match(line):
            current = None
        elif current is not None:
            current["lines"].append(line)
    return entries


def _fields(lines: list[str]) -> list[list]:
    """``[label or None, text]`` pieces of an entry's body: a top-level bullet's ``**Label:**`` fields (also after a
    `` · ``), the last of a bullet taking its indented continuation lines; any other line a piece of its own."""
    pieces, open_piece = [], None
    for line in lines:
        if line.startswith("-"):
            marks = list(_FIELD.finditer(line))
            if not marks:
                open_piece = [None, line]
                pieces.append(open_piece)
                continue
            if marks[0].start() > 0:
                pieces.append([None, line[:marks[0].start()]])
            for at, mark in enumerate(marks):
                end = marks[at + 1].start() if at + 1 < len(marks) else len(line)
                pieces.append([mark.group(1).strip().lower(), line[mark.end():end]])
            open_piece = pieces[-1]
        elif line[:1] in (" ", "\t") and line.strip() and open_piece is not None:
            open_piece[1] += " " + line
        else:
            open_piece = None
            pieces.append([None, line])
    return pieces


def _fold(text: str) -> str:
    return " ".join(text.split())


def adds_rule(entry: dict) -> bool:
    """Whether the entry adds a rule (see the module's text)."""
    pieces = _fields(entry["lines"])
    if any(label == "adds" and _NO_RULE.match(text.strip()) for label, text in pieces):
        return False
    scanned = [entry["title"]] + [text for label, text in pieces if label not in ("basis", "governing sources")]
    return any(_RULE_WORD.search(text) for text in scanned)


def basis_of(entry: dict) -> str | None:
    """The text of the entry's ``**Basis:**`` field with its continuation lines, whitespace folded; None without one."""
    texts = [text for label, text in _fields(entry["lines"]) if label == "basis"]
    return _fold(" ".join(texts)) if texts else None


def _names_incident(text: str, exists) -> bool:
    if _DATE.search(text):
        words = [w for w in _DATE.sub(" ", text).split() if re.search(r"[A-Za-z]", w)]
        if len(words) >= _MORE_WORDS:
            return True
    for token in _PATHISH.findall(text)[:200]:
        path = re.sub(r"(:\d+(-\d+)?)?(#\S*)?[.:]*$", "", token.strip(".,:;"))
        path = path[2:] if path.startswith("./") else path
        if not path or path.startswith(("/", "~", "-")) or not re.search(r"[A-Za-z]", path):
            continue
        if ("/" in path or re.search(r"\.[A-Za-z0-9]{1,6}$", path)) and exists(path):
            return True
    return False


def judge(entry: dict, exists) -> tuple[str, str]:
    """``(verdict, reason)`` of an entry; ``exists(path)`` says whether a path is in the tree at the range's end."""
    if not adds_rule(entry):
        return ("pass", "adds no rule")
    text = basis_of(entry)
    if text is None:
        return ("fail", "no basis line")
    if _names_incident(text, exists):
        return ("pass", "basis names an incident")
    return ("fail", "basis names no incident")


def _record(entry: dict, exists) -> dict:
    verdict, reason = judge(entry, exists)
    return {"id": entry["id"], "title": entry["title"], "rule": adds_rule(entry), "basis": basis_of(entry),
            "verdict": verdict, "reason": reason}


# --- git objects ---------------------------------------------------------------------------------------------------

def _run(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**git_env(root, pinned=True, base={k: v for k, v in os.environ.items() if not k.startswith("GIT_")}),
           "GIT_GRAFT_FILE": os.devnull, "GIT_SHALLOW_FILE": os.devnull}
    try:
        return subprocess.run([*_GIT, "-C", str(root), *args], capture_output=True, stdin=subprocess.DEVNULL, env=env)
    except OSError as error:
        raise BasisError("BASIS_GIT_FAILED", f"git cannot be run: {error.strerror or error}") from None


def _out(root: Path, *args: str) -> str:
    done = _run(root, *args)
    if done.returncode != 0:
        why = " ".join(done.stderr.decode("utf-8", "replace").split())[:300] or f"exit {done.returncode}"
        raise BasisError("BASIS_GIT_FAILED", f"git {args[0]} failed in {root}: {why}")
    return done.stdout.decode("utf-8", "replace")


def _commit(root: Path, name: str) -> str:
    done = _run(root, "rev-parse", "--verify", "-q", f"{name}^{{commit}}")
    if done.returncode != 0:
        raise BasisError("BASIS_RANGE_INVALID", f"{name!r} is not a commit of the repository in {root}")
    return done.stdout.decode().strip()


def _register_path(root: Path, register: str) -> str:
    """The register's path as git names it from ``root``: relative, with no leading ``./``."""
    given = Path(register)
    if given.is_absolute():
        try:
            given = Path(os.path.realpath(given)).relative_to(os.path.realpath(root))
        except ValueError:
            raise BasisError("BASIS_REGISTER_INVALID", f"{register} is not inside {root}") from None
    return given.as_posix()


def _text_at(root: Path, commit: str | None, path: str) -> str | None:
    """The register's text in ``commit``'s tree, None when the commit (or the file there) does not exist."""
    if commit is None:
        return None
    done = _run(root, "show", f"{commit}:./{path}")
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def _exists_in(root: Path, commit: str):
    cache: dict[str, bool] = {}

    def exists(path: str) -> bool:
        if path not in cache:
            cache[path] = _run(root, "cat-file", "-e", f"{commit}:{path}").returncode == 0
        return cache[path]
    return exists


def _new_entries(before: str | None, after: str) -> list[dict]:
    seen = {e["id"] for e in parse_entries(before or "")}
    return [e for e in parse_entries(after) if e["id"] not in seen]


def check_range(root: Path, range_: str | None, register: str) -> dict:
    """``{range, entries}`` for the entries ``range_`` (``A..B``; default ``HEAD^..HEAD``) adds to ``register``."""
    root, path = Path(root), _register_path(Path(root), register)
    if range_ is None:
        head = _commit(root, "HEAD")
        parent = _run(root, "rev-parse", "--verify", "-q", "HEAD^{commit}^").stdout.decode().strip()
        start, end, label = (parent or None), head, RANGE_DEFAULT
    else:
        first, dots, last = range_.partition("..")
        if not dots or not first or "." in last[:1]:
            raise BasisError("BASIS_RANGE_INVALID", f"{range_!r} is not <A>..<B>")
        start, end, label = _commit(root, first), _commit(root, last or "HEAD"), range_
    after = _text_at(root, end, path)
    if after is None:
        raise BasisError("BASIS_REGISTER_MISSING", f"{path} is not in the tree of {end[:12]}")
    exists = _exists_in(root, end)
    return {"range": label, "entries": [_record(e, exists) for e in _new_entries(_text_at(root, start, path), after)]}


def week(root: Path, since: str | None, register: str, now: datetime | None = None) -> dict:
    """``{range, since, entries}``: every entry present at HEAD and absent at the last commit before ``since`` (a
    ``YYYY-MM-DD`` date, default 7 days before ``now``), each with the date of the commit that added it."""
    root, path = Path(root), _register_path(Path(root), register)
    now = now or datetime.now(timezone.utc)
    try:
        day = date.fromisoformat(since) if since else (now - timedelta(days=7)).date()
    except ValueError:
        raise BasisError("BASIS_RANGE_INVALID", f"--since {since!r} is not YYYY-MM-DD") from None
    head = _commit(root, "HEAD")
    boundary = f"{day.isoformat()} 00:00:00 +0000"
    base = _out(root, "rev-list", "-1", f"--before={boundary}", head).strip() or None
    after = _text_at(root, head, path)
    if after is None:
        raise BasisError("BASIS_REGISTER_MISSING", f"{path} is not in the tree of {head[:12]}")
    new = _new_entries(_text_at(root, base, path), after)
    wanted, added = {e["id"] for e in new}, {}
    log = _out(root, "log", "--reverse", "--format=%H %ct", *([f"{base}..{head}"] if base else [head]), "--", path)
    for line in log.splitlines():
        if not wanted - set(added):
            break
        commit, _sp, stamp = line.partition(" ")
        text = _text_at(root, commit, path) or ""
        for found in re.finditer(r"^###[ \t]+(DEC-\d+)[ \t]", text, re.MULTILINE):
            if found.group(1) in wanted and found.group(1) not in added:
                added[found.group(1)] = datetime.fromtimestamp(int(stamp), timezone.utc).date().isoformat()
    exists = _exists_in(root, head)
    entries = [{**_record(e, exists), "added": added.get(e["id"])} for e in new]
    return {"range": f"{base[:12] if base else 'the start'}..{head[:12]}", "since": day.isoformat(), "entries": entries}
