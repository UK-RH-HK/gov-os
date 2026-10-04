"""Support code for the W1-09 acceptance tests (standard library only).

W1-09 vendors the ticket script and builds the claim lock and the READY rule.
No ``gov`` command belongs to this ticket (``src/gov/cli/**`` is outside its
paths and the registry reserves no claim or ready command), so the tests use
the Python interface of ``gov.tasks``, stated in the README:

- ``claim``, ``release`` and ``holder``;
- ``ready`` and ``blocked``;
- ``create``.

How the tests call it:

- **Every call runs in a new Python process**, through a small driver written to
  a temporary directory, with this worktree's ``src/`` on ``PYTHONPATH``. A
  claim is therefore always read by another process than the one that made it,
  and a race is a race between processes.
- **Nothing is written in this worktree.** Every project is a temporary git
  repository with its own ``.tickets/``, ``.tickets/.claims/`` and
  ``tests/acceptance/<id>/`` folders.
- **The environment is built from scratch:** a ``PATH`` without any folder that
  holds a ``tk``, an empty temporary ``HOME``, ``TMPDIR``, locale,
  ``PYTHONPATH`` and ``PYTHONPYCACHEPREFIX``. ``GOV_ROLE`` and ``GOV_TICKET``
  of the session that runs the tests are not passed on.
- **Before the ready queue is read, the project is committed and the store is
  loaded** (``gov.store.load``), so the rule may read records from the working
  tree or from the record graph. Claims are never committed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
TASKS_MODULE = "gov.tasks"
STORE_MODULE = "gov.store"
INTERFACE = ("claim", "release", "holder", "ready", "blocked", "create")
CALL_TIMEOUT_S = 120.0
MISSING_EXIT = 3

# The vendored ticket script (DEC-074 T3, ADR-0002 section 3).
VENDORED_REL = "template/governance/kernel/bin/tk"
VENDORED = REPO_ROOT / VENDORED_REL
PROJECT_TK_REL = "governance/kernel/bin/tk"   # where an adopted project holds it (ADR-0002 section 5)
TOOL_REGISTRY = REPO_ROOT / "governance" / "project" / "tool-registry.yaml"
TK_VERSION = "v0.3.2"
TK_SHA256 = "408f2c113ecc3bc071507593a78386f1b4cc743be6491c9e9f2627efd4d9902b"

CLAIMS_REL = ".tickets/.claims"

# GovError codes of the interface.
CLAIM_HELD = "CLAIM_HELD"
CLAIM_NOT_HELD = "CLAIM_NOT_HELD"
TICKET_NOT_FOUND = "TICKET_NOT_FOUND"
TICKET_CLOSED = "TICKET_CLOSED"

# Reason codes of ``blocked``.
DEPENDENCY_OPEN = "DEPENDENCY_OPEN"
CLAIMED = "CLAIMED"
NO_ACCEPTANCE_TESTS = "NO_ACCEPTANCE_TESTS"
SPEC_NOT_CLOSED = "SPEC_NOT_CLOSED"
INPUT_ABSENT = "INPUT_ABSENT"
INPUT_SUPERSEDED = "INPUT_SUPERSEDED"
DECISION_OPEN = "DECISION_OPEN"
REASONS = (DEPENDENCY_OPEN, CLAIMED, NO_ACCEPTANCE_TESTS, SPEC_NOT_CLOSED, INPUT_ABSENT, INPUT_SUPERSEDED,
           DECISION_OPEN)

RACE_CONTENDERS = 8
RACE_ROUNDS = 4
RACE_DELAY_S = 1.5

_DRIVER = '''\
import importlib, json, sys, time
from pathlib import Path

request = json.loads(sys.stdin.read())
functions = []
for call in request["calls"]:
    try:
        functions.append(getattr(importlib.import_module(call["module"]), call["function"]))
    except ModuleNotFoundError as exc:
        if exc.name != "gov.tasks":
            raise
        print(f"no module {exc.name}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
time.sleep(max(0.0, request.get("not_before", 0.0) - time.time()))
out = []
for function, call in zip(functions, request["calls"]):
    try:
        out.append({"value": function(Path(call["root"]), *call["args"], **call["kwargs"])})
    except Exception as exc:
        if type(exc).__name__ != "GovError":
            raise
        out.append({"error": {"code": exc.code, "message": str(exc.message), "details": exc.details}})
print(json.dumps(out))
'''


class TasksMissing(AssertionError):
    """``gov.tasks`` does not exist yet."""


@dataclass(frozen=True)
class Outcome:
    """What one call gave: a value, or the GovError it raised."""
    value: object = None
    error: dict | None = None

    @property
    def ok(self):
        return self.error is None

    def describe(self):
        return f"value: {self.value!r}" if self.ok else f"GovError: {self.error!r}"


def assert_error(outcome, code, what):
    """``outcome`` is a GovError with ``code``; its details are returned."""
    assert not outcome.ok, f"{what}: no GovError was raised ({outcome.describe()})"
    assert outcome.error["code"] == code, f"{what}: the GovError code is not {code} ({outcome.describe()})"
    assert isinstance(outcome.error["details"], dict), f"{what}: the GovError has no details map"
    return outcome.error["details"]


def path_without_tk():
    """``PATH`` without any folder that holds a ``tk``: nothing may lean on the script installed on this machine."""
    folders = [folder for folder in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
               if folder and not (Path(folder) / "tk").exists()]
    return os.pathsep.join(folders)


# --------------------------------------------------------------------------
# Calling the public interface
# --------------------------------------------------------------------------

class Api:
    """Calls ``gov.tasks`` (and ``gov.store.load``) of this worktree, each batch in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "requests"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self._requests = 0

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

    def _start(self, calls, not_before=0.0):
        request = {"not_before": not_before,
                   "calls": [{"module": module, "function": function, "root": str(root), "args": list(args),
                              "kwargs": kwargs} for module, function, root, args, kwargs in calls]}
        self._requests += 1
        path = self.workdir / "requests" / f"{self._requests}.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        with path.open(encoding="utf-8") as stdin:
            return subprocess.Popen([sys.executable, str(self.driver)], stdin=stdin, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, env=self.environment(),
                                    cwd=str(self.workdir))

    @staticmethod
    def _finish(process, what):
        try:
            stdout, stderr = process.communicate(timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        if process.returncode == MISSING_EXIT:
            raise TasksMissing(f"the task interface does not exist: {stderr.strip()} under src/")
        assert process.returncode == 0, f"{what} failed (exit code {process.returncode}):\n{stderr}"
        try:
            answers = json.loads(stdout)
        except ValueError:
            raise AssertionError(f"{what} did not return JSON values:\n{stdout}\n{stderr}") from None
        return [Outcome(answer.get("value"), answer.get("error")) for answer in answers]

    def attempt(self, function, root, *args, module=TASKS_MODULE, **kwargs):
        """One call in a new process; an ``Outcome`` (a GovError is an outcome, any other exception fails)."""
        what = f"{module}.{function}{args!r}"
        return self._finish(self._start([(module, function, root, args, kwargs)]), what)[0]

    def call(self, function, root, *args, module=TASKS_MODULE, **kwargs):
        """One call in a new process; its value. A GovError fails the test."""
        outcome = self.attempt(function, root, *args, module=module, **kwargs)
        assert outcome.ok, f"{module}.{function}{args!r} raised a GovError: {outcome.error!r}"
        return outcome.value

    def race(self, function, root, argument_sets):
        """The same function from one new process per argument set, all released at the same moment."""
        not_before = time.time() + RACE_DELAY_S
        processes = [self._start([(TASKS_MODULE, function, root, args, {})], not_before) for args in argument_sets]
        return [self._finish(process, f"{TASKS_MODULE}.{function}{args!r}")[0]
                for process, args in zip(processes, argument_sets)]

    def exists(self):
        """Raise TasksMissing unless every function of the public interface can be imported."""
        source = "import importlib,sys\n" + "".join(
            f"getattr(importlib.import_module({TASKS_MODULE!r}), {name!r})\n" for name in INTERFACE)
        done = subprocess.run([sys.executable, "-c", source], capture_output=True, text=True, cwd=str(self.workdir),
                              env=self.environment())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise TasksMissing(f"the task interface does not exist: {last}")


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
        "GIT_AUTHOR_NAME": "W1-09 tests", "GIT_AUTHOR_EMAIL": "w1-09@example.invalid",
        "GIT_COMMITTER_NAME": "W1-09 tests", "GIT_COMMITTER_EMAIL": "w1-09@example.invalid",
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


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def registry_entry(name):
    """The ``key -> value`` lines of one tool's entry in ``governance/project/tool-registry.yaml``."""
    text = TOOL_REGISTRY.read_text(encoding="utf-8")
    match = re.search(rf"^  - name: {re.escape(name)}\n((?:    .*\n)+)", text, re.MULTILINE)
    assert match, f"the tool registry has no entry named {name}"
    return {key: value.strip().strip('"') for key, value in re.findall(r"^    (\w+): (.*)$", match.group(1),
                                                                        re.MULTILINE)}


def frontmatter_lines(path):
    """The lines of a file's frontmatter, without the two ``---`` lines."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    assert lines[0] == "---" and "---" in lines[1:], f"{path} has no frontmatter"
    return lines[1:lines.index("---", 1)]


# --------------------------------------------------------------------------
# A temporary project
# --------------------------------------------------------------------------

def _yaml_key(key, value):
    if isinstance(value, (list, tuple)):
        return [f"{key}: []"] if not value else [f"{key}:"] + [f"- {item}" for item in value]
    return [f"{key}: {value}"]


def ticket_text(ticket, wbs, status="open", deps=(), depends_on=(), cls="implementation", acceptance=True, **keys):
    """A ticket file as this repository's tickets are written: tk's own fields, then the task contract."""
    lines = [
        f"id: {ticket}", f"status: {status}", f"deps: [{', '.join(deps)}]", "links: []",
        "created: 2026-09-01T12:00:00Z", "type: task", "priority: 2", "assignee: engineer",
    ]
    if wbs:
        lines += [f"external-ref: {wbs}", "tags: [test]", f"wbs_id: {wbs}"]
    lines += [f"title: Ticket {wbs or ticket}", f"class: {cls}", "state_class: AUTHORITATIVE", "role: engineer"]
    lines += _yaml_key("depends_on", list(depends_on))
    lines += ["allowed_paths:", "- src/example/**", "kpis:", "  success:", "  - It works", "  failure:",
              "  - It does not work", "profile: STANDARD", "sources:", "- DEC-000", "est_loc: 10"]
    for key, value in keys.items():
        lines += _yaml_key(key, value)
    if acceptance:
        folder = acceptance if isinstance(acceptance, str) else f"tests/acceptance/{wbs}/"
        lines += ["acceptance_tests:", f"  path: {folder}",
                  "  author: independent-test-designer; written before implementation"]
    return "---\n" + "\n".join(lines) + f"\n---\n# {wbs or ticket} A ticket\n\nBody text.\n"


def record_text(record_id, record_type, status, **keys):
    """A record file: the shared frontmatter (DEC-239), the given keys, and a body."""
    lines = [f"id: {record_id}", f"type: {record_type}", f"status: {status}", "state_class: AUTHORITATIVE",
             f"title: Record {record_id}"]
    for key, value in keys.items():
        lines += _yaml_key(key, value)
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {record_id}\n\nBody text.\n"


class Project:
    """A temporary git repository with tickets, records and acceptance test folders."""

    def __init__(self, root, api):
        self.root = Path(root)
        self.api = api
        self.wbs = {}   # ticket id -> WBS id
        self.root.mkdir(parents=True, exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        write(self.root, "README.md", "# A project\n")
        write(self.root, ".gitignore", ".gov-runtime/\n")
        if VENDORED.is_file():   # an adopted project holds the kernel's vendored script
            target = self.root / PROJECT_TK_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(VENDORED, target)
            target.chmod(0o755)

    # ---- building

    def ticket(self, ticket, wbs, status="open", deps=(), tests=True, **keys):
        """Write a ticket; ``tests`` also creates its acceptance tests folder ``tests/acceptance/<wbs>/``."""
        self.wbs[ticket] = wbs
        depends_on = [self.wbs[dep] for dep in deps if self.wbs.get(dep)]
        write(self.root, f".tickets/{ticket}.md",
              ticket_text(ticket, wbs, status=status, deps=deps, depends_on=depends_on, **keys))
        if tests:
            self.tests_folder(wbs or ticket)
        return ticket

    def tests_folder(self, name):
        return write(self.root, f"tests/acceptance/{name}/README.md", f"# {name}: acceptance tests\n").parent

    def set_status(self, ticket, status):
        path = self.root / ".tickets" / f"{ticket}.md"
        text, count = re.subn(r"^status: .*$", f"status: {status}", path.read_text(encoding="utf-8"), count=1,
                              flags=re.MULTILINE)
        assert count == 1, f"{path} has no status line"
        path.write_text(text, encoding="utf-8")

    def record(self, rel, record_id, record_type, status, **keys):
        return write(self.root, rel, record_text(record_id, record_type, status, **keys))

    def lock(self, ticket):
        return self.root / CLAIMS_REL / ticket

    # ---- calling

    def settle(self):
        """Commit everything except the claims, and load the store."""
        git(self.root, "add", "-A", "--", ".", f":!{CLAIMS_REL}")
        git(self.root, "commit", "-q", "--allow-empty", "-m", "fixture")
        self.api.call("load", self.root, module=STORE_MODULE)

    def claim(self, ticket, holder):
        return self.api.attempt("claim", self.root, ticket, holder)

    def release(self, ticket, holder):
        return self.api.attempt("release", self.root, ticket, holder)

    def holder(self, ticket):
        return self.api.call("holder", self.root, ticket)

    def ready(self, settle=True):
        """The ready queue, sorted; the project is committed and loaded first."""
        if settle:
            self.settle()
        value = self.api.call("ready", self.root)
        assert isinstance(value, list) and all(isinstance(item, str) for item in value), \
            f"ready did not return a list of ticket ids: {value!r}"
        assert len(set(value)) == len(value), f"ready lists a ticket twice: {value!r}"
        return sorted(value)

    def blocked(self, settle=True):
        """``ticket id -> sorted reason codes`` of every ticket that is open and not READY."""
        if settle:
            self.settle()
        value = self.api.call("blocked", self.root)
        assert isinstance(value, dict), f"blocked did not return a map of ticket id to reasons: {value!r}"
        for ticket, reasons in value.items():
            assert isinstance(reasons, list) and reasons, f"blocked gives {ticket} no reason: {reasons!r}"
            unknown = sorted(set(reasons) - set(REASONS))
            assert not unknown, f"blocked gives {ticket} reasons outside the interface: {unknown}"
        return {ticket: sorted(reasons) for ticket, reasons in value.items()}

    def queue(self):
        """``(ready, blocked)`` of one settled state."""
        return self.ready(), self.blocked(settle=False)
