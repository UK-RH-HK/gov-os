"""``gov links`` (W2-129; DEC-1073 (5)(b), DEC-1052, LINK-INTEGRITY §4): every unlinked or contradicted record.

Read-only, from ``HEAD`` as the store's loader reads it (no store, no model, no network): the records (every Markdown
file's frontmatter), the register the path map names, ``ARCHIVE-SUPERSEDED.md`` and ``DECISIONS-IN-FORCE.md`` in
``governance/project/orchestration/`` where the project has them, ``docs/contract/contract.yaml`` and
``CONTRACT_v*.md``, the kernel's role, skill and template texts, the project's briefs and prompts, the path map, the
test files and the commits. The only file written is the mark (``command.py``).

The eight kinds (``CODES``), each finding carrying its code, ids, path and line, the role from ``ROLE_TABLE`` (a
commit's finding: its ``Role:``, and once landed the lead, ``commit_role_field``) and a one-line fix, ``text`` when
a free-text pattern found it:

- UNMARKED_CHANGE: a register entry another entry, the register's change log or ARCHIVE-SUPERSEDED §A supersedes or
  amends, whose status line does not name that changer. The statements are the loader's ``register_statements``
  (one pattern set); §A is read with the loader's own ``_BY`` pattern, as W2-92's drift script reads it.
- UNKNOWN_ID: an id or path in a typed place that names nothing that exists.
- UNLINKED_ID: an id a ticket's KPI brackets name, or a worker commit's ``Implements:`` names, missing from the
  ticket's ``sources:``.
- STATUS_CONFLICT: two records that disagree on a status.
- NOT_IN_FORCE_AS_RULE: a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision named in a rule-bearing place.
- ENFORCES_SUPERSEDED: W2-55's ``gov.decisions.propagation`` findings, as that module gives them.
- CLOSED_TICKET_EDITED and TICKET_CHANGE_UNMARKED (S16, DEC-1088 (6)): a commit that edits a closed ticket's file,
  or changes an open ticket's scope fields with no decision id (``ticket_changes``).

Incremental (``touched``, ``is_new``): the whole record set and every commit are read every run; a finding is new
when it touches what changed in ``<base>..HEAD``: a commit in the range; the record it sits in (a file with a
frontmatter id, changed whole); the line it sits on, or was stated on, in any other file (a hand list, a kernel
text, the path map: judged by line); in the register, an entry whose own text changed (the changer's new entry
among them); or, for the status-based codes, a decision whose status changed. Every other finding is standing:
counted by code and role, and listed with ``--all``.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

from gov.cli.errors import GovError
from gov.store import loader
from gov.store.loader import register_entries, register_statements

UNMARKED_CHANGE, UNKNOWN_ID, UNLINKED_ID = "UNMARKED_CHANGE", "UNKNOWN_ID", "UNLINKED_ID"
STATUS_CONFLICT, NOT_IN_FORCE_AS_RULE, ENFORCES_SUPERSEDED = "STATUS_CONFLICT", "NOT_IN_FORCE_AS_RULE", "ENFORCES_SUPERSEDED"
CLOSED_TICKET_EDITED, TICKET_CHANGE_UNMARKED = "CLOSED_TICKET_EDITED", "TICKET_CHANGE_UNMARKED"  # S16, DEC-1088 (6)
CODES = (UNMARKED_CHANGE, UNKNOWN_ID, UNLINKED_ID, STATUS_CONFLICT, NOT_IN_FORCE_AS_RULE, ENFORCES_SUPERSEDED,
         CLOSED_TICKET_EDITED, TICKET_CHANGE_UNMARKED)

ORCHESTRATOR, PRODUCT_SPEC, ENGINEER = "orchestrator", "product-spec", "engineer"
TEST_DESIGNER, AUDITOR, RESEARCH = "independent-test-designer", "independent-auditor", "research"
WORKERS = (ENGINEER, TEST_DESIGNER, PRODUCT_SPEC, RESEARCH, AUDITOR)  # a landing commit's Role is none of them

MARK_REL = ".gov-runtime/links/mark"
LISTS = "governance/project/orchestration/"  # the repository's place for the two hand lists (no path-map key)
ARCHIVE_REL = LISTS + "ARCHIVE-SUPERSEDED.md"
IN_FORCE_REL = LISTS + "DECISIONS-IN-FORCE.md"
CONTRACT_REL = "docs/contract/contract.yaml"
_CONTRACT_TEXT = re.compile(r"docs/contract/CONTRACT_v[^/]*\.md")
TICKETS = ".tickets/"
PLANS = "docs/plan/"
KERNEL_TEXTS = ("template/governance/kernel/roles/", "template/governance/kernel/skills/",
                "template/governance/kernel/templates/")
VENDORED = ("template/governance/kernel/skills/superpowers/",)
RULE_TEXTS = ("governance/project/briefs/", "governance/project/prompts/")
TESTS = "tests/"

NOT_IN_FORCE = ("PROPOSED", "REJECTED", "WITHDRAWN", "SUPERSEDED")
NOT_A_CHANGER = ("PROPOSED", "REJECTED", "WITHDRAWN")  # its Supersedes: or change changed nothing
OPEN = ("open", "in_progress")  # a ticket whose sources and KPI brackets bear a rule now
ACCEPTANCE_JUDGED = ("in_progress", "closed")  # a ticket whose acceptance_tests.path must exist
CLOSE_NOT_DONE = ("SUPERSEDED", "WITHDRAWN", "REJECTED", "REVOKED", "REFUSED")  # a close record that closed nothing
EXEMPT_TASKS = ("decision-record",)  # DEC-861
CHANGE_CLASSES = ("supersede", "amend")
RECORD_KEYS = loader.CITE_KEYS + ("constrains",)  # a record's id keys; ``task`` apart
TICKET_KEYS = ("sources", "closes", "links", "parent")  # depends_on is core-graph's (LINK-INTEGRITY §4.1)

# The store's id grammars (common.schema.json): decision, capability (and item), master rule, work-breakdown and
# list row, lesson; a ticket id by the prefixes the project's own tickets use (``_Repo.ticket``).
_ID = re.compile(r"(?<![A-Za-z0-9_])(?:(?:DEC|ADR)-[0-9]{3,}|CAP-[0-9]{2,}(?:\.[a-z](?![A-Za-z0-9]))?|MR-[0-9]+"
                 r"|W[0-9]+-[0-9]{2,}[a-z]?|W[0-9]+-[A-Z][0-9]+|L-[0-9]{4,})(?![A-Za-z0-9_])")
# A test file's ids, by the census's two patterns (D4B-link-census.py §5): a decision and a wave-1-to-3 ticket; the
# other grammars in a test file are planted stand-ins far more often than citations.
_TEST_ID = re.compile(r"\bDEC-[0-9]{3,}\b|\bW[123]-[0-9]+[a-z]?(?![A-Za-z0-9])(?!-)")
_DEC_WORD = re.compile(r"(?<![A-Za-z0-9_])DEC-[0-9]+(?![A-Za-z0-9_])")  # gov.decisions.register's decision id
_FAR = 1 << 30  # a literal that runs on past the line's end
_LONE_CR = re.compile(r"\r(?!\n)")
_LEAD = re.compile(r"\s*([A-Za-z][A-Za-z0-9]*(?:[-.][A-Za-z0-9]+)*)")  # the loader's: "DEC-954 Q9c" names DEC-954
_BRACKETS = re.compile(r"\[([^\[\]]*)\]")
_BRACKETS_OR_PARENS = re.compile(r"\[([^\[\]]*)\]|\(([^()]*)\)")
_ROW = re.compile(r"^\|\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*\|")
_CARD = re.compile(r"^#{2,6}\s+([A-Za-z0-9]+-[A-Za-z0-9._-]+)")
_ROLE = re.compile(r"^Role:[ \t]*(\S+)", re.MULTILINE | re.IGNORECASE)
_LOG = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Task,key=Implements,key=Role,unfold)%x1f%B"

# The role responsible, by path (LINK-INTEGRITY §4.1, the KPI's one fixed table); the register and the path map are
# the orchestrator's, as is any path the table does not name. A commit's finding: ``commit_role_field``.
ROLE_TABLE = (
    ((TICKETS, PLANS, "governance/project/prompts/", "governance/project/briefs/", "docs/lessons/", LISTS),
     ORCHESTRATOR),
    (("template/governance/kernel/", "docs/contract/"), PRODUCT_SPEC),
    (("src/",), ENGINEER),
    ((TESTS,), TEST_DESIGNER),
    (("docs/audit/",), AUDITOR),
    (("docs/research/",), RESEARCH),
)


def role_of(path: str) -> str:
    """The role responsible for a finding at ``path``, from ``ROLE_TABLE``; the orchestrator for any other path."""
    for prefixes, role in ROLE_TABLE:
        if path.startswith(prefixes):
            return role
    return ORCHESTRATOR


def commit_role_field(commit_role: str | None, *, landed: bool) -> tuple[str, str | None]:
    """A commit's finding's role and lead (S9): the role field names the commit's ``Role:`` trailer, the
    orchestrator for a commit with no ``Role:``; once landed, the ticket's lead (orchestrator) is the finding's
    ``lead`` (in ``--json``). The text line's role field stays the one role (the record, §4 reading 5)."""
    if not commit_role or commit_role == ORCHESTRATOR:
        return ORCHESTRATOR, None
    return commit_role, (ORCHESTRATOR if landed else None)


