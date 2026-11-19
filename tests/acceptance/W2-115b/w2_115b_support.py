"""Support code for W2-115b's acceptance tests: ``gov queue``, the product's deterministic landing (README).

- **Public interfaces only:** ``python3 -m gov.cli.main queue ... --root <project> --json`` with this worktree's
  ``src/`` on ``PYTHONPATH``, the git state of the planted repository, and the files the queue writes there.
- **Planted projects under pytest's tmp folders:** a small git repository each (a package ``app`` under ``src/``,
  tickets, a test map, the kernel's ticket tool at ``governance/kernel/bin/tk``, an acceptance suite per ticket,
  unit tests that import the package's modules), and work branches with ``Task:`` and ``Role:`` trailers.
- **Telling tests:** every planted test appends one JSON line per run to a file of its own outside the project
  (the tree it ran in, what it saw of the package's modules, whether it passed), unless ``SELF_CHECK`` is set.
- **No network, no model:** the embedding endpoint is a dead local address and its program a stand-in.
"""

from __future__ import annotations

import json
import os
import shutil
import site
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
QUEUE_SRC = SRC / "gov" / "queue"
KERNEL_TK = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
TEST_MAP_SCHEMA = REPO_ROOT / "template" / "governance" / "kernel" / "schemas" / "test-map.schema.json"

TK_REL = "governance/kernel/bin/tk"
TEST_MAP_REL = "governance/project/test-map.yaml"
PATH_MAP_REL = "governance/project/path-map.yaml"
QUEUE_YAML_REL = "governance/project/queue.yaml"
CLONE_REL = ".gov-runtime/close/clone"
QUEUE_RECORD_PREFIX = ".gov-runtime/queue/"
NOTES_REL = "governance/project/notes.yaml"   # outside every ticket's allowed paths; the test map places it nowhere

SELF_CHECK = "W2_115B_SELF_CHECK"   # set only for the fixtures' own plain pytest runs: the telling tests keep quiet
GOV_TIMEOUT_S = 900

EXIT_LANDED, EXIT_REFUSED_TO_RUN, EXIT_NOT_ALL_LANDED = 0, 1, 3
STEPS = ("merge", "selection", "run", "close", "total")
RECORD_KEYS = ("close", "commit", "selection", "runs", "reds", "culprits", "base", "queue")

ENGINEER = ("The Engineer", "engineer@example.invalid")
DESIGNER = ("The Test Designer", "designer@example.invalid")
OWNER = ("The Owner", "owner@example.invalid")
ORCHESTRATOR = ("The Orchestrator", "orchestrator@example.invalid")

# --------------------------------------------------------------------------
# The planted project's tickets and tests
# --------------------------------------------------------------------------


class Ticket:
    """A ticket of the planted project: its id, WBS id, modules (``src/app/<m>.py``), allowed paths and acceptance
    folder. Its suite ``<folder>/test_<slug>.py`` imports and guards its modules (red when one says BROKEN)."""

    def __init__(self, tid, wbs, modules, acceptance=None, extra_allowed=()):
        self.id, self.wbs, self.modules = tid, wbs, list(modules)
        self.slug = wbs.split("-")[1]
        self.acceptance = acceptance or f"tests/acceptance/{wbs}/"
        self.allowed = [module_rel(m) for m in self.modules] + [self.acceptance + "**", *extra_allowed]

    @property
    def suite_file(self):
        return f"{self.acceptance}test_{self.slug}.py"

    @property
    def node(self):
        return f"{self.suite_file}::test_{self.slug}"

    @property
    def ticket_rel(self):
        return f".tickets/{self.id}.md"


def module_rel(module):
    return f"src/app/{module}.py"


