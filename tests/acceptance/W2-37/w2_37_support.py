"""Support code for the W2-37 acceptance tests (DAEO-6n5k): ``gov impact``.

How the tests run (the README says more):

- **Through public interfaces only.**
  - ``gov impact`` (``python -m gov.cli.main impact``), read through its ``--json`` envelope (API-0002). Every key
    the tests read is named once, below, under "The interface the tests assume", so that a package that renames one
    changes one line.
  - ``gov closure --json`` (DEC-391), only to compare the depth a radius gives and as the premise that the fixture's
    records are linked as the tests say.
  - ``gov.store.load(root)`` and ``gov.codeintel.index(root)``, to build the record store and the code index of a
    temporary repository, as the W1-20 suite does. ``gov impact`` is never expected to build either.
  - ``gov check --json`` for row W2-M056 (the W1-26 check families).
- **This worktree's code** (DEC-732): every process a case starts gets ``child_env()``, whose ``PYTHONPATH`` is this
  worktree's ``src/`` (``SRC``, found from this file's own place).
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's temporary folder. Single named files of this checkout are read (the kernel schemas, one check
  declaration at a time, the change skill, the readiness dimensions, the decision register), never a folder.
- **Deterministic, no network.** Fixed authors and dates; every call in a new process.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import site
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
SCHEMAS = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"
CHECKS = REPO_ROOT / "template" / "governance" / "kernel" / "checks"
OWN_REGISTER = REPO_ROOT / "docs" / "DECISION_REGISTER.md"
SKILL_TEMPLATE = REPO_ROOT / "template" / "governance" / "kernel" / "skills" / "change" / "SKILL.md"
SKILL_COPY = REPO_ROOT / ".claude" / "skills" / "change" / "SKILL.md"
DIMENSIONS_REL = "docs/contract/readiness-dimensions.yaml"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template" / ".gitleaks.toml"
TOOL = "codebase-memory-mcp"
TIMEOUT_S = 300.0

# --------------------------------------------------------------------------
# The interface the tests assume (README, "The interface"). One place only.
# --------------------------------------------------------------------------

COMMAND = "impact"
COMPARE = "--compare"            # gov impact --compare <CIT-E path>: the CIT-E checked against its CIT-P (KPI 2)
OUT = "--out"                    # gov impact --out <path>: the CIT-P written as a record file, and nothing else
KINDS = ("specifications", "decisions", "tickets", "tests", "code")   # the five kinds of CAP-33's acceptance line
GRAPHS = ("record", "code")      # the two graphs: the record graph and the code graph
GRAPH_OK = "ok"                  # result.graphs.<graph> when that graph was read in full and is current
CITP_TYPE, CITE_TYPE = "change-impact-proposal", "change-execution-record"
ONLY_IN = ("proposal", "execution")   # a difference names the one record the item is in
OPTIONS = ("apply now", "defer", "re-baseline")   # DEC-105's three options
RADIUS = re.compile(r"^R[0-9]+\+?$")              # R0, R1, R2, R3 or R3+ (DEC-035)
DECISION_ID = re.compile(r"^(ADR|DEC)-[0-9]{3,}$")
DOCUMENT_ID = re.compile(r"^[A-Z][A-Z0-9]*-[A-Za-z0-9._-]+$")
STATE_CLASSES = ("AUTHORITATIVE", "DERIVED", "NARRATIVE", "EVIDENCE", "HISTORICAL", "UNKNOWN_OR_CONFLICTING")
CLOSED = "CLOSED"                # reading R9: the status of a closed specification (package P-5)


class Missing(AssertionError):
    """``gov impact`` does not exist yet."""


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    """Places outside any repository: HOME, TMPDIR, a runtime directory, a working directory, a ``bare`` PATH."""
    base: Path
    home: Path
    tmp: Path
    runtime: Path
    elsewhere: Path
    bare: Path

    @property
    def full(self):
        """The session's own PATH: the code tool and gitleaks, when this machine has them."""
        return os.environ.get("PATH", "/usr/bin:/bin")


