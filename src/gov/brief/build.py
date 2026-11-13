"""The builder behind ``gov brief`` (W2-152; W2-128 TPL-2 S3, TPL-3, TPL-5 S3; DEC-1050, DEC-1052, DEC-1083, DEC-1088).

It reads only the ticket files under ``<root>/.tickets/``, ``<root>/governance/project/facts.yaml``, the kernel
templates with ``keys.yaml``, and the ``--part``/``--repair`` files; it writes nothing and uses no clock, so the same
inputs give the same bytes. ``build`` returns the brief, the ready check's warnings, the refusal findings (each
``{code, detail}``) and the prose size against facts.yaml's ``budgets.brief``; the command decides what to print.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

from gov.brief import ROLE_TEMPLATES
from gov.cli.errors import GovError
from gov.util.frontmatter import FrontmatterError, ids, parse, with_body

EST_LOC_LIMIT = 400  # DEC-1083: over it, a warning (suggest a split), never a refusal
# {KEY}, {KEY: description}, {CMD:name}, {STEP:name}; a brace a shell's $ opens (${HOME}) is none
PLACEHOLDER = re.compile(r"(?<!\$)\{([A-Z][A-Z0-9_]*)(?::([^{}\n]*))?\}")
STEP_NAME = re.compile(r"(?<!\$)\{STEP:\s*([^{}\s]+)\s*\}")
UNTIL = re.compile(r"\buntil\s+(DAEO-[A-Za-z0-9]+|W\d+-[A-Za-z0-9]+)", re.IGNORECASE)
VERIFY = re.compile(r"\s*Verify:\s*(?=\S)")
KIND_LINE = re.compile(r"^\*\*([A-Za-z]+)\*\*:")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TICKET_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
MAX_DEPTH = 8  # a facts value may name another key ({MAIN}/...); no deeper chain is filled


def _read(path: Path) -> str:
    """The file's text; a file that is not UTF-8 or cannot be opened is a named refusal, never a traceback (F5)."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as error:
        raise GovError("BRIEF_FILE_UNREADABLE", f"{path}: {error}", {"path": str(path)}) from None


def _finding(code: str, detail: object = "") -> dict:
    return {"code": code, "detail": str(detail)}


W2_FIELD = re.compile(r"^(?:external-ref|wbs_id):\s*['\"]?([A-Za-z0-9][A-Za-z0-9_.-]*)['\"]?\s*$", re.MULTILINE)


class Tickets:
    """The tickets under ``<root>/.tickets/``, by tk id (the file's stem) or by W2 id (``external-ref``/``wbs_id``).
    A ticket that is not UTF-8, or whose front-matter block is unclosed or not a YAML mapping, reads as empty and
    its reason is kept in ``unreadable`` (F5, F6)."""

    def __init__(self, root: Path):
        self.folder = root / ".tickets"
        self._read: dict[Path, tuple[dict, str]] = {}
        self._by_w2: dict[str, Path] | None = None
        self.unreadable: dict[Path, str] = {}

    def load(self, path: Path) -> tuple[dict, str]:
        if path not in self._read:
            try:
                text = _read(path)
                front = parse(text, rstrip=True)
            except GovError:
                self.unreadable[path] = "not UTF-8"
                front, text = None, None
            except FrontmatterError as error:
                self.unreadable[path] = f"front matter {error.kind}"
                front, text = None, None
            if text is None:
                self._read[path] = ({}, "")
            elif front is None:
                self._read[path] = ({}, text.strip())
            else:
                lines = text.split("\n")
                end = [line.rstrip() for line in lines].index("---", 1)
                self._read[path] = (front, "\n".join(lines[end + 1:]).strip())
        return self._read[path]

    def _w2_of_unreadable(self, path: Path) -> list[str]:
        """The W2 ids an unreadable ticket's raw lines name, so a W2 id still finds it and it is refused by name."""
        return W2_FIELD.findall(path.read_bytes().decode("utf-8", errors="replace"))

    def find(self, ref: str) -> Path | None:
        """The file of the ticket ``ref`` names, or None."""
        if not TICKET_REF.match(ref):
            return None
        path = self.folder / f"{ref}.md"
        if path.is_file():
            return path
        if self._by_w2 is None:
            self._by_w2 = {}
            for other in sorted(self.folder.glob("*.md")) if self.folder.is_dir() else ():
                front = self.load(other)[0]
                named = [front[field] for field in ("external-ref", "wbs_id") if isinstance(front.get(field), str)]
                for w2 in named or (self._w2_of_unreadable(other) if other in self.unreadable else []):
                    self._by_w2.setdefault(w2, other)
        return self._by_w2.get(ref)

    def get(self, ref: str) -> tuple[dict, str] | None:
        """(front matter, body) of the ticket ``ref`` names, or None."""
        found = self.find(ref)
        return self.load(found) if found else None

    def closed(self, ref: str) -> bool:
        ticket = self.get(ref)
        return ticket is not None and ticket[0].get("status") == "closed"