A = Ticket("PROJ-aaaa", "F-aa", ["widget", "helper"])
B = Ticket("PROJ-bbbb", "F-bb", ["gadget"])
# G-1's batch (README, "The planted runs": authors)
C = Ticket("PROJ-cccc", "F-cc", ["mod_cc"])
D = Ticket("PROJ-dddd", "F-dd", ["mod_dd"])
E = Ticket("PROJ-eeee", "F-ee", ["mod_ee"])
G = Ticket("PROJ-gggg", "F-gg", ["mod_gg"])
H = Ticket("PROJ-hhhh", "F-hh", ["mod_hh"])
K = Ticket("PROJ-kkkk", "F-kk", ["mod_kk"], acceptance="tests/checks/F-kk/")   # its acceptance path elsewhere
M = Ticket("PROJ-mmmm", "F-mm", ["mod_mm"])   # its suite moves the integration branch during the run

# Unit tests beside the tickets' suites: (file, the module it imports and guards)
USES_WIDGET = ("tests/unit/test_uses_widget.py", "widget")   # a suite that imports A's changed module
USES_HELPER = ("tests/unit/test_uses_helper.py", "helper")   # reached only through the untrailered commit's change
GIZMO = ("tests/unit/test_gizmo.py", "gizmo")                # reached by nothing any case changes
UNIT_TESTS = (USES_WIDGET, USES_HELPER, GIZMO)
KNOWN_RED = "tests/unit/test_known_red.py"                   # red on the base too (imports the widget)


def node(rel, name=None):
    return f"{rel}::{name or 'test_' + Path(rel).stem[5:]}"


USES_WIDGET_NODE = node(USES_WIDGET[0])
KNOWN_RED_NODE = node(KNOWN_RED)

TEST_MAP = {
    "version": 1,
    "shared_core": ["src/app/core/**"],   # nothing lives there: no case changes the shared core
    "record_only": [".tickets/**", "docs/checkpoints/**", "docs/close/**"],
    "record_reading": [],
    "every_close": [],
    "couplings": [],
    "test_inputs": [],
    "per_test_timeout": 120,
}

PATH_MAP = {
    "namespaces": {"all": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "engineer", "independent-test-designer"],
        "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "not embedded",
        "provenance": "written by the W2-115b tests", "deletion_rebuild": "authoritative; restored from git only"}},
}


def readme_text(ticket):
    """The acceptance folder's README: the KPI map ``gov accept`` reads (each of the ticket's two lines on its
    suite's one test), as a real ticket's folder holds it."""
    case = f"`test_{ticket.slug}.py::test_{ticket.slug}`"
    return (f"# {ticket.wbs}\n\n| KPI | tests |\n|---|---|\n| success-1 | {case} |\n| failure-1 | {case} |\n")


def ticket_text(ticket, status="open"):
    lines = [f"id: {ticket.id}", f"status: {status}", "deps: []", "links: []", "created: 2026-11-01T12:00:00Z",
             "type: task", "priority: 2", "assignee: engineer", f"external-ref: {ticket.wbs}",
             f"wbs_id: {ticket.wbs}", f"title: Ticket {ticket.wbs}", "class: implementation",
             "state_class: AUTHORITATIVE", "role: engineer", "profile: STANDARD", "allowed_paths:"]
    lines += [f"- {p}" for p in ticket.allowed]
    lines += ["kpis:", "  success:", "  - It works", "  failure:", "  - It does not work", "sources: []",
              "acceptance_tests:", f"  path: {ticket.acceptance}", "  author: independent-test-designer"]
    return "---\n" + "\n".join(lines) + f"\n---\n# {ticket.wbs} a planted ticket\n\nBody.\n"


GUARD = ("    ok = all('BROKEN' not in (_seen()[rel] or '') for rel in GUARDED)\n"
         "    _tell(ok)\n    assert ok, 'a guarded module is broken'\n")
RED_ALWAYS = "    _tell(False)\n    assert False, 'red on the base too'\n"


def mover_body(root, marker):
    """A test that, run outside the fixtures' own checks, commits once to the branch checked out at ``root`` (the
    planted root, written in at plant time): the integration branch moves while the queue's run runs."""
    return (f"    _tell(True)\n"
            f"    if os.environ.get({SELF_CHECK!r}) or os.path.exists({str(marker)!r}):\n        return\n"
            f"    git = ['git', '-C', {str(root)!r}, '-c', 'user.name=Another Lander', '-c',\n"
            f"           'user.email=lander@example.invalid', '-c', 'commit.gpgsign=false']\n"
            f"    subprocess.run(git + ['commit', '-q', '--allow-empty', '-m', 'another landing during the run'],\n"
            f"                   check=True, capture_output=True)\n"
            f"    sha = subprocess.run(git + ['rev-parse', 'HEAD'], check=True, capture_output=True, text=True)\n"
            f"    Path({str(marker)!r}).write_text(sha.stdout.strip(), encoding='utf-8')\n")


