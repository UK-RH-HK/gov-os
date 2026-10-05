"""Support code for the W1-14 acceptance tests (the proposal-to-ticket bridge).

The tests use public interfaces and nothing else:

- the bridge: ``gov.tasks.bridge.derive(root, change)`` (README, "The interface the tests assume"; package DP-1);
- ``gov.tasks.ready`` and ``gov.tasks.blocked`` (W1-09) and ``gov.store.load`` (W1-10), to show that a derived
  ticket is one the READY rule can use.

How they run:

- **Nothing is written in this worktree** (DEC-322). Every project is a temporary git repository with its own
  ``.tickets/``, its own copy of the vendored ticket script, and its own ``openspec/`` folder (a copy of
  ``template/openspec/``, as an adopted project holds it).
- **Every call runs in a new Python process**, with this worktree's ``src/`` on ``PYTHONPATH`` and an environment
  built from scratch: ``GOV_ROLE`` and ``GOV_TICKET`` of the session that runs the tests are not passed on, and
  ``PATH`` holds no ``tk`` of this machine.
- **This file imports no other suite's helpers.** What it shares with ``w1_09_support`` and ``w1_13_support`` is
  copied here.

Everything a decision package of ``README.md`` could change is named once, in the block below, and the format of
a task is written by one function, ``tasks_md``.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
TEMPLATE_OPENSPEC = REPO_ROOT / "template" / "openspec"
TEMPLATES = TEMPLATE_OPENSPEC / "schemas" / "feature-readiness" / "templates"
SCHEMAS = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"   # ticket.schema.json (W1-08)
VENDORED_TK = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
PROJECT_TK_REL = "governance/kernel/bin/tk"   # where an adopted project holds the script (ADR-0002 section 5)
TICKETS_REL = ".tickets"
CLAIMS_REL = ".tickets/.claims"
CHANGES_REL = "openspec/changes"
CALL_TIMEOUT_S = 120.0

# --- DP-1 (recommended option): the public interface ---------------------------------------------------------------
BRIDGE_MODULE, DERIVE_FUNCTION = "gov.tasks.bridge", "derive"   # derive(root, change), change = the folder name
KEY_CHANGE, KEY_SPECIFICATION, KEY_TICKETS = "change", "specification", "tickets"   # keys of the returned map
KEY_TASK, KEY_TICKET = "task", "ticket"                         # keys of each entry of ``tickets``
TASKS_INVALID = "TASKS_INVALID"                                 # GovError code: a task cannot become a ticket
KEY_INVALID = "invalid"                                         # error.details.invalid: [{"task": "1.2", ...}]

# --- DP-3 (recommended option): the specification must be closed ---------------------------------------------------
SPEC_NOT_CLOSED = "SPEC_NOT_CLOSED"                             # the code ``gov.readiness`` and the READY rule give
STATUS_OPEN, STATUS_CLOSED = "DRAFT", "CLOSED"                  # DEC-307

# --- DP-2 and DP-4 (recommended options): what a task carries ------------------------------------------------------
TASK_DEPENDS = "depends_on"                                     # task numbers of this file, or ids of tickets
FENCE = "```"

# --- settled by the sources -----------------------------------------------------------------------------------------
BACK_REFERENCE = "specification"                                # DEC-307: the key the READY rule reads
ENGINEER, TEST_DESIGNER = "engineer", "independent-test-designer"
ACCEPTANCE = "tests/acceptance"

# Reason codes of ``gov.tasks.blocked`` (W1-09).
DEPENDENCY_OPEN, NO_ACCEPTANCE_TESTS = "DEPENDENCY_OPEN", "NO_ACCEPTANCE_TESTS"

SPEC, CHANGE = "SPEC-zq14", "zq14-sample-feature"
OTHER_SPEC, OTHER_CHANGE = "SPEC-zq15", "zq15-other-feature"


# --------------------------------------------------------------------------
# Calling a public function in a new process
# --------------------------------------------------------------------------

_DRIVER = '''\
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())
try:
    function = getattr(importlib.import_module(request["module"]), request["function"])
except ModuleNotFoundError as exc:
    if exc.name != request["module"]:
        raise
    print(json.dumps({"missing": f"no module {exc.name}"}))
    sys.exit(0)
except AttributeError:
    print(json.dumps({"missing": f"{request['module']} has no function {request['function']}"}))
    sys.exit(0)
try:
    print(json.dumps({"value": function(Path(request["root"]), *request["args"])}, default=str))
except Exception as exc:
    if type(exc).__name__ == "GovError":
        print(json.dumps({"error": {"code": exc.code, "message": str(exc.message), "details": exc.details}},
                         default=str))
    else:
        print(json.dumps({"exception": f"{type(exc).__name__}: {exc}"}))
'''


@dataclass(frozen=True)
class Outcome:
    """What one call gave: a value, a GovError, any other exception, or "the function does not exist"."""
    value: object = None
    error: dict | None = None
    exception: str | None = None
    missing: str | None = None

    @property
    def ok(self):
        return self.error is None and self.exception is None and self.missing is None

    def describe(self):
        if self.missing:
            return f"missing: {self.missing}"
        if self.exception:
            return f"exception: {self.exception}"
        return f"GovError: {self.error!r}" if self.error else f"value: {self.value!r}"


def path_without_tk():
    """``PATH`` without any folder that holds a ``tk``: nothing may lean on the script installed on this machine."""
    folders = [folder for folder in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
               if folder and not (Path(folder) / "tk").exists()]
    return os.pathsep.join(folders)


class Driver:
    """Calls one function of this worktree's ``src/`` in a new process, with an environment built from scratch."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.script = self.workdir / "driver.py"
        self.script.write_text(_DRIVER, encoding="utf-8")

    def environment(self):
        return {
            "PATH": path_without_tk(),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
        }

    def attempt(self, module, function, root, *args):
        request = json.dumps({"module": module, "function": function, "root": str(root), "args": list(args)})
        what = f"{module}.{function}{args!r}"
        try:
            done = subprocess.run([sys.executable, str(self.script)], input=request, capture_output=True, text=True,
                                  env=self.environment(), cwd=str(self.workdir), timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr}"
        try:
            answer = json.loads(done.stdout.strip().split("\n")[-1])
        except ValueError:
            raise AssertionError(f"{what} did not return a JSON value:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(answer.get("value"), answer.get("error"), answer.get("exception"), answer.get("missing"))

    def call(self, module, function, root, *args):
        outcome = self.attempt(module, function, root, *args)
        assert outcome.ok, f"{module}.{function}{args!r} did not return a value ({outcome.describe()})"
        return outcome.value


# --------------------------------------------------------------------------
# git and files
# --------------------------------------------------------------------------

FIXED_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-14 tests", "GIT_AUTHOR_EMAIL": "w1-14@example.invalid",
        "GIT_COMMITTER_NAME": "W1-14 tests", "GIT_COMMITTER_EMAIL": "w1-14@example.invalid",
        "GIT_AUTHOR_DATE": FIXED_DATE, "GIT_COMMITTER_DATE": FIXED_DATE,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def tree(root, skip=(".git", ".gov-runtime")):
    """``relative path -> content`` of everything under ``root`` (a folder is ``<dir>``, a link ``-> target``)."""
    root = Path(root)
    found = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel.split("/")[0] in skip:
            continue
        if path.is_symlink():
            found[rel] = f"-> {os.readlink(path)}"
        elif path.is_dir():
            found[rel] = "<dir>"
        else:
            found[rel] = path.read_bytes()
    return found


def front_of(path):
    """The frontmatter map of a Markdown file."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    assert lines[0] == "---" and "---" in lines[1:], f"{path} has no frontmatter"
    front = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    assert isinstance(front, dict), f"{path} has no frontmatter map"
    return front


# --------------------------------------------------------------------------
# The fixtures' own files: a specification record, its rows, tasks.md, a ticket written by hand
# --------------------------------------------------------------------------

def complete_rows():
    """The rows of W1-12's record template, all 26 PRESENT with evidence: no profile has a row open."""
    rows = yaml.safe_load((TEMPLATES / "readiness.yaml").read_text(encoding="utf-8"))["rows"]
    assert len(rows) == 26, "W1-12's readiness.yaml template does not have 26 rows"
    rows = copy.deepcopy(rows)
    for row in rows:
        row.update(state="PRESENT", evidence=["DEC-085"])
    return rows


def open_rows(number=1):
    """``complete_rows`` with one row MISSING. Row 1 (intent) is mandatory in every profile (DEC-085)."""
    rows = complete_rows()
    for row in rows:
        if row["n"] == number:
            row.update(state="MISSING", evidence=[])
    return rows


def proposal_text(spec_id, status, profile, spine, capability_types):
    """A ``proposal.md`` whose frontmatter is the specification record (DEC-350)."""
    front = {"id": spec_id, "type": "specification", "status": status, "state_class": "AUTHORITATIVE",
             "title": f"Specification {spec_id}", "profile": profile, "spine": spine,
             "capability_types": list(capability_types)}
    return ("---\n" + yaml.safe_dump(front, sort_keys=False).rstrip("\n")
            + "\n---\n# Proposal\n\n## Why\n\nA fixture of the W1-14 acceptance tests.\n")


def task(number, text=None, **changes):
    """One task of ``tasks.md`` as a map: a complete engineer task, with ``changes`` applied (``None`` drops a key).

    ``number`` and ``text`` are the checkbox line (``- [ ] <number> <text>``); every other key goes into the task's
    YAML block.
    """
    slug = number.replace(".", "_")
    fields = {
        "role": ENGINEER,
        "class": "implementation",
        "profile": "STANDARD",
        "allowed_paths": [f"src/feature/part_{slug}/**", f"tests/unit/part_{slug}/**"],
        "kpis": {"success": [f"Part {number} returns the expected output for the sample input"],
                 "failure": [f"Part {number} loses a row of the sample input"]},
    }
    fields.update(changes)
    fields = {key: value for key, value in fields.items() if value is not None}
    return {"number": number, "text": text or f"Build part {number} and verify its unit tests pass", "fields": fields}


def tasks_md(tasks):
    """The text of a ``tasks.md``: W1-12's template (numbered groups, checkbox lines), each task with its YAML block.

    The format (package DP-2): a task is a checkbox line ``- [ ] <number> <description>``; the fenced ``yaml``
    block indented under it, before the next checkbox line or heading, is one map with the task's ``role``,
    ``class``, ``profile``, ``allowed_paths``, ``kpis`` and, optionally, ``depends_on`` and ``inputs``. A task
    whose ``fields`` is empty is written without a block, as the template's own lines are.
    """
    lines, group = ["# Tasks"], None
    for item in tasks:
        head = item["number"].split(".")[0]
        if head != group:
            group = head
            lines += ["", f"## {group}. Group {group}", ""]
        lines.append(f"- [ ] {item['number']} {item['text']}")
        if item["fields"]:
            block = yaml.safe_dump(item["fields"], sort_keys=False, width=1000).rstrip("\n").split("\n")
            lines += [f"  {FENCE}yaml"] + [f"  {line}" for line in block] + [f"  {FENCE}"]
    return "\n".join(lines) + "\n"


def ticket_text(ticket, status="open", deps=(), role=ENGINEER):
    """A ticket written by hand, as this repository's tickets are: tk's own fields, then the task contract."""
    front = {
        "id": ticket, "status": status, "deps": list(deps), "links": [], "created": "2026-09-01T12:00:00Z",
        "type": "task", "priority": 2, "assignee": role, "title": f"Ticket {ticket}", "class": "implementation",
        "state_class": "AUTHORITATIVE", "role": role, "allowed_paths": ["src/existing/**"],
        "kpis": {"success": ["It works"], "failure": ["It does not work"]}, "profile": "STANDARD",
    }
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n# {ticket} A ticket\n\nBody text.\n"


# --------------------------------------------------------------------------
# A temporary project
# --------------------------------------------------------------------------

class Project:
    """A temporary git repository: an adopted project with OpenSpec changes, tickets and its own store."""

    def __init__(self, root, driver):
        self.root = Path(root)
        self.driver = driver
        self.root.mkdir(parents=True, exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        write(self.root, "README.md", "# A project\n")
        write(self.root, ".gitignore", ".gov-runtime/\n")
        shutil.copytree(TEMPLATE_OPENSPEC, self.root / "openspec")
        target = self.root / PROJECT_TK_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(VENDORED_TK, target)
        target.chmod(0o755)
        (self.root / TICKETS_REL).mkdir()
        self.commit()

    # ---- building

    def specification(self, spec_id=SPEC, change=CHANGE, status=STATUS_CLOSED, profile="STANDARD", spine=False,
                      capability_types=("backend",), rows=None):
        """A change folder with its specification record and readiness record: closed and complete by default."""
        folder = f"{CHANGES_REL}/{change}"
        write(self.root, f"{folder}/.openspec.yaml", "schema: feature-readiness\n")
        write(self.root, f"{folder}/proposal.md", proposal_text(spec_id, status, profile, spine, capability_types))
        rows = complete_rows() if rows is None else rows
        write(self.root, f"{folder}/readiness.yaml",
              "# Feature-readiness record.\n" + yaml.safe_dump({"rows": rows}, sort_keys=False))
        return spec_id

    def tasks(self, tasks, change=CHANGE):
        """(Re)write the change's ``tasks.md``; ``tasks`` is a list of ``task(...)`` maps, or the file's text."""
        text = tasks if isinstance(tasks, str) else tasks_md(tasks)
        return write(self.root, f"{CHANGES_REL}/{change}/tasks.md", text)

    def change(self, tasks, **specification):
        """A closed specification and its ``tasks.md``."""
        self.specification(**specification)
        self.tasks(tasks, specification.get("change", CHANGE))

    def set_specification_status(self, status, change=CHANGE):
        path = self.root / CHANGES_REL / change / "proposal.md"
        text, count = re.subn(r"^status: .*$", f"status: {status}", path.read_text(encoding="utf-8"), count=1,
                              flags=re.MULTILINE)
        assert count == 1, f"{path} has no status line"
        path.write_text(text, encoding="utf-8")

    def existing_ticket(self, ticket, **keys):
        """A ticket that was in ``.tickets/`` before the bridge ran."""
        write(self.root, f"{TICKETS_REL}/{ticket}.md", ticket_text(ticket, **keys))
        return ticket

    def set_ticket_status(self, ticket, status):
        path = self.root / TICKETS_REL / f"{ticket}.md"
        text, count = re.subn(r"^status: .*$", f"status: {status}", path.read_text(encoding="utf-8"), count=1,
                              flags=re.MULTILINE)
        assert count == 1, f"{path} has no status line"
        path.write_text(text, encoding="utf-8")

    def tests_folder(self, ticket):
        """Create the acceptance tests folder the READY rule looks for (W1-09): the one the ticket names, or its id's."""
        front = self.ticket_front(ticket)
        named = front.get("acceptance_tests")
        rel = (named.get("path") if isinstance(named, dict) else None) \
            or f"{ACCEPTANCE}/{front.get('wbs_id') or ticket}"
        return write(self.root, f"{rel.rstrip('/')}/README.md", "# Acceptance tests\n").parent

    # ---- reading

    def tickets(self):
        """The ids of the tickets in the working tree."""
        return sorted(path.stem for path in (self.root / TICKETS_REL).glob("*.md"))

    def ticket_path(self, ticket):
        return self.root / TICKETS_REL / f"{ticket}.md"

    def ticket_front(self, ticket):
        return front_of(self.ticket_path(ticket))

    def ticket_files(self):
        """``ticket id -> bytes`` of every ticket file."""
        return {path.stem: path.read_bytes() for path in sorted((self.root / TICKETS_REL).glob("*.md"))}

    def tree(self):
        return tree(self.root)

    def head(self):
        return git(self.root, "rev-parse", "HEAD").strip()

    # ---- state

    def commit(self):
        """Commit everything except the claims; no commit is made when nothing changed."""
        has_head = bool(git(self.root, "rev-parse", "-q", "--verify", "HEAD", check=False).strip())
        if has_head and not git(self.root, "status", "--porcelain").strip():
            return
        git(self.root, "add", "-A", "--", ".", f":!{CLAIMS_REL}")
        git(self.root, "commit", "-q", "--allow-empty", "-m", "fixture")

    def settle(self):
        """Commit everything except the claims, and load the store: what the READY rule reads records from."""
        self.commit()
        self.driver.call("gov.store", "load", self.root)

    # ---- calling

    def derive(self, change=CHANGE):
        """``gov.tasks.bridge.derive(root, change)`` in a new process, on the committed project; an ``Outcome``."""
        self.commit()
        outcome = self.driver.attempt(BRIDGE_MODULE, DERIVE_FUNCTION, self.root, change)
        assert outcome.missing is None, f"{BRIDGE_MODULE}.{DERIVE_FUNCTION} does not exist ({outcome.missing})"
        return outcome

    def derived(self, change=CHANGE):
        """Derive, expecting success: ``task number -> ticket id``, in the order of ``tasks.md``."""
        return tickets_of(self.derive(change), self)

    def queue(self):
        """``(ready, blocked)`` of ``gov.tasks`` on the settled project."""
        self.settle()
        ready = self.driver.call("gov.tasks", "ready", self.root)
        blocked = self.driver.call("gov.tasks", "blocked", self.root)
        return sorted(ready), {ticket: sorted(reasons) for ticket, reasons in blocked.items()}


# --------------------------------------------------------------------------
# Reading what the bridge answered
# --------------------------------------------------------------------------

def tickets_of(outcome, project):
    """``task number -> ticket id`` of a successful derivation; every id names a ticket file of the project."""
    assert outcome.ok, f"the derivation was expected to succeed ({outcome.describe()})"
    value = outcome.value
    assert isinstance(value, dict) and isinstance(value.get(KEY_TICKETS), list), \
        f"derive did not return a map with a list under '{KEY_TICKETS}': {value!r}"
    found = {}
    for entry in value[KEY_TICKETS]:
        assert isinstance(entry, dict) and isinstance(entry.get(KEY_TASK), str) \
            and isinstance(entry.get(KEY_TICKET), str), \
            f"an entry of '{KEY_TICKETS}' is not {{'{KEY_TASK}': <number>, '{KEY_TICKET}': <id>}}: {entry!r}"
        assert entry[KEY_TASK] not in found, f"the task {entry[KEY_TASK]} is listed twice: {value!r}"
        assert project.ticket_path(entry[KEY_TICKET]).is_file(), \
            f"the task {entry[KEY_TASK]} names the ticket {entry[KEY_TICKET]}, which is not in {TICKETS_REL}/"
        found[entry[KEY_TASK]] = entry[KEY_TICKET]
    assert len(set(found.values())) == len(found), f"two tasks share one ticket: {found!r}"
    return found


def refused(outcome, code=None):
    """The derivation was refused with a ``GovError`` (never a raw exception); its error map."""
    assert outcome.exception is None, f"the bridge raised a raw exception, not a GovError ({outcome.describe()})"
    assert outcome.error is not None, f"the derivation was expected to be refused ({outcome.describe()})"
    if code is not None:
        assert outcome.error["code"] == code, f"expected the GovError code {code} ({outcome.describe()})"
    return outcome.error


def invalid_tasks(outcome):
    """The task numbers a ``TASKS_INVALID`` refusal names in ``error.details.invalid``."""
    error = refused(outcome, TASKS_INVALID)
    invalid = error["details"].get(KEY_INVALID) if isinstance(error.get("details"), dict) else None
    assert isinstance(invalid, list) and invalid and all(
        isinstance(entry, dict) and isinstance(entry.get(KEY_TASK), str) for entry in invalid), \
        f"error.details.{KEY_INVALID} is not a non-empty list of maps with '{KEY_TASK}': {error!r}"
    return sorted({entry[KEY_TASK] for entry in invalid})


def refused_and_nothing_written(project, before, outcome, code=None):
    """Refused, and the project's files are what they were: no ticket, whole or partial, was left behind."""
    error = refused(outcome, code)
    assert project.tree() == before, \
        f"the refused derivation changed the project: tickets now {project.tickets()} ({outcome.describe()})"
    return error


# --------------------------------------------------------------------------
# The ticket schema (W1-08) and the DAG
# --------------------------------------------------------------------------

def _schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def schema_faults(front):
    """Why ``front`` does not pass ``ticket.schema.json``; an empty list when it passes.

    The schema's ``required`` lists and the shapes of the task contract are always checked by hand, from the schema
    files as they are now. When the ``jsonschema`` library can be imported, the whole schema is applied as well.
    """
    ticket, common = _schema("ticket.schema.json"), _schema("common.schema.json")
    defs = common["$defs"]
    front = json.loads(json.dumps(front, default=str))   # dates as tk writes them become strings
    faults = [f"the required key '{key}' is absent"
              for key in [*defs["frontmatter"]["required"], *ticket["required"]] if key not in front]
    if not re.match(defs["ticket_id"]["pattern"], str(front.get("id", ""))):
        faults.append(f"id {front.get('id')!r} is not a ticket id")
    if front.get("state_class") not in defs["state_class"]["enum"]:
        faults.append(f"state_class {front.get('state_class')!r} is not a state class")
    paths, kpis = front.get("allowed_paths"), front.get("kpis")
    if not (isinstance(paths, list) and paths and all(isinstance(item, str) and item for item in paths)):
        faults.append("allowed_paths is not a non-empty list of non-empty strings")
    if not (isinstance(kpis, dict) and isinstance(kpis.get("success"), list) and kpis["success"]
            and isinstance(kpis.get("failure"), list)
            and all(isinstance(item, str) and item for item in kpis["success"] + kpis["failure"])):
        faults.append("kpis is not {success: [at least one line], failure: [lines]}")
    if "profile" in front and front["profile"] not in ticket["properties"]["profile"]["enum"]:
        faults.append(f"profile {front['profile']!r} is not a profile")
    deps = front.get("deps", [])
    if not (isinstance(deps, list) and all(isinstance(dep, str) and re.match(defs["ticket_id"]["pattern"], dep)
                                           for dep in deps)):
        faults.append(f"deps {deps!r} is not a list of ticket ids")
    try:
        import jsonschema
    except ImportError:
        return faults
    base = SCHEMAS.as_uri() + "/"
    resolver = jsonschema.RefResolver(base_uri=base + "ticket.schema.json", referrer=ticket,
                                      store={base + "common.schema.json": common})
    validator = jsonschema.Draft202012Validator(ticket, resolver=resolver)
    return faults + [f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
                     for error in validator.iter_errors(front)]


def graph(project):
    """``ticket id -> deps`` of every ticket of the project, as the READY rule reads them (``deps``, W1-09)."""
    found = {}
    for ticket in project.tickets():
        deps = project.ticket_front(ticket).get("deps") or []
        assert isinstance(deps, list), f"{ticket}: deps is not a list: {deps!r}"
        found[ticket] = [str(dep) for dep in deps]
    return found


def dag_faults(edges):
    """Why ``edges`` is not a DAG over its own tickets: dangling edges and cycles; an empty list when it is one."""
    faults = [f"{ticket} depends on {dep}, which is no ticket" for ticket, deps in edges.items()
              for dep in deps if dep not in edges]
    state = {}

    def visit(ticket, trail):
        if state.get(ticket) == "done" or ticket not in edges:
            return
        if state.get(ticket) == "open":
            faults.append("cycle: " + " -> ".join(trail[trail.index(ticket):] + [ticket]))
            return
        state[ticket] = "open"
        for dep in edges[ticket]:
            visit(dep, trail + [ticket])
        state[ticket] = "done"

    for ticket in sorted(edges):
        visit(ticket, [])
    return faults