def make_box(base):
    base = Path(base)
    places = [base / name for name in ("home", "tmp", "runtime", "elsewhere", "bare")]
    for place in places:
        place.mkdir(parents=True, exist_ok=True)
    git_tool = base / "bare" / "git"
    git_tool.write_text(f'#!/bin/sh\nexec "{shutil.which("git")}" "$@"\n', encoding="utf-8")
    git_tool.chmod(0o755)
    return Box(base, *places)


def child_env(box, path=None):
    """This worktree's ``src/`` on ``PYTHONPATH`` (DEC-732); a throwaway HOME; ``bare`` PATH unless told."""
    found = {
        "PATH": str(box.bare if path is None else path),
        "HOME": str(box.home),
        "TMPDIR": str(box.tmp),
        "XDG_RUNTIME_DIR": str(box.runtime),
        "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if site.ENABLE_USER_SITE:
        found["PYTHONUSERBASE"] = site.getuserbase()
    return found


# --------------------------------------------------------------------------
# Running gov
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"gov {' '.join(self.argv)}\nexit code: {self.returncode}\n"
                f"stdout:\n{self.stdout[-4000:]}\nstderr:\n{self.stderr[-3000:]}")


def gov(box, *argv, path=None, cwd=None):
    """``python -m gov.cli.main <argv>`` in a new process, never in the repository under test."""
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *argv], cwd=str(cwd or box.elsewhere),
                              env=child_env(box, path), capture_output=True, text=True, timeout=TIMEOUT_S,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(argv)} did not end within {TIMEOUT_S:.0f} s") from None
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr)


def impact(root, change, box, path=None, out=None):
    """``gov impact --json --root <root> [--out <path>] <change>...``."""
    argv = [COMMAND, "--json", "--root", str(root)]
    if out is not None:
        argv += [OUT, str(out)]
    return gov(box, *argv, *([change] if isinstance(change, str) else list(change)), path=path)


def compare(root, execution_rel, box, path=None):
    """``gov impact --json --root <root> --compare <CIT-E path>``."""
    return gov(box, COMMAND, "--json", "--root", str(root), COMPARE, str(execution_rel), path=path)


def envelope(run, command=COMMAND):
    """The API-0002 envelope of a ``--json`` run. A traceback is never an answer."""
    assert "Traceback" not in run.stderr, f"gov {command} ended with a traceback\n{run.describe()}"
    try:
        document = json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"gov {command} --json did not print one JSON document\n{run.describe()}") from None
    assert isinstance(document, dict) and document.get("command") == command and "ok" in document, \
        f"gov {command} --json did not print the envelope (`command`, `ok`)\n{run.describe()}"
    return document


def result(run):
    """The ``result`` of a ``gov impact`` run that succeeded, checked for the shape the README states."""
    document = envelope(run)
    assert run.returncode == 0 and document["ok"] is True, f"gov impact did not succeed\n{run.describe()}"
    found = document.get("result")
    assert isinstance(found, dict), f"the result is not a map\n{run.describe()}"
    return found


