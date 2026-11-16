"""Stage AS of ``gov adopt --lite``: the spec audit (W2-192; DEC-1200 (4), P-ADOPT-SPEC-AUDIT-1 section 2).

AS follows A2 and precedes A3. It reads A1's inventory (path and blob of each tracked file), A2's classes (path and
namespace), the files' bytes by their inventory blob ids and git history, and records ``governance/adoption/
AS-spec-audit.md``. It reads nothing outside the repository, uses no network and no model, changes no file outside
``governance/adoption/``, and never refuses for what it finds: a project with no spec, no module or no ticket gets a
record with empty lists. A gap's ``answer`` is written null here and by nothing in AS or A3: the owner's route to
record an answer is not built by this stage.

The rule, as the finders apply it (every name is a path of the A1 inventory, never of HEAD's working tree):

* **A spec** is a Markdown file (``.md`` or ``.markdown``) whose front matter says ``type: spec``, or that lies under a
  folder named ``specs``, or that A2 classed in a path-map namespace named ``specs``. Its ``title`` is the front
  matter's ``title``, else its first ``# `` heading (null when it has neither); ``wave`` and ``status`` are the front
  matter's, as stated (null where absent).
* **A top-level code module** is a ``.py`` file directly under ``src/`` other than ``__init__.py``, and a package folder
  directly under ``src/`` (named as its folder path, ``src/<name>``) that holds a ``.py`` file at any depth. Nothing
  under ``tests/`` is a module.
* **A ticket** is ``.tickets/<id>.md`` with front matter: ``id`` (else the file's name), ``status`` (``closed`` is
  done; anything else is not), and its wave from ``wave: <n>`` or else a tag ``wave-<n>`` (null for neither).
* **A spec names its code** by repository-relative paths in backticks in its text: a token that starts with ``src/`` or
  ends in a code extension and is not a test file (a path under a ``tests`` folder, or a ``test_*`` file). A named
  path is *present* when it is a file of the inventory, or a folder holding one.
* **Built** is every named code path present and a test file naming one of them (the path as a whole path in its
  text, or importing the module it is); **partly built** is some but not all named paths present, or all present and
  no test naming any; **not built** is none present (a spec that names no code path is not built). Evidence: ``code``
  is the present named paths, ``tests`` the inventory's test files that name them, ``commits`` the full hashes of
  the commits of HEAD's history that touched the present paths (``git log --format=%H -- <paths>``).
* **A gap** is each partly built spec, each not built spec and each module no spec names (a spec names a module
  when one of its named code paths is the module or lies under it). Each is one question to the owner, with
  ``answer: null`` as the place for the answer. A built spec and a named module are no gap.

The lite checks (``gate``, applied first by A3, and ``check`` by AS before it commits): the record names every spec and
every top-level code module the inventory holds, and every gap carries a non-empty question.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from gov.adopt import project
from gov.adopt.project import refuse
from gov.cli.errors import GovError

SPEC_SUFFIXES = (".md", ".markdown")
CODE_SUFFIXES = (".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".rb", ".sh", ".c", ".h", ".cc",
                 ".cpp", ".cs", ".php", ".swift", ".scala")
BUILT, PARTLY, NOT_BUILT = "built", "partly built", "not built"
TICKETS = ".tickets"
_TICKS = re.compile(r"`([^`\s]+)`")
_PATH = re.compile(r"^[\w.\-]+(?:/[\w.\-]+)*$")
_HEADING = re.compile(r"^# +(.+?)\s*#*\s*$")
_WAVE_TAG = re.compile(r"^wave-(\w+)$")


# --------------------------------------------------------------------------
# What the inventory holds
# --------------------------------------------------------------------------

def inventory_of(records: dict) -> dict[str, str]:
    """Path -> blob id from A1's record; ``RECORD_UNREADABLE`` when it is not a list of those."""
    listed = (records.get("A1") or {}).get("artefacts")
    if not isinstance(listed, list) or not all(isinstance(item, dict) and isinstance(item.get("path"), str)
                                              and isinstance(item.get("blob"), str) for item in listed):
        raise refuse("RECORD_UNREADABLE", f"{project.record_path('A1')} has no list 'artefacts' of path and blob: the "
                                          "spec audit reads the inventory", record=project.record_path("A1"))
    return {item["path"]: item["blob"] for item in listed}


def classes_of(records: dict) -> dict[str, str | None]:
    """Path -> namespace from A2's record (empty for what it does not list)."""
    listed = (records.get("A2") or {}).get("artefacts")
    return {item["path"]: item.get("namespace") for item in listed or []
            if isinstance(item, dict) and isinstance(item.get("path"), str)}


class Reader:
    """The text of the inventory's files, by blob id, each read once. None for what is no text (a NUL byte, or an
    entry that is no blob of this repository)."""

    def __init__(self, root, inventory: dict[str, str]):
        self.root, self.inventory, self._seen = root, inventory, {}

    def text(self, rel: str) -> str | None:
        blob_id = self.inventory[rel]
        if blob_id not in self._seen:
            try:
                data = project.blob(self.root, blob_id)
            except GovError:
                data = b"\0"
            self._seen[blob_id] = None if b"\0" in data else data.decode("utf-8", "replace")
        return self._seen[blob_id]