def telling(rel, told, modules, body=GUARD, name=None, also_watch=()):
    """A test file at ``rel`` with one test that imports ``modules`` of ``app`` and guards their files (red when
    one says BROKEN), watches those and ``also_watch``, and tells."""
    name = name or "test_" + Path(rel).stem[5:]
    depth = len(Path(rel).parts) - 1
    guarded = [module_rel(m) for m in modules]
    watch = guarded + [module_rel(m) for m in also_watch]
    imports = "".join(f"import app.{m}  # noqa: F401,E402\n" for m in modules)
    return (
        "import json\nimport os\nimport subprocess\nfrom pathlib import Path\n\n"
        f"{imports}\n"
        f"TREE = Path(__file__).resolve().parents[{depth}]\n"
        f"GUARDED = {guarded!r}\nWATCH = {watch!r}\n\n\n"
        "def _seen():\n"
        "    return {rel: ((TREE / rel).read_text(encoding='utf-8') if (TREE / rel).is_file() else None)\n"
        "            for rel in WATCH}\n\n\n"
        "def _tell(ok):\n"
        f"    if os.environ.get({SELF_CHECK!r}):\n        return\n"
        f"    with open(os.path.join({str(told)!r}, {name + '.jsonl'!r}), 'a', encoding='utf-8') as out:\n"
        "        out.write(json.dumps({'tree': str(TREE), 'seen': _seen(), 'ok': ok}) + '\\n')\n\n\n"
        f"def {name}():\n    subprocess  # noqa: B018\n{body}"
    )


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

def _git_env(home, who):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": who[0], "GIT_AUTHOR_EMAIL": who[1],
            "GIT_COMMITTER_NAME": who[0], "GIT_COMMITTER_EMAIL": who[1]}


def git(root, *args, who=ENGINEER, date=None, check=True):
    env = _git_env(Path(root).parent, who)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"fixture: git {' '.join(args)} failed in {root}:\n{done.stderr}")
    return done.stdout


def rev(root, name):
    out = git(root, "rev-parse", "--verify", "--quiet", f"{name}^{{commit}}", check=False).strip()
    return out or None


def parents(root, commit):
    return git(root, "rev-list", "--parents", "-n", "1", commit).split()[1:]


def changed_paths(root, commit):
    return [p for p in git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines() if p]


def trailers(root, commit):
    body = git(root, "log", "-1", "--format=%(trailers:unfold,only)", commit)
    return [line.strip() for line in body.splitlines() if line.strip()]


def is_ancestor(root, commit, of):
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, of],
                          capture_output=True).returncode == 0


