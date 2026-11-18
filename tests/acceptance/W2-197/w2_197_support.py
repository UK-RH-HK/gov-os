"""Shared helpers of the W2-197 acceptance tests (README): the planted store, the brief's repository, the command line
in process, and readers for the memory block and the memory-use log.

- ``plant_store(base)``: one git repository and a store folder as the integration store keeps it (W2-116): a detached
  worktree of the repository at its one commit, with its lexical index and record store built in place
  (``lexical.refresh``, ``store.load``), as W2-138's support builds its stores. No vectors, no model. The repository
  holds the READY ticket, a path map with a ``role_paths`` section, a register and files whose words meet the ticket's
  title, one of them under the ticket's acceptance path and one under its implementation path (S2).
- ``BriefRepo(root)``: a repository for ``gov brief``: this tree's kernel templates and facts file (copied at test
  time, ``ready.new_since`` set to the fixture's date) and the READY ticket, as W2-152's ``real_repo`` builds it.
- ``BriefRepo`` also holds the installed judging-work skill (W2-195), which the independent-auditor brief needs.
- ``gov(capsys, *argv)``: ``gov.cli.main.main`` in this process, so the stand-ins of ``conftest.py`` (no reranker, no
  semantic route) hold for the command line too.

Nothing here reads this ticket's implementation; the interface is the ticket's ("Interface", S1, S8, S9, F1, F2).
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(REPO / "src"))

TEMPLATES_REL = "template/governance/kernel/templates"
TEMPLATES = REPO / TEMPLATES_REL
FACTS = REPO / "governance/project/facts.yaml"
KEYS = TEMPLATES / "keys.yaml"
BRIEF_T0 = TEMPLATES / "brief.md"
JUDGING_SKILL = REPO / "template/governance/kernel/skills/judging-work/SKILL.md"
JUDGING_SKILL_RELS = ("template/governance/kernel/skills/judging-work/SKILL.md",
                      ".claude/skills/judging-work/SKILL.md")
RETRIEVAL_SKILL_REL = "template/governance/kernel/skills/retrieval/SKILL.md"

SECTION = "## What memory holds for this ticket"
# S4's shared line, verbatim; S5's form names the command in place of {CMD:retrieve}
MEMORY_LINE = ("**Memory first:** {CMD:retrieve} before you grep for a concept; read every item of the bundle, never "
               "`head` or cut it, and cite the ids you use; if it does not answer, search once more in your own, "
               "different words; look a decision up by id in the register.")
SKILL_MEMORY_LINE = MEMORY_LINE.replace("{CMD:retrieve}", '`gov retrieve "<question>"`')
READ_EVERY_ITEM = "read every item of the bundle, never head or cut it, and cite the ids you use"
ROLE_TEMPLATE_STEMS = ("role-cto", "role-lead", "role-engineer", "role-test-designer", "role-reviewer",
                       "role-product-spec", "role-research")
# gov brief's roles (W2-152) and the template each is filled with
BRIEF_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "product-spec", "research", "lead")

TICKET_ID = "DAEO-fx01"
TICKET_W2 = "W2-901"
TITLE = "Build the widget"
NEW_SINCE = "2026-11-10"
CREATED_AFTER = "2026-11-11T08:00:00Z"

ACCEPTANCE_FILE = f"tests/acceptance/{TICKET_W2}/test_widget_build.py"
IMPL_FILE = "src/widget/build.py"
LONG_HEADING = "# Building the widget: " + "the parts list, the frame, the gears and the casing, in that order, " * 2

UNIT = re.compile(r"(?<!\$)\{[A-Z][A-Z0-9_]*(?::[^{}\n]*)?\}")  # an unfilled {UPPER} or {UPPER: description} slot


# --- the ticket ------------------------------------------------------------------------------------------------------

def ready_front(**changes) -> dict:
    """A READY ticket's front matter (W2-152's ready check: every required field, the dependency fields set)."""
    front = {
        "id": TICKET_ID, "status": "in_progress", "deps": [], "links": [], "type": "task", "priority": 1,
        "assignee": "engineer", "external-ref": TICKET_W2, "tags": ["fixture"], "wbs_id": TICKET_W2, "title": TITLE,
        "class": "tool", "state_class": "AUTHORITATIVE", "role": "engineer", "depends_on": [],
        "allowed_paths": ["src/widget/**", "tests/unit/widget/**"], "reads": ["src/widget/**"], "needs": [],
        "waits_on": [],
        "kpis": {"success": [{"line": "S1 The widget is built from its parts list [DEC-101].",
                              "verify": "a unit test builds the widget"}],
                 "failure": [{"line": "No widget is built.", "verify": "the unit test of S1 fails"}]},
        "non_goals": ["No graphical interface."], "done_when": ["DOD-1"], "profile": "STANDARD",
        "sources": ["DEC-101"], "est_loc": 120, "acceptance_tests": {"path": f"tests/acceptance/{TICKET_W2}/"},
    }
    for key, value in changes.items():
        if value is DROP:
            front.pop(key, None)
        else:
            front[key] = value
    return front


class _Drop:
    def __repr__(self) -> str:
        return "DROP"


DROP = _Drop()


def ticket_text(front: dict, body: str | None = None) -> str:
    """The ticket file as tk writes it: front matter between ``---`` lines, ``created`` unquoted, then the body."""
    dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False)
    lines = dumped.rstrip("\n").split("\n")
    lines.insert(3, f"created: {CREATED_AFTER}")
    if body is None:
        body = f"# {TICKET_W2} {TITLE}\n\nThe widget is built from its parts list.\n"
    return "---\n" + "\n".join(lines) + "\n---\n" + body


# --- the planted store -----------------------------------------------------------------------------------------------

REGISTER = "decisions/REGISTER.md"
PATH_MAP = f"""namespaces: {{}}
decision_register: {REGISTER}
role_paths:
  engineer:
    reads_denied: ["{{ticket_tests}}"]
  independent-test-designer:
    reads_denied: ["{IMPL_FILE.rsplit('/', 1)[0]}/**"]