def kpi_rows(front: dict) -> list[tuple[str, str, str | None]]:
    """(label S<n>/F<n>, line, verify or None) of every KPI line: a ``{line, verify}`` with a non-empty verify, or a
    string holding ``Verify:`` followed by text (the ticket's "Interface")."""
    kpis = front.get("kpis") if isinstance(front.get("kpis"), dict) else {}
    rows = []
    for prefix, field in (("S", "success"), ("F", "failure")):
        items = kpis.get(field) if isinstance(kpis.get(field), list) else []
        for number, item in enumerate(items, 1):
            if isinstance(item, dict):
                verify = item.get("verify")
                verify = verify.strip() if isinstance(verify, str) and verify.strip() else None
                rows.append((f"{prefix}{number}", str(item.get("line", "")).strip(), verify))
                continue
            text = str(item)
            split = VERIFY.search(text)
            rows.append((f"{prefix}{number}", text[:split.start()].strip() if split else text.strip(),
                         text[split.end():].strip() if split else None))
    return rows


def _day(value) -> str | None:
    """The ISO day of a date, a timestamp or their text; None when it is none of these."""
    day = str(value)[:10] if value is not None else ""
    return day if ISO_DATE.match(day) else None


def _since(value) -> str | None:
    """facts.yaml's ``ready.new_since`` as an ISO day; None when it is not a date (F3)."""
    if isinstance(value, datetime.date):
        return value.isoformat()[:10]
    text = value.strip() if isinstance(value, str) else ""
    try:
        return text if ISO_DATE.match(text) and datetime.date.fromisoformat(text) else None
    except ValueError:
        return None


def _wait_ref(item) -> str:
    """The id or record path of a waits_on item: ``ref`` of a mapping, a string's first word (``DAEO-x — why``)."""
    if isinstance(item, dict):
        return str(item.get("ref") or "").strip()
    words = str(item).split()
    return words[0].rstrip(":,;") if words else ""


def ready_check(front: dict, tickets: Tickets, root: Path, new_since) -> tuple[list[dict], list[dict]]:
    """(refusals, warnings) of the ready check, DEC-1052 as DEC-1083 amends it, with DEC-1088 (3)'s dependency fields."""
    refuse, warn = [], []
    ticket_id = str(front.get("id", ""))
    if not front.get("allowed_paths"):
        refuse.append(_finding("ALLOWED_PATHS_EMPTY", ticket_id))
    kpis = front.get("kpis")
    if not isinstance(kpis, dict) or not isinstance(kpis.get("success"), list) or not kpis["success"]:
        refuse.append(_finding("KPI_NO_VERIFY", "kpis"))  # no readable success line: none is verified (F4)
    refuse += [_finding("KPI_NO_VERIFY", label) for label, _, verify in kpi_rows(front) if verify is None]
    for dep in ids(front.get("depends_on")):
        if not tickets.closed(dep):
            refuse.append(_finding("DEPENDS_NOT_CLOSED", dep))
    since, created = _day(new_since), _day(front.get("created"))
    if since and created and created >= since:
        for field, code in (("reads", "READS_MISSING"), ("needs", "NEEDS_MISSING"), ("waits_on", "WAITS_ON_MISSING")):
            if not isinstance(front.get(field), list):  # an empty list is a declared none
                refuse.append(_finding(code, ticket_id))
    waits = front.get("waits_on") if isinstance(front.get("waits_on"), list) else []
    for item in waits:
        ref = _wait_ref(item)
        known = (root / ref).exists() if "/" in ref else tickets.get(ref) is not None
        if not ref or not known:
            refuse.append(_finding("WAITS_ON_UNKNOWN", ref or item))
    if not front.get("non_goals"):
        warn.append(_finding("NON_GOALS_MISSING", ticket_id))
    est = front.get("est_loc")
    if isinstance(est, int) and not isinstance(est, bool) and est > EST_LOC_LIMIT:
        warn.append(_finding("EST_LOC_OVER", est))
    return refuse, warn