def _head(text: str | None) -> dict | None:
    try:
        return project.frontmatter(text) if text is not None else None
    except ValueError:
        return None


def _plain(value):
    return value if value is None or isinstance(value, (str, int, float, bool)) else str(value)


def _body(text: str) -> list[str]:
    """The lines after the front matter, when the text has one that closes."""
    lines = text.split("\n")
    if lines and lines[0].rstrip() == "---":
        for number in range(1, len(lines)):
            if lines[number].rstrip() == "---":
                return lines[number + 1:]
    return lines


# --------------------------------------------------------------------------
# The finders
# --------------------------------------------------------------------------

def find_specs(reader: Reader, classes: dict) -> list[dict]:
    """The specs of the inventory: ``{"path", "head", "text"}`` each, sorted by path."""
    found = []
    for rel in sorted(reader.inventory):
        if not rel.lower().endswith(SPEC_SUFFIXES):
            continue
        text = reader.text(rel)
        head = _head(text)
        if (head or {}).get("type") == "spec" or "specs" in PurePosixPath(rel).parts[:-1] or classes.get(rel) == "specs":
            found.append({"path": rel, "head": head or {}, "text": text or ""})
    return found


def find_modules(paths) -> list[str]:
    """The top-level code modules among ``paths``: see the module's docstring."""
    modules = set()
    for rel in paths:
        parts = rel.split("/")
        if parts[0] != "src" or len(parts) < 2 or parts[1] in ("tests", "__pycache__") or not rel.endswith(".py"):
            continue
        if len(parts) == 2:
            if parts[1] != "__init__.py":
                modules.add(rel)
        else:
            modules.add("src/" + parts[1])
    return sorted(modules)


def find_tickets(reader: Reader) -> list[dict]:
    found = []
    for rel in sorted(reader.inventory):
        parts = rel.split("/")
        if len(parts) != 2 or parts[0] != TICKETS or not parts[1].endswith(".md"):
            continue
        head = _head(reader.text(rel))
        if head is None:
            continue
        wave = _plain(head.get("wave"))
        if wave is None:
            for tag in head.get("tags") if isinstance(head.get("tags"), list) else []:
                tagged = _WAVE_TAG.match(tag) if isinstance(tag, str) else None
                if tagged:
                    wave = int(tagged[1]) if tagged[1].isdigit() else tagged[1]
                    break
        status = head.get("status")
        found.append({"id": str(head["id"]) if head.get("id") is not None else parts[1][:-3], "wave": wave,
                      "done": isinstance(status, str) and status.strip().casefold() == "closed"})
    return sorted(found, key=lambda item: item["id"])


def _is_test(rel: str) -> bool:
    parts = rel.split("/")
    return "tests" in parts[:-1] or (parts[-1].startswith("test_") and parts[-1].endswith(".py"))


def named_code(text: str) -> list[str]:
    """The code paths ``text`` names in backticks, in order, once each."""
    named = []
    for token in _TICKS.findall(text):
        token = re.sub(r":\d+(?:-\d+)?$", "", token.split("::")[0]).removeprefix("./").rstrip("/")
        if _PATH.match(token) and ".." not in token.split("/") and not _is_test(token) \
                and (token.startswith("src/") or token.endswith(CODE_SUFFIXES)) and token not in named:
            named.append(token)
    return named


def _present(rel: str, paths) -> bool:
    return rel in paths or any(path.startswith(rel + "/") for path in paths)


def _names(text: str, rel: str) -> bool:
    """Whether the test ``text`` names ``rel`` as a whole path, or imports the module it is."""
    if re.search(r"(?<![\w\-./])" + re.escape(rel) + r"(?![\w\-/]|\.[\w\-])", text):
        return True
    dotted = rel[:-3] if rel.endswith(".py") else rel
    dotted = dotted.removesuffix("/__init__").replace("/", ".")
    for name in {dotted, dotted.removeprefix("src.")}:
        if not name or name == "src":
            continue
        parent, _, last = name.rpartition(".")
        if re.search(r"(?m)^\s*(?:from|import)\s+" + re.escape(name) + r"(?![\w])", text):
            return True
        if parent and re.search(r"(?m)^\s*from\s+" + re.escape(parent) + r"\s+import\s+[^\n]*\b" + re.escape(last)
                                + r"\b", text):
            return True
    return False


def _question(kind: str, subject: str, evidence: dict | None = None) -> str:
    if kind == "module":
        return (f"The code module {subject} is named by no spec. Which spec establishes it, and when; or is the code "
                "retired?")
    missing = [path for path in evidence["named"] if path not in evidence["code"]]
    if kind == PARTLY:
        return (f"The spec {subject} is only partly built: {', '.join(missing) or 'a test for it'} "
                f"{'is' if len(missing) == 1 else 'are'} "
                f"{'not in the repository' if missing else 'missing'}. How and when is it established, or is it retired?")
    return f"The spec {subject} has no code in the repository. How and when is it established, or is it withdrawn?"