def _num(record_id: str) -> tuple:
    head, _, tail = record_id.rpartition("-")
    return (head, int(tail)) if tail.isdigit() else (record_id, -1)


def _line(text: str, needle: str, after: int = 0) -> int:
    """The 1-based number of the first line from line ``after + 1`` on that holds ``needle``; ``after + 1`` if none."""
    for number, line in enumerate(text.split("\n")[after:], after + 1):
        if needle in line:
            return number
    return after + 1


def _key_line(text: str, key: str) -> int:
    match = re.search(rf"^[ \t]*{re.escape(key)}[ \t]*:", text, re.MULTILINE)
    return text.count("\n", 0, match.start()) + 1 if match else 1


def _values(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [str(item) for item in value.values() if isinstance(item, (str, int))]
    return [str(item) for item in (value if isinstance(value, list) else [value]) if item is not None]


def _kpi_lines(front: dict) -> list[str]:
    kpis = front.get("kpis")
    if isinstance(kpis, dict):
        return [str(line) for lines in kpis.values() for line in (lines if isinstance(lines, list) else [lines])]
    return [str(line) for line in kpis] if isinstance(kpis, list) else []


def _yaml(text: str):
    """``text`` as YAML, by the C loader where PyYAML has it (the design's measure), else the pure one."""
    import yaml

    return yaml.load(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))


def _front(text: str):
    """The frontmatter document of ``text`` as the loader's ``_frontmatter`` reads it; None when it has none or
    cannot be read (a record that cannot be read is the store's to name, not a link)."""
    import yaml

    if not text.startswith("---"):
        return None
    lines = [line.rstrip() for line in text.split("\n")]
    if lines[0] != "---" or "---" not in lines[1:]:
        return None
    try:
        return _yaml("\n".join(lines[1:lines.index("---", 1)]))
    except (yaml.YAMLError, ValueError):
        return None


