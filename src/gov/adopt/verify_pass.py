"""The Verify pass of an adopted repository's tickets (W2-174; DEC-1130, DEC-1083, DEC-1050).

``missing`` lists, for each open or in-progress ticket under ``<root>/.tickets/``, the KPI lines that carry no verify
(read with ``gov.brief.build.kpi_rows``, so the list and ``gov brief``'s ready check agree). ``apply`` takes an answers
file ``{<ticket id>: {S1: "<clause>", F2: "<clause>"}}``, checks all of it, then appends `` Verify: <clause>`` to each
named line by editing the ticket's text (never a YAML dump: comments and key order stay) and adds the one front-matter
line ``verify_pass: <date> <session>``. Nothing is written unless every check and every re-read passed. The module
opens nothing outside ``<root>/.tickets/`` and the answers file, and uses no network or model.
"""

from __future__ import annotations

import datetime
import os
import re
from pathlib import Path

import yaml

from gov.brief.build import kpi_rows
from gov.cli.errors import GovError
from gov.util.frontmatter import FrontmatterError, parse

OPEN = ("open", "in_progress")
EMPTY = {"", "tbd", "todo", "n/a", "none"}
STR_TAG = "tag:yaml.org,2002:str"
FIELDS = (("S", "success"), ("F", "failure"))


def _refuse(code: str, message: str, **details) -> GovError:
    return GovError(code, message, details)


def _tickets(root: Path) -> dict[str, tuple[Path, str, dict]]:
    """{id: (file, text, front matter)} of the readable tickets under ``<root>/.tickets/``."""
    found = {}
    for path in sorted((Path(root) / ".tickets").glob("*.md")):
        try:
            text = path.read_bytes().decode("utf-8")
            front = parse(text, rstrip=True)
        except (OSError, UnicodeDecodeError, FrontmatterError):
            continue
        if front is not None:
            found.setdefault(str(front.get("id") or path.stem), (path, text, front))
    return found


def missing(root) -> list[dict]:
    """``[{"ticket": id, "labels": [...]}]`` by id: open or in-progress tickets with a line lacking a verify."""
    out = []
    for ticket, (_, _, front) in sorted(_tickets(Path(root)).items()):
        labels = [label for label, _, verify in kpi_rows(front) if verify is None]
        if labels and front.get("status") in OPEN:
            out.append({"ticket": ticket, "labels": labels})
    return out


def _answers(path) -> dict[str, dict[str, object]]:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise _refuse("VERIFY_PASS_ANSWERS_UNREADABLE", f"{path}: {error}", path=str(path)) from None
    if not isinstance(data, dict) or not all(isinstance(entry, dict) for entry in data.values()):
        raise _refuse("VERIFY_PASS_ANSWERS_UNREADABLE", f"{path}: not a mapping of tickets to mappings of clauses",
                      path=str(path))
    return {str(ticket): {str(label): clause for label, clause in entry.items()} for ticket, entry in data.items()}


def _clause(ticket: str, label: str, clause) -> str:
    text = " ".join(clause.split()) if isinstance(clause, str) and ("\n" in clause or "\r" in clause) else clause
    if not isinstance(text, str) or text.strip().rstrip(".").strip().casefold() in EMPTY:
        raise _refuse("VERIFY_PASS_EMPTY_CLAUSE", f"{ticket} {label}: the clause is not text of its own",
                      ticket=ticket, label=label)
    return text.strip()


def _checked(root: Path, tickets: dict, answers: dict) -> dict[str, dict[str, str]]:
    """The answers, every entry checked (L4): ``{ticket: {label: clause}}``; the first refusal is raised."""
    checked = {}
    for ticket, entry in answers.items():
        if ticket not in tickets:
            raise _refuse("VERIFY_PASS_UNKNOWN_TICKET", f"{ticket}: no such ticket under .tickets/", ticket=ticket)
        front = tickets[ticket][2]
        if front.get("status") == "closed":
            raise _refuse("VERIFY_PASS_CLOSED", f"{ticket} is closed", ticket=ticket)
        lacking = [label for label, _, verify in kpi_rows(front) if verify is None]
        for label in entry:
            if label not in lacking:
                raise _refuse("VERIFY_PASS_UNKNOWN_LABEL", f"{ticket}: no line {label} lacking a verify", ticket=ticket,
                              label=label)
        for label in lacking:
            if label not in entry:
                raise _refuse("VERIFY_PASS_UNANSWERED", f"{ticket}: line {label} still lacks a verify", ticket=ticket,
                              label=label)
        if entry:
            checked[ticket] = {label: _clause(ticket, label, clause) for label, clause in entry.items()}
    return checked


def _quoted(node, clause: str) -> tuple[int, int, str]:
    """(start, end, text): the clause inside the item's quotes, or the plain item as one single-quoted scalar."""
    start, end, style, add = node.start_mark.index, node.end_mark.index, node.style, f" Verify: {clause}"
    if style == '"':
        return end - 1, end - 1, add.replace("\\", "\\\\").replace('"', '\\"')
    if style == "'":
        return end - 1, end - 1, add.replace("'", "''")
    # a plain scalar cannot hold ``Verify: <clause>`` (its ``: `` opens a mapping): that one item becomes single-quoted
    return start, end, "'" + (node.value + add).replace("'", "''") + "'"