def audit(root, reader: Reader, classes: dict, specs: list[dict], modules: list[str]) -> dict:
    """The AS record's front matter keys (the schema of the module's docstring)."""
    paths = set(reader.inventory)
    tests = [(rel, reader.text(rel)) for rel in sorted(paths) if _is_test(rel)]
    tests = [(rel, text) for rel, text in tests if text is not None]
    rows, gaps, named_by_any = [], [], set()
    for spec in specs:
        named = named_code(spec["text"])
        named_by_any.update(named)
        code = [rel for rel in named if _present(rel, paths)]
        found_in = [rel for rel, text in tests if any(_names(text, path) for path in code)]
        built = BUILT if named and len(code) == len(named) and found_in else PARTLY if code else NOT_BUILT
        commits = project.git(root, "--literal-pathspecs", "log", "--format=%H", "--", *code).split() if code else []
        head = spec["head"]
        title = head.get("title")
        title = title.strip() if isinstance(title, str) and title.strip() else next(
            (match[1] for match in map(_HEADING.match, _body(spec["text"])) if match), None)
        rows.append({"path": spec["path"], "title": title, "wave": _plain(head.get("wave")),
                     "status": _plain(head.get("status")), "built": built,
                     "evidence": {"code": code, "tests": found_in, "commits": commits}, "_named": named})
        if built != BUILT:
            gaps.append({"subject": spec["path"], "question": _question(built, spec["path"], {"named": named, "code": code}),
                         "answer": None})
    unnamed = [rel for rel in modules if not any(path == rel or path.startswith(rel + "/") for path in named_by_any)]
    gaps += [{"subject": rel, "question": _question("module", rel), "answer": None} for rel in unnamed]
    for row in rows:
        del row["_named"]
    return {"specs": rows, "modules": list(modules), "tickets": find_tickets(reader),
            "specs_without_code": [row["path"] for row in rows if row["built"] == NOT_BUILT],
            "code_without_spec": unnamed, "gaps": gaps}


# --------------------------------------------------------------------------
# The lite checks (S3)
# --------------------------------------------------------------------------

def _recorded(record: dict, key: str, field: str | None) -> set:
    listed = record.get(key)
    if not isinstance(listed, list):
        return set()
    return {(item.get(field) if isinstance(item, dict) else None) if field else item for item in listed}


def check(record: dict, spec_paths, module_paths) -> None:
    """Refuse a record (an AS record's front matter) that leaves out a spec or a module of the inventory, or holds a
    gap without a question: ``ADOPT_SPEC_AUDIT_INCOMPLETE`` and ``ADOPT_GAP_WITHOUT_QUESTION``, each naming them."""
    specs = sorted(set(spec_paths) - _recorded(record, "specs", "path"))
    modules = sorted(set(module_paths) - _recorded(record, "modules", None))
    rel = project.record_path("AS")
    if specs or modules:
        raise refuse("SPEC_AUDIT_INCOMPLETE", f"{rel} leaves out " + "; ".join(
            part for part in (("the spec(s) " + ", ".join(specs)) if specs else "",
                              ("the top-level code module(s) " + ", ".join(modules)) if modules else "") if part)
                     + ": every spec and every top-level code module of the inventory is named; run AS again",
                     specs=specs, modules=modules)
    gaps = record.get("gaps")
    gaps = gaps if isinstance(gaps, list) else [] if gaps is None else [None]
    bare = [str(gap.get("subject")) if isinstance(gap, dict) else repr(gap) for gap in gaps
            if not (isinstance(gap, dict) and isinstance(gap.get("question"), str) and gap["question"].strip())]
    if bare:
        raise refuse("GAP_WITHOUT_QUESTION", f"{rel} holds a gap with no question to the owner: " + ", ".join(bare)
                     + ": each gap is one question; run AS again", gaps=bare)


def gate(run) -> None:
    """A3's first check: the committed AS record (``run.records["AS"]``) is complete for the A1 inventory."""
    inventory = inventory_of(run.records)
    specs = find_specs(Reader(run.root, inventory), classes_of(run.records))
    check(run.records["AS"], [spec["path"] for spec in specs], find_modules(inventory))


def stage(run) -> dict:
    """Stage AS: record the audit of the inventory's specs; the record is checked as A3 will check it before it is
    committed."""
    inventory = inventory_of(run.records)
    classes = classes_of(run.records)
    reader = Reader(run.root, inventory)
    specs, modules = find_specs(reader, classes), find_modules(inventory)
    data = audit(run.root, reader, classes, specs, modules)
    check(data, [spec["path"] for spec in specs], modules)
    return run.finish(data, specs=len(data["specs"]), modules=len(modules), tickets=len(data["tickets"]),
                      gaps=len(data["gaps"]))