class _Repo:
    """What ``HEAD`` holds, read once."""

    def __init__(self, root: Path):
        self.root = root
        self.tree = loader._tree(root)
        register = loader._register(root, self.tree)  # STORE_REGISTER_UNREADABLE: the run cannot be made
        self.register_path, self.register_text = register if register else (None, "")
        wanted = [path for path, (mode, kind, _) in self.tree.items() if kind == "blob" and mode != "120000"
                  and (path.endswith(".md") or path == CONTRACT_REL or path == loader.PATH_MAP_REL
                       or (path.startswith(TESTS) and path.endswith(".py")))]
        self.files = _read(root, self.tree, wanted)
        self.entries = register_entries(self.register_text)[0] if register else []
        self.entry = {entry["id"]: entry for entry in self.entries}
        self.fronts: list[tuple[str, dict]] = []
        for path, text in self.files.items():
            if not path.endswith(".md"):
                continue
            front = _front(text)
            if isinstance(front, dict) and front.get("id") is not None and str(front["id"]).strip():
                self.fronts.append((path, front))
        self.tickets = [(path, front) for path, front in self.fronts if path.startswith(TICKETS)]
        prefixes = sorted({str(front["id"]).rpartition("-")[0] for _, front in self.tickets
                           if "-" in str(front["id"])})
        self.ticket = re.compile(rf"(?<![A-Za-z0-9_])(?:{'|'.join(map(re.escape, prefixes))})-[a-z0-9]{{4}}"
                                 r"(?![A-Za-z0-9_])") if prefixes else None
        self.contract = self._contract()
        self.status = {entry["id"]: entry["status"] for entry in self.entries}
        for _, front in self.fronts:
            if front.get("type") == "decision" and isinstance(front.get("status"), str):
                self.status.setdefault(str(front["id"]), front["status"])
        self.alias: dict[str, str] = {}
        for path, front in self.fronts:
            for key in loader.ALIAS_KEYS:
                if isinstance(front.get(key), str) and front[key].strip():
                    self.alias.setdefault(front[key].strip(), str(front["id"]))
        self.known = set(self.entry) | {str(front["id"]) for _, front in self.fronts} | set(self.alias)
        self.known |= self.contract_ids | self._list_rows()
        self._planted: dict[str, dict[int, list[tuple[int, int]]] | None] = {}

    def planted(self, path: str, line: int, column: int) -> bool:
        """S17: whether column ``column`` of line ``line`` of ``path`` stands inside a planted literal; False for
        any file but a ``tests/**/*.py`` file that parses. Each file is parsed once per run, when first asked."""
        if not (path.startswith(TESTS) and path.endswith(".py")):
            return False
        if path not in self._planted:
            text = self.files.get(path)
            self._planted[path] = planted_spans(text) if text is not None else None
        spans = self._planted[path]
        return spans is not None and any(start <= column < end for start, end in spans.get(line, ()))

    def _contract(self) -> dict | None:
        import yaml

        text = self.files.get(CONTRACT_REL)
        self.contract_ids: set[str] = set()
        if text is None:
            return None
        try:
            contract = _yaml(text)
        except yaml.YAMLError:
            return None
        if not isinstance(contract, dict):
            return None
        for kind in ("capabilities", "master_rules"):
            for item in contract.get(kind) or []:
                if isinstance(item, dict) and item.get("id"):
                    self.contract_ids.add(str(item["id"]))
                    for cover in item.get("covers") or []:
                        if isinstance(cover, dict) and cover.get("id"):
                            self.contract_ids.add(str(cover["id"]))
        if contract.get("id"):
            self.contract_ids.add(str(contract["id"]))
        return contract

    def _list_rows(self) -> set[str]:
        """The ids the plan's list files hold: a table row's first cell and a card's heading (not findings)."""
        rows = set()
        for path, text in self.files.items():
            if path.startswith(PLANS) and path.endswith(".md"):
                for line in text.split("\n"):
                    found = _ROW.match(line) or _CARD.match(line)
                    if found and (_ID.fullmatch(found.group(1)) or "-" in found.group(1)):
                        rows.add(found.group(1))
        return rows

    def ids_in(self, text: str) -> list[str]:
        """The ids ``text`` names, of the store's grammars, in order, each once."""
        found = [(m.start(), m.group(0)) for m in _ID.finditer(text)]
        if self.ticket is not None:
            found += [(m.start(), m.group(0)) for m in self.ticket.finditer(text)]
        return list(dict.fromkeys(record_id for _, record_id in sorted(found)))

    def lead_id(self, value: str) -> str | None:
        """The id a typed value names by its first token, None where it names none of the grammars (free text)."""
        token = _LEAD.match(value)
        if not token:
            return None
        named = token.group(1)
        return named if (_ID.fullmatch(named) or (self.ticket and self.ticket.fullmatch(named))) else None

    def resolves(self, record_id: str) -> bool:
        return record_id in self.known

    def status_line(self, entry: dict) -> int:
        """The line of the register that holds the entry's status line."""
        lines = entry["span"].split("\n")
        return entry["line"] + next((n for n, line in enumerate(lines[1:], 1) if line.strip()), 0)


def planted_spans(text: str) -> dict[int, list[tuple[int, int]]] | None:
    """S17 (DEC-1109 (2)): ``line -> [(start, end), ...]``, the character columns of each line of a Python file
    that stand inside a string literal that is not a docstring (plain, triple-quoted, bytes or f-string, assigned or
    not: a fixture's planted id); None when the file does not parse, so it is judged as before. A docstring is the
    first statement's string of a module, class or function. An f-string is one span, its ``{...}`` parts within."""
    if _LONE_CR.search(text):  # ast counts a lone CR as a line end, ``str.split("\n")`` does not: judged as before
        return None
    try:
        tree = ast.parse(text)
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (SyntaxError, ValueError, tokenize.TokenError, RecursionError, MemoryError):
        return None
    lines = text.split("\n")

    def column(row: int, offset: int) -> int:  # ast's columns are UTF-8 bytes, tokenize's characters
        return len(lines[row - 1].encode("utf-8")[:offset].decode("utf-8", errors="ignore"))

    docstrings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                string = first.value
                docstrings.append(((string.lineno, column(string.lineno, string.col_offset)),
                                   (string.end_lineno, column(string.end_lineno, string.end_col_offset))))
    spans: dict[int, list[tuple[int, int]]] = {}

    def span(start: tuple[int, int], end: tuple[int, int]) -> None:
        for row in range(start[0], end[0] + 1):
            spans.setdefault(row, []).append((start[1] if row == start[0] else 0, end[1] if row == end[0] else _FAR))

    fstring_start, fstring_end = getattr(tokenize, "FSTRING_START", None), getattr(tokenize, "FSTRING_END", None)
    depth, opened = 0, (0, 0)
    for token in tokens:
        if fstring_start is not None and token.type == fstring_start:
            if depth == 0:
                opened = token.start
            depth += 1
        elif fstring_end is not None and token.type == fstring_end and depth:
            depth -= 1
            if depth == 0:
                span(opened, token.end)
        elif token.type == tokenize.STRING and depth == 0:
            if not any(start <= token.start < end for start, end in docstrings):
                span(token.start, token.end)
    return spans


def _blobs(root: Path, ids: list[str]) -> dict[str, str]:
    """``object id -> text`` of each of ``ids`` held as UTF-8 text, in one ``git cat-file --batch``."""
    if not ids:
        return {}
    out = loader._git(root, "cat-file", "--batch", stdin="".join(f"{object_id}\n" for object_id in ids).encode())
    texts, position = {}, 0
    for object_id in ids:
        header_end = out.index(b"\n", position)
        header = out[position:header_end].split()
        if len(header) < 3:  # "<id> missing"
            position = header_end + 1
            continue
        size = int(header[2])
        blob, position = out[header_end + 1:header_end + 1 + size], header_end + size + 2
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if "\0" not in text:
            texts[object_id] = text
    return texts


def _read(root: Path, tree: dict, paths: list[str]) -> dict[str, str]:
    """``path -> text`` of each of ``paths`` that ``HEAD`` holds as UTF-8 text."""
    texts = _blobs(root, [tree[path][2] for path in paths])
    return {path: texts[tree[path][2]] for path in paths if tree[path][2] in texts}