class Filler:
    """Fills placeholders: ``literal`` values (the ticket's, the flags') as they are; ``values`` (facts' paths and
    forms) filled again; a key with no value is left as written when ``keys.yaml`` holds it (a form key the session
    fills), else it is a ``PLACEHOLDER_LEFT``, as is a ``CMD:``/``STEP:`` name facts.yaml does not hold."""

    def __init__(self, literal: dict, values: dict, facts: dict, keys: set[str]):
        self.literal, self.values, self.keys = literal, values, keys
        self.commands = facts.get("commands") if isinstance(facts.get("commands"), dict) else {}
        self.steps = facts.get("steps") if isinstance(facts.get("steps"), dict) else {}
        self.left: list[str] = []

    def _leave(self, key: str, text: str) -> str:
        if key not in self.left:
            self.left.append(key)
        return text

    def text(self, text: str, depth: int = 0) -> str:
        def one(match: re.Match) -> str:
            key, rest = match.group(1), match.group(2)
            if key in ("CMD", "STEP") and rest is not None:
                name = rest.strip()
                entry = (self.commands if key == "CMD" else self.steps).get(name)
                form = entry.get("run" if key == "CMD" else "line") if isinstance(entry, dict) else None
                return self.text(form, depth + 1) if isinstance(form, str) else self._leave(f"{key}:{name}",
                                                                                          match.group(0))
            if key in self.literal:
                return self.literal[key]
            if key in self.values:
                return self.text(self.values[key], depth + 1)
            return match.group(0) if key in self.keys else self._leave(key, match.group(0))

        return text if depth > MAX_DEPTH else PLACEHOLDER.sub(one, text)

    def step_off(self, line: str) -> bool:
        return any(isinstance(self.steps.get(name), dict) and self.steps[name].get("on") is False
                   for name in STEP_NAME.findall(line))

    def lines(self, text: str) -> str:
        """The text filled line by line; a line holding a step switched off is dropped whole (TPL-2 S3)."""
        return "\n".join(self.text(line) for line in text.split("\n") if not self.step_off(line))


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _summary(body: str) -> str:
    """The body's first paragraph that is not a heading, its lines joined."""
    held: list[str] = []
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if held:
                break
            continue
        held.append(stripped)
    return " ".join(held)


def run_section(body: str, kind: str) -> list[str]:
    """T-7's "## Your run: {RUN_KIND}" heading and that kind's block: from its "**<kind>**:" line to the next such
    line or the section's first {STEP:} line (TPL-3 S7)."""
    lines = body.split("\n")
    start = next((n for n, line in enumerate(lines) if line.startswith("## Your run:")), None)
    if start is None:
        raise GovError("BRIEF_RUN_MISSING", "role-lead.md has no \"## Your run:\" section", {"run": kind})
    block, inside = [], False
    for line in lines[start + 1:]:
        if line.startswith("## ") or STEP_NAME.search(line):
            break
        heading = KIND_LINE.match(line)
        inside = heading.group(1) == kind if heading else inside
        if inside:
            block.append(line)
    while block and not block[-1].strip():
        block.pop()
    if not block:
        raise GovError("BRIEF_RUN_MISSING", f"role-lead.md has no \"**{kind}**:\" block", {"run": kind})
    return [lines[start], *block]


def prose_size(text: str) -> int:
    """R3 §C's measure: the characters left without fenced code blocks and table lines."""
    kept, fenced = [], False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and not stripped.startswith("|"):
            kept.append(line)
    return len("\n".join(kept))


