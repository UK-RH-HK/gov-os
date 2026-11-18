"""The hidden-set transcript scan: which transcripts of a window name the set's path or one of its question ids
(W2-198 S3, F2; EMERGENCY-2 2.7, A-12).

``scan`` reads every ``*.jsonl`` under the projects root (sub-agent transcripts included) whose mtime is at or after
``since``, and in each the lines whose ``timestamp`` lies in ``[since, until]`` (a line with none counts, its file being in
the window). A line names the set when one of its decoded text values holds the set's path (absolute real path, its
``~/`` and ``$HOME/`` forms, its part from a ``fixtures/evaluation/`` segment on) or a question id as a whole token. A
line gives one finding: the most specific path form it names, else an id. The ids are the stems of the ``*.yaml``
files' names under the set, listed and never opened (the questions stay unread, F2). A transcript that cannot be read
is a problem, never a clean result. Nothing here keeps or returns a transcript line's text.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

_SEGMENT = ("fixtures", "evaluation")


def set_ids(set_path) -> list[str]:
    """The stems of the ``*.yaml`` files under ``set_path``, sorted; names only, no file is opened."""
    path = Path(set_path)
    if path.is_file():
        return [path.stem] if path.suffix == ".yaml" else []
    found = set()
    for _folder, _dirs, files in os.walk(path):
        found.update(name[:-len(".yaml")] for name in files if name.endswith(".yaml") and name != ".yaml")
    return sorted(found)


def path_forms(set_path, home: str | None = None) -> list[str]:
    """The strings that name the set's path in a transcript, the most specific first: the absolute real path (and the
    absolute path as given, when it differs), ``~/<rest>`` and ``$HOME/<rest>`` when the set is under the home folder,
    the part from a ``fixtures/evaluation/`` segment on when it has one."""
    real = os.path.realpath(set_path)
    forms = [real]
    given = os.path.abspath(set_path)
    if given != real:
        forms.append(given)
    home_real = os.path.realpath(home if home is not None else os.path.expanduser("~"))
    if real != home_real and real.startswith(home_real.rstrip(os.sep) + os.sep):
        rest = real[len(home_real.rstrip(os.sep)) + 1:]
        forms += ["~/" + rest, "$HOME/" + rest]
    parts = real.split(os.sep)
    for at in range(len(parts) - 1):
        if tuple(parts[at:at + 2]) == _SEGMENT:
            forms.append("/".join(parts[at:]))
            break
    return forms


class Matcher:
    """Finds what a line's decoded text values name: ``(kind, match)`` or None."""

    def __init__(self, forms: list[str], ids: list[str]):
        self.forms = forms
        ordered = sorted(set(ids), key=lambda one: (-len(one), one))
        self.ids = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(one) for one in ordered)
                              + r")(?![A-Za-z0-9_])") if ordered else None

    def find(self, texts: list[str]) -> tuple[str, str] | None:
        for form in self.forms:
            if any(form in text for text in texts):
                return ("path", form)
        if self.ids is not None:
            for text in texts:
                found = self.ids.search(text)
                if found:
                    return ("id", found.group(1))
        return None


def texts_of(raw: bytes) -> tuple[list[str], object]:
    """``(decoded text values, parsed JSON or None)`` of one line; a line that is not JSON is read as text."""
    text = raw.decode("utf-8", "replace")
    try:
        parsed = json.loads(text)
    except (ValueError, RecursionError):
        return ([text], None)
    texts, stack = [], [parsed]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            texts.append(item)
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return (texts, parsed)


def _moment(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        at = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    return at if at.tzinfo else at.replace(tzinfo=timezone.utc)


def in_window(parsed, since: datetime, until: datetime) -> bool:
    """A line is in the window by its ``timestamp``; one without a readable timestamp counts."""
    at = _moment(parsed.get("timestamp")) if isinstance(parsed, dict) else None
    return True if at is None else since <= at <= until


def _role(path: Path):
    try:
        meta = json.loads((path.parent / f"{path.stem}.meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    role = meta.get("agentType") if isinstance(meta, dict) else None
    return role if isinstance(role, str) else None


def _transcripts(projects: Path, problems: list) -> list[Path]:
    def lost(error: OSError) -> None:
        problems.append({"file": str(error.filename or projects), "error": error.strerror or "unreadable"})

    if not projects.is_dir():
        problems.append({"file": str(projects), "error": "no such folder"})
        return []
    return sorted(Path(folder) / name for folder, _dirs, files in os.walk(projects, onerror=lost)
                  for name in files if name.endswith(".jsonl"))


def scan(set_path, since: datetime, until: datetime, ids, allow, projects, home: str | None = None) -> dict:
    """The scan's result: ``{set, since, until, ids_count, transcripts_read, findings, allowed, problems}``."""
    ids = list(ids) if ids else set_ids(set_path)
    matcher = Matcher(path_forms(set_path, home), ids)
    allow = set(allow or ())
    findings, allowed, problems, read = [], [], [], 0
    for path in _transcripts(Path(projects), problems):
        try:
            if os.stat(path).st_mtime < since.timestamp():
                continue
            handle = open(path, "rb")
        except OSError as error:
            problems.append({"file": str(path), "error": error.strerror or "unreadable"})
            continue
        role = None
        try:
            with handle:
                read += 1
                for number, raw in enumerate(handle, 1):
                    if not raw.strip():
                        continue
                    texts, parsed = texts_of(raw)
                    if not in_window(parsed, since, until):
                        continue
                    hit = matcher.find(texts)
                    if hit is None:
                        continue
                    session = parsed.get("sessionId") if isinstance(parsed, dict) else None
                    session = session if isinstance(session, str) and session else path.stem
                    if role is None:
                        role = _role(path) or ""
                    finding = {"file": str(path), "session": session, "line": number, "role": role or None,
                               "kind": hit[0], "match": hit[1]}
                    (allowed if session in allow else findings).append(finding)
        except OSError as error:
            problems.append({"file": str(path), "error": error.strerror or "unreadable"})
    return {"set": os.path.realpath(set_path), "since": since.isoformat(), "until": until.isoformat(),
            "ids_count": len(set(ids)), "transcripts_read": read, "findings": findings, "allowed": allowed,
            "problems": problems}