def _finding(code, ids, path, line, fix, subject, *, text=False, role=None, lead=None, commit=None, via=()) -> dict:
    """One finding; ``via`` names the other places that stated it, ``(path, line)`` or a record's ``path`` (an
    ARCHIVE §A line, a close record, contract.yaml's status line), so a range that changes one makes it new;
    ``lead`` is a landed commit's lead (``commit_role_field``)."""
    found = {"code": code, "ids": list(ids), "path": path, "line": int(line), "role": role or role_of(path),
             "fix": " ".join(str(fix).split()).replace("|", "/"), "subject": " ".join(subject.split()).replace("|", "/"),
             "text": bool(text)}
    if lead:
        found["lead"] = lead
    if commit is not None:
        found["commit"] = commit
    if via:
        found["via"] = [list(place) if isinstance(place, tuple) else place for place in dict.fromkeys(via)]
    return found


# ---------------------------------------------------------------- UNMARKED_CHANGE (and the register's typed places)

def _statements(repo: _Repo) -> list[dict]:
    """Every register statement with the entry that states it (``origin``; None for the change log), then
    ARCHIVE-SUPERSEDED §A's, read with the loader's ``_BY`` pattern as W2-92's drift script reads it."""
    found = []
    for entry in repo.entries:
        found += [{**statement, "origin": entry["id"]} for statement in register_statements("", [entry])]
    if repo.register_path:
        found += [{**statement, "origin": None} for statement in register_statements(repo.register_text, repo.entries)
                  if statement["where"] == "preamble"]
    archive = repo.files.get(ARCHIVE_REL)
    if archive is not None:
        for number, line in _section(archive, "A"):
            if not line.startswith("- "):
                continue
            head, _, tail = line[2:].partition(":")
            for said in loader._BY.finditer(tail):
                for target in loader._DEC.findall(head):
                    for source in loader._DEC.findall(said.group(2)):
                        found.append({"source": "DEC-" + source, "target": "DEC-" + target,
                                      "cls": loader._verb_class(said.group(1)),
                                      "form": f"ARCHIVE-SUPERSEDED §A: {said.group(1)} by", "whole": False,
                                      "where": "archive", "origin": None, "line": number})
    return found


def _section(text: str, letter: str) -> list[tuple[int, str]]:
    """``(line number, line)`` of section ``letter`` of a hand list: from its ``## <letter>`` heading to the next
    level-2 heading; for §A with no such heading, everything before §B (the drift script's reading)."""
    lines, inside, out = text.split("\n"), False, []
    heading = re.compile(rf"##\s+{letter}\b")
    if letter == "A" and not any(heading.match(line) for line in lines):
        for number, line in enumerate(lines, 1):
            if re.match(r"##\s+B\b", line):
                break
            out.append((number, line))
        return out
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            inside = bool(heading.match(line))
            continue
        if inside:
            out.append((number, line))
    return out


_PART = r"\s*((?:\([^)]{1,60}\))|(?:(?:item|items|Q|§|part)\s*[\w.()]+))"


def part_of(repo: _Repo, statement: dict) -> str:
    """The part a statement names after its target id (``(item 3)``, ``Q5``), or ``""``."""
    if statement["whole"] and statement["cls"] == "supersede":
        return ""
    origin = repo.entry.get(statement.get("origin") or "")
    if origin is None:
        return ""
    found = re.search(re.escape(statement["target"]) + r"(?![0-9])" + _PART, origin["span"])
    if not found:
        return ""
    part = found.group(1).strip()
    return part if part.startswith("(") else f"({part})"


_WHERE_RANK = {"label": 0, "text": 1, "preamble": 2, "archive": 3}


def unmarked(repo: _Repo, statements: list[dict]) -> list[dict]:
    """UNMARKED_CHANGE: one per (changed entry, changer) whose status line does not name the changer. A source
    that is PROPOSED, REJECTED or WITHDRAWN is no changer, wherever its statement stands (no finding, no mark)."""
    chosen: dict[tuple[str, str], dict] = {}
    from_archive: set[tuple[str, str]] = set()
    for statement in statements:
        target, source = statement["target"], statement["source"]
        if statement["cls"] not in CHANGE_CLASSES or target not in repo.entry or source == target:
            continue
        if repo.status.get(source) in NOT_A_CHANGER:
            continue
        key = (target, source)
        if statement["where"] == "archive":
            from_archive.add((*key, statement["line"]))
        if key not in chosen or _WHERE_RANK[statement["where"]] < _WHERE_RANK[chosen[key]["where"]]:
            chosen[key] = statement
    found = []
    for (target, source), statement in sorted(chosen.items(), key=lambda item: (_num(item[0][0]), _num(item[0][1]))):
        entry = repo.entry[target]
        if re.search(rf"\b{re.escape(source)}(?![0-9])", entry["first"]):
            continue
        whole = statement["whole"] and statement["cls"] == "supersede"  # the loader's SUPERSEDES: ids alone
        mark =f"SUPERSEDED by {source}" if whole else f"**Changed by:** {source} {part_of(repo, statement)}".rstrip()
        found.append(_finding(
            UNMARKED_CHANGE, [target, source], repo.register_path, repo.status_line(entry),
            f'add "{mark}" to {target}\'s status line',
            f"{target} <- {source} ({statement['form']}; {'whole' if whole else 'part'})",
            text=statement["where"] != "label",
            via=[(ARCHIVE_REL, line) for t, s, line in from_archive if (t, s) == (target, source)])
            | {"whole": whole, "form": statement["form"], "mark": mark})
    return found


def register_places(repo: _Repo, statements: list[dict]) -> list[dict]:
    """UNKNOWN_ID in the register's labels, and NOT_IN_FORCE_AS_RULE in a register entry's ``**Under:**``."""
    found = []
    for statement in statements:
        origin = repo.entry.get(statement.get("origin") or "")
        if origin is None or statement["where"] != "label":
            continue
        other = statement["target"] if statement["source"] == origin["id"] else statement["source"]
        line = origin["line"] + _line(origin["span"], other) - 1
        if not repo.resolves(other):
            found.append(_finding(UNKNOWN_ID, [other, origin["id"]], repo.register_path, line,
                                  f"correct or remove {other} in {origin['id']}'s {statement['form']}",
                                  f"{other} in {origin['id']}'s {statement['form']}"))
        elif statement["cls"] == "under" and repo.status.get(other) in NOT_IN_FORCE:
            found.append(_finding(NOT_IN_FORCE_AS_RULE, [other, origin["id"]], repo.register_path, line,
                                  f"decide {other} or name an entry in force under {origin['id']}'s **Under:**",
                                  f"{other} ({repo.status[other]}) in {origin['id']}'s **Under:**"))
    return found


# ---------------------------------------------------------------- the records' typed places

