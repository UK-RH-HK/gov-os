"""Support code for the W1-13 acceptance tests (``gov readiness``).

The tests use two public interfaces and nothing else:

- the ``gov readiness`` command line: its arguments, its API-0002 envelope, its exit code, and what it leaves in
  the project (nothing: it is a read command, CAP-27);
- public functions of packages: ``gov.readiness.close`` (package DP-2), ``gov.tasks.ready`` and
  ``gov.tasks.blocked`` (W1-09) and ``gov.store.load`` (W1-10).

How they run:

- **Nothing is written in this worktree** (DEC-322). Every project is a temporary git repository with its own
  ``.tickets/``, its own copy of the vendored ticket script, its own ``openspec/`` folder (a copy of
  ``template/openspec/``, as an adopted project holds it) and its own store.
- **The code under test is this worktree's ``src/``**, through W1-07's console-script stand-in
  (``w1_07_support.run_gov_with_code``) and through a small driver that calls one function in a new process.
- **Before a command or a function runs, the project is committed and its store is loaded**
  (``gov.store.load``), so the checker may read from the working tree or from the record graph.
- **Expected rows come from** ``docs/contract/readiness-dimensions.yaml`` **at test time**, never from a copy.

Everything a decision package of ``README.md`` could change is named once, in the block below.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _name in ("W1-07", "W1-09"):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_07_support as cli_support  # noqa: E402  the ``gov`` console script, without an install
import w1_09_support as tasks_support  # noqa: E402  temporary git projects, ticket and record files

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
SOURCE_REL = "docs/contract/readiness-dimensions.yaml"
TEMPLATE_OPENSPEC = REPO_ROOT / "template" / "openspec"
RECORD_TEMPLATE = TEMPLATE_OPENSPEC / "schemas" / "feature-readiness" / "templates" / "readiness.yaml"
NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED
COMMAND = "readiness"

# --- DP-3 (recommended option): the specification as a record ------------------------------------------------------
# A specification is the Markdown record of its OpenSpec change (DEC-307: "a record id"; the store loads Markdown
# files with ``id``, ``type`` and ``status``). The readiness record is the ``readiness.yaml`` of the same folder
# (DEC-305). The record's frontmatter declares the profile, whether it is a spine, and its capability types.
CHANGES_REL = "openspec/changes"
SPEC_RECORD_NAME = "proposal.md"
READINESS_NAME = "readiness.yaml"
SPEC_TYPE = "specification"
STATUS_OPEN, STATUS_CLOSED = "DRAFT", "CLOSED"       # DEC-307: closed is the status ``CLOSED``, anything else is not
KEY_PROFILE, KEY_SPINE, KEY_CAPABILITY_TYPES = "profile", "spine", "capability_types"

# --- DP-4 (recommended option): arguments, report keys, error codes, exit codes -------------------------------------
ARG_SPECIFICATION, ARG_TICKET = "--specification", "--ticket"
KEY_SPECIFICATION, KEY_REPORT_PROFILE, KEY_CLOSED, KEY_OPEN = "specification", "profile", "closed", "open"
ROW_N, ROW_KEY, ROW_STATE, ROW_GAP = "n", "key", "state", "gap_ticket"
UNLINKED = "UNLINKED"                                # the KPI's own word (DEC-089)
SPEC_NOT_CLOSED = "SPEC_NOT_CLOSED"                  # the reason code the READY rule already gives (W1-09)
READINESS_INVALID = "READINESS_INVALID"
KEY_INVALID = "invalid"                              # error.details.invalid: the rejected rows, each with ``n``
EXIT_OPEN = 3                                        # API-0002: "verification failed / unhealthy"
EXIT_INVALID = 1                                     # API-0002: governance error

# --- DP-2 (recommended option): closing a specification -------------------------------------------------------------
READINESS_MODULE, CLOSE_FUNCTION = "gov.readiness", "close"
KEY_AUDIT_TICKET = "audit_ticket"
AUDIT_ROLE, AUDIT_CLASS = "independent-auditor", "audit"   # as the one audit ticket of this repository (W1-43)

SPEC, CHANGE = "SPEC-zq13", "zq13-sample-feature"
OTHER_SPEC, OTHER_CHANGE = "SPEC-zq14", "zq14-other-feature"
EVIDENCE = ["DEC-085"]
CALL_TIMEOUT_S = 120.0


# --------------------------------------------------------------------------
# The source of truth: rows, states and what each profile requires
# --------------------------------------------------------------------------

def source():
    """``docs/contract/readiness-dimensions.yaml`` as it is now."""
    return yaml.safe_load((REPO_ROOT / SOURCE_REL).read_text(encoding="utf-8"))


def row_keys():
    """``n -> key`` of the 26 rows."""
    return {row["n"]: row["key"] for row in source()["dimensions"]}


def required(profile, spine=False, capability_types=()):
    """The row numbers the profile requires (DEC-085): the whole table for FULL and for a spine."""
    doc = source()
    if spine or profile == "FULL":
        return sorted(row_keys())
    rows = set(doc["mandatory_rows"])
    if profile == "STANDARD":
        for name in capability_types:
            rows |= set(doc["capability_types"]["extra_rows_for_standard"][name])
    return sorted(rows)


def not_required(profile, spine=False, capability_types=()):
    return sorted(set(row_keys()) - set(required(profile, spine, capability_types)))


# --------------------------------------------------------------------------
# A readiness record: the rows of W1-12's template, changed by the test
# --------------------------------------------------------------------------

def fresh_rows():
    """The rows of the delivered record template: 26 rows, every one MISSING (DEC-305)."""
    rows = yaml.safe_load(RECORD_TEMPLATE.read_text(encoding="utf-8"))["rows"]
    assert len(rows) == 26 and all(row["state"] == "MISSING" for row in rows), \
        "W1-12's readiness.yaml template is not 26 MISSING rows"
    return copy.deepcopy(rows)


def edit(rows, numbers, **fields):
    """Set ``fields`` on the rows numbered ``numbers`` (one number or several); the same list, for chaining."""
    wanted = {numbers} if isinstance(numbers, int) else set(numbers)
    found = [row for row in rows if row["n"] in wanted]
    assert len(found) == len(wanted), f"no row numbered {sorted(wanted - {row['n'] for row in found})}"
    for row in found:
        row.update(copy.deepcopy(fields))
    return rows


def satisfy(rows, numbers):
    """Make the rows PRESENT, each citing a decision id."""
    return edit(rows, numbers, state="PRESENT", evidence=list(EVIDENCE))


def complete_rows(profile="FULL", spine=False, capability_types=()):
    """A record whose every required row is PRESENT; every other row stays MISSING."""
    return satisfy(fresh_rows(), required(profile, spine, capability_types))


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
            "PATH": tasks_support.path_without_tk(),   # nothing leans on a ``tk`` installed on this machine
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
# A temporary project
# --------------------------------------------------------------------------

def specification_text(spec_id, status, profile, spine, capability_types):
    lines = [f"id: {spec_id}", f"type: {SPEC_TYPE}", f"status: {status}", "state_class: AUTHORITATIVE",
             f"title: Specification {spec_id}"]
    if profile is not None:
        lines.append(f"{KEY_PROFILE}: {profile}")
    lines.append(f"{KEY_SPINE}: {'true' if spine else 'false'}")
    lines.append(f"{KEY_CAPABILITY_TYPES}: [{', '.join(capability_types)}]")
    return "---\n" + "\n".join(lines) + "\n---\n# Proposal\n\n## Why\n\nA fixture of the W1-13 acceptance tests.\n"


class Project:
    """A temporary git repository: an adopted project with OpenSpec changes, tickets and its own store."""

    def __init__(self, root, driver, tk=True):
        self.root = Path(root)
        self.driver = driver
        self._settled = None
        self.root.mkdir(parents=True, exist_ok=True)
        tasks_support.git(self.root, "init", "-q", "-b", "main")
        tasks_support.write(self.root, "README.md", "# A project\n")
        tasks_support.write(self.root, ".gitignore", ".gov-runtime/\n")
        shutil.copytree(TEMPLATE_OPENSPEC, self.root / "openspec")
        if tk:   # an adopted project holds the kernel's vendored ticket script (ADR-0002 section 5)
            target = self.root / tasks_support.PROJECT_TK_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tasks_support.VENDORED, target)
            target.chmod(0o755)

    # ---- building

    def record_path(self, change=CHANGE):
        return self.root / CHANGES_REL / change / SPEC_RECORD_NAME

    def specification(self, rows, spec_id=SPEC, change=CHANGE, profile="FULL", spine=False, capability_types=(),
                      status=STATUS_OPEN):
        """Write a specification record and its readiness record; ``rows`` is the list under ``rows:``."""
        folder = f"{CHANGES_REL}/{change}"
        tasks_support.write(self.root, f"{folder}/.openspec.yaml", "schema: feature-readiness\n")
        tasks_support.write(self.root, f"{folder}/{SPEC_RECORD_NAME}",
                            specification_text(spec_id, status, profile, spine, capability_types))
        self.rows(rows, change)
        return spec_id

    def rows(self, rows, change=CHANGE):
        """(Re)write the readiness record of a change."""
        text = "# Feature-readiness record.\n" + yaml.safe_dump({"rows": rows}, sort_keys=False)
        return tasks_support.write(self.root, f"{CHANGES_REL}/{change}/{READINESS_NAME}", text)

    def status(self, change=CHANGE):
        """The ``status`` of a specification record, as the working tree holds it."""
        lines = tasks_support.frontmatter_lines(self.record_path(change))
        found = [line.split(":", 1)[1].strip() for line in lines if line.startswith("status:")]
        assert len(found) == 1, f"the specification record has {len(found)} status lines"
        return found[0]

    def ticket(self, ticket, wbs, specification=None, **keys):
        """An open implementation ticket with its acceptance tests folder; ``specification`` is DEC-307's key."""
        if specification is not None:
            keys["specification"] = specification
        tasks_support.write(self.root, f".tickets/{ticket}.md", tasks_support.ticket_text(ticket, wbs, **keys))
        tasks_support.write(self.root, f"tests/acceptance/{wbs}/README.md", f"# {wbs}: acceptance tests\n")
        return ticket

    def tickets(self):
        """The ids of the tickets in the working tree."""
        return sorted(path.stem for path in (self.root / ".tickets").glob("*.md"))

    def ticket_front(self, ticket):
        text = "\n".join(tasks_support.frontmatter_lines(self.root / ".tickets" / f"{ticket}.md"))
        front = yaml.safe_load(text)
        assert isinstance(front, dict), f".tickets/{ticket}.md has no frontmatter map"
        return front

    def ticket_title(self, ticket):
        """The ticket's title: the frontmatter ``title`` and the heading the ticket script writes."""
        lines = (self.root / ".tickets" / f"{ticket}.md").read_text(encoding="utf-8").split("\n")
        headings = [line[2:] for line in lines if line.startswith("# ")]
        return " | ".join([str(self.ticket_front(ticket).get("title", ""))] + headings)

    # ---- state

    def settle(self):
        """Commit everything except the claims, and load the store; nothing happens when nothing changed."""
        head = tasks_support.git(self.root, "rev-parse", "-q", "--verify", "HEAD", check=False).strip()
        dirty = tasks_support.git(self.root, "status", "--porcelain").strip()
        if head and not dirty and head == self._settled:
            return
        tasks_support.git(self.root, "add", "-A", "--", ".", f":!{tasks_support.CLAIMS_REL}")
        tasks_support.git(self.root, "commit", "-q", "--allow-empty", "-m", "fixture")
        self.driver.call("gov.store", "load", self.root)
        self._settled = tasks_support.git(self.root, "rev-parse", "HEAD").strip()

    def state(self):
        """What a command that only reads leaves alone: the files, ``git status`` and the refs."""
        return (cli_support.snapshot(self.root), cli_support.porcelain(self.root), cli_support.git_state(self.root))

    def tree(self):
        return cli_support.snapshot(self.root)

    # ---- calling

    def gov(self, sandbox, *args):
        """``gov <args>`` in this project, settled first, with this worktree's code."""
        self.settle()
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)

    def close(self, spec_id=SPEC):
        """``gov.readiness.close(root, spec_id)`` in a new process, on the settled project; an ``Outcome``."""
        self.settle()
        outcome = self.driver.attempt(READINESS_MODULE, CLOSE_FUNCTION, self.root, spec_id)
        assert outcome.missing is None, \
            f"{READINESS_MODULE}.{CLOSE_FUNCTION} does not exist ({outcome.missing}): package DP-2"
        return outcome

    def queue(self):
        """``(ready, blocked)`` of ``gov.tasks`` on the settled project."""
        self.settle()
        ready = self.driver.call("gov.tasks", "ready", self.root)
        blocked = self.driver.call("gov.tasks", "blocked", self.root)
        return sorted(ready), {ticket: sorted(reasons) for ticket, reasons in blocked.items()}