"""
STORE_FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": PATH_MAP,
    REGISTER: ("# Decision register\n\n### DEC-101 — The widget rule\n- **Status:** ACCEPTED\n"
               "- **Decision:** build the widget from its parts list.\n"),
    "notes/widget.md": (LONG_HEADING + "\n\nTo build the widget, read the parts list and build the frame first.\n"
                        "The widget build then fits the gears.\n"),
    "notes/parts.md": "\n\n# The parts list\n\nThe widget build takes the parts list first: frame, gears, casing.\n",
    "notes/harbour.md": "# The harbour\n\nThe harbour keeps its lanterns lit at night.\n",
    IMPL_FILE: '"""Build the widget from its parts list."""\n\n\ndef make(parts):\n    return list(parts)\n',
    ACCEPTANCE_FILE: ('"""Acceptance: build the widget and check the widget build."""\n\n\n'
                      "def test_widget_build():\n    assert True\n"),
}

_GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
            "GIT_AUTHOR_DATE": "2026-11-11T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-11T12:00:00Z"}


def git(folder: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(folder), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                           *args], capture_output=True, text=True, env={**_GIT_ENV, "HOME": str(folder)}, check=False)
    if done.returncode:
        raise AssertionError(f"git {' '.join(args)} failed in {folder}: {done.stderr}")
    return done.stdout


def _write(root: Path, files: dict) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


@dataclass(frozen=True)
class Store:
    repo: Path    # the main worktree
    folder: Path  # the store: a detached linked worktree, built in place
    commit: str   # the commit it was built at


def plant_store(base: Path) -> Store:
    """The repository and its store folder (module docstring). The caller replaces the secret filter."""
    from gov import store
    from gov.retrieval import lexical

    repo = base / "repo"
    repo.mkdir(parents=True)
    _write(repo, {**STORE_FILES, f".tickets/{TICKET_ID}.md": ticket_text(ready_front())})
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "C1")
    commit = git(repo, "rev-parse", "HEAD").strip()
    folder = base / "store"
    git(repo, "worktree", "add", "-q", "--detach", str(folder), commit)
    lexical.refresh(folder)
    store.load(folder)
    return Store(repo.resolve(), folder.resolve(), commit)


def store_forms(folder: Path) -> set[str]:
    """The ways a block may name a store folder: as given, or with its links followed."""
    return {str(folder), os.path.realpath(folder)}


# --- the brief's repository ------------------------------------------------------------------------------------------

def real_facts(**paths) -> dict:
    """This tree's facts file, ``ready.new_since`` set to the fixture's date, ``paths`` changed as given (a value
    ``DROP`` removes the path)."""
    data = copy.deepcopy(yaml.safe_load(FACTS.read_text(encoding="utf-8")))
    data["ready"] = {"new_since": NEW_SINCE}
    for key, value in paths.items():
        if value is DROP:
            data["paths"].pop(key, None)
        else:
            data["paths"][key] = value
    return data


class BriefRepo:
    """A repository ``gov brief`` reads: this tree's kernel templates and facts file, and the READY ticket."""

    def __init__(self, root: Path, facts: dict | None = None):
        self.root = root
        folder = root / TEMPLATES_REL
        folder.mkdir(parents=True)
        for path in sorted(TEMPLATES.iterdir()):
            if path.is_file():
                shutil.copyfile(path, folder / path.name)
        self.write_facts(facts if facts is not None else real_facts())
        self.ticket(ready_front())
        self.install_judging_skill()

    def install_judging_skill(self) -> None:
        """The project's installed judging-work skill (W2-195): the kernel file and the preloaded copy of the same
        version, as an adopted project holds them; the independent-auditor brief is refused without it."""
        for rel in JUDGING_SKILL_RELS:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(JUDGING_SKILL, path)

    def write_facts(self, data: dict) -> None:
        path = self.root / "governance/project/facts.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")

    def ticket(self, front: dict, body: str | None = None) -> None:
        path = self.root / ".tickets" / f"{front['id']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ticket_text(front, body), encoding="utf-8")


