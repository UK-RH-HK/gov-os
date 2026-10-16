"""Support code for the W2-50 acceptance tests (standard library and PyYAML only).

W2-50 makes ``~/gov-os-runs/`` the one durable scratch root outside the
repository: a session writes only under ``~/gov-os-runs/<its own ticket>/``
(DEC-728). The tests drive three public interfaces and nothing else:

- **the guard**, the kernel's PreToolUse hook
  (``template/governance/kernel/hooks/pretooluse.py``), run as the harness
  runs it, with the call on stdin, as W1-03's suite runs it. The one file is
  copied into the temporary project at ``governance/kernel/hooks/``, where a
  product repository has it;
- **``gov launch``**, with a stand-in for the CLI at ``<HOME>/.local/bin/claude``
  that starts no session (W1-46's way): it records the settings the session
  would have been started with, and does what a plan file asks of a session;
- **``gov rebuild``** and **the secrets-indexing check** (its ``command`` read
  from ``template/governance/kernel/checks/secrets-indexing.yaml``, run by
  ``sh -c`` in the project's root).

**The code under test** is this worktree's ``src/``. Every child process gets
``PYTHONPATH``: the runner's own value when it has one (DEC-732 sets it per
command), else this worktree's ``src``. ``test_w2_50_code_under_test.py``
shows which ``gov`` a child imports.

**Homes and temp folders.** Every test has a base folder of its own (pytest's
``tmp_path``) holding three disjoint siblings:

- ``home/``: the ``HOME`` of every process under test. ``~/gov-os-runs`` is
  ``home/gov-os-runs``; the project lies at ``home/gov-os-worktrees/W2-90``, as
  a ticket worktree does;
- ``systmp/``: the ``TMPDIR`` of every process under test, so that
  ``tempfile.gettempdir()`` there is ``systmp/`` and never holds ``home/``;
- ``elsewhere/``: outside the project, outside ``home/`` and outside the temp
  folder.

The guard allows writes in the temp folder; since ``home/`` is not under
``systmp/``, nothing under ``home/`` is allowed for that reason. The real
``~/gov-os-runs``, ``~/gov-os-worktrees`` and ``~/gov-os-workbench`` are never
named, created, listed or written.

**The fixture project** is built from scratch: tickets, a few files, a
``.claude/settings.json`` written here that registers the copied guard, and a
git history of one commit. Nothing of this repository is copied but single
named files (the guard, ``template/.gitleaks.toml``).
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
GUARD_SOURCE = REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
CHECK_DECLARATION = REPO_ROOT / "template/governance/kernel/checks/secrets-indexing.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
PYPROJECT = REPO_ROOT / "pyproject.toml"

RUNS = "gov-os-runs"               # the durable scratch root, under HOME (DEC-728)
WORKTREES = "gov-os-worktrees"
WORKBENCH = "gov-os-workbench"

ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
RESEARCH = "research"
ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, ORCHESTRATOR, PRODUCT_SPEC, RESEARCH)
LAUNCHED_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, PRODUCT_SPEC, RESEARCH)   # DEC-161, DEC-386

COMMAND_TIMEOUT_S = 60.0
REBUILD_TIMEOUT_S = 300.0


# --------------------------------------------------------------------------
# The fixture tickets
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    tk: str                   # the tk id, what GOV_TICKET holds
    role: str
    wbs: str | None           # the W2 id (external-ref); None: the ticket has none
    allowed: tuple

    @property
    def folder(self):
        """The name of the ticket's own folder under the root: its W2 id, or its tk id when it has none."""
        return self.wbs or self.tk


MAIN = Ticket("DAEO-zz90", ENGINEER, "W2-90", ("src/app/**",))
OTHER = Ticket("DAEO-zz91", ENGINEER, "W2-91", ("src/other/**",))
SPEC = Ticket("DAEO-zz92", PRODUCT_SPEC, "W2-92", ("docs/spec/**",))
AUDIT = Ticket("DAEO-zz94", AUDITOR, "W2-94", ("docs/audit/**",))
EXPERIMENT = Ticket("DAEO-zz97", RESEARCH, "W2-97", ("experiments/spikes/exp-901/**",))
NO_W2_ID = Ticket("DAEO-zz98", ENGINEER, None, ("src/app/**",))
SUFFIXED = Ticket("DAEO-zz99", ENGINEER, "W2-99a", ("src/app/**",))
TICKETS = (MAIN, OTHER, SPEC, AUDIT, EXPERIMENT, NO_W2_ID, SUFFIXED)
UNKNOWN_TICKET = "DAEO-zz00"     # no file in .tickets/

