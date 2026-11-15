"""The Verify pass of an adopted repository's tickets (W2-174; DEC-1130, DEC-1083, DEC-1050).

``missing`` lists, for each open or in-progress ticket under ``<root>/.tickets/``, the KPI lines that carry no verify
(read with ``gov.brief.build.kpi_rows``, so the list and ``gov brief``'s ready check agree). ``apply`` takes an answers
file ``{<ticket id>: {S1: "<clause>", F2: "<clause>"}}``, checks all of it, then appends `` Verify: <clause>`` to each
named line by editing the ticket's text (never a YAML dump: comments and key order stay) and adds the one front-matter
line ``verify_pass: <date> <session>``. Nothing is written unless every check and every re-read passed.

DEC-1188 (S6, S7, F4): the same list and apply also take the six launch fields (``role``, ``allowed_paths``, ``kpis``,
``reads``, ``needs``, ``waits_on``) a ticket lacks: a field is lacking when its key is absent, a field the ticket has is
never overwritten, each answered field is checked (its form, the role, a path that reaches ``tests/acceptance/``, a KPI
line's verify) and inserted as YAML text lines before the marker, and the ticket as it would be written must validate
against the kernel's ticket schema. The module opens nothing outside ``<root>/.tickets/``, the answers file and the
schemas shipped with gov, and uses no network or model.
"""

from __future__ import annotations

import datetime
import json
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
LAUNCH_FIELDS = ("role", "allowed_paths", "kpis", "reads", "needs", "waits_on")  # L10: the order of list and write
ROLES = ("orchestrator", "product-spec", "independent-test-designer", "engineer", "independent-auditor", "research")
TEST_DESIGNER = "independent-test-designer"
ACCEPTANCE = "tests/acceptance/"
SCHEMA_REL = Path("template/governance/kernel/schemas")
SCHEMA_FILES = ("ticket.schema.json", "common.schema.json")


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


def _lacking(front: dict) -> tuple[list[str], list[str]]:
    """(the labels of the KPI lines lacking a verify, the launch fields whose key is absent), each in its own order."""
    return [label for label, _, verify in kpi_rows(front) if verify is None], \
        [field for field in LAUNCH_FIELDS if field not in front]


def missing(root) -> list[dict]:
    """``[{"ticket": id, "labels": [...], "fields": [...]}]`` by id: open or in-progress tickets with a line lacking a
    verify or a launch field whose key is absent."""
    out = []
    for ticket, (_, _, front) in sorted(_tickets(Path(root)).items()):
        labels, fields = _lacking(front)
        if (labels or fields) and front.get("status") in OPEN:
            out.append({"ticket": ticket, "labels": labels, "fields": fields})
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


def _text(value) -> str | None:
    """A non-empty string as one line (newlines folded to single spaces, ends stripped); None for anything else."""
    if not isinstance(value, str):
        return None
    text = " ".join(value.split()) if "\n" in value or "\r" in value else value
    return text.strip() or None


def _bad(ticket: str, field: str, why: str) -> GovError:
    return _refuse("VERIFY_PASS_BAD_FIELD", f"{ticket} {field}: {why}", ticket=ticket, field=field)


def _strings(ticket: str, field: str, value) -> list[str]:
    if not isinstance(value, list) or any(_text(item) is None for item in value):
        raise _bad(ticket, field, "not a list of non-empty strings")
    return [_text(item) for item in value]


def _segments(ticket: str, pattern: str) -> str:
    """The pattern with ``.`` and empty segments dropped; a ``..`` segment or a leading ``/`` is a bad field (L13)."""
    if pattern.startswith("/") or ".." in pattern.split("/"):
        raise _bad(ticket, "allowed_paths", f"{pattern!r}: no absolute path and no '..' segment")
    return "/".join(part for part in pattern.split("/") if part not in ("", "."))


def _reaches_acceptance(ticket: str, pattern: str) -> bool:
    """True when the pattern can match something under ``tests/acceptance/``: its literal part (the text before its
    first ``*``, ``?`` or ``[``) starts with that folder or is a prefix of it (L13)."""
    literal = re.split(r"[*?\[]", _segments(ticket, pattern), 1)[0].casefold()
    return literal.startswith(ACCEPTANCE) or ACCEPTANCE.startswith(literal)