def records(repo: _Repo) -> list[dict]:
    """UNKNOWN_ID, UNLINKED_ID and NOT_IN_FORCE_AS_RULE in the tickets' and the other records' frontmatter."""
    found = []

    def unknown(record_id, path, line, place, owner):
        found.append(_finding(UNKNOWN_ID, [record_id, owner], path, line, f"correct or remove {record_id} in {place}",
                              f"{record_id} in {place}"))

    def ruled(record_id, path, line, place, owner):
        status = repo.status.get(record_id)
        if status in NOT_IN_FORCE:
            found.append(_finding(NOT_IN_FORCE_AS_RULE, [record_id, owner], path, line,
                                  f"decide {record_id} or cite it in the body as {status.lower()}",
                                  f"{record_id} ({status}) in {place}"))

    for path, front in repo.fronts:
        text, owner = repo.files[path], str(front["id"])
        is_ticket = path.startswith(TICKETS)
        status = str(front.get("status", ""))
        for key in (TICKET_KEYS if is_ticket else RECORD_KEYS):
            for value in _values(front.get(key)):
                named = repo.lead_id(value)
                if named is None:
                    continue
                line = _line(text, value, _key_line(text, key) - 1)
                if not repo.resolves(named):
                    unknown(named, path, line, f"{owner}'s {key}", owner)
                elif is_ticket and key == "sources" and status in OPEN:
                    ruled(named, path, line, f"{owner}'s sources", owner)
        for key in loader.TASK_KEYS:
            if not is_ticket and front.get(key) is not None:
                value = str(front[key]).strip()
                if value and value not in EXEMPT_TASKS and not repo.resolves(value):
                    unknown(value, path, _key_line(text, key), f"{owner}'s {key}", owner)
        if not is_ticket:
            continue
        cited = {named for value in _values(front.get("sources")) if (named := repo.lead_id(value))}
        own = {owner} | {str(front[key]).strip() for key in loader.ALIAS_KEYS if isinstance(front.get(key), str)}
        kpis = _key_line(text, "kpis") - 1
        for kpi in _kpi_lines(front):
            for bracket in _BRACKETS.findall(kpi):
                for named in repo.ids_in(bracket):
                    line = _line(text, named, kpis)
                    if not repo.resolves(named):
                        unknown(named, path, line, f"{owner}'s KPI brackets", owner)
                        continue
                    if status in OPEN:
                        ruled(named, path, line, f"{owner}'s KPI brackets", owner)
                    if named not in cited and named not in own:
                        cited.add(named)  # one finding per id and ticket
                        found.append(_finding(UNLINKED_ID, [named, owner], path, _key_line(text, "sources"),
                                              f"add {named} to {owner}'s sources:",
                                              f"{named} in {owner}'s KPI brackets, not in its sources"))
        tests = front.get("acceptance_tests")
        if status in ACCEPTANCE_JUDGED and isinstance(tests, dict) and isinstance(tests.get("path"), str):
            wanted = tests["path"].strip().rstrip("/")
            if wanted and wanted not in repo.tree and not any(p.startswith(wanted + "/") for p in repo.tree):
                found.append(_finding(UNKNOWN_ID, [wanted, owner], path, _line(text, tests["path"], kpis),
                                      f"write the tests at {wanted} or correct {owner}'s acceptance_tests.path",
                                      f"{wanted} in {owner}'s acceptance_tests.path"))
    return found


def contract(repo: _Repo) -> list[dict]:
    """UNKNOWN_ID in ``contract.yaml``'s providers and sources, and NOT_IN_FORCE_AS_RULE in ``CONTRACT_v*.md``."""
    found = []
    if repo.contract is not None:
        text = repo.files[CONTRACT_REL]
        items = []
        for kind in ("capabilities", "master_rules"):
            for item in repo.contract.get(kind) or []:
                if isinstance(item, dict):
                    items.append(item)
                    items += [cover for cover in item.get("covers") or [] if isinstance(cover, dict)]
        for item in items:
            owner = str(item.get("id", "?"))
            after = _line(text, f"id: {owner}") - 1
            for key in ("provider", "sources", "source"):
                for value in _values(item.get(key)):
                    for part in re.split(r"[;,]", value) if key == "source" else [value]:
                        named = repo.lead_id(part)
                        if named and not repo.resolves(named):
                            found.append(_finding(UNKNOWN_ID, [named, owner], CONTRACT_REL, _line(text, part, after),
                                                  f"correct or remove {named} in {owner}'s {key}",
                                                  f"{named} in {owner}'s {key}"))
    for path, text in repo.files.items():
        if _CONTRACT_TEXT.fullmatch(path):
            found += _rule_lines(repo, path, text, "the Contract's text")
    return found


def _rule_lines(repo: _Repo, path: str, text: str, place: str, comments_only: bool = False) -> list[dict]:
    """NOT_IN_FORCE_AS_RULE for each line of a rule-bearing text that names a decision not in force."""
    found = []
    for number, line in enumerate(text.split("\n"), 1):
        if comments_only:
            line = line.partition("#")[2] if "#" in line else ""
        for named in loader._DEC.findall(line):
            record_id = "DEC-" + named
            status = repo.status.get(record_id)
            if status in NOT_IN_FORCE:
                found.append(_finding(NOT_IN_FORCE_AS_RULE, [record_id], path, number,
                                      f"decide {record_id} or name it as {status.lower()}, not as a rule",
                                      f"{record_id} ({status}) in {place}"))
    return found


def texts(repo: _Repo) -> list[dict]:
    """The kernel's role, skill and template lines (UNKNOWN_ID for bracketed ids, NOT_IN_FORCE_AS_RULE), the
    project's briefs and prompts and the path map's comments (NOT_IN_FORCE_AS_RULE), and the test files' ids
    (UNKNOWN_ID)."""
    found = []
    for path, text in repo.files.items():
        if path.startswith(KERNEL_TEXTS) and not path.startswith(VENDORED):
            for number, line in enumerate(text.split("\n"), 1):
                for groups in _BRACKETS_OR_PARENS.findall(line):
                    for named in repo.ids_in(groups[0] or groups[1]):
                        if not repo.resolves(named):
                            found.append(_finding(UNKNOWN_ID, [named], path, number, f"correct or remove {named}",
                                                  f"{named} in a kernel line"))
            found += _rule_lines(repo, path, text, "a kernel line")
        elif path.startswith(RULE_TEXTS):
            found += _rule_lines(repo, path, text, "a brief or prompt line")
        elif path == loader.PATH_MAP_REL:
            found += _rule_lines(repo, path, text, "a path-map comment", comments_only=True)
        elif path.startswith(TESTS) and path.endswith(".py"):
            for number, line in enumerate(text.split("\n"), 1):
                for match in _TEST_ID.finditer(line):
                    if not repo.resolves(match.group(0)) and not repo.planted(path, number, match.start()):  # S17
                        found.append(_finding(UNKNOWN_ID, [match.group(0)], path, number,
                                              f"correct {match.group(0)} or name the planted id as a stand-in",
                                              f"{match.group(0)} in a test file"))
    return found