def _templates(root: Path) -> Path:
    kernel = root / "template/governance/kernel/templates"
    return kernel if kernel.is_dir() else root / "governance/kernel/templates"


def _template(folder: Path, stem: str) -> tuple[dict, str, str]:
    """(front matter, body, the whole file's text) of a kernel template."""
    path = folder / f"{stem}.md"
    if not path.is_file():
        raise GovError("BRIEF_TEMPLATE_MISSING", f"no template {stem}.md in {folder}", {"template": stem})
    text = _read(path)
    front, body = with_body(text)
    return (front if isinstance(front, dict) else {}), body, text


def _yaml(path: Path, code: str = "BRIEF_FILE_UNREADABLE") -> dict:
    """The YAML mapping in ``path``, {} when there is no such file; YAML that cannot be read is ``code`` (F5)."""
    import yaml

    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(_read(path))
    except GovError as error:
        raise GovError(code, error.message, {"path": str(path)}) from None
    except yaml.YAMLError as error:
        raise GovError(code, f"{path}: not valid YAML: {error}", {"path": str(path)}) from None
    return data if isinstance(data, dict) else {}


def _flag_file(path: str | None, flag: str) -> str | None:
    if path is None:
        return None
    if not Path(path).is_file():
        raise GovError("BRIEF_FILE_MISSING", f"{flag} {path}: no such file", {"flag": flag, "path": path})
    return _read(Path(path)).rstrip("\n")


def build(root: Path, role: str, ticket_ref: str, run: str | None = None, part: str | None = None,
          repair: str | None = None) -> dict:
    """``{brief, warnings, findings, size, budget, ticket}``; findings non-empty means BRIEF_NOT_READY."""
    if (role == "lead") != (run is not None):
        raise GovError("BRIEF_RUN_MISSING", "--run <kind> goes with the lead role, and only with it",
                       {"role": role, "run": run})
    tickets = Tickets(root)
    ticket_path = tickets.find(ticket_ref)
    if ticket_path is None:
        raise GovError("BRIEF_TICKET_UNKNOWN", f"no ticket {ticket_ref} in {root / '.tickets'}", {"ticket": ticket_ref})
    front, body = tickets.load(ticket_path)
    facts_path = root / "governance/project/facts.yaml"
    if not facts_path.is_file():
        raise GovError("BRIEF_FACTS_MISSING", f"no facts file at {facts_path}", {"path": str(facts_path)})
    facts = _yaml(facts_path, "BRIEF_FACTS_UNREADABLE")
    budgets = facts.get("budgets") if isinstance(facts.get("budgets"), dict) else {}
    if ticket_path in tickets.unreadable:  # F6: refused by its own name, not as the fields it seems to miss
        return {"brief": "", "warnings": [], "size": 0, "budget": budgets.get("brief"), "ticket": ticket_ref,
                "findings": [_finding("TICKET_UNREADABLE", f"{ticket_ref}: {tickets.unreadable[ticket_path]}")]}
    folder = _templates(root)
    keys = _yaml(folder / "keys.yaml").get("keys")
    keys = {str(key) for key in keys} if isinstance(keys, list) else set()
    _, t0, t0_text = _template(folder, "brief")
    role_front, role_body, role_text = _template(folder, ROLE_TEMPLATES[role])
    lead_lines = run_section(role_body, run) if run else []
    part_text, repair_text = _flag_file(part, "--part"), _flag_file(repair, "--repair")

    ready = facts.get("ready")
    new_since = ready.get("new_since") if isinstance(ready, dict) else None
    since = _since(new_since)
    refuse, warnings = ready_check(front, tickets, root, since)
    if since is None:  # F3: the dependency-field check never switches off silently
        missing = not isinstance(ready, dict) or new_since is None
        refuse.append(_finding("READY_NEW_SINCE_MISSING" if missing else "READY_NEW_SINCE_NOT_DATE", "ready.new_since"))
    # F1: the whole role template, every role's, goes as the system prompt (W2-153), so all of it is scanned
    for line in [*t0_text.split("\n"), *role_text.split("\n"), *(part_text or "").split("\n")]:
        for ref in UNTIL.findall(line):
            if tickets.closed(ref) and _finding("UNTIL_CLOSED", ref) not in refuse:
                refuse.append(_finding("UNTIL_CLOSED", ref))

    literal, values = _values(front, body, facts, role, role_front, run, part_text, repair_text, root)
    filler = Filler(literal, values, facts, keys)
    literal["COMMANDS_TABLE"] = _commands_table(role_body, filler)
    brief = filler.lines(t0).rstrip("\n") + "\n"
    if lead_lines:
        brief += "\n" + filler.lines("\n".join(lead_lines)) + "\n"
    findings = refuse + [_finding("PLACEHOLDER_LEFT", key) for key in filler.left]
    return {"brief": brief, "warnings": warnings, "findings": findings, "size": prose_size(brief),
            "budget": budgets.get("brief"), "ticket": str(front.get("id", ticket_ref))}