def _kpi_item(ticket: str, item):
    """One KPI line of the answers: the normalised item (a ``{line, verify}`` mapping or a string) with its verify
    checked by the rules of ``kpi_rows`` and of the clauses."""
    if isinstance(item, dict):
        if set(item) - {"line", "verify"} or _text(item.get("line")) is None:
            raise _bad(ticket, "kpis", "a line is a string or {line, verify}, the line non-empty")
        verify = item.get("verify")
        if not isinstance(verify, str):
            raise _refuse("VERIFY_PASS_KPI_NO_VERIFY", f"{ticket}: a KPI line has no verify", ticket=ticket)
        return {"line": _text(item["line"]), "verify": _clause(ticket, "kpis", verify)}
    text = _text(item)
    if text is None:
        raise _bad(ticket, "kpis", "a line is a string or {line, verify}, the line non-empty")
    verify = kpi_rows({"kpis": {"success": [text]}})[0][2]
    if verify is None:
        raise _refuse("VERIFY_PASS_KPI_NO_VERIFY", f"{ticket}: a KPI line has no verify", ticket=ticket)
    _clause(ticket, "kpis", verify)
    return text


def _kpis(ticket: str, value) -> dict:
    if not isinstance(value, dict) or set(value) != {"success", "failure"} or \
            not isinstance(value["success"], list) or not isinstance(value["failure"], list) or not value["success"]:
        raise _bad(ticket, "kpis", "a mapping {success: [at least one line], failure: [lines]}")
    return {field: [_kpi_item(ticket, item) for item in value[field]] for field in ("success", "failure")}


def _wait(ticket: str, item):
    if isinstance(item, dict):
        if set(item) != {"ref", "reason"} or _text(item["ref"]) is None or _text(item["reason"]) is None:
            raise _bad(ticket, "waits_on", "an item is a string or {ref, reason}, both non-empty")
        return {"ref": _text(item["ref"]), "reason": _text(item["reason"])}
    if _text(item) is None:
        raise _bad(ticket, "waits_on", "an item is a string or {ref, reason}, both non-empty")
    return _text(item)


def _field(ticket: str, field: str, value, role) -> object:
    """The answer for one launch field in the form the ticket is written with; the first refusal is raised (L13)."""
    if field == "role":
        if not isinstance(value, str):
            raise _bad(ticket, field, "not a string")
        if value not in ROLES:
            raise _refuse("VERIFY_PASS_UNKNOWN_ROLE", f"{ticket}: {value!r} is not a role a ticket is launched under",
                          ticket=ticket, role=value)
        return value
    if field == "allowed_paths":
        paths = _strings(ticket, field, value)
        if not paths:
            raise _bad(ticket, field, "an empty list")
        for pattern in paths:
            if role != TEST_DESIGNER and _reaches_acceptance(ticket, pattern):
                raise _refuse("VERIFY_PASS_ACCEPTANCE_PATH", f"{ticket}: {pattern!r} can reach {ACCEPTANCE} and the "
                              f"role is not {TEST_DESIGNER}", ticket=ticket, path=pattern)
            _segments(ticket, pattern)
        return paths
    if field == "kpis":
        return _kpis(ticket, value)
    if field == "waits_on":
        if not isinstance(value, list):
            raise _bad(ticket, field, "not a list")
        return [_wait(ticket, item) for item in value]
    return _strings(ticket, field, value)  # reads, needs