# ---------------------------------------------------------------- STATUS_CONFLICT

def statuses(repo: _Repo) -> list[dict]:
    """The register against ARCHIVE-SUPERSEDED §B and DECISIONS-IN-FORCE; a ticket against its close record; a
    generated master-rule record against ``contract.yaml``."""
    from gov.decisions.register import read

    found = []
    register = read(repo.root) if repo.register_path else None
    superseded = set(register["superseded"]) if register else set()
    done = set(register["done"]) if register else set()

    def current(record_id):  # a PROPOSED decision is never current (DEC-1073 (2))
        status = repo.status.get(record_id)
        return status is not None and status not in NOT_IN_FORCE + ("DONE",) and record_id not in superseded \
            and record_id not in done

    archive = repo.files.get(ARCHIVE_REL)
    if archive is not None and repo.register_path:
        for number, line in _section(archive, "B"):
            if line.startswith("- ") and re.search(r"\b[Ss]pent\b", line):
                for named in loader._DEC.findall(line[2:].split(":")[0]):
                    record_id = "DEC-" + named
                    if current(record_id):
                        found.append(_finding(STATUS_CONFLICT, [record_id], ARCHIVE_REL, number,
                                              f"reconcile {record_id}: mark it done or superseded in the register, "
                                              "or take it off the spent list",
                                              f"{record_id} {repo.status[record_id]} in the register, spent in "
                                              "ARCHIVE-SUPERSEDED §B"))
    in_force = repo.files.get(IN_FORCE_REL)
    if in_force is not None and repo.register_path:
        lifted = False
        for number, line in enumerate(in_force.split("\n"), 1):
            if line.startswith("## "):
                lifted = "lifted" in line.lower()
                continue
            if lifted or not line.startswith("- "):
                continue
            for named in loader._DEC.findall(line[2:].split(":")[0]):
                record_id = "DEC-" + named
                status = repo.status.get(record_id)
                if status is None:
                    continue
                said = "superseded" if (status == "SUPERSEDED" or record_id in superseded) else \
                    "done" if (status == "DONE" or record_id in done) else None
                if said:
                    found.append(_finding(STATUS_CONFLICT, [record_id], IN_FORCE_REL, number,
                                          f"take {record_id} off the in-force list, or correct its register status",
                                          f"{record_id} {said} in the register, listed in DECISIONS-IN-FORCE"))
    tickets = {str(front["id"]): (path, front) for path, front in repo.tickets}
    for path, front in repo.fronts:
        if front.get("type") != "close" or not isinstance(front.get("task"), str):
            continue
        task = front["task"].strip()
        if task not in tickets:
            continue
        ticket_path, ticket = tickets[task]
        closed = str(front.get("status", "")).upper() not in CLOSE_NOT_DONE
        if closed != (ticket.get("status") == "closed"):
            found.append(_finding(STATUS_CONFLICT, [task, str(front["id"])], ticket_path,
                                  _key_line(repo.files[ticket_path], "status"),
                                  f"make {task}'s status and its close record {front['id']} agree",
                                  f"{task} {ticket.get('status')} against its close record {front['id']} "
                                  f"{front.get('status')}", via=[path]))
    if repo.contract is not None and isinstance(repo.contract.get("status"), str):
        rules = {str(rule["id"]) for rule in repo.contract.get("master_rules") or []
                 if isinstance(rule, dict) and rule.get("id")}
        for path, front in repo.fronts:
            if str(front["id"]) in rules and path != CONTRACT_REL and front.get("status") != repo.contract["status"]:
                found.append(_finding(STATUS_CONFLICT, [str(front["id"])], path, _key_line(repo.files[path], "status"),
                                      f"regenerate {front['id']} with contract.yaml's status "
                                      f"{repo.contract['status']}",
                                      f"{front['id']} {front.get('status')} against contract.yaml "
                                      f"{repo.contract['status']}",
                                      via=[(CONTRACT_REL, _key_line(repo.files[CONTRACT_REL], "status"))]))
    return found


# ---------------------------------------------------------------- the commits

def commits(repo: _Repo, judged: set[str] | None) -> tuple[list[dict], int]:
    """UNKNOWN_ID in ``Task:`` and ``Implements:``, UNLINKED_ID for a worker commit's ``Implements:`` id missing
    from its ticket's ``sources:``, and NOT_IN_FORCE_AS_RULE in ``Implements:``. Every commit is judged, so no
    finding older than the mark is lost; one about a commit outside the range (``judged``; None: every commit is in
    it) is standing. Returns the findings and the number of commits in the range."""
    log = loader._git(repo.root, "-c", "core.quotePath=false", "log", _LOG, "HEAD").decode("utf-8", "replace")
    first_parent = set(loader._git(repo.root, "rev-list", "--first-parent", "HEAD").decode().split())
    tickets = {}
    for path, front in repo.tickets:
        tickets[str(front["id"])] = (path, front)
    found, in_range = [], 0
    for entry in log.split("\x1e")[1:]:
        sha, date, block, message = entry.split("\x1f", 3)
        message = message.rstrip("\n")
        read_from = message if date < loader.TRAILER_RULE_DATE else block
        role_match = _ROLE.search(read_from)
        commit_role = role_match.group(1) if role_match else None
        role, lead = commit_role_field(commit_role, landed=sha not in first_parent)
        new = judged is None or sha in judged
        in_range += new
        lines = message.split("\n")

        def at(key, value):
            for number in range(len(lines), 0, -1):  # the trailer block is the message's end
                if re.match(rf"{key}:", lines[number - 1], re.IGNORECASE) and value in lines[number - 1]:
                    return number
            return 1

        tasks, implements = [], []
        for key, value in loader._TRAILER.findall(read_from):
            items = [item for item in re.split(r"[,\s]+", value) if item]
            (tasks if key.lower() == "task" else implements).extend(items[:1] if key.lower() == "task" else items)
        for task in tasks:
            if task not in EXEMPT_TASKS and not repo.resolves(task):
                found.append(_finding(UNKNOWN_ID, [task], sha, at("Task", task),
                                      f"name the ticket {task} should have named (history is not rewritten)",
                                      f"{task} in {sha[:12]}'s Task:", role=role, lead=lead, commit=sha))
        ticket = None
        for task in tasks:
            named = repo.alias.get(task, task)
            if named in tickets:
                ticket = tickets[named]
        cited = set()
        if ticket is not None:
            cited = {named for value in _values(ticket[1].get("sources")) if (named := repo.lead_id(value))}
            cited |= {str(ticket[1]["id"])} | {str(ticket[1][k]).strip() for k in loader.ALIAS_KEYS
                                                 if isinstance(ticket[1].get(k), str)}
        for value in dict.fromkeys(implements):
            named = repo.lead_id(value)
            if named is None:
                continue
            if not repo.resolves(named):
                found.append(_finding(UNKNOWN_ID, [named], sha, at("Implements", named),
                                      f"name the id {named} should have named (history is not rewritten)",
                                      f"{named} in {sha[:12]}'s Implements:", role=role, lead=lead, commit=sha))
                continue
            status = repo.status.get(named)
            if status in NOT_IN_FORCE:
                found.append(_finding(NOT_IN_FORCE_AS_RULE, [named], sha, at("Implements", named),
                                      f"decide {named} or implement a decision in force",
                                      f"{named} ({status}) in {sha[:12]}'s Implements:", role=role, lead=lead,
                                      commit=sha))
            if ticket is not None and commit_role in WORKERS and named not in cited:
                cited.add(named)
                path, front = ticket
                found.append(_finding(UNLINKED_ID, [named, str(front["id"]), sha], path,
                                      _key_line(repo.files[path], "sources"), f"add {named} to {front['id']}'s sources:",
                                      f"{named} in {sha[:12]}'s Implements: ({commit_role}), not in {front['id']}'s "
                                      "sources", commit=sha))
    return found, in_range


