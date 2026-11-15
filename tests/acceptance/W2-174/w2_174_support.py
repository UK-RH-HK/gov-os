"""Shared helpers of the W2-174 acceptance tests (README).

Every case builds a repository of its own under ``tmp_path`` (a ``.tickets/`` with planted tickets, optionally a facts
file and the kernel templates) and drives the public interface: ``python3 -m gov.cli.main adopt ... --root <tmp>`` as a
subprocess, and the two functions the ticket's "Interface" names (``gov.adopt.verify_pass.missing`` / ``apply``,
``gov.adopt.facts.write_default``). Nothing here reads this ticket's implementation.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import site
import stat
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
TEMPLATES = REPO / "template/governance/kernel/templates"
FACTS = REPO / "governance/project/facts.yaml"
FACTS_SCHEMA = REPO / "template/governance/kernel/schemas/facts.schema.json"
FACTS_REL = "governance/project/facts.yaml"
TEMPLATES_REL = "template/governance/kernel/templates"

BASE_COMMIT = "f2b1d38af"  # the base this ticket branches from (F2)
TIMEOUT = 90

# One fixed, distinctive folder name for every fixture repository: the facts file must not name it (S5).
REPO_NAME = "adopted-fixture-q7x"
NEW_SINCE = "2026-11-10"
CREATED_AFTER = "2026-11-11T08:00:00Z"
TODAY = datetime.date(2026, 11, 12)
SESSION = "sess-174a"

CLAUSE = "a unit test runs the widget and reads what it prints"


# --- tickets --------------------------------------------------------------------------------------------------------

def plain(text: str, verify: str | None = None) -> str:
    """A KPI item as a plain scalar. With ``verify`` it is the form ``gov brief`` reads (`` Verify: <text>`` appended),
    which YAML cannot hold in a plain scalar (``: `` opens a mapping), so that item is single-quoted."""
    return f"- {text}" if not verify else f"- '{text} Verify: {verify}'"


def single(text: str) -> str:
    return f"- '{text}'"


def double(text: str) -> str:
    return f'- "{text}"'


def mapping(line: str, verify: str) -> str:
    return f'- line: "{line}"\n  verify: "{verify}"'


def front_text(ticket_id: str, w2: str, status: str, success: list[str], failure: list[str],
               body: str | None = None) -> str:
    """A ticket file as tk writes it (front matter between ``---`` lines, then the body), READY on every count but
    the KPI lines' verifies; ``success`` and ``failure`` are lists of KPI items already in YAML text form."""
    def block(items: list[str]) -> str:
        return "\n".join(f"  {item}".replace("\n", "\n  ") for item in items)

    if body is None:
        body = f"# {w2} Fixture ticket {w2}\n\nThe widget prints its name when asked, and refuses an empty one.\n"
    return (
        "---\n"
        f"id: {ticket_id}\n"
        f"status: {status}\n"
        "deps: []\n"
        "links: []\n"
        f"created: {CREATED_AFTER}\n"
        "type: task\n"
        "priority: 1\n"
        "assignee: engineer\n"
        f"external-ref: {w2}\n"
        "tags:\n- fixture\n"
        f"wbs_id: {w2}\n"
        f"title: Fixture ticket {w2}\n"
        "class: tool\n"
        "state_class: AUTHORITATIVE\n"
        "role: engineer\n"
        "depends_on: []\n"
        "allowed_paths:\n- src/widget/**\n- tests/unit/widget/**\n"
        "reads:\n- src/widget/**\n"
        "needs: []\n"
        "waits_on: []\n"
        "kpis:\n"
        "  success:\n" + block(success) + "\n"
        "  failure:\n" + block(failure) + "\n"
        "non_goals:\n- No graphical interface.\n"
        "done_when:\n- DOD-1\n- DOD-2\n- DOD-3\n- DOD-5\n- DOD-6\n"
        "profile: STANDARD\n"
        "sources:\n- DEC-1\n"
        "est_loc: 120\n"
        f"acceptance_tests:\n  path: tests/acceptance/{w2}/\n"
        "track: A\n"
        "---\n" + body
    )


def lacking(text: str = "The widget does a thing [DEC-1].") -> str:
    return plain(text)


def verified(text: str = "The widget does a thing [DEC-1].") -> str:
    return plain(text, "a unit test of the thing")