def brief_args(role: str) -> list[str]:
    """``gov brief``'s positional arguments for a role (the lead needs its run)."""
    return [role, TICKET_ID, *(["--run", "build"] if role == "lead" else [])]


# --- the command line, in process ------------------------------------------------------------------------------------

@dataclass
class Run:
    argv: tuple
    code: int
    out: str
    err: str

    def envelope(self) -> dict:
        try:
            value = json.loads(self.out)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    @property
    def result(self) -> dict:
        value = self.envelope().get("result")
        return value if isinstance(value, dict) else {}

    def describe(self, tail: int = 3000) -> str:
        note = ""
        if self.code == 2 and "invalid choice" in self.err:
            note = " [the command line has no such command or option]"
        elif self.code == 2 and "unrecognized arguments" in self.err:
            note = " [the command line refuses an option: " + self.err.strip().splitlines()[-1][-200:] + "]"
        return (f"gov {' '.join(map(str, self.argv))}\nexit code {self.code}{note}\nstdout:\n{self.out[:tail]}\n"
                f"stderr:\n{self.err[-tail:]}")


def gov(capsys, *argv) -> Run:
    from gov.cli import main as cli

    capsys.readouterr()
    try:
        code = cli.main([str(arg) for arg in argv])
    except SystemExit as stop:  # a usage error
        code = stop.code if isinstance(stop.code, int) else 2
    captured = capsys.readouterr()
    return Run(tuple(argv), code, captured.out, captured.err)


def brief(capsys, repo: BriefRepo, role: str, *extra, json_out: bool = False) -> Run:
    return gov(capsys, "brief", *brief_args(role), *extra, "--root", repo.root, *(["--json"] if json_out else []))


def ok_brief(run: Run) -> str:
    assert run.code == 0 and run.out.strip(), f"gov brief did not print a brief:\n{run.describe()}"
    return run.out


def library_bundle(monkeypatch, folder: Path, query: str, role: str) -> dict:
    """``gov.retrieval.retrieve.retrieve(<store>, <query>, ticket=<ID>, role=<role>)``, as the role's own session
    would call it (``GOV_TICKET`` its ticket, DEC-1065 (2)); the environment restored after."""
    from gov.retrieval.retrieve import retrieve

    with monkeypatch.context() as patch:
        patch.setenv("GOV_TICKET", TICKET_ID)
        patch.delenv("GOV_ROLE", raising=False)
        return retrieve(folder, query, ticket=TICKET_ID, role=role)


def store_commit(folder: Path) -> str:
    from gov.retrieval.retrieve import store_of

    return store_of(folder)["commit"]


# --- the memory block ------------------------------------------------------------------------------------------------

INDEX_LINE = re.compile(r"^(\d+)\. (\S+):(\d+)-(\d+) (\S+)(?: (.*))?$")