def _values(front, body, facts, role, role_front, run, part_text, repair_text, root) -> tuple[dict, dict]:
    """(literal, facts-filled) values of the keys."""
    w2 = front.get("external-ref") or front.get("wbs_id")
    paths = [str(path) for path in front.get("allowed_paths") or []] if isinstance(front.get("allowed_paths"), list) \
        else []
    sources = ", ".join(ids(front.get("sources")))
    dod = facts.get("dod") if isinstance(facts.get("dod"), list) else []
    rows = kpi_rows(front)
    table = ["| id | line | verify |", "|---|---|---|"]
    table += [f"| {label} | {_cell(line)} | {_cell(verify or 'none')} |" for label, line, verify in rows]
    unit = next((path for path in paths if path.startswith("tests/unit/")), None)
    literal = {
        "ID": str(front.get("id", "")),
        "TITLE": str(front.get("title", "")),
        "TICKET_SUMMARY": _summary(body),
        "PATHS": ", ".join(paths) or "none",
        "SOURCES": sources or "none",
        "IMPL": sources or "none",
        "KPI_TABLE": "\n".join(table),
        "NON_GOALS": "; ".join(ids(front.get("non_goals"))) or "none",
        "DOD_REFS": ", ".join(ids(front.get("done_when"))
                              or [str(item.get("id")) for item in dod if isinstance(item, dict)]) or "none",
        "ROLE": str(role_front.get("role") or role),
        "ROLE_TEMPLATE": ROLE_TEMPLATES[role],
        "ROLE_VERSION": str(role_front.get("version", "")),
        "LEAD_NOTE": part_text if part_text else "none",
        "REPAIR": repair_text if repair_text else "none",
        "HARNESS_ALLOWED": ", ".join(str(item) for item in facts.get("harness_allowed") or []) or "none",
    }
    for key, value in (("W2", w2), ("PROFILE", front.get("profile")), ("EST", front.get("est_loc")),
                       ("IMPL_ROLE", front.get("role")), ("RUN_KIND", run),
                       ("UNIT_TEST_PATH", unit[:-2] if unit and unit.endswith("**") else unit)):
        if value is not None:
            literal[key] = str(value)
    values = {name.upper(): str(path) for name, path in (facts.get("paths") or {}).items()} \
        if isinstance(facts.get("paths"), dict) else {}
    designer = role == "independent-test-designer"
    values["WRITE_TREE"] = "{TESTS_TREE}" if designer else "{TREE}"
    if w2 is not None:
        values["BRANCH"] = f"w2/{w2}-tests" if designer else f"w2/{w2}"
    return literal, values


def _commands_table(role_body: str, filler: Filler) -> str:
    """The commands the role's template names ({CMD:name}, in order of first use), each with its filled form."""
    names: list[str] = []
    for key, rest in PLACEHOLDER.findall(role_body):
        if key == "CMD" and rest.strip() and rest.strip() not in names and rest.strip() in filler.commands:
            names.append(rest.strip())
    rows = ["| name | command |", "|---|---|"]
    rows += [f"| {name} | `{_cell(filler.text('{CMD:' + name + '}'))}` |" for name in names]
    return "\n".join(rows)