def _checked(root: Path, tickets: dict, answers: dict) -> dict[str, dict[str, dict]]:
    """The answers, every entry checked (L4, L13): ``{ticket: {"labels": {label: clause}, "fields": {field: value}}}``;
    the first refusal is raised."""
    checked = {}
    for ticket, entry in answers.items():
        if ticket not in tickets:
            raise _refuse("VERIFY_PASS_UNKNOWN_TICKET", f"{ticket}: no such ticket under .tickets/", ticket=ticket)
        front = tickets[ticket][2]
        if front.get("status") == "closed":
            raise _refuse("VERIFY_PASS_CLOSED", f"{ticket} is closed", ticket=ticket)
        lacking, absent = _lacking(front)
        for label in entry:
            if label in LAUNCH_FIELDS:
                if label in front:
                    raise _refuse("VERIFY_PASS_FIELD_SET", f"{ticket}: {label} is already set and is never overwritten",
                                  ticket=ticket, field=label)
            elif label not in lacking:
                raise _refuse("VERIFY_PASS_UNKNOWN_LABEL", f"{ticket}: no line {label} lacking a verify", ticket=ticket,
                              label=label)
        for label in (*lacking, *absent):
            if label not in entry:
                raise _refuse("VERIFY_PASS_UNANSWERED", f"{ticket}: {label} is still lacking", ticket=ticket,
                              label=label)
        role = entry["role"] if "role" in entry else front.get("role")
        fields = {field: _field(ticket, field, entry[field], role) for field in LAUNCH_FIELDS if field in entry}
        if entry:
            checked[ticket] = {"labels": {label: _clause(ticket, label, entry[label]) for label in lacking},
                               "fields": fields}
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


def _field_lines(fields: dict) -> list[str]:
    """The YAML text lines of the answered fields, in L10 order (a dump of those values alone, never of the ticket)."""
    lines = []
    for field in LAUNCH_FIELDS:
        if field in fields:
            dumped = yaml.safe_dump({field: fields[field]}, default_flow_style=False, sort_keys=False,
                                    allow_unicode=True, width=1 << 30)
            lines += dumped.rstrip("\n").split("\n")
    return lines


def _rewrite(ticket: str, text: str, answered: dict, marker: str) -> str:
    """The new text: the clauses appended in place, the field lines and the marker line before the closing ---: the
    fields before the marker when it is last, otherwise at the end after it (the marker is replaced in place)."""
    lines = text.split("\n")
    end = [line.rstrip() for line in lines].index("---", 1)
    front = "\n".join(lines[1:end])
    if answered["labels"]:
        for start, stop, new in sorted(_edits(ticket, front, answered["labels"]), reverse=True):
            front = front[:start] + new + front[stop:]
    new_lines = front.split("\n")
    eol = "\r" if lines[end].endswith("\r") or (end > 1 and lines[end - 1].endswith("\r")) else ""
    added = [line + eol for line in _field_lines(answered["fields"])]
    slot = next((n for n, line in enumerate(new_lines) if re.match(r"verify_pass:", line)), None)
    if slot is None:
        new_lines += [*added, marker + eol]
    else:
        new_lines[slot] = marker + (eol if new_lines[slot].endswith("\r") else "")
        at = slot if slot == len(new_lines) - 1 else len(new_lines)
        new_lines[at:at] = added
    return "\n".join([lines[0], *new_lines, *lines[end:]])


def _reread(ticket: str, old: dict, new_text: str, answered: dict, value: str) -> dict:
    """The edit's check (L5, L14): the new text reads and holds the old front matter plus exactly the answered fields,
    clauses and the marker; the new front matter."""
    labels, fields = answered["labels"], answered["fields"]
    try:
        new = parse(new_text, rstrip=True)
    except FrontmatterError:
        new = None
    fail = lambda why: _refuse("VERIFY_PASS_EDIT_FAILED", f"{ticket}: {why}", ticket=ticket)  # noqa: E731
    if new is None:
        raise fail("the edited front matter cannot be read")
    rest = lambda front: {key: item for key, item in front.items()  # noqa: E731
                          if key not in ("kpis", "verify_pass", *fields)}
    if rest(new) != rest(old) or new.get("verify_pass") != value:
        raise fail("a front-matter value changed or the marker did not read back")
    if any(field not in new or new[field] != expected for field, expected in fields.items()):
        raise fail("a field did not read back as answered")
    if "kpis" in fields:
        return new
    old_rows, new_rows = kpi_rows(old), kpi_rows(new)
    if len(old_rows) != len(new_rows) or any(
            (label, line) != (n_label, n_line) or (verify if label not in labels else labels[label]) != n_verify
            for (label, line, verify), (n_label, n_line, n_verify) in zip(old_rows, new_rows)):
        raise fail("a KPI line or its verify did not read back as expected")
    for field in ("success", "failure"):
        old_items, new_items = old["kpis"].get(field) or [], new["kpis"].get(field) or []
        prefix = field[0].upper()
        if len(old_items) != len(new_items) or any(
                old_item != new_item for number, (old_item, new_item) in enumerate(zip(old_items, new_items), 1)
                if f"{prefix}{number}" not in labels):
            raise fail("a KPI line the answers do not name changed")
    if {k: v for k, v in old["kpis"].items() if k not in ("success", "failure")} != \
            {k: v for k, v in new["kpis"].items() if k not in ("success", "failure")}:
        raise fail("kpis changed beyond its lines")
    return new