def assessment(run):
    """The result of an impact assessment, checked for every key the README names."""
    found = result(run)
    show = run.describe()
    assert isinstance(found.get("change"), list) and found["change"], f"`change` is not a non-empty list\n{show}"
    for entry in found["change"]:
        assert isinstance(entry, dict) and isinstance(entry.get("id"), str), f"a `change` entry: {entry!r}\n{show}"
    assert isinstance(found.get("radius"), str) and RADIUS.match(found["radius"]), \
        f"`radius` is not one of R0, R1, R2, R3 (or R3+): {found.get('radius')!r}\n{show}"
    assert isinstance(found.get("depth"), int) and not isinstance(found["depth"], bool) and found["depth"] >= 0, \
        f"`depth` is not a whole number: {found.get('depth')!r}\n{show}"
    affected = found.get("affected")
    assert isinstance(affected, dict) and sorted(affected) == sorted(KINDS), \
        f"`affected` is not grouped by exactly the five kinds {KINDS}: {sorted(affected or {})}\n{show}"
    for kind in KINDS:
        assert isinstance(affected[kind], list), f"`affected.{kind}` is not a list\n{show}"
        for item in affected[kind]:
            assert isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("graph") in GRAPHS, \
                f"an item of `affected.{kind}` is not a map with an `id` and a `graph` of {GRAPHS}: {item!r}\n{show}"
    graphs = found.get("graphs")
    assert isinstance(graphs, dict) and all(isinstance(graphs.get(g), str) for g in GRAPHS), \
        f"`graphs` does not state the record and the code graph: {graphs!r}\n{show}"
    assert isinstance(found.get("complete"), bool), f"`complete` is not true or false\n{show}"
    assert isinstance(found.get("gaps"), list), f"`gaps` is not a list\n{show}"
    return found


def ask(root, change, box, path=None):
    return assessment(impact(root, change, box, path=path))


def require_built(box):
    """Raise Missing unless ``gov`` lists an ``impact`` command."""
    listing = gov(box, "--help")
    run = gov(box, COMMAND, "--help")
    if run.returncode != 0 or not re.search(rf"^\s+{COMMAND}\s", listing.stdout, re.MULTILINE):
        first = (run.stderr.strip().splitlines() or ["(nothing)"])[-1]
        raise Missing(f"gov impact is not built: `gov --help` lists no `impact` command, and `gov impact --help` "
                      f"exits {run.returncode}: {first[:200]}")


# --------------------------------------------------------------------------
# Reading an assessment
# --------------------------------------------------------------------------

def names_symbol(item_id, name):
    """An item id names the symbol ``name``: the name itself or a qualified name ending in it."""
    return item_id == name or re.search(rf"[.:/#]{re.escape(name)}$", item_id) is not None


def items(found, kind):
    return found["affected"][kind]


def ids_of(found, kind=None):
    kinds = KINDS if kind is None else (kind,)
    return sorted(item["id"] for k in kinds for item in found["affected"][k])


def where(found, wanted, symbol=False):
    """``[(kind, graph)]`` of every listing of ``wanted`` in ``affected``."""
    places = []
    for kind in KINDS:
        for item in found["affected"][kind]:
            if (names_symbol(item["id"], wanted) if symbol else item["id"] == wanted):
                places.append((kind, item["graph"]))
    return places


def gap_ids(found):
    return sorted(str(gap.get("id")) for gap in found["gaps"] if isinstance(gap, dict))


def in_gaps(found, wanted, symbol=False):
    return any(names_symbol(gap, wanted) if symbol else gap == wanted for gap in gap_ids(found))