# --- the fixture repository -----------------------------------------------------------------------------------------

class Repo:
    """A temporary repository: ``tmp/adopted-fixture-q7x`` with ``.tickets/``; the answers file lives outside it."""

    def __init__(self, tmp: Path, name: str = REPO_NAME):
        self.tmp = tmp
        self.root = tmp / name
        self.tickets = self.root / ".tickets"
        self.tickets.mkdir(parents=True)
        self.outside = tmp / "outside"
        self.outside.mkdir()
        (tmp / "empty-home").mkdir(exist_ok=True)  # the children's HOME, made now so a snapshot never sees it appear

    def ticket(self, ticket_id: str, w2: str, status: str, success: list[str], failure: list[str],
               body: str | None = None) -> Path:
        path = self.tickets / f"{ticket_id}.md"
        path.write_text(front_text(ticket_id, w2, status, success, failure, body), encoding="utf-8")
        return path

    def bare(self, ticket_id: str, w2: str, status: str = "open", state_class: bool = True, **fields) -> Path:
        """A ticket without the six fields (``bare_text``), with the given ones set (``with_fields``)."""
        return self.raw_ticket(ticket_id, with_fields(bare_text(ticket_id, w2, status, state_class), **fields))

    def raw_ticket(self, ticket_id: str, text: str) -> Path:
        path = self.tickets / f"{ticket_id}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def answers(self, data, name: str = "answers.yaml") -> Path:
        path = self.outside / name
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
        return path

    def answers_text(self, text: str, name: str = "answers.yaml") -> Path:
        path = self.outside / name
        path.write_text(text, encoding="utf-8")
        return path

    def file(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def kernel_templates(self) -> None:
        folder = self.root / TEMPLATES_REL
        folder.mkdir(parents=True, exist_ok=True)
        for path in sorted(TEMPLATES.iterdir()):
            if path.is_file():
                shutil.copyfile(path, folder / path.name)

    def filled_facts(self) -> None:
        """This tree's own facts file with every command filled and ``ready.new_since`` set to the fixtures' date
        (what an adopted project's CTO has after the defaults; the ticket's S3 fixture)."""
        data = yaml.safe_load(FACTS.read_text(encoding="utf-8"))
        data["ready"] = {"new_since": NEW_SINCE}
        path = self.root / FACTS_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")

    def ticket_bytes(self, ticket_id: str) -> bytes:
        return (self.tickets / f"{ticket_id}.md").read_bytes()

    def ticket_text(self, ticket_id: str) -> str:
        return (self.tickets / f"{ticket_id}.md").read_text(encoding="utf-8")

    # the run
    def gov(self, *args: str, session: str | None = None, json_out: bool = True) -> subprocess.CompletedProcess:
        argv = [*args, "--root", str(self.root)]
        if session is not None:
            argv += ["--session", session]
        if json_out:
            argv.append("--json")
        return subprocess.run([sys.executable, "-B", "-m", "gov.cli.main", *argv], capture_output=True, text=True,
                              timeout=TIMEOUT, cwd=str(self.tmp), env=child_env(self.tmp),
                              stdin=subprocess.DEVNULL)

    def adopt(self, *args: str, session: str | None = None, json_out: bool = True) -> subprocess.CompletedProcess:
        return self.gov("adopt", *args, session=session, json_out=json_out)

    def verify_list(self) -> subprocess.CompletedProcess:
        return self.adopt("--verify-list")

    def verify_apply(self, answers: Path, session: str | None = SESSION,
                     json_out: bool = True) -> subprocess.CompletedProcess:
        return self.adopt("--verify-apply", str(answers), session=session, json_out=json_out)


def child_env(scratch: Path, extra: dict | None = None) -> dict:
    """The child's environment: this tree's ``src`` first, an empty ``HOME``, no bytecode written, no network."""
    home = scratch / "empty-home"
    home.mkdir(exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "GOV_"))}
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    dead = "http://127.0.0.1:9"
    env.update({"PYTHONPATH": str(SRC), "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1",
                "http_proxy": dead, "https_proxy": dead, "HTTP_PROXY": dead, "HTTPS_PROXY": dead,
                "OLLAMA_HOST": "127.0.0.1:9", "CUDA_VISIBLE_DEVICES": ""})
    if extra:
        env.update(extra)
    return env