def show(root, revision, rel):
    done = subprocess.run(["git", "-C", str(root), "show", f"{revision}:{rel}"], capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def front_matter(text):
    if not text or not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    return (yaml.safe_load(parts[1]) or {}) if len(parts) >= 3 else {}


def status_at(root, revision, tid):
    return front_matter(show(root, revision, f".tickets/{tid}.md")).get("status")


# --------------------------------------------------------------------------
# The planted project
# --------------------------------------------------------------------------

class Planted:
    """A planted project at ``root``; ``told`` is the telling tests' folder. ``tickets`` are its tickets (A and B
    unless given); ``unit`` its unit tests; ``extra`` more files ``{rel: text}``; ``queue_yaml`` the text of
    ``governance/project/queue.yaml`` (none without it). The initial commit, the owner's, holds everything, on
    ``branch``."""

    def __init__(self, root, told, tickets=(A, B), branch="main", unit=UNIT_TESTS, extra=None, queue_yaml=None):
        self.root, self.told = Path(root), Path(told)
        self.root.mkdir(parents=True)
        self.told.mkdir(parents=True)
        self.tickets = {t.id: t for t in tickets}
        self.tips = {}          # ticket -> its work branch's tip as planted
        self.branches = {}      # ticket -> its work branch's name
        self._second = 0
        git(self.root, "init", "-q", "-b", branch)
        git(self.root, "config", "user.name", "The Project")
        git(self.root, "config", "user.email", "project@example.invalid")
        git(self.root, "config", "commit.gpgsign", "false")
        modules = sorted({m for t in tickets for m in t.modules} | {m for _, m in unit} | {"gizmo"})
        files = {
            "README.md": "# A planted project\n",
            ".gitignore": ".gov-runtime/\n__pycache__/\n",
            PATH_MAP_REL: yaml.safe_dump(PATH_MAP, sort_keys=False),
            TEST_MAP_REL: yaml.safe_dump(TEST_MAP, sort_keys=False),
            NOTES_REL: "notes: []\n",
            "src/app/__init__.py": "",
            **{module_rel(m): f"# the {m}\nVALUE = 1\n" for m in modules},
            **{rel: telling(rel, self.told, [m]) for rel, m in unit},
        }
        for t in tickets:
            files[t.ticket_rel] = ticket_text(t)
            files[t.acceptance + "README.md"] = readme_text(t)
            files[t.suite_file] = telling(t.suite_file, self.told, t.modules)
        if queue_yaml is not None:
            files[QUEUE_YAML_REL] = queue_yaml
        files.update(extra or {})
        for rel, text in files.items():
            self.write(rel, text)
        tool = self.root / TK_REL
        tool.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(KERNEL_TK, tool)
        tool.chmod(0o755)
        self.base = self.commit("the planted project", OWNER, ["Role: owner"])
        self.home_branch = branch

    # -- writing and committing -------------------------------------------------

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _date(self):
        self._second += 1
        return f"2026-11-01T12:{self._second // 60:02d}:{self._second % 60:02d}+00:00"

    def commit(self, message, who, trailer_lines, files=None):
        for rel, text in (files or {}).items():
            self.write(rel, text)
        date = self._date()
        git(self.root, "add", "-A", who=who, date=date)
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for line in trailer_lines:
            args += ["--trailer", line]
        git(self.root, *args, who=who, date=date)
        return rev(self.root, "HEAD")

    def checkout(self, *args):
        git(self.root, "checkout", "-q", *args)

    def branch_from(self, name, start=None):
        self.checkout("-b", name, start or self.base)

    def home(self):
        self.checkout(self.home_branch)

    def work(self, ticket, files, role="engineer", task=True, who=ENGINEER, message="work on the ticket"):
        lines = ([f"Task: {ticket.id}"] if task else []) + [f"Role: {role}"]
        return self.commit(message, who, lines, files)

    def plant_branch(self, ticket, name, steps):
        """``ticket``'s work branch ``name`` from the base: each step ``(files, role, task)``; the home branch is
        checked out again. Returns the tip."""
        self.branch_from(name)
        for files, role, task in steps:
            who = {"engineer": ENGINEER, "independent-test-designer": DESIGNER, "owner": OWNER}.get(role, ENGINEER)
            self.work(ticket, files, role=role, task=task, who=who)
        tip = rev(self.root, "HEAD")
        self.home()
        self.tips[ticket.id], self.branches[ticket.id] = tip, name
        return tip

    def record_branch(self, ticket, name):
        self.tips[ticket.id], self.branches[ticket.id] = rev(self.root, name), name

    # -- reading ------------------------------------------------------------------

    def state(self):
        """What a refusal must leave as it was: every ref, what HEAD is, the working tree's status and the
        tracked files' bytes."""
        head = git(self.root, "symbolic-ref", "-q", "HEAD", check=False).strip() or rev(self.root, "HEAD")
        files = {}
        for rel in git(self.root, "ls-files").splitlines():
            path = self.root / rel
            files[rel] = path.read_bytes().hex() if path.is_file() else None
        return {"refs": git(self.root, "for-each-ref", "--format=%(refname) %(objectname)"),
                "head": head, "status": git(self.root, "status", "--porcelain"), "files": files}

    def told_runs(self, test_name):
        path = self.told / f"{test_name}.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# The fixtures' own checks (a broken fixture must not pass for a red)
# --------------------------------------------------------------------------

def plain_pytest(project, revision, targets):
    """``{node id: outcome}`` of a plain pytest run of ``targets`` in a scratch clone of the project at
    ``revision`` (telling tests quiet, so the project's run logs stay the queue's alone)."""
    scratch = project.root.parent / f"{project.root.name}-selfcheck"
    if scratch.exists():
        shutil.rmtree(scratch)
    git(project.root.parent, "clone", "-q", "--no-checkout", str(project.root), str(scratch))
    git(scratch, "checkout", "-q", "--detach", revision)
    junit = scratch.parent / f"{scratch.name}.xml"
    env = {**base_env(scratch.parent / f"{scratch.name}-env"), "PYTHONPATH": str(scratch / "src"), SELF_CHECK: "1"}
    done = subprocess.run([sys.executable, "-m", "pytest", *targets, "-q", "-p", "no:cacheprovider",
                           "-o", "junit_family=xunit1", f"--junitxml={junit}", "--rootdir", str(scratch)],
                          cwd=str(scratch), env=env, capture_output=True, text=True, timeout=300)
    outcomes = junit_outcomes(junit)
    shutil.rmtree(scratch, ignore_errors=True)
    assert outcomes, f"fixture: the planted tests did not run at {revision[:12]}:\n{done.stdout}\n{done.stderr}"
    return outcomes


def self_check(project, expect):
    """``expect``: ``{revision: {node id: "passed" | "failed"}}``; plus the test map against the kernel's schema
    and ``tk close`` closing a ticket in a scratch copy."""
    import jsonschema

    jsonschema.validate(yaml.safe_load((project.root / TEST_MAP_REL).read_text(encoding="utf-8")),
                        json.loads(TEST_MAP_SCHEMA.read_text(encoding="utf-8")))
    for revision, nodes in expect.items():
        got = plain_pytest(project, revision, sorted({n.split("::")[0] for n in nodes}))
        for n, want in nodes.items():
            assert got.get(n) == want, f"fixture: {n} at {revision[:12]} is {got.get(n)}, not {want}: {got}"
    scratch = project.root.parent / f"{project.root.name}-tkcheck"
    if scratch.exists():
        shutil.rmtree(scratch)
    git(project.root.parent, "clone", "-q", str(project.root), str(scratch))
    tid = next(iter(project.tickets))
    done = subprocess.run([str(scratch / TK_REL), "close", tid], cwd=str(scratch), capture_output=True, text=True,
                          env={**base_env(scratch.parent / f"{scratch.name}-env"),
                               "TICKETS_DIR": str(scratch / ".tickets")})
    closed = front_matter((scratch / ".tickets" / f"{tid}.md").read_text(encoding="utf-8")).get("status")
    shutil.rmtree(scratch, ignore_errors=True)
    assert done.returncode == 0 and closed == "closed", f"fixture: tk close does not close:\n{done.stderr}"


# --------------------------------------------------------------------------
# Running gov queue
# --------------------------------------------------------------------------

def base_env(folder):
    """A clean environment: a home and temp folder of its own (with a git identity, as a user's machine has), this
    worktree's ``src/``, the installed packages of the interpreter running the suite, the embedding endpoint at a
    dead local address and a stand-in for its program."""
    folder = Path(folder)
    home, tmp = folder / "home", folder / "tmp"
    home.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    (home / ".gitconfig").write_text("[user]\n\tname = The Machine's User\n\temail = user@example.invalid\n"
                                     "[commit]\n\tgpgsign = false\n", encoding="utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        dead = f"127.0.0.1:{probe.getsockname()[1]}"
    program = folder / "endpoint" / "ollama"
    program.parent.mkdir(parents=True, exist_ok=True)
    program.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    program.chmod(0o755)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "TMPDIR": str(tmp),
           "LC_ALL": "C.UTF-8", "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1",
           "OLLAMA_HOST": dead, "GOV_QUERY_OLLAMA_HOST": dead, "GOV_OLLAMA_BIN": str(program)}
    if site.ENABLE_USER_SITE:
        env["PYTHONUSERBASE"] = site.getuserbase()
    if os.environ.get("GOV_REBUILD_LOCK"):
        env["GOV_REBUILD_LOCK"] = os.environ["GOV_REBUILD_LOCK"]
    return env


def run_queue(project, *args, env_folder=None):
    """``python3 -m gov.cli.main queue <args> --root <project> --json``: ``{"code", "stdout", "stderr",
    "seconds"}``."""
    env = base_env(env_folder or project.root.parent / f"{project.root.name}-env")
    cmd = [sys.executable, "-m", "gov.cli.main", "queue", *args, "--root", str(project.root), "--json"]
    started = time.perf_counter()
    try:
        done = subprocess.run(cmd, cwd=str(project.root), env=env, capture_output=True, text=True,
                              timeout=GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov queue {' '.join(args)} did not end within {GOV_TIMEOUT_S} s") from None
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr,
            "seconds": time.perf_counter() - started}


def describe(run):
    return (f"gov queue {' '.join(run['args'])}: exit {run['code']}\n--- stdout\n{run['stdout'][-4000:]}"
            f"\n--- stderr\n{run['stderr'][-4000:]}")


def envelope(run):
    try:
        env = json.loads(run["stdout"])
    except ValueError:
        raise AssertionError(f"no JSON envelope on stdout\n{describe(run)}") from None
    assert isinstance(env, dict) and env.get("command") == "queue", f"not the queue's envelope\n{describe(run)}"
    return env


def answer(run, code):
    """The ``result`` of an ``ok: true`` answer that exited ``code``."""
    env = envelope(run)
    assert env.get("ok") is True, f"the queue's answer is not ok\n{describe(run)}"
    assert run["code"] == code, f"exit {run['code']}, not {code}\n{describe(run)}"
    assert isinstance(env.get("result"), dict), f"no result\n{describe(run)}"
    return env["result"]


def refusal(run, code, exit_code):
    """The ``error`` of an ``ok: false`` answer with ``code`` that exited ``exit_code``; the code on stderr too."""
    env = envelope(run)
    assert env.get("ok") is False, f"the queue did not refuse\n{describe(run)}"
    error = env.get("error") or {}
    assert error.get("code") == code, f"refused with {error.get('code')!r}, not {code}\n{describe(run)}"
    assert run["code"] == exit_code, f"exit {run['code']}, not {exit_code}\n{describe(run)}"
    assert f"{code}:" in run["stderr"], f"stderr does not say {code}\n{describe(run)}"
    return error


# --------------------------------------------------------------------------
# What the landing left
# --------------------------------------------------------------------------

def junit_outcomes(path):
    """``{node id: outcome}`` of one JUnit file (xunit1 or xunit2)."""
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError):
        return {}
    found = {}
    for case in tree.iter("testcase"):
        found[case_node(case)] = ("failed" if case.find("failure") is not None or case.find("error") is not None
                                  else "skipped" if case.find("skipped") is not None else "passed")
    return found