def text_of(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def assert_incomplete(run, graph, word=None):
    """The run does not read as complete, and it says which graph (and, when given, the word: stale, missing)."""
    document = envelope(run)
    show = run.describe()
    if document["ok"] is True:
        found = assessment(run)
        assert found["complete"] is False, f"the report reads as complete although the {graph} graph was not\n{show}"
        state = found["graphs"][graph]
        assert state != GRAPH_OK, f"`graphs.{graph}` says {GRAPH_OK!r} although that graph was not\n{show}"
        if word is not None:
            said = text_of(found["graphs"]) + text_of(found["gaps"]) + text_of(found.get("warnings", []))
            assert word in said.lower(), f"the report does not say the {graph} graph is {word}\n{show}"
        return found
    assert run.returncode != 0, f"a refusal ends with exit code 0\n{show}"
    said = text_of(document.get("error"))
    names = {"record": ("record", "store"), "code": ("code",)}[graph]
    assert any(name in said.lower() for name in names), \
        f"the refusal does not say which graph ({graph}) it could not read: {said}\n{show}"
    if word is not None:
        assert word in said.lower(), f"the refusal does not say the {graph} graph is {word}: {said}\n{show}"
    return None


def assert_refused(run, *named):
    """Refused with a clear error: not ok, exit code not 0, no traceback, an error that names each of ``named``."""
    show = run.describe()
    assert "Traceback" not in run.stderr, f"gov impact ended with a traceback\n{show}"
    assert run.returncode != 0, f"gov impact did not refuse (exit code 0)\n{show}"
    try:
        document = json.loads(run.stdout)
    except ValueError:
        document = None
    if isinstance(document, dict) and document.get("command") == COMMAND:
        assert document.get("ok") is False, f"a refusal reads ok\n{show}"
        error = document.get("error")
        assert isinstance(error, dict) and isinstance(error.get("code"), str) and error["code"], \
            f"the refusal carries no error code\n{show}"
        said = text_of(error)
    else:
        said = run.stdout + run.stderr     # a usage error of the command line
        assert said.strip(), f"the refusal says nothing\n{show}"
    for name in named:
        assert name in said, f"the refusal does not name {name!r}\n{show}"
    return document


# --------------------------------------------------------------------------
# Python calls in a child process: gov.store, gov.codeintel
# --------------------------------------------------------------------------

_CHILD = (
    "import importlib, json, sys\n"
    "from pathlib import Path\n"
    "module, function, root, args = json.loads(sys.argv[1])\n"
    "value = getattr(importlib.import_module(module), function)(Path(root), *args)\n"
    "print('W2-37-RESULT ' + json.dumps(value, default=str))\n"
)


def call(module, function, root, box, *args, path=None):
    request = json.dumps([module, function, str(root), list(args)])
    done = subprocess.run([sys.executable, "-c", _CHILD, request], cwd=str(box.elsewhere),
                          env=child_env(box, path), capture_output=True, text=True, timeout=TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
    lines = [line for line in done.stdout.splitlines() if line.startswith("W2-37-RESULT ")]
    assert done.returncode == 0 and lines, \
        f"{module}.{function} failed (exit code {done.returncode}):\n{done.stdout[-2000:]}\n{done.stderr[-3000:]}"
    return json.loads(lines[-1][len("W2-37-RESULT "):])


def load_store(root, box):
    """``gov.store.load(root)``: the record store, built in the temporary repository."""
    return call("gov.store", "load", root, box)


def build_index(root, box):
    """``gov.codeintel.index(root)``: the code index, built in the temporary repository with the real tool."""
    return call("gov.codeintel", "index", root, box, path=box.full)


def closure(root, ids, box, depth=None, radius=None, path=None):
    """The checked ``result`` of ``gov closure --json``."""
    argv = ["closure", "--json", "--root", str(root)]
    argv += ["--depth", str(depth)] if depth is not None else ["--radius", str(radius)]
    run = gov(box, *argv, *ids, path=path)
    document = envelope(run, command="closure")
    assert run.returncode == 0 and document["ok"] is True, f"gov closure did not succeed\n{run.describe()}"
    return document["result"]


def closure_ids(found):
    return sorted(entry["id"] for entry in found["closure"])


# --------------------------------------------------------------------------
# git and the temporary project
# --------------------------------------------------------------------------

DATE = "2026-10-09T{hour:02d}:{minute:02d}:00+00:00"


class Project:
    """A temporary git repository whose commits a case makes one by one."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.minute = 0
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        self.minute += 1
        hour, minute = divmod(self.minute, 60)
        date = DATE.format(hour=1 + hour, minute=minute)
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.root.parent), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "W2-37 tests", "GIT_AUTHOR_EMAIL": "w2-37@example.invalid",
            "GIT_COMMITTER_NAME": "W2-37 tests", "GIT_COMMITTER_EMAIL": "w2-37@example.invalid",
            "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
        }
        done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=environment)
        assert done.returncode == 0, f"git {' '.join(args)} failed in {self.root}:\n{done.stderr}"
        return done.stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, subject="work"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", subject,
                 "--trailer", "Task: PROJ-ab01", "--trailer", "Role: engineer")
        return self.git("rev-parse", "HEAD").strip()


def clone(source, destination):
    """A clone of a temporary fixture repository (never of this repository)."""
    assert REPO_ROOT not in Path(source).resolve().parents and Path(source).resolve() != REPO_ROOT
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def snapshot(root):
    """Everything a read command must leave as it was: every file outside ``.git`` with its bytes' hash, and git's
    view (HEAD, the refs, the stash, the status)."""
    root = Path(root)
    files = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] == ".git":
            continue
        if path.is_symlink():
            files[str(rel)] = "link:" + os.readlink(path)
        elif path.is_file():
            files[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            files[str(rel) + "/"] = "dir"
    project = Project.__new__(Project)
    project.root, project.minute = root, 0
    state = {
        "head": project.git("rev-parse", "HEAD").strip(),
        "refs": project.git("for-each-ref", "--format=%(refname) %(objectname)"),
        "stash": project.git("stash", "list"),
        "status": project.git("status", "--porcelain", "--untracked-files=all", "--ignored"),
    }
    return files, state


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def frontmatter(fields, title="A record", body="Body text."):
    """A record file. Every value is written as JSON, which YAML reads as the same value (a flow value)."""
    lines = [f"{key}: {json.dumps(value)}" for key, value in fields.items()]
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {title}\n\n{body}\n"


def rec(record_id, record_type, status="ACTIVE", state_class="AUTHORITATIVE", body="Body text.", **keys):
    fields = {"id": record_id, "type": record_type, "status": status, "state_class": state_class,
              "title": f"Record {record_id}"}
    fields.update(keys)
    return frontmatter(fields, title=record_id, body=body)


def decision(record_id, status="ACCEPTED", **edges):
    """A schema-valid MADR decision file (madr.schema.json)."""
    return rec(record_id, "decision", status=status, **edges)


def specification(record_id, status="ACTIVE", **edges):
    return rec(record_id, "specification", status=status, **edges)


def capability(record_id, **edges):
    return rec(record_id, "capability", **edges)


def ticket(ticket_id, **edges):
    """A ticket as tk writes it, with the task contract (ticket.schema.json)."""
    fields = {"id": ticket_id, "status": "open", "type": "task", "state_class": "AUTHORITATIVE",
              "role": "engineer", "allowed_paths": ["app/**"], "kpis": {"success": ["It works."], "failure": []},
              "title": f"Ticket {ticket_id}"}
    fields.update(edges)
    return frontmatter(fields, title=ticket_id)


def evidence(record_id, **edges):
    return rec(record_id, "evidence", status="FINAL", state_class="EVIDENCE", **edges)


def path_map(namespaces=None, code=True, register=None):
    """A path map valid under the kernel's schema (its required systems read from the schema); ``register`` names
    the decision register (DEC-479)."""
    schema = json.loads((SCHEMAS / "path-map.schema.json").read_text(encoding="utf-8"))
    policies = {
        "security": "hard-block", "authority": "hard-block", "test": "hard-block", "change": "hard-block",
        "human_gate": "hard-block", "tool": "hard-block", "memory": "warning", "context": "warning",
        "checkpoint": "warning", "model_routing": "informational", "budget": "informational",
        "learning": "informational", "archive": "informational",
    }

    def namespace(paths, memory_class="governance"):
        return {"paths": paths, "memory_class": memory_class, "sensitivity": "internal",
                "permitted_roles": ["orchestrator", "engineer", "independent-test-designer"],
                "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "embedded",
                "provenance": "written by the W2-37 tests", "deletion_rebuild": "authoritative; from git"}

    spaces = namespaces or {"everything": (["**"], "governance")}
    document = {
        "state_class": "AUTHORITATIVE",
        "namespaces": {name: namespace(paths, memory_class) for name, (paths, memory_class) in spaces.items()},
        "capabilities": {"code_intelligence": ({"enabled": True, "languages": ["python"]} if code
                                               else {"enabled": False}),
                         "research_corpus": {"enabled": False}},
        "policies": policies,
        "systems": {name: {"status": "absent", "reason": "a fixture"}
                    for name in schema["properties"]["systems"]["required"]},
    }
    if register is not None:
        document["decision_register"] = register
    return yaml.safe_dump(document, sort_keys=False)


# --------------------------------------------------------------------------
# The fixture: one decision change touching all five kinds through both graphs
# --------------------------------------------------------------------------

# The changed decision and what links it, one hop away (edges both ways):
CHANGED = "DEC-001"
SPEC = "SPEC-001"           # DEC-001 constrains it                        -> specifications (record)
CAP = "CAP-901"             # depends on DEC-001                           -> specifications (record)
OTHER_DECISION = "DEC-002"  # depends on DEC-001                           -> decisions (record)
TICKET = "PROJ-ab01"        # implements DEC-001                           -> tickets (record)
TEST_RECORD = "TR-0001"     # tests DEC-001                                -> tests (record)
SYMBOL = "w37_apply"        # DEC-001 constrains it by name (G-16)         -> code (code)
# Two hops away:
FAR_SPEC = "SPEC-002"       # depends on SPEC-001
# Linked to nothing the change reaches:
UNRELATED = ("SPEC-099", "DEC-099", "PROJ-zz99", "TR-0099")
# A decision with many links, to show that no list is cut short:
WIDE = "DEC-003"
WIDE_SPECS = [f"SPEC-{n:03d}" for n in range(101, 131)]
WIDE_TICKETS = [f"PROJ-w{n:03d}" for n in range(101, 131)]
# A decision nothing links and that links nothing (G-24):
SOLO = "DEC-050"
# A decision that names a symbol nothing calls (G-24's join):
NAMING = "DEC-051"
NAMED_ONLY = "w37_named_only"
# A closed specification (W2-M320) and an open one:
CLOSED_SPEC, OPEN_SPEC = "SPEC-300", "SPEC-301"
# A decision that is an entry of the register (W2-03), and the ticket that implements it:
REGISTER_REL = "records/decision-log.md"
ENTRY_DECISION, ENTRY_TICKET = "DEC-070", "PROJ-ab70"
REGISTER = (
    "# Decision log\n\n"
    f"### {ENTRY_DECISION} — A decision kept in the register\n"
    "- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** a fixture\n"
    "- **Decision:** the fixture's register entry.\n"
)
# A record whose prose mentions a symbol without any edge (the join is by id, not by text):
PROSE = "DEC-060"
# The proposal and the execution records of KPI 2:
CITP, CITE = "CITP-001", "CITE-001"

# The code: helper <- apply <- entry; helper <- orphan; apply <- the test; named_only alone.
CODE_REL, TEST_REL = "app/flow.py", "tests/test_flow.py"
HELPER, ENTRY, ORPHAN, TEST_FUNCTION = "w37_helper", "w37_entry", "w37_orphan", "test_w37_apply"
CODE = (
    f"def {HELPER}(value):\n    return value + 1\n\n\n"
    f"def {SYMBOL}(value):\n    return {HELPER}(value) * 2\n\n\n"
    f"def {ENTRY}(value):\n    return {SYMBOL}(value) - 3\n\n\n"
    f"def {ORPHAN}(value):\n    return {HELPER}(value) + 5\n\n\n"
    f"def {NAMED_ONLY}(value):\n    return value * 7\n"
)
TEST_CODE = (
    f"from app.flow import {SYMBOL}\n\n\n"
    f"def {TEST_FUNCTION}():\n    assert {SYMBOL}(1) == 4\n"
)
CALLERS = {HELPER: [SYMBOL, ORPHAN], SYMBOL: [ENTRY, TEST_FUNCTION], ENTRY: [], ORPHAN: [], NAMED_ONLY: []}


def record_files():
    """``path -> text`` of the fixture's records."""
    files = {
        f"docs/adr/{CHANGED}.md": decision(CHANGED, constrains=[SPEC, SYMBOL]),
        f"docs/specs/{SPEC}.md": specification(SPEC),
        f"docs/specs/{FAR_SPEC}.md": specification(FAR_SPEC, depends_on=[SPEC]),
        f"docs/contract/{CAP}.md": capability(CAP, depends_on=[CHANGED]),
        f"docs/adr/{OTHER_DECISION}.md": decision(OTHER_DECISION, depends_on=[CHANGED]),
        f".tickets/{TICKET}.md": ticket(TICKET, implements=[CHANGED]),
        f"docs/evidence/{TEST_RECORD}.md": evidence(TEST_RECORD, tests=[CHANGED]),
        f"docs/specs/{UNRELATED[0]}.md": specification(UNRELATED[0]),
        f"docs/adr/{UNRELATED[1]}.md": decision(UNRELATED[1], constrains=[UNRELATED[0]]),
        f".tickets/{UNRELATED[2]}.md": ticket(UNRELATED[2], implements=[UNRELATED[1]]),
        f"docs/evidence/{UNRELATED[3]}.md": evidence(UNRELATED[3], tests=[UNRELATED[0]]),
        f"docs/adr/{WIDE}.md": decision(WIDE),
        f"docs/adr/{SOLO}.md": decision(SOLO),
        f"docs/adr/{NAMING}.md": decision(NAMING, constrains=[NAMED_ONLY]),
        f"docs/specs/{CLOSED_SPEC}.md": specification(CLOSED_SPEC, status=CLOSED),
        f"docs/specs/{OPEN_SPEC}.md": specification(OPEN_SPEC, status="DRAFT"),
        f".tickets/{ENTRY_TICKET}.md": ticket(ENTRY_TICKET, implements=[ENTRY_DECISION]),
        f"docs/adr/{PROSE}.md": decision(PROSE, body=f"We might one day remove {ORPHAN} and {NAMED_ONLY}."),
    }
    for spec_id in WIDE_SPECS:
        files[f"docs/specs/{spec_id}.md"] = specification(spec_id, depends_on=[WIDE])
    for ticket_id in WIDE_TICKETS:
        files[f".tickets/{ticket_id}.md"] = ticket(ticket_id, implements=[WIDE])
    return files


def build_fixture(root, code=False):
    """The fixture repository, committed. ``code`` adds the code, its test and the gitleaks rules the index needs."""
    project = Project(root)
    project.write(".gitignore", ".gov-runtime/\n")
    project.write("README.md", "# A project\n\nNo frontmatter here.\n")
    project.write(PATH_MAP_REL, path_map(register=REGISTER_REL))
    project.write(REGISTER_REL, REGISTER)
    for rel, text in sorted(record_files().items()):
        project.write(rel, text)
    if code:
        project.write(".gitleaks.toml", GITLEAKS_TEMPLATE.read_text(encoding="utf-8"))
        project.write(CODE_REL, CODE)
        project.write("app/__init__.py", "")
        project.write(TEST_REL, TEST_CODE)
    project.commit("fixture")
    return project.root


# --------------------------------------------------------------------------
# W2-M150: which paths are governance is the path map's to say
# --------------------------------------------------------------------------

UNUSUAL_REL, USUAL_REL = "policy/DEC-010.md", "governance/notes/DEC-011.md"
UNUSUAL, USUAL = "DEC-010", "DEC-011"


def governance_project(root, swapped=False):
    """A project whose path map puts ``policy/**`` in governance memory and ``governance/notes/**`` in product
    memory (``swapped``: the other way round). Each holds one decision, and a ticket implements each."""
    policy, notes = ("product", "governance") if swapped else ("governance", "product")
    project = Project(root)
    project.write(".gitignore", ".gov-runtime/\n")
    project.write(PATH_MAP_REL, path_map({
        "rules": (["policy/**"], policy),
        "notes": (["governance/notes/**"], notes),
        "rest": ([".gitignore", "governance/project/**", ".tickets/**"], "governance"),
    }, code=False))
    project.write(UNUSUAL_REL, decision(UNUSUAL))
    project.write(USUAL_REL, decision(USUAL))
    project.write(".tickets/PROJ-gv10.md", ticket("PROJ-gv10", implements=[UNUSUAL]))
    project.write(".tickets/PROJ-gv11.md", ticket("PROJ-gv11", implements=[USUAL]))
    project.commit("governance fixture")
    return project.root


# --------------------------------------------------------------------------
# CIT-P and CIT-E record files (KPI 2)
# --------------------------------------------------------------------------

PROPOSED = {
    "specifications": [SPEC, CAP],
    "decisions": [OTHER_DECISION],
    "tickets": [TICKET],
    "tests": [TEST_RECORD],
    "code": [SYMBOL],
}


def proposal_file(record_id=CITP, affected=None, change=(CHANGED,)):
    return frontmatter({"id": record_id, "type": CITP_TYPE, "status": "ACCEPTED", "state_class": "EVIDENCE",
                        "change": list(change), "radius": "R2", "depth": 3,
                        "affected": affected if affected is not None else PROPOSED},
                       title=f"{record_id}: the impact of changing {', '.join(change)}")


def execution_file(record_id=CITE, proposal=CITP, affected=None, **extra):
    fields = {"id": record_id, "type": CITE_TYPE, "status": "APPLIED", "state_class": "EVIDENCE"}
    if proposal is not None:
        fields["proposal"] = proposal
    if affected is not False:
        fields["affected"] = affected if affected is not None else PROPOSED
    fields.update(extra)
    return frontmatter(fields, title=f"{record_id}: what the change did")


def read_frontmatter(path):
    text = Path(path).read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    end = text.index("\n---", 4)
    found = yaml.safe_load(text[4:end])
    assert isinstance(found, dict), f"{path}'s frontmatter is not a map"
    return found, text


def check_frontmatter(found, type_name):
    """The shared frontmatter (common.schema.json) and the record type's own constant."""
    schema = json.loads((SCHEMAS / f"{type_name}.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["type"]["const"] == type_name
    for key in ("id", "type", "status", "state_class"):
        assert key in found, f"the {type_name} has no `{key}`: {found!r}"
    assert found["type"] == type_name, f"`type` is {found['type']!r}, not {type_name!r}"
    assert isinstance(found["id"], str) and DOCUMENT_ID.match(found["id"]), f"`id` {found['id']!r} is no document id"
    assert isinstance(found["status"], str) and found["status"], f"`status` is empty: {found!r}"
    assert found["state_class"] in STATE_CLASSES, f"`state_class` {found['state_class']!r} is no state class"


# --------------------------------------------------------------------------
# The code tool's daemon folders, removed at the end of the session (as W1-20 does)
# --------------------------------------------------------------------------

def remove_daemon_dirs(box, roots):
    folder = f"cbm-daemon-{os.getuid()}"
    for root in sorted(roots):
        try:
            path = Path(call("gov.codeintel", "daemon_dir", root, box))
            if path.is_symlink() or not path.is_dir() or os.listdir(path) not in ([], [folder]):
                continue
            inside = list(os.scandir(path / folder)) if (path / folder).is_dir() else []
            if (path / folder).is_symlink() or any(not entry.is_file(follow_symlinks=False) for entry in inside):
                continue
            for entry in inside:
                os.unlink(entry.path)
            if (path / folder).is_dir():
                (path / folder).rmdir()
            path.rmdir()
        except (AssertionError, OSError, subprocess.TimeoutExpired):
            continue