# --- the modules under test -----------------------------------------------------------------------------------------

def verify_pass():
    """``gov.adopt.verify_pass``; a missing module is a failed case with its reason, not an error."""
    try:
        import gov.adopt.verify_pass as module
    except ImportError as error:
        raise AssertionError(f"src/gov/adopt/verify_pass.py is missing or does not import: {error}") from None
    return module


def facts_module():
    try:
        import gov.adopt.facts as module
    except ImportError as error:
        raise AssertionError(f"src/gov/adopt/facts.py is missing or does not import: {error}") from None
    return module


# --- reading what came back -----------------------------------------------------------------------------------------

def describe(done: subprocess.CompletedProcess) -> str:
    return f"exit {done.returncode}\n--- stdout ---\n{done.stdout[-2500:]}\n--- stderr ---\n{done.stderr[-2500:]}"


def envelope(done: subprocess.CompletedProcess) -> dict:
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"no JSON envelope on stdout: {describe(done)}") from None
    assert isinstance(data, dict) and "ok" in data, f"not an API-0002 envelope: {done.stdout[:500]}"
    return data


def result_of(done: subprocess.CompletedProcess) -> dict:
    """The ``result`` of a run that must succeed (exit 0, ``ok: true``)."""
    assert done.returncode == 0, f"gov adopt did not succeed: {describe(done)}"
    data = envelope(done)
    assert data.get("ok") is True, f"the envelope is not ok: {done.stdout[:500]}"
    assert isinstance(data.get("result"), dict), f"no result mapping in the envelope: {done.stdout[:500]}"
    return data["result"]


def refused_code(done: subprocess.CompletedProcess) -> str:
    """The error code of a ``--json`` refusal: exit 1, ``ok: false``, ``error.code``."""
    assert done.returncode == 1, f"expected a GovError refusal (exit 1): {describe(done)}"
    data = envelope(done)
    assert data.get("ok") is False, f"the envelope is not a refusal: {done.stdout[:500]}"
    error = data.get("error")
    assert isinstance(error, dict) and isinstance(error.get("code"), str), f"no error code: {done.stdout[:500]}"
    return error["code"]


# --- the tree as it stands ------------------------------------------------------------------------------------------

def snapshot(root: Path) -> dict[str, tuple]:
    """Every entry under ``root``: kind, mode and, for a file, size, modification time and content hash."""
    found = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        rel = str(path.relative_to(root))
        if stat.S_ISDIR(info.st_mode):
            found[rel] = ("dir", stat.S_IMODE(info.st_mode))
        else:
            found[rel] = ("file", stat.S_IMODE(info.st_mode), info.st_size, info.st_mtime_ns,
                          hashlib.sha256(path.read_bytes()).hexdigest())
    return found


def changed_entries(before: dict, after: dict) -> list[str]:
    return sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))


def utc_today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


# --- front matter reading -------------------------------------------------------------------------------------------

def front_of(text: str) -> dict:
    lines = text.split("\n")
    assert lines[0] == "---", "a ticket file does not open with ---"
    end = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:end]))


def rows_of(text: str) -> list[tuple[str, str, str | None]]:
    from gov.brief.build import kpi_rows

    return kpi_rows(front_of(text))


def lacking_labels(text: str) -> list[str]:
    return [label for label, _, verify in rows_of(text) if verify is None]


def marker_lines(text: str) -> list[str]:
    """The ``verify_pass:`` lines of the front matter."""
    lines = text.split("\n")
    end = lines.index("---", 1)
    return [line for line in lines[1:end] if line.startswith("verify_pass:")]


def differing_lines(before: str, after: str) -> list[tuple[int, str, str]]:
    """(1-based line number in ``before``, old line, new line) for each line that changed, when both texts have the
    same number of lines, plus every line one has and the other lacks otherwise (``-1``)."""
    old, new = before.split("\n"), after.split("\n")
    if len(old) != len(new):
        return [(-1, "\n".join(old), "\n".join(new))]
    return [(n, a, b) for n, (a, b) in enumerate(zip(old, new), 1) if a != b]