# The ticket each role's session runs under. The test designer and the ticket lead (orchestrator) work on MAIN.
TICKET_OF = {ENGINEER: MAIN, TEST_DESIGNER: MAIN, ORCHESTRATOR: MAIN, PRODUCT_SPEC: SPEC, AUDITOR: AUDIT,
             RESEARCH: EXPERIMENT}


def ticket_text(ticket):
    lines = [
        "---",
        f"id: {ticket.tk}",
        "status: in_progress",
        "deps: []",
        "links: []",
        "created: 2026-10-16T16:35:12Z",
        "type: task",
        "priority: 1",
        f"assignee: {ticket.role}",
    ]
    if ticket.wbs:
        lines.append(f"external-ref: {ticket.wbs}")
    lines += ["tags: [wave-2, implementation, full]"]
    if ticket.wbs:
        lines.append(f"wbs_id: {ticket.wbs}")
    lines += [
        "title: W2-50 fixture ticket",
        "class: implementation",
        f"role: {ticket.role}",
        "depends_on: []",
        "allowed_paths:",
        *[f"- {path}" for path in ticket.allowed],
        "kpis:",
        "  success:",
        "  - The fixture component exists",
        "  failure:",
        "  - The fixture component is missing",
        "profile: FULL",
        "acceptance_tests:",
        f"  path: tests/acceptance/{ticket.folder}/",
        "---",
        f"# {ticket.folder} W2-50 fixture ticket",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The sandbox: home, temp folder and elsewhere, disjoint
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path        # HOME of every process under test
    tmpdir: Path      # TMPDIR of every process under test
    elsewhere: Path   # outside the project, HOME and the temp folder
    pycache: Path

    @property
    def root(self):
        """``~/gov-os-runs`` as the processes under test see it."""
        return self.home / RUNS

    def own(self, ticket=MAIN):
        return self.root / ticket.folder

    @property
    def project(self):
        """The fixture project: a ticket worktree, ``~/gov-os-worktrees/W2-90``."""
        return self.home / WORKTREES / MAIN.folder


def make_sandbox(base):
    base = Path(base).resolve()
    box = Sandbox(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache")
    for directory in (box.home, box.tmpdir, box.elsewhere, box.pycache):
        directory.mkdir(parents=True, exist_ok=True)
    for one, two in ((box.home, box.tmpdir), (box.tmpdir, box.home)):
        assert one != two and two not in one.parents, f"{one} and {two} are not disjoint"
    return box


def python_path():
    """What every child's PYTHONPATH is: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def base_environment(sandbox, role=None, ticket=None, project=None):
    """A minimal environment, built from scratch. ``ticket=""`` sets GOV_TICKET empty; ``None`` leaves it out."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-50 acceptance", "GIT_AUTHOR_EMAIL": "w2-50@example.invalid",
        "GIT_COMMITTER_NAME": "W2-50 acceptance", "GIT_COMMITTER_EMAIL": "w2-50@example.invalid",
    }
    if project is not None:
        env["CLAUDE_PROJECT_DIR"] = str(project)
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return env


# --------------------------------------------------------------------------
# The fixture project, from scratch
# --------------------------------------------------------------------------

GUARD_COMMAND = f'python3 "$CLAUDE_PROJECT_DIR"/{GUARD_REL}'
PROJECT_FILES = {
    "README.md": "# W2-50 fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "src/app/main.py": "VALUE = 1\n",
    "src/other/main.py": "VALUE = 1\n",
    "docs/notes.md": "notes\n",
    "docs/spec/feature.md": "spec\n",
    "docs/audit/earlier.md": "audit\n",
    "experiments/spikes/exp-901/README.md": "# Experiment 901\n",
}
# Single named files of this repository the fixture project holds where a product repository has them.
COPIED_FILES = {
    GUARD_REL: GUARD_SOURCE,
    "template/governance/kernel/launch/research-allowlist.yaml":
        REPO_ROOT / "template/governance/kernel/launch/research-allowlist.yaml",   # read by a research launch
}


def git(directory, *args, check=True):
    proc = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-50 acceptance",
                           "-c", "user.email=w2-50@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=COMMAND_TIMEOUT_S)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_project(sandbox, extra=None):
    """The committed fixture project at ``~/gov-os-worktrees/W2-90`` with the guard registered for every tool."""
    project = sandbox.project
    files = dict(PROJECT_FILES)
    files.update(extra or {})
    for ticket in TICKETS:
        files[f".tickets/{ticket.tk}.md"] = ticket_text(ticket)
    files[".claude/settings.json"] = json.dumps({"hooks": {
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": GUARD_COMMAND}]}],
    }}, indent=2) + "\n"
    for rel, text in files.items():
        write(project / rel, text)
    for rel, source in COPIED_FILES.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, project / rel)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-50 fixture project")
    return project