def _edits(ticket: str, text: str, answered: dict[str, str]) -> list[tuple[int, int, str]]:
    """The text edits (offsets into the front matter's text) that append each clause."""
    refuse = lambda why: _refuse("VERIFY_PASS_EDIT_FAILED", f"{ticket}: {why}", ticket=ticket)  # noqa: E731
    try:
        node = yaml.compose(text)
    except yaml.YAMLError as error:
        raise refuse(f"front matter cannot be composed: {error}") from None
    kpis = next((value for key, value in node.value if key.value == "kpis"), None) if node else None
    if not isinstance(kpis, yaml.MappingNode):
        raise refuse("no kpis mapping")
    edits = []
    for prefix, field in FIELDS:
        seq = next((value for key, value in kpis.value if key.value == field), None)
        for number, item in enumerate(seq.value if isinstance(seq, yaml.SequenceNode) else (), 1):
            clause = answered.get(f"{prefix}{number}")
            if clause is None:
                continue
            if not isinstance(item, yaml.ScalarNode) or item.tag != STR_TAG or item.style in ("|", ">"):
                raise refuse(f"line {prefix}{number} is not a string scalar the tool can extend")
            edits.append(_quoted(item, clause))
    return edits


def _rewrite(ticket: str, text: str, answered: dict[str, str], marker: str) -> str:
    """The new text: the clauses appended in place, the marker line replaced or added before the closing ---."""
    lines = text.split("\n")
    end = [line.rstrip() for line in lines].index("---", 1)
    front = "\n".join(lines[1:end])
    for start, stop, new in sorted(_edits(ticket, front, answered), reverse=True):
        front = front[:start] + new + front[stop:]
    new_lines = front.split("\n")
    eol = "\r" if lines[end].endswith("\r") or (end > 1 and lines[end - 1].endswith("\r")) else ""
    slot = next((n for n, line in enumerate(new_lines) if re.match(r"verify_pass:", line)), None)
    if slot is None:
        new_lines.append(marker + eol)
    else:
        new_lines[slot] = marker + (eol if new_lines[slot].endswith("\r") else "")
    return "\n".join([lines[0], *new_lines, *lines[end:]])


def _reread(ticket: str, old: dict, new_text: str, answered: dict[str, str], value: str) -> None:
    """The edit's check (L5): the new text reads, each answered label holds its clause, nothing else changed."""
    try:
        new = parse(new_text, rstrip=True)
    except FrontmatterError:
        new = None
    fail = lambda why: _refuse("VERIFY_PASS_EDIT_FAILED", f"{ticket}: {why}", ticket=ticket)  # noqa: E731
    if new is None:
        raise fail("the edited front matter cannot be read")
    rest = lambda front: {key: item for key, item in front.items() if key not in ("kpis", "verify_pass")}  # noqa: E731
    if rest(new) != rest(old) or new.get("verify_pass") != value:
        raise fail("a front-matter value changed or the marker did not read back")
    old_rows, new_rows = kpi_rows(old), kpi_rows(new)
    if len(old_rows) != len(new_rows) or any(
            (label, line) != (n_label, n_line) or (verify if label not in answered else answered[label]) != n_verify
            for (label, line, verify), (n_label, n_line, n_verify) in zip(old_rows, new_rows)):
        raise fail("a KPI line or its verify did not read back as expected")
    for field in ("success", "failure"):
        old_items, new_items = old["kpis"].get(field) or [], new["kpis"].get(field) or []
        prefix = field[0].upper()
        if len(old_items) != len(new_items) or any(
                old_item != new_item for number, (old_item, new_item) in enumerate(zip(old_items, new_items), 1)
                if f"{prefix}{number}" not in answered):
            raise fail("a KPI line the answers do not name changed")
    if {k: v for k, v in old["kpis"].items() if k not in ("success", "failure")} != \
            {k: v for k, v in new["kpis"].items() if k not in ("success", "failure")}:
        raise fail("kpis changed beyond its lines")


def _write(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp{os.getpid()}")
    temporary.write_bytes(text.encode("utf-8"))
    os.chmod(temporary, path.stat().st_mode & 0o7777)
    os.replace(temporary, path)


def apply(root, answers_path, session: str, today: datetime.date) -> list[str]:
    """Check the answers file whole, then edit; the ids of the tickets changed. Nothing is written on a refusal."""
    root = Path(root)
    tickets = _tickets(root)
    checked = _checked(root, tickets, _answers(answers_path))
    value, new_texts = f"{today.isoformat()} {session}", {}
    marker = f"verify_pass: {value}"
    for ticket, answered in sorted(checked.items()):
        path, text, front = tickets[ticket]
        new_texts[path] = _rewrite(ticket, text, answered, marker)
        _reread(ticket, front, new_texts[path], answered, value)
    written = {}
    try:
        for path, new_text in new_texts.items():
            old = path.read_bytes()
            _write(path, new_text)
            written[path] = old
    except OSError as error:  # no half apply: what was written goes back
        for path, old in written.items():
            path.write_bytes(old)
        raise _refuse("VERIFY_PASS_WRITE_FAILED", f"a ticket could not be written: {error}") from None
    return sorted(checked)