def case_node(case):
    rel = case.get("file")
    if not rel:
        classname = case.get("classname", "")
        rel = classname.replace(".", "/") + ".py"
    return f"{rel}::{case.get('name')}"


def queue_junit(project):
    """Every test case of every JUnit file the queue left under the project's ``.gov-runtime/`` (the warm clone's
    own tree aside)."""
    runtime = project.root / ".gov-runtime"
    clone = project.root / CLONE_REL
    cases = {}
    for path in sorted(runtime.rglob("*.xml")) if runtime.is_dir() else []:
        if clone in path.parents:
            continue
        cases.update(junit_outcomes(path))
    return cases


def files_of(cases):
    return {n.split("::")[0] for n in cases}


def close_record(project, revision, tid):
    text = show(project.root, revision, f"docs/close/{tid}/CL-{tid}.md")
    assert text is not None, f"no close record docs/close/{tid}/CL-{tid}.md at {revision[:12]}"
    return front_matter(text)


def own_places(tid):
    return (f".tickets/{tid}.md", f"docs/close/{tid}/", f"docs/checkpoints/{tid}/")


def assert_landed_through_close_commits(project, result, onto, old_head):
    """The integration branch's head reaches the tested merge through one close commit per landed ticket, each
    changing only that ticket's ticket file, close record folder and checkpoint folder, the first on the tested
    merge; returns ``{ticket: close commit}``."""
    root = project.root
    head, tested = rev(root, onto), result.get("tested")
    assert head == result.get("head"), f"{onto} is at {head}, the answer's head is {result.get('head')}"
    assert tested and is_ancestor(root, tested, head), f"the tested merge {tested} is not under {onto}"
    chain = git(root, "rev-list", "--reverse", f"{tested}..{head}").split()
    landed = result.get("landed") or []
    assert len(chain) == len(landed), f"{len(chain)} commit(s) over the tested merge for {len(landed)} landed"
    below, by_ticket = tested, {}
    for commit in chain:
        assert parents(root, commit) == [below], f"{commit[:12]} is not one commit on {below[:12]}"
        tasks = [t.split(":", 1)[1].strip() for t in trailers(root, commit) if t.startswith("Task:")]
        assert len(tasks) == 1 and tasks[0] in landed, f"{commit[:12]} names no landed ticket: {tasks}"
        tid = tasks[0]
        assert tid not in by_ticket, f"two close commits for {tid}"
        ticket_file, record_dir, checkpoint_dir = own_places(tid)
        paths = changed_paths(root, commit)
        stray = [p for p in paths if p != ticket_file and not p.startswith((record_dir, checkpoint_dir))]
        assert not stray, f"the close commit of {tid} changes more than its records: {stray}"
        assert ticket_file in paths and f"{record_dir}CL-{tid}.md" in paths, f"{tid}'s close commit: {paths}"
        by_ticket[tid], below = commit, commit
    assert set(by_ticket) == set(landed)
    closes = {c.get("ticket"): c.get("commit") for c in result.get("closes") or []}
    assert closes == by_ticket, f"the answer's closes {closes} are not the close commits {by_ticket}"
    assert result.get("base") == old_head, f"base {result.get('base')} is not the old head {old_head}"
    return by_ticket