# --------------------------------------------------------------------------
# Second batch (DEC-136): a change that is no specification record, and the project's own schema
# --------------------------------------------------------------------------

PROPOSAL_TEMPLATE = TEMPLATE_OPENSPEC / "schemas" / "feature-readiness" / "templates" / "proposal.md"
SCHEMA_REL = "openspec/schemas/feature-readiness/schema.yaml"
ARCHIVE_NAME = "archive"                             # ``openspec/changes/archive/``: archived changes, not a change
PROPOSAL_BODY = "# Proposal\n\n## Why\n\nA fixture of the W1-13 acceptance tests.\n"


def frontmatter(spec_id=SPEC, **changes):
    """The frontmatter keys of a readable FULL specification, as a map; ``changes`` replaces a key, ``None`` drops it."""
    keys = {"id": spec_id, "type": SPEC_TYPE, "status": STATUS_OPEN, "state_class": "AUTHORITATIVE",
            "title": f"Specification {spec_id}", KEY_PROFILE: "FULL", KEY_SPINE: False, KEY_CAPABILITY_TYPES: []}
    keys.update(changes)
    return {key: value for key, value in keys.items() if value is not None}


def proposal_text(front):
    """A ``proposal.md``: ``front`` is a map (dumped as YAML), raw text put between the marks, or ``None`` (no marks)."""
    if front is None:
        return PROPOSAL_BODY
    inner = front if isinstance(front, str) else yaml.safe_dump(front, sort_keys=False)
    return "---\n" + inner.rstrip("\n") + "\n---\n" + PROPOSAL_BODY