def marker_invariant(root: Path) -> None:
    """No ticket under ``root`` carries ``verify_pass:`` while one of its KPI lines lacks a verify (F1)."""
    for path in sorted((root / ".tickets").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if marker_lines(text):
            assert not lacking_labels(text), \
                f"{path.name} is marked verify_pass while {lacking_labels(text)} still lack a verify"


ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --- the launch fields (S6, S7, F4; DEC-1188) -----------------------------------------------------------------------

FIELD_NAMES = ("role", "allowed_paths", "kpis", "reads", "needs", "waits_on")  # L10, in this order
SCHEMAS = REPO / "template/governance/kernel/schemas"
ROLES = ("orchestrator", "product-spec", "independent-test-designer", "engineer", "independent-auditor", "research")


def bare_text(ticket_id: str, w2: str, status: str = "open", state_class: bool = True, body: str | None = None) -> str:
    """A ticket as ``tk create`` writes it plus the common keys the schema requires (L16), none of the six fields, no
    ``class`` and no ``non_goals``; a comment sits between keys so a re-dump would lose it."""
    if body is None:
        body = f"# {w2} Fixture ticket {w2}\n\nThe adoption's coordination work, written before the product.\n"
    head = ["---", f"id: {ticket_id}", f"status: {status}", "deps: []", "links: []", f"created: {CREATED_AFTER}",
            "type: task", "priority: 1", "assignee: operator", f"external-ref: {w2}", "tags:", "- adoption",
            f"wbs_id: {w2}", f"title: Fixture ticket {w2}", "# a comment between keys that must stay"]
    if state_class:
        head.append("state_class: AUTHORITATIVE  # a trailing comment that must stay")
    return "\n".join([*head, "---"]) + "\n" + body


def field_text(name: str, value) -> str:
    """The YAML text lines of one front-matter field."""
    return yaml.safe_dump({name: value}, sort_keys=False, allow_unicode=True, width=1000)


def with_fields(text: str, **values) -> str:
    """``text`` with the given fields inserted just before the front matter's closing ``---`` (L10 order)."""
    lines = text.split("\n")
    end = lines.index("---", 1)
    added = "".join(field_text(name, values[name]) for name in FIELD_NAMES if name in values)
    return "\n".join([*lines[:end], *added.rstrip("\n").split("\n"), *lines[end:]]) if added else text


def good_kpis(tag: str = "The widget") -> dict:
    return {"success": [{"line": f"{tag} prints its name [DEC-1].", "verify": "a unit test runs it and reads what it prints"}],
            "failure": [{"line": f"{tag} never crashes on an empty name.", "verify": "a unit test feeds an empty name and sees a refusal"}]}


def good_fields(role: str = "engineer", tag: str = "The widget") -> dict:
    """An answer for all six fields that every check accepts."""
    return {"role": role, "allowed_paths": ["src/widget/**", "tests/unit/widget/**"], "kpis": good_kpis(tag),
            "reads": ["src/widget/**"], "needs": [], "waits_on": []}


def schema_errors(front: dict) -> list[str]:
    """The errors of ``front`` against the kernel's ticket schema, ``common.schema.json`` resolved (a read of this tree's
    kernel schemas, the copy ``gov check`` uses)."""
    import jsonschema

    schema = json.loads((SCHEMAS / "ticket.schema.json").read_text(encoding="utf-8"))
    common = json.loads((SCHEMAS / "common.schema.json").read_text(encoding="utf-8"))
    try:
        from referencing import Registry, Resource
        from referencing.jsonschema import DRAFT202012

        registry = Registry().with_resource("common.schema.json", Resource.from_contents(common, DRAFT202012))
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:
        resolver = jsonschema.RefResolver.from_schema(schema, store={"common.schema.json": common})
        validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    instance = json.loads(json.dumps(front, default=str))
    return [f"/{'/'.join(map(str, error.absolute_path))}: {error.message}" for error in validator.iter_errors(instance)]


def refusals_of(root: Path, ticket_id: str) -> list[str]:
    """``ready_check``'s refusals of one ticket as ``CODE detail`` (the fixtures' ``new_since``)."""
    from gov.brief.build import Tickets, ready_check

    tickets = Tickets(root)
    front = tickets.load(root / ".tickets" / f"{ticket_id}.md")[0]
    return [f"{item['code']} {item['detail']}" for item in ready_check(front, tickets, root, NEW_SINCE)[0]]