def assert_closed_iff_merged(project, onto, every=None):
    """Failure line 2: each planted ticket's status at the integration head is ``closed`` exactly when its work
    branch's tip (as planted) is an ancestor of that head; a ticket with no branch is not closed."""
    root, head = project.root, rev(project.root, onto)
    for tid in every or project.tickets:
        closed = status_at(root, head, tid) == "closed"
        tip = project.tips.get(tid)
        merged = bool(tip) and is_ancestor(root, tip, head)
        assert closed == merged, (f"{tid}: closed at {onto} is {closed}, its branch tip merged is {merged}")


# --------------------------------------------------------------------------
# A planted run, as the cases read it
# --------------------------------------------------------------------------

class Landing:
    """One planted run of ``gov queue``, shared by the cases that read it: the project (``root``, ``told``, the
    tickets' ids, the work branches' tips as planted), the integration branch, its head before the run, the
    project's state before the run, the run itself and what the scenario adds (``extra``)."""

    def __init__(self, data):
        self.data = data
        self.root, self.told = Path(data["root"]), Path(data["told"])
        self.tickets, self.tips, self.branches = data["tickets"], data["tips"], data["branches"]
        self.onto, self.old_head, self.before = data["onto"], data["old_head"], data["before"]
        self.run, self.extra = data["run"], data.get("extra", {})

    told_runs = Planted.told_runs

    def state(self):
        return Planted.state(self)


def landing_data(project, run, onto, old_head, before, **extra):
    return {"root": str(project.root), "told": str(project.told), "tickets": list(project.tickets),
            "tips": dict(project.tips), "branches": dict(project.branches), "onto": onto, "old_head": old_head,
            "before": before, "run": run, "extra": extra}


def heads(state):
    """``{branch ref: sha}`` of a ``state()``."""
    pairs = (line.split(" ", 1) for line in state["refs"].splitlines() if line.startswith("refs/heads/"))
    return {name: sha for name, sha in pairs}