def _validator(ticket: str):
    """The ticket schema as a validator class instance: ``ticket.schema.json`` with ``common.schema.json``'s definitions
    merged into its ``$defs`` (so no reference leaves the file), read from gov's own source tree, else from the copy
    shipped inside the package, never from the repository being adopted. Refuses ``VERIFY_PASS_SCHEMA`` (fail closed)
    when ``jsonschema`` or the schema files cannot be had."""
    try:
        import jsonschema
    except ImportError:
        raise _refuse("VERIFY_PASS_SCHEMA", f"{ticket}: jsonschema is not installed: the ticket cannot be checked "
                      "against the ticket schema", ticket=ticket) from None
    here = Path(__file__).resolve()
    tree = next((folder / SCHEMA_REL for folder in here.parents if (folder / SCHEMA_REL / SCHEMA_FILES[0]).is_file()),
                here.parent / "no-source-tree" / SCHEMA_REL)  # the nearest ancestor of gov that holds the schemas
    looked = [tree, here.parent.parent / "_shipped" / SCHEMA_REL]
    for folder in looked:
        try:
            texts = [(folder / name).read_text(encoding="utf-8") for name in SCHEMA_FILES]
            ticket_schema, common = (json.loads(text) for text in texts)
            merged = json.loads(json.dumps(ticket_schema).replace("common.schema.json#", "#"))
            merged["$defs"] = {**ticket_schema.get("$defs", {}), **common.get("$defs", {})}
            return jsonschema.Draft202012Validator(merged)
        except (OSError, UnicodeDecodeError, ValueError, AttributeError, jsonschema.SchemaError):
            continue
    raise _refuse("VERIFY_PASS_SCHEMA", f"{ticket}: the kernel's ticket schema cannot be read (looked in: "
                  + "; ".join(str(folder) for folder in looked) + ")", ticket=ticket)


def _valid(ticket: str, validator, front: dict) -> None:
    """L13: the ticket as it would be written validates against the ticket schema, else ``VERIFY_PASS_SCHEMA``."""
    def iso(value):
        if isinstance(value, (datetime.date, datetime.time)):
            return value.isoformat()
        raise TypeError(f"{type(value).__name__} has no JSON form")
    try:
        errors = sorted(validator.iter_errors(json.loads(json.dumps(front, default=iso, allow_nan=False))),
                        key=lambda error: [str(part) for part in error.path])
    except (TypeError, ValueError) as error:
        raise _refuse("VERIFY_PASS_SCHEMA", f"{ticket}: the front matter has no JSON form ({error})",
                      ticket=ticket) from None
    if errors:
        raise _refuse("VERIFY_PASS_SCHEMA", f"{ticket}: fails the ticket schema: " + "; ".join(
            f"{'/'.join(str(part) for part in error.path) or 'ticket'}: {error.message}" for error in errors[:3]),
            ticket=ticket)


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
    validator = None
    for ticket, answered in sorted(checked.items()):
        path, text, front = tickets[ticket]
        new_texts[path] = _rewrite(ticket, text, answered, marker)
        new = _reread(ticket, front, new_texts[path], answered, value)
        validator = validator or _validator(ticket)
        _valid(ticket, validator, new)
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