def section(text: str) -> list[str]:
    """The lines of the brief's memory section, from its heading to the next ``## `` heading."""
    lines = text.split("\n")
    at = [n for n, line in enumerate(lines) if line.strip() == SECTION]
    assert at, f"the brief has no section {SECTION!r}:\n{text[-2500:]}"
    end = next((n for n in range(at[0] + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    return lines[at[0] + 1:end]


def fence(lines: list[str]) -> list[str]:
    """The lines inside the section's first fenced block."""
    marks = [n for n, line in enumerate(lines) if line.strip().startswith("```")]
    assert len(marks) >= 2, f"the memory section holds no fenced block: {lines}"
    return lines[marks[0] + 1:marks[1]]


def outside_fence(lines: list[str]) -> list[str]:
    out, inside = [], False
    for line in lines:
        if line.strip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            out.append(line)
    return out


def index_rows(text: str) -> list[tuple[int, str, int, int, str, str]]:
    """``(rank, path, start, end, id, first line)`` of each index line inside the memory section's fenced block."""
    rows = []
    for line in fence(section(text)):
        if not line.strip():
            continue
        found = INDEX_LINE.match(line.rstrip())
        assert found, f"a line in the memory block is not '<n>. <path>:<start>-<end> <id> <first line>': {line!r}"
        rank, path, start, end, rid, first = found.groups()
        rows.append((int(rank), path, int(start), int(end), rid, first or ""))
    return rows


def expected_rows(bundle: dict) -> list[tuple[int, str, int, int, str]]:
    return [(n, item["path"], item["start_line"], item["end_line"], str(item["id"]))
            for n, item in enumerate(bundle["evidence"], 1)]


def first_line(item: dict) -> str:
    return next((line.strip() for line in item["text"].split("\n") if line.strip()), "")


def commands_of(folder: Path, query: str) -> tuple[set[str], set[str]]:
    """The two commands the block must hold, for each form of the store's folder."""
    whole = {f'gov retrieve --root {form} --ticket {TICKET_ID} "{query}"' for form in store_forms(folder)}
    again = {f'gov retrieve --root {form} "<your question>"' for form in store_forms(folder)}
    return whole, again


def not_reached(text: str) -> list[tuple[str, str]]:
    """``(code, detail)`` of each ``Memory not reached: <CODE> <detail>.`` in the memory section."""
    found = []
    for line in section(text):
        hit = re.search(r"Memory not reached: ([A-Z][A-Z0-9_]*) (.+)\.", line)
        if hit:
            found.append(hit.groups())
    return found


# --- the memory-use log ----------------------------------------------------------------------------------------------

FIELDS = ("ts", "command", "role", "ticket", "session", "query_sha256", "stop_reason", "items", "characters",
          "latency_ms", "refusal", "store_commit", "reranked", "search_number")


def log_lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def query_hash(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]


def is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def check_types(record: dict) -> list[str]:
    """What is wrong with a log record's fields and their types (S8); empty when nothing is."""
    import datetime

    wrong = [f"no field {name}" for name in FIELDS if name not in record]
    if wrong:
        return wrong
    try:
        ts = datetime.datetime.fromisoformat(str(record["ts"]).replace("Z", "+00:00"))
        if ts.utcoffset() != datetime.timedelta(0):
            wrong.append(f"ts is not UTC: {record['ts']!r}")
    except ValueError:
        wrong.append(f"ts is not ISO: {record['ts']!r}")
    if record["command"] not in ("retrieve", "brief"):
        wrong.append(f"command is {record['command']!r}")
    for name in ("role", "ticket", "session", "stop_reason", "refusal", "store_commit"):
        if record[name] is not None and not isinstance(record[name], str):
            wrong.append(f"{name} is not a string or null: {record[name]!r}")
    if not (isinstance(record["query_sha256"], str) and re.fullmatch(r"[0-9a-f]{16}", record["query_sha256"])):
        wrong.append(f"query_sha256 is not 16 hex digits: {record['query_sha256']!r}")
    for name in ("items", "characters"):
        if not (is_int(record[name]) and record[name] >= 0):
            wrong.append(f"{name} is not a count: {record[name]!r}")
    latency = record["latency_ms"]
    if not (isinstance(latency, (int, float)) and not isinstance(latency, bool) and latency >= 0):
        wrong.append(f"latency_ms is not a number of milliseconds: {latency!r}")
    if record["reranked"] is not None and not isinstance(record["reranked"], bool):
        wrong.append(f"reranked is not a boolean: {record['reranked']!r}")
    if record["search_number"] is not None and not (is_int(record["search_number"]) and record["search_number"] >= 1):
        wrong.append(f"search_number is not a count from 1 or null: {record['search_number']!r}")
    return wrong


def names_commit(value, commit: str) -> bool:
    """``value`` names ``commit``: its full id or at least its first 12 hex digits."""
    return isinstance(value, str) and len(value) >= 12 and commit.startswith(value)


# --- text ------------------------------------------------------------------------------------------------------------

def fold(text: str) -> str:
    """Lower case, backticks dropped, white space as single spaces."""
    return " ".join(text.replace("`", "").lower().split())


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return text[end + 4:].split("\n", 1)[1] if "\n" in text[end + 4:] else ""
    return text


def retrieve_sandbox_split(text: str) -> list[str]:
    """Lines that name retrieve and split it by the sandbox (outside/inside it), or say no retrieve in the sandbox."""
    hits = []
    for line in text.split("\n"):
        folded = fold(line)
        if "retrieve" not in folded:
            continue
        if re.search(r"outside the sandbox|inside the sandbox|inside it|in the sandbox", folded):
            hits.append(line)
    return hits