def write_change(project, change, proposal, rows, parent=CHANGES_REL):
    """A change folder written file by file: ``proposal`` is the text of ``proposal.md``, or ``None`` for no file."""
    folder = f"{parent}/{change}"
    tasks_support.write(project.root, f"{folder}/.openspec.yaml", "schema: feature-readiness\n")
    if proposal is not None:
        tasks_support.write(project.root, f"{folder}/{SPEC_RECORD_NAME}", proposal)
    text = "# Feature-readiness record.\n" + yaml.safe_dump({"rows": rows}, sort_keys=False)
    tasks_support.write(project.root, f"{folder}/{READINESS_NAME}", text)
    return folder


def edit_schema(project, change):
    """Rewrite the project's own copy of the ``feature-readiness`` schema: ``change(schema)`` edits the loaded map."""
    path = project.root / SCHEMA_REL
    schema = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(schema)
    path.write_text(yaml.safe_dump(schema, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return schema


# --------------------------------------------------------------------------
# Reading what the command answered
# --------------------------------------------------------------------------

def select(spec_id=SPEC):
    return (COMMAND, ARG_SPECIFICATION, spec_id, "--json")


def envelope_of(run, interface):
    """The API-0002 envelope of a run of a built ``gov readiness``."""
    envelope = cli_support.assert_envelope(run, interface, command=COMMAND)
    code = (envelope.get("error") or {}).get("code")
    assert code != NOT_IMPLEMENTED, f"gov readiness is reserved and not built yet\n{run.describe()}"
    return envelope


def report_of(run, interface):
    """The report: the envelope's ``result`` when the specification passes, ``error.details`` when it does not."""
    envelope = envelope_of(run, interface)
    report = envelope["result"] if envelope["ok"] else envelope["error"]["details"]
    assert isinstance(report, dict), f"the report is not a map\n{run.describe()}"
    for key in (KEY_SPECIFICATION, KEY_REPORT_PROFILE, KEY_CLOSED, KEY_OPEN):
        assert key in report, f"the report lacks the key {key!r}\n{run.describe()}"
    assert isinstance(report[KEY_CLOSED], bool), f"'{KEY_CLOSED}' is not a boolean\n{run.describe()}"
    assert isinstance(report[KEY_OPEN], list), f"'{KEY_OPEN}' is not a list\n{run.describe()}"
    for row in report[KEY_OPEN]:
        assert isinstance(row, dict), f"an open row is not a map: {row!r}\n{run.describe()}"
        assert type(row.get(ROW_N)) is int, f"an open row has no row number: {row!r}\n{run.describe()}"
        for key in (ROW_KEY, ROW_STATE, ROW_GAP):
            assert isinstance(row.get(key), str) and row[key].strip(), \
                f"the open row {row.get(ROW_N)} has no '{key}': {row!r}\n{run.describe()}"
    return report


def passed(run, interface):
    """Every required row is satisfied: ``ok``, exit code 0, ``closed: true`` and no open row. The report."""
    report = report_of(run, interface)
    assert run.returncode == 0 and report[KEY_CLOSED] is True and report[KEY_OPEN] == [], \
        f"the specification was expected to pass\n{run.describe()}"
    return report


def held(run, interface):
    """Required rows are open: the error ``SPEC_NOT_CLOSED``, exit code 3, ``closed: false``. The report."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False and envelope["error"]["code"] == SPEC_NOT_CLOSED, \
        f"expected the error {SPEC_NOT_CLOSED}\n{run.describe()}"
    assert run.returncode == EXIT_OPEN, f"expected exit code {EXIT_OPEN}\n{run.describe()}"
    report = report_of(run, interface)
    assert report[KEY_CLOSED] is False and report[KEY_OPEN], \
        f"the report of a held specification says closed, or names no open row\n{run.describe()}"
    return report


def rejected(run, interface):
    """The record is invalid: the error ``READINESS_INVALID``, exit code 1. The numbers of the rejected rows."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False and envelope["error"]["code"] == READINESS_INVALID, \
        f"expected the error {READINESS_INVALID}\n{run.describe()}"
    assert run.returncode == EXIT_INVALID, f"expected exit code {EXIT_INVALID}\n{run.describe()}"
    invalid = envelope["error"]["details"].get(KEY_INVALID)
    assert isinstance(invalid, list) and all(isinstance(row, dict) and type(row.get(ROW_N)) is int
                                             for row in invalid), \
        f"error.details.{KEY_INVALID} is not a list of rows with their number\n{run.describe()}"
    return sorted(row[ROW_N] for row in invalid)


def not_passed(run, interface):
    """The specification does not pass, whichever of the two errors says so."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != 0, \
        f"the specification passes, and it must not\n{run.describe()}"
    assert envelope["error"]["details"].get(KEY_CLOSED) is not True, \
        f"the specification is reported closed\n{run.describe()}"
    return envelope["error"]


def unreadable(run, interface, change):
    """A change the checker cannot read as a specification: ``READINESS_INVALID``, exit code 1, the change named."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != 0, \
        f"the command passes over the change {change!r}, which it cannot judge\n{run.describe()}"
    assert envelope["error"]["code"] == READINESS_INVALID, f"expected the error {READINESS_INVALID}\n{run.describe()}"
    assert run.returncode == EXIT_INVALID, f"expected exit code {EXIT_INVALID}\n{run.describe()}"
    assert change in json.dumps(envelope["error"]), f"the error does not name the change {change!r}\n{run.describe()}"
    return envelope["error"]


def open_numbers(report):
    return [row[ROW_N] for row in report[KEY_OPEN]]


def gap_tickets(report):
    """``row number -> gap ticket id or UNLINKED`` of the open rows."""
    return {row[ROW_N]: row[ROW_GAP] for row in report[KEY_OPEN]}