# ---------------------------------------------------------------- S16: ticket changes (DEC-1088 (6))

WATCHED = ("title", "kpis", "allowed_paths", "reads", "needs", "waits_on", "depends_on", "acceptance_tests")
_TICKET_LOG = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Implements,key=Decided-by,unfold)%x1f%B%x1f"
_MARKING = re.compile(r"^(?:Implements|Decided-by):[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_DEC_ANY = re.compile(r"(?<![A-Za-z0-9_])DEC-[0-9]+(?![0-9])")
_NO_BLOB = "0" * 40


def _first_change(before: str, after: str) -> int:
    """The 1-based line of ``after`` where it first differs from ``before``."""
    old, new = before.split("\n"), after.split("\n")
    for number, (a, b) in enumerate(zip(old, new), 1):
        if a != b:
            return number
    return min(len(old), len(new)) + 1 if len(old) != len(new) else 1


def ticket_changes(repo: _Repo) -> list[dict]:
    """CLOSED_TICKET_EDITED and TICKET_CHANGE_UNMARKED for every commit that changed a ticket's file. Each is the
    commit's finding (``commit``), so it is new only when its commit is in the range, and standing otherwise.

    - Closed means the ticket's status in the commit's parent; a decision id does not excuse the edit.
    - An open or in-progress ticket's ``WATCHED`` field changed, with no ``DEC-n`` in the changed lines (added or
      removed) nor in the commit's ``Implements:`` or ``Decided-by:``, is one finding per field.
    - A change of any other field (``status``, ``assignee``, ``links``, …) is none; nor is a merge (its changes are its parents' commits'), nor the commit that adds the ticket.
    - The commit that closes the ticket is judged as any other: the status change gives nothing, an unmarked change
      of a ``WATCHED`` field in the same commit is a finding."""
    from collections import Counter

    log = loader._git(repo.root, "-c", "core.quotePath=false", "log", "--full-history", "--raw", "--no-abbrev",
                      "--no-renames", _TICKET_LOG, "HEAD", "--", TICKETS).decode("utf-8", "replace")
    changes, wanted = [], {}
    for chunk in log.split("\x1e")[1:]:
        sha, date, block, message, raw = chunk.split("\x1f", 4)
        said = message if date < loader.TRAILER_RULE_DATE else block
        marked = any(_DEC_ANY.search(value) for value in _MARKING.findall(said))
        for line in raw.split("\n"):
            meta, tab, path = line.partition("\t")
            parts = meta.split()
            if not tab or not line.startswith(":") or len(parts) < 5:
                continue
            old, new = parts[2], parts[3]
            if not path.startswith(TICKETS) or not path.endswith(".md") or old == _NO_BLOB:
                continue
            changes.append((sha, marked, path, old, new))
            wanted[old] = wanted[new] = None
    wanted.pop(_NO_BLOB, None)
    texts = _blobs(repo.root, list(wanted))
    fronts: dict[str, object] = {}

    def front(object_id):
        if object_id not in fronts:
            fronts[object_id] = _front(texts[object_id]) if object_id in texts else None
        return fronts[object_id]

    found = []
    for sha, marked, path, old, new in changes:
        was = front(old)
        if not isinstance(was, dict):
            continue
        deleted = new == _NO_BLOB
        after = "" if deleted else texts.get(new)
        now = {} if deleted else front(new)
        if after is None or not isinstance(now, dict):
            continue
        ticket, short = str(was.get("id") or now.get("id") or path), sha[:12]
        status = str(was.get("status", "")).strip()
        if status == "closed":
            keys = list(dict.fromkeys([*now, *was]))
            fields = "the file (deleted)" if deleted else \
                ", ".join(key for key in keys if was.get(key) != now.get(key)) or "body"
            found.append(_finding(
                CLOSED_TICKET_EDITED, [ticket, short], path, 1 if deleted else _first_change(texts[old], after),
                f"revert {short}'s edit of {ticket} or carry the change in a new ticket; a closed ticket is not edited",
                f"{ticket} {short} {fields}: closed before the commit", role=ORCHESTRATOR, commit=sha)
                | {"field": fields})
            continue
        if deleted or status not in OPEN:
            continue
        # the closing commit is judged as any other: its status change is no finding, its watched fields are
        fields = [key for key in WATCHED if was.get(key) != now.get(key)]
        if not fields or marked:
            continue
        before_lines, after_lines = Counter(texts[old].split("\n")), Counter(after.split("\n"))
        if any(_DEC_ANY.search(line) for line in (before_lines - after_lines) + (after_lines - before_lines)):
            continue
        at_head = repo.files.get(path, after)
        for field in fields:
            found.append(_finding(
                TICKET_CHANGE_UNMARKED, [ticket, short], path, _key_line(at_head, field),
                f"name the decision behind {short}'s change of {ticket}'s {field} (a DEC-n in a commit's "
                "Implements: or Decided-by:), or revert it",
                f"{ticket} {short} {field}: changed with no DEC-n in the lines, Implements: or Decided-by:",
                role=ORCHESTRATOR, commit=sha) | {"field": field})
    return found


# ---------------------------------------------------------------- ENFORCES_SUPERSEDED

def _planted_cite(repo: _Repo, finding: dict, path: str, number: int, said: str) -> bool:
    """S17 (DEC-1109 (2)): a finding that only cites its old id on a line of a ``tests/**/*.py`` file that parses,
    where the old id stands only inside planted literals (a fixture's register or record). A value it holds
    (``holds '...'``) is no id and is carried as before."""
    old = finding["ids"][0] if finding["ids"] else ""
    if said.split(": it still ", 1)[0] != f"cites {old}":
        return False
    line = (repo.files.get(path) or "").split("\n")[number - 1:number]
    places = [match.start() for match in _DEC_WORD.finditer(line[0] if line else "") if match.group(0) == old]
    return bool(places) and all(repo.planted(path, number, place) for place in places)


def enforces(repo: _Repo) -> list[dict]:
    """W2-55's ``check_propagation`` findings, as that module gives them, each at its path and line; a test file's
    finding is carried only where the old id stands outside a planted literal (S17, ``_planted_cite``)."""
    from gov.decisions.propagation import check_propagation

    if not repo.register_path:
        return []
    found = []
    for finding in check_propagation(repo.root):
        path = finding["paths"][0] if finding["paths"] else ""
        at = re.match(rf"{re.escape(path)}:(\d+) ", finding["message"])
        number = int(at.group(1)) if at else 1
        said = finding["message"].split(" ", 1)[-1] if at else finding["message"]
        if at and _planted_cite(repo, finding, path, number, said):
            continue
        found.append(_finding(ENFORCES_SUPERSEDED, finding["ids"], path, number,
                              "cite the decision in force, or record a **Kept:** reason in the register", said))
    return found


# ---------------------------------------------------------------- the run

def not_applicable(repo: _Repo) -> list[str]:
    """The kinds of record this repository does not have: reported, never an error."""
    gone = []
    if loader.PATH_MAP_REL not in repo.tree:
        gone.append("path map")
    if not repo.register_path:
        gone.append("register")
    for rel, name in ((ARCHIVE_REL, "ARCHIVE-SUPERSEDED"), (IN_FORCE_REL, "DECISIONS-IN-FORCE"),
                      (CONTRACT_REL, "contract.yaml")):
        if rel not in repo.files:
            gone.append(name)
    if not repo.tickets:
        gone.append(".tickets")
    return gone


def findings(repo: _Repo, judged: set[str] | None) -> tuple[list[dict], int]:
    """Every finding of ``HEAD``, in a fixed order, and the number of commits in the range (``judged``)."""
    said = _statements(repo)
    found = unmarked(repo, said) + register_places(repo, said) + records(repo) + contract(repo) + texts(repo)
    found += statuses(repo)
    from_commits, in_range = commits(repo, judged)
    found += from_commits + enforces(repo) + ticket_changes(repo)
    unique = {}
    for finding in found:
        key = (finding["code"], tuple(finding["ids"]), finding["path"], finding["line"], finding.get("field"))
        unique.setdefault(key, finding)
    ordered = sorted(unique.values(), key=lambda f: (CODES.index(f["code"]), f["path"], f["line"], f["ids"]))
    return ordered, in_range


STATUS_CODES = (STATUS_CONFLICT, NOT_IN_FORCE_AS_RULE, ENFORCES_SUPERSEDED)  # judged on a decision's status


_HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", re.MULTILINE)


def _changed_lines(root: Path, base: str, paths: list[str]) -> dict[str, set[int]]:
    """``path -> the lines of HEAD's text the range added or changed``, for ``paths``."""
    if not paths:
        return {}
    diff = loader._git(root, "-c", "core.quotePath=false", "diff", "-U0", "--no-renames", "--no-color", base, "HEAD",
                       "--", *paths).decode("utf-8", "replace")
    lines: dict[str, set[int]] = {}
    for part in diff.split("\ndiff --git ")[0:]:
        target = re.search(r"^\+\+\+ b/(.*)$", part, re.MULTILINE)
        if not target:
            continue
        found = lines.setdefault(target.group(1), set())
        for start, count in _HUNK.findall(part):
            found.update(range(int(start), int(start) + (int(count) if count else 1)))
    return lines


def touched(repo: _Repo, base: str | None) -> dict | None:
    """What ``<base>..HEAD`` changed (None: everything is new): the commits in it, the record files it changed
    (a file with a frontmatter id: the record changed whole), the lines it changed in every other file (a hand
    list, a kernel text, a brief, the path map, a test file: judged by line), the register entries whose text it
    changed, and the entries whose status it changed (a new entry among them)."""
    if base is None:
        return None
    root = repo.root
    judged = set(loader._git(root, "rev-list", f"{base}..HEAD").decode().split())
    names = loader._git(root, "-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", "-z", base, "HEAD")
    changed = {name for name in names.decode("utf-8", "replace").split("\0") if name}
    records = {path for path, _ in repo.fronts} & changed
    lines = _changed_lines(root, base, sorted(changed - records - {repo.register_path} - {""}))
    entries, statuses = set(), set()
    if repo.register_path and repo.register_path in changed:
        try:
            before = loader._git(root, "cat-file", "blob", f"{base}:{repo.register_path}").decode("utf-8", "replace")
        except GovError:
            before = ""
        old = {entry["id"]: entry for entry in register_entries(before)[0]}
        for entry in repo.entries:
            was = old.get(entry["id"])
            if was is None or was["content_hash"] != entry["content_hash"]:
                entries.add(entry["id"])
            if was is None or was["status"] != entry["status"]:
                statuses.add(entry["id"])
    return {"commits": judged, "records": records, "lines": lines, "entries": entries, "statuses": statuses}


def is_new(finding: dict, repo: _Repo, range_: dict | None) -> bool:
    """Whether a finding touches what the range changed: a commit in it; the record it sits in, or the line of
    another file it sits on or was stated on; for a finding in the register, an entry whose text changed (the
    register is judged by entry, not as a file); or, for a finding judged on a decision's status, a decision whose
    status changed."""
    if range_ is None:
        return True
    if "commit" in finding:
        return finding["commit"] in range_["commits"]

    def at(place) -> bool:
        if isinstance(place, (list, tuple)):
            return place[1] in range_["lines"].get(place[0], ())
        return place in range_["records"]

    if any(at(place) for place in finding.get("via", ())):
        return True
    if finding["path"] == repo.register_path:
        return bool(set(finding["ids"]) & range_["entries"])
    if finding["path"] in range_["records"] or at((finding["path"], finding["line"])):
        return True
    return finding["code"] in STATUS_CODES and finding["ids"][0] in range_["statuses"]


def render(finding: dict) -> str:
    """One finding as one line: ``code subject | path:line | role | fix``, ``(text)`` for a free-text pattern."""
    subject = f"{finding['code']} {finding['subject']}" + (" (text)" if finding["text"] else "")
    return f"{subject} | {finding['path']}:{finding['line']} | {finding['role']} | {finding['fix']}"