# --------------------------------------------------------------------------
# The guard
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Decision:
    decision: str    # allow | ask | deny | error
    reason: str
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self):
        return (f"decision={self.decision} exit={self.returncode} reason={self.reason[:400]!r} "
                f"stderr={self.stderr.strip()[:300]!r}")


def _decision(returncode, stdout, stderr):
    if returncode is None:
        return "error", "timed out"
    if returncode == 2:
        return "deny", stderr.strip()
    if returncode != 0:
        return "error", stderr.strip()
    try:
        data = json.loads(stdout.strip() or "null")
    except ValueError:
        return "allow", ""
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    if isinstance(specific, dict) and specific.get("permissionDecision") in ("deny", "ask"):
        return specific["permissionDecision"], str(specific.get("permissionDecisionReason") or "")
    return "allow", ""


_CALLS = iter(range(1, 10_000_000))


def ask_guard(sandbox, tool_name, tool_input, role, ticket, project=None):
    """Run the project's guard once, as the harness does before a call. ``ticket`` is a tk id, ``""`` or None."""
    project = Path(project or sandbox.project)
    data = {
        "session_id": "w2-50-acceptance-session",
        "transcript_path": str(sandbox.elsewhere / "transcript.jsonl"),
        "cwd": str(project),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_w2_50_{next(_CALLS):06d}",
    }
    try:
        proc = subprocess.run([sys.executable, str(project / GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(project),
                              env=base_environment(sandbox, role, ticket, project), timeout=COMMAND_TIMEOUT_S)
        returncode, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        returncode, stdout, stderr = None, "", "timed out"
    decision, reason = _decision(returncode, stdout, stderr)
    return Decision(decision, reason, returncode, stdout, stderr)


def tool_input(tool_name, target):
    """The input of a Write or Edit call on ``target``, or of a Bash call whose command is ``target``."""
    if tool_name == "Write":
        return {"file_path": str(target), "content": "written by the W2-50 acceptance test\n"}
    if tool_name == "Edit":
        return {"file_path": str(target), "old_string": "a", "new_string": "b"}
    if tool_name == "Bash":
        return {"command": str(target), "description": "W2-50 acceptance call"}
    raise ValueError(tool_name)


def q(path):
    return shlex.quote(str(path))


def assert_allowed(result, what):
    assert result.decision == "allow", f"{what} was not allowed: {result.describe()}"


def assert_refused(result, what, *names):
    """Refused, with a reason: the refusal's text is not empty and names the target or why.

    ``names`` are strings of which the reason must hold one: the path as given,
    a form of it, or a word that says why. The guard's own wording is not
    prescribed.
    """
    assert result.decision == "deny", f"{what} was not refused: {result.describe()}"
    reason = result.reason.strip()
    assert reason, f"{what} was refused without a reason: {result.describe()}"
    if names:
        assert any(str(name) in reason for name in names if name), (
            f"{what}: the refusal's reason names neither the target nor why (one of {[str(n) for n in names]}): "
            f"{reason[:400]!r}")


def why_words(path, sandbox):
    """What a refusal of ``path`` may name: the path, its normal and real forms, the root's name, a reason word."""
    path = str(path)
    words = {path, os.path.normpath(path), os.path.realpath(path), RUNS, WORKBENCH, WORKTREES, "ticket",
             "outside", "role"}
    return sorted(words)


# --------------------------------------------------------------------------
# gov, through its console script entry point (no install)
# --------------------------------------------------------------------------

def _entry_point():
    scripts = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    return module.strip(), attribute.strip()


def gov_argv(*args):
    module, attribute = _entry_point()
    code = (f"import sys\nimport {module} as _m\n_t = _m\nfor _n in {attribute!r}.split('.'):\n"
            "    _t = getattr(_t, _n)\nsys.argv[0] = 'gov'\nsys.exit(_t())\n")
    return [sys.executable, "-c", code, *args]


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-2000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")


def run_gov(sandbox, cwd, *args, env=None, timeout=COMMAND_TIMEOUT_S):
    try:
        done = subprocess.run(gov_argv(*args), cwd=str(cwd), env=env or base_environment(sandbox),
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
    return Run(tuple(args), done.returncode, done.stdout, done.stderr)


# --------------------------------------------------------------------------
# The stand-in CLI for gov launch
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W2-50 acceptance tests). Starts no session; records its call; follows a plan."""
import json, os, subprocess, sys

args = sys.argv[1:]
if "--version" in args or "-v" in args:
    print("2.1.288 (Claude Code)")
    sys.exit(0)
settings = []
i = 0
while i < len(args):
    value = None
    if args[i] == "--settings" and i + 1 < len(args):
        value = args[i + 1]
        i += 1
    elif args[i].startswith("--settings="):
        value = args[i].split("=", 1)[1]
    if value is not None:
        if value.lstrip().startswith("{"):
            settings.append(value)
        else:
            try:
                with open(value, encoding="utf-8") as handle:
                    settings.append(handle.read())
            except OSError as exc:
                settings.append("unreadable: " + str(exc))
    i += 1
plan = {}
if os.path.isfile(@PLAN@):
    with open(@PLAN@, encoding="utf-8") as handle:
        plan = json.load(handle)
seen = {path: os.path.isdir(path) for path in plan.get("check", [])}
listed = {path: (sorted(os.listdir(path)) if os.path.isdir(path) else None) for path in plan.get("list", [])}
cloned = []
for source, destination in plan.get("clone", []):
    done = subprocess.run(["git", "clone", "-q", "--no-hardlinks", source, destination], capture_output=True,
                          text=True)
    cloned.append([destination, done.returncode, done.stderr[-400:]])
for path, text in plan.get("files", {}).items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
record = {"args": args, "env": dict(os.environ), "settings": settings, "seen": seen, "listed": listed,
          "cloned": cloned}
with open(@LOG@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record) + "\n")
'''


@dataclass(frozen=True)
class Cli:
    path: Path
    log: Path
    plan: Path


def install_stand_in_cli(sandbox):
    log, plan = sandbox.elsewhere / "claude-calls.jsonl", sandbox.elsewhere / "claude-plan.json"
    path = sandbox.home / ".local/bin/claude"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_STUB.replace("@PYTHON@", sys.executable).replace("@PLAN@", repr(str(plan)))
                    .replace("@LOG@", repr(str(log))), encoding="utf-8")
    path.chmod(0o755)
    return Cli(path, log, plan)


def set_plan(cli, check=(), listing=(), clone=(), files=None):
    cli.plan.write_text(json.dumps({"check": [str(p) for p in check], "list": [str(p) for p in listing],
                                    "clone": [[str(s), str(d)] for s, d in clone],
                                    "files": {str(k): v for k, v in (files or {}).items()}}), encoding="utf-8")


def calls(cli):
    if not cli.log.is_file():
        return []
    return [json.loads(line) for line in cli.log.read_text(encoding="utf-8").splitlines() if line.strip()]


@dataclass(frozen=True)
class Launch:
    run: Run
    calls: tuple

    def describe(self):
        return f"{self.run.describe()}\nsessions recorded: {len(self.calls)}"

    def session(self):
        assert self.run.returncode == 0 and len(self.calls) == 1, (
            f"gov launch did not start exactly one session\n{self.describe()}")
        return self.calls[0]

    def settings(self):
        entries = self.session()["settings"]
        assert len(entries) == 1, f"the session was started with {len(entries)} --settings values\n{self.describe()}"
        try:
            data = json.loads(entries[0])
        except ValueError:
            raise AssertionError(f"the --settings value is not JSON: {entries[0][:300]!r}") from None
        assert isinstance(data, dict), "the --settings value is not a JSON object"
        return data

    def variable(self, name):
        block = self.settings().get("env")
        if isinstance(block, dict) and name in block:
            return block[name]
        return self.session()["env"].get(name)

    def allow_write(self):
        """The sandbox's filesystem write list, as given."""
        block = (self.settings().get("sandbox") or {}).get("filesystem") or {}
        entries = block.get("allowWrite", []) if isinstance(block, dict) else []
        assert isinstance(entries, list), f"sandbox.filesystem.allowWrite is not a list: {entries!r}"
        return entries


def launch(sandbox, cli, role, ticket):
    before = len(calls(cli))
    run = run_gov(sandbox, sandbox.project, "launch", role, ticket.tk if isinstance(ticket, Ticket) else ticket)
    return Launch(run, tuple(calls(cli)[before:]))


def entry_path(entry, sandbox):
    """The absolute path a sandbox write entry names: ``//abs``, ``~/rel`` or ``/abs``; glob tails dropped."""
    text = str(entry)
    if text.startswith("//"):
        text = text[1:]
    elif text.startswith("~/"):
        text = str(sandbox.home) + text[1:]
    elif text == "~":
        text = str(sandbox.home)
    for tail in ("/**", "/*"):
        if text.endswith(tail):
            text = text[: -len(tail)]
    return os.path.realpath(os.path.normpath(text)) if text.startswith("/") else None


def covers(entry_real, path):
    """Whether a write entry (a real absolute path) holds ``path``."""
    path = os.path.realpath(str(path))
    return entry_real is not None and (path == entry_real or path.startswith(entry_real.rstrip("/") + "/"))


# --------------------------------------------------------------------------
# Planted strings, built at run time from parts
# --------------------------------------------------------------------------

def _body(seed, length):
    out, count = "", 0
    while len(out) < length:
        out += hashlib.sha256(f"{seed}{count}".encode()).hexdigest()
        count += 1
    mixed = "".join(ch.upper() if i % 3 == 0 else ch for i, ch in enumerate(out))
    return mixed[:length]


# A token of the shape a gitleaks default rule finds (github-pat). Not a credential.
SECRET = "ghp" + "_" + _body("w2-50-pat", 36)
# Plain words that only the tests write: one inside the repository, one under the root, one in a clone.
REPO_MARKER = "zqxw" + "repomarker" + "5011"
RUNS_MARKER = "zqxw" + "runsmarker" + "5012"
CLONE_MARKER = "zqxw" + "clonemarker" + "5013"


def holders(top, needle, skip=()):
    """The regular files under ``top`` (links not followed) whose bytes hold ``needle``."""
    found = []
    skip = {os.path.realpath(str(s)) for s in skip}
    needle = needle.encode()
    for directory, names, files in os.walk(top):
        names[:] = [n for n in names if os.path.realpath(os.path.join(directory, n)) not in skip
                    and not os.path.islink(os.path.join(directory, n))]
        for name in files:
            path = os.path.join(directory, name)
            if os.path.islink(path):
                continue
            try:
                with open(path, "rb") as handle:
                    if needle in handle.read():
                        found.append(path)
            except OSError:
                pass
    return found


def snapshot(top, skip_names=()):
    """``relative path -> sha256`` of every regular file under ``top`` (links recorded by their target).

    Folders named in ``skip_names`` are left out with everything in them.
    """
    result = {}
    top = Path(top)
    if not top.exists():
        return result
    for directory, names, files in os.walk(top):
        names[:] = [name for name in names if name not in skip_names]
        for name in names + files:
            path = Path(directory) / name
            rel = str(path.relative_to(top))
            if path.is_symlink():
                result[rel] = "link:" + os.readlink(path)
            elif path.is_file():
                result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def path_map_text():
    """The kernel template's path map with one indexed namespace, ``docs``, for the rebuild cases."""
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document.setdefault("namespaces", {})["docs"] = {
        "paths": ["docs/**"],
        "memory_class": "governance",
        "sensitivity": "internal",
        "permitted_roles": list(ROLES),
        "retention": "kept in git history",
        "export_policy": "allowed",
        "embedding_policy": "embedded",
        "provenance": "written by the W2-50 tests",
        "deletion_rebuild": "authoritative; restored from git only",
    }
    return yaml.safe_dump(document, sort_keys=False)


def check_command():
    """The secrets-indexing check's command, from its declaration."""
    data = yaml.safe_load(CHECK_DECLARATION.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("command"), str), (
        f"{CHECK_DECLARATION.relative_to(REPO_ROOT)} declares no command")
    return data["command"]


def run_check(sandbox, project):
    """Run the check as the family runner does: by ``sh -c``, in the project's root."""
    command = check_command()
    try:
        done = subprocess.run(command, shell=True, cwd=str(project), env=base_environment(sandbox),
                              capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the check did not end: {command}") from None
    return Run(("secrets-indexing",), done.returncode, done.stdout, done.stderr)
