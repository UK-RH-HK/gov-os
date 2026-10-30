"""Support code for the W2-58 acceptance tests (standard library, PyYAML and jsonschema only).

W2-58 puts Policy 2 (DEC-820) in the guard and the launcher: reads are open,
and only four things are refused: (a) secrets, (b) the held-out material's
contents, (c) the counterpart's work on the same ticket, (d) the hidden half of
an evaluation set. The tests drive four public interfaces and nothing else:

- **the guard**, the kernel's PreToolUse hook
  (``template/governance/kernel/hooks/pretooluse.py``), copied as one file into
  the temporary project at ``governance/kernel/hooks/`` and run as the harness
  runs it, with the call on stdin and the session's role and ticket in
  ``GOV_ROLE`` and ``GOV_TICKET``;
- **``gov launch <role> <ticket>``**, with a stand-in for the CLI at
  ``<HOME>/.local/bin/claude`` that starts no session: it records the
  ``--settings`` value it was handed;
- **``python3 -m gov.guard.hooks``**, the hook-listing helper;
- **the path-map schema** ``template/governance/kernel/schemas/path-map.schema.json``
  and this repository's own ``governance/project/path-map.yaml``, read as files.

**The code under test** is this worktree's ``src/``. Every child process gets
``PYTHONPATH``: the runner's own value when it has one (DEC-732 sets it per
command), else the ``src`` folder of the worktree that holds this file.

**Homes and temp folders.** Every test has its own base folder (pytest's
``tmp_path``) holding disjoint siblings: ``home/`` (the ``HOME`` of every
process under test: it holds the project, the stand-in held-out material and a
stand-in ``~/.ssh``), ``systmp/`` (their ``TMPDIR``), ``elsewhere/`` (the
stand-in CLI's log) and ``pycache/``. No real secret, no real held-out path,
no real ``~/.ssh`` is ever named or opened: every such file is made up here.

**The fixture project** is a git repository built from scratch at
``home/gov-os-worktrees/W2-95``: tickets, a few files, a settings file that
registers the copied guard, a held-out list naming the stand-in material, and
two commits: the base, then ticket T's own commit on branch ``w2/W2-95``. With
``base=True`` the base is the branch ``w2/integrate``; with ``base=False`` the
repository has no such branch (its first branch is ``main``).
"""

from __future__ import annotations

import json
import os
import re
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
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
SCHEMAS = REPO_ROOT / "template/governance/kernel/schemas"
PATH_MAP_SCHEMA = SCHEMAS / "path-map.schema.json"
REPO_PATH_MAP = REPO_ROOT / "governance/project/path-map.yaml"
PYPROJECT = REPO_ROOT / "pyproject.toml"
# One named file a research launch reads (copied into a fixture project that launches a research session).
ALLOWLIST_TEMPLATE_REL = "template/governance/kernel/launch/research-allowlist.yaml"
ALLOWLIST_TEMPLATE = REPO_ROOT / ALLOWLIST_TEMPLATE_REL

SETTINGS_REL = ".claude/settings.json"
HELD_OUT_LIST_REL = "governance/project/held-out.yaml"     # its names are readable (DEC-820 (b))
HELD_OUT_KEY = "held_out_paths"                            # DEC-218
PATH_MAP_REL = "governance/project/path-map.yaml"

ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
RESEARCH = "research"
ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, ORCHESTRATOR, PRODUCT_SPEC, RESEARCH)

COMMAND_TIMEOUT_S = 60.0
INTEGRATE = "w2/integrate"

# Words only these tests write, so that an output can be searched for them.
WORD = "zqxw58"                          # in ordinary files: what the searches look for
TEST_WORD = "zqxw58testsource"           # only in T's acceptance tests
CHANGED_WORD = "zqxw58changedcode"       # only in the branch's version of T's changed files
BASE_WORD = "zqxw58basecode"             # only in the base's version of src/app/main.py
SECRET_WORD = "zqxw58secretvalue"        # only in the stand-in secret files
HELD_WORD = "zqxw58heldoutanswer"        # only in the stand-in held-out material
HIDDEN_WORD = "zqxw58hiddenanswer"       # only in the hidden part of the evaluation set
FAILURE_WORD = "zqxw58failuremessage"    # the failure message of T's failing acceptance test


# --------------------------------------------------------------------------
# The fixture tickets
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    tk: str            # what GOV_TICKET holds
    role: str
    wbs: str           # wbs_id, the name of the ticket's acceptance folder
    allowed: tuple

    @property
    def acceptance(self):
        return f"tests/acceptance/{self.wbs}"


T = Ticket("DAEO-zz58", ENGINEER, "W2-95", ("src/app/**",))
OTHER = Ticket("DAEO-zz59", ENGINEER, "W2-96", ("src/other/**",))
SPEC = Ticket("DAEO-zz60", PRODUCT_SPEC, "W2-97", ("docs/spec/**",))
AUDIT = Ticket("DAEO-zz61", AUDITOR, "W2-98", ("docs/audit/**",))
EXPERIMENT = Ticket("DAEO-zz62", RESEARCH, "W2-99", ("experiments/spikes/exp-962/**",))
MEASURED = Ticket("DAEO-zz63", ENGINEER, "W2-93", ("src/measured/**",))
TICKETS = (T, OTHER, SPEC, AUDIT, EXPERIMENT, MEASURED)

# The ticket each role's session runs under: the engineer, the test designer,
# the ticket lead and the auditor work on T (DEC-820 (c), item 6 of the brief).
TICKET_OF = {ENGINEER: T, TEST_DESIGNER: T, ORCHESTRATOR: T, AUDITOR: T, PRODUCT_SPEC: SPEC,
             RESEARCH: EXPERIMENT}


def ticket_text(ticket, note=""):
    lines = [
        "---",
        f"id: {ticket.tk}",
        "status: in_progress",
        "deps: []",
        "links: []",
        "created: 2026-10-20T07:08:28Z",
        "type: task",
        "priority: 1",
        f"assignee: {ticket.role}",
        f"external-ref: {ticket.wbs}",
        "tags: [wave-2, implementation, standard]",
        f"wbs_id: {ticket.wbs}",
        "title: W2-58 fixture ticket",
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
        "profile: STANDARD",
        "acceptance_tests:",
        f"  path: {ticket.acceptance}/",
        "---",
        f"# {ticket.wbs} W2-58 fixture ticket",
        "",
    ]
    if note:
        lines += [note, ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The sandbox: home, temp folder and elsewhere, disjoint
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path
    tmpdir: Path
    elsewhere: Path
    pycache: Path

    @property
    def project(self):
        return self.home / "gov-os-worktrees" / T.wbs

    @property
    def held_out(self):
        """The stand-in held-out material: a folder under HOME, outside the project."""
        return self.home / "held-out-material"

    @property
    def ssh(self):
        return self.home / ".ssh"


def make_sandbox(base):
    base = Path(base).resolve()
    box = Sandbox(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache")
    for directory in (box.home, box.tmpdir, box.elsewhere, box.pycache):
        directory.mkdir(parents=True, exist_ok=True)
    return box


def python_path():
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def base_environment(sandbox, role=None, ticket=None, project=None):
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
        "GIT_AUTHOR_NAME": "W2-58 acceptance", "GIT_AUTHOR_EMAIL": "w2-58@example.invalid",
        "GIT_COMMITTER_NAME": "W2-58 acceptance", "GIT_COMMITTER_EMAIL": "w2-58@example.invalid",
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

# Stand-in secrets: made-up words, named as DEC-820 (a)'s name rule names secrets.
SECRET_FILES = (
    ".env",
    ".env.local",
    "services/api/.env",
    "services/api/.env.production",
    "certs/server.pem",
    "certs/server.key",
    "config/secrets.yaml",
    "config/secrets.json",
)
# Their neighbours: ordinary files a name rule for secrets must leave readable.
SECRET_NEIGHBOURS = ("config/settings.yaml", "docs/environment.md", "src/app/keys.py", "certs/README.md")
SSH_FILES = ("id_ed25519", "config")

BASE_FILES = {
    "README.md": f"# W2-58 fixture project {WORD}\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n.pytest_cache/\n",
    "src/app/main.py": f"def value():\n    return 1  # {BASE_WORD} {WORD}\n",
    "src/app/keys.py": f"KEYS = ()  # {WORD}\n",
    "src/other/main.py": f"VALUE = 1  # {WORD}\n",
    "src/measured/main.py": f"VALUE = 1  # {WORD}\n",
    "docs/notes.md": f"notes {WORD}\n",
    "docs/environment.md": f"environment notes {WORD}\n",
    "docs/spec/feature.md": f"spec {WORD}\n",
    "docs/audit/earlier.md": f"audit {WORD}\n",
    "experiments/spikes/exp-962/README.md": f"# Experiment 962 {WORD}\n",
    "config/settings.yaml": f"name: {WORD}\n",
    "certs/README.md": f"certificates {WORD}\n",
    f"{OTHER.acceptance}/test_other.py": f"def test_other():\n    assert '{WORD}'\n",
    "governance/project/notes.md": f"project notes {WORD}\n",
}
BRANCH_FILES = {
    "src/app/main.py": f"def value():\n    return 2  # {CHANGED_WORD} {WORD}\n",
    "src/app/added.py": f"ADDED = True  # {CHANGED_WORD} {WORD}\n",
    f"{T.acceptance}/test_feature.py": (
        f"# {TEST_WORD} {WORD}\n"
        "def test_the_feature_passes():\n"
        "    assert True\n"
        "\n"
        "def test_the_feature_fails_with_a_message():\n"
        f"    assert False, '{FAILURE_WORD}'\n"
    ),
    f"{T.acceptance}/README.md": f"# The tests of W2-95 {TEST_WORD} {WORD}\n",
}
# The files T's branch changes against its base, other than tests and tickets.
CHANGED = ("src/app/main.py", "src/app/added.py")
UNCHANGED = ("src/other/main.py", "docs/notes.md")


def git(directory, *args, check=True):
    proc = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-58 acceptance",
                           "-c", "user.email=w2-58@example.invalid", "-c", "commit.gpgsign=false",
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


def settings_text():
    return json.dumps({"hooks": {
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": GUARD_COMMAND}]}],
    }}, indent=2) + "\n"


def held_out_text(*paths):
    return yaml.safe_dump({HELD_OUT_KEY: [str(p) for p in paths]}, sort_keys=False)


def make_outside_files(sandbox):
    """The stand-in held-out material and the stand-in ``~/.ssh``, under the temporary HOME."""
    write(sandbox.held_out / "answers.md", f"{HELD_WORD}\n")
    write(sandbox.held_out / "cases" / "test_hidden.py", f"# {HELD_WORD}\n")
    for name in SSH_FILES:
        write(sandbox.ssh / name, f"stand-in, not a key {SECRET_WORD}\n")


def make_project(sandbox, base=True, extra=None, branch_extra=None, orphan=False):
    """The fixture project: the base commit, then T's own commit on ``w2/W2-95``.

    ``base`` True: the base commit is on ``w2/integrate``; False: on ``main``
    and the repository has no ``w2/integrate``. ``orphan`` True: T's branch
    shares no commit with ``w2/integrate`` (git can find no merge base).
    ``extra`` adds files to the base commit, ``branch_extra`` to T's commit.
    """
    make_outside_files(sandbox)
    project = sandbox.project
    files = dict(BASE_FILES)
    for rel in SECRET_FILES:
        files[rel] = f"STAND_IN={SECRET_WORD}\n"
    for ticket in TICKETS:
        files[f".tickets/{ticket.tk}.md"] = ticket_text(ticket)
    files[SETTINGS_REL] = settings_text()
    files[HELD_OUT_LIST_REL] = held_out_text(sandbox.held_out)
    files.update(extra or {})
    for rel, text in files.items():
        write(project / rel, text)
    (project / GUARD_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GUARD_SOURCE, project / GUARD_REL)
    git(project, "init", "-q", "-b", INTEGRATE if base else "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-58 fixture: the base")
    if orphan:
        git(project, "checkout", "-q", "--orphan", f"w2/{T.wbs}")
    else:
        git(project, "checkout", "-q", "-b", f"w2/{T.wbs}")
    branch = dict(BRANCH_FILES)
    branch[f".tickets/{T.tk}.md"] = ticket_text(T, note="Claimed on the ticket branch.")
    branch.update(branch_extra or {})
    for rel, text in branch.items():
        write(project / rel, text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-58 fixture: T's own commit")
    return project


# --------------------------------------------------------------------------
# The evaluation set (DEC-820 (d), DEC-845)
# --------------------------------------------------------------------------

EVAL_SET = "fixture-questions"
VISIBLE_FILES = {"eval/memory/visible/questions.yaml": f"- q1 {WORD}\n- q2 {WORD}\n"}
HIDDEN_FILES = {
    "eval/memory/hidden/answers.yaml": f"q1: {HIDDEN_WORD}-one\nq2: {HIDDEN_WORD}-two\n",
    "eval/memory/answers-extra.yaml": f"q3: {HIDDEN_WORD}-three\n",
}
# Matched by no hidden glob: ``*`` stays in one folder, so ``eval/memory/answers-*.yaml`` leaves it out.
BESIDE_HIDDEN = {"eval/memory/answers-old/notes.yaml": f"notes {WORD}\n"}
SCORER_REL = "eval/score.py"
SCORER = (
    "import pathlib, sys\n"
    "root = pathlib.Path(__file__).resolve().parent\n"
    "answers = (root / 'memory/hidden/answers.yaml').read_text()\n"
    "extra = (root / 'memory/answers-extra.yaml').read_text()\n"
    "given = {'q1': '" + HIDDEN_WORD + "-one', 'q2': 'wrong'}\n"
    "right = sum(1 for k, v in given.items() if f'{k}: {v}' in answers)\n"
    "print(f'score: {right}/{len(given)}')\n"
)
EVAL_FILES = {**VISIBLE_FILES, **HIDDEN_FILES, **BESIDE_HIDDEN, SCORER_REL: SCORER}


def evaluation_block(roles=(RESEARCH,), tickets=(MEASURED.tk,)):
    measures = {}
    if roles:
        measures["roles"] = list(roles)
    if tickets:
        measures["tickets"] = list(tickets)
    return {EVAL_SET: {
        "visible": ["eval/memory/visible/**"],
        "hidden": ["eval/memory/hidden/**", "eval/memory/answers-*.yaml"],
        "measures": measures,
    }}


def path_map_text(block):
    """The kernel template's path map with an ``evaluation_sets`` block (``block`` written as given)."""
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document["evaluation_sets"] = block
    return yaml.safe_dump(document, sort_keys=False)


def make_eval_project(sandbox, block=None, base=True):
    files = dict(EVAL_FILES)
    files[PATH_MAP_REL] = path_map_text(evaluation_block() if block is None else block)
    return make_project(sandbox, base=base, extra=files)


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
    """Run the project's guard once, as the harness does before a call."""
    project = Path(project or sandbox.project)
    data = {
        "session_id": "w2-58-acceptance-session",
        "transcript_path": str(sandbox.elsewhere / "transcript.jsonl"),
        "cwd": str(project),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_w2_58_{next(_CALLS):06d}",
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


@dataclass(frozen=True)
class Call:
    """One tool call: its tool and its input. ``label`` is what a failure message shows."""
    tool: str
    input: dict
    label: str

    def __str__(self):
        return self.label


def read(path):
    return Call("Read", {"file_path": str(path)}, f"Read {path}")


def grep(path=None, pattern=WORD, glob=None):
    data = {"pattern": pattern, "output_mode": "content"}
    if path is not None:
        data["path"] = str(path)
    if glob is not None:
        data["glob"] = glob
    where = f"path {path}" if path is not None else "no path"
    return Call("Grep", data, f"Grep {pattern!r} ({where}{', glob ' + glob if glob else ''})")


def glob_call(pattern, path=None):
    data = {"pattern": pattern}
    if path is not None:
        data["path"] = str(path)
    return Call("Glob", data, f"Glob {pattern!r}" + (f" in {path}" if path is not None else ""))


def bash(command):
    return Call("Bash", {"command": command, "description": "W2-58 acceptance call"}, f"Bash `{command}`")


def write_call(path):
    return Call("Write", {"file_path": str(path), "content": "written by the W2-58 acceptance test\n"},
                f"Write {path}")


def edit_call(path):
    return Call("Edit", {"file_path": str(path), "old_string": "hooks", "new_string": "hooks"}, f"Edit {path}")


def q(path):
    return shlex.quote(str(path))


def assert_allowed(result, call, who=""):
    assert result.decision == "allow", f"{who}{call} was not allowed: {result.describe()}"


def assert_refused(result, call, who=""):
    assert result.decision == "deny", f"{who}{call} was not refused: {result.describe()}"
    assert result.reason.strip(), f"{who}{call} was refused without a reason: {result.describe()}"


@dataclass(frozen=True)
class World:
    """A sandbox and its fixture project, shared by the read-only cases of one module."""
    sandbox: Sandbox
    project: Path

    def path(self, rel):
        return self.project / rel

    def ask(self, call, role, ticket=None):
        ticket = ticket or TICKET_OF[role]
        return ask_guard(self.sandbox, call.tool, call.input, role, ticket.tk, self.project)


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
        return (f"{' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-2000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")


def run_gov(sandbox, cwd, *args, timeout=COMMAND_TIMEOUT_S):
    try:
        done = subprocess.run(gov_argv(*args), cwd=str(cwd), env=base_environment(sandbox),
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
    return Run(("gov", *args), done.returncode, done.stdout, done.stderr)


def run_in_project(sandbox, project, argv, role=None, ticket=None, timeout=COMMAND_TIMEOUT_S, extra_path=()):
    """Run a command in the project as a session's shell would (no guard: the guard was asked before).

    ``extra_path`` adds folders to the child's PYTHONPATH (pytest's own, which a
    temporary HOME hides when it lives in the user's site folder).
    """
    env = base_environment(sandbox, role, ticket, project)
    if extra_path:
        env["PYTHONPATH"] = os.pathsep.join([env["PYTHONPATH"], *map(str, extra_path)])
    done = subprocess.run(argv, cwd=str(project), env=env, capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr)


# --------------------------------------------------------------------------
# The stand-in CLI for gov launch
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W2-58 acceptance tests). Starts no session; records its --settings."""
import json, os, sys

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
with open(@LOG@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps({"args": args, "settings": settings}) + "\n")
'''


@dataclass(frozen=True)
class Cli:
    path: Path
    log: Path


def install_stand_in_cli(sandbox):
    log = sandbox.elsewhere / "claude-calls.jsonl"
    path = sandbox.home / ".local/bin/claude"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_STUB.replace("@PYTHON@", sys.executable).replace("@LOG@", repr(str(log))), encoding="utf-8")
    path.chmod(0o755)
    return Cli(path, log)


def _calls(cli):
    if not cli.log.is_file():
        return []
    return [json.loads(line) for line in cli.log.read_text(encoding="utf-8").splitlines() if line.strip()]


@dataclass(frozen=True)
class Launch:
    run: Run
    calls: tuple

    def describe(self):
        return f"{self.run.describe()}\nsessions recorded: {len(self.calls)}"

    @property
    def started(self):
        return self.run.returncode == 0 and len(self.calls) == 1

    def settings(self):
        assert self.started, f"gov launch did not start exactly one session\n{self.describe()}"
        entries = self.calls[0]["settings"]
        assert len(entries) == 1, f"the session was started with {len(entries)} --settings values\n{self.describe()}"
        data = json.loads(entries[0])
        assert isinstance(data, dict), "the --settings value is not a JSON object"
        return data


def launch(sandbox, cli, role, ticket):
    before = len(_calls(cli))
    run = run_gov(sandbox, sandbox.project, "launch", role, ticket.tk)
    return Launch(run, tuple(_calls(cli)[before:]))


# --------------------------------------------------------------------------
# The Read rules of a --settings value, read as the CLI reads them
# --------------------------------------------------------------------------

def read_deny_specs(settings):
    """The specifiers of the ``permissions.deny`` rules of the Read tool."""
    rules = (settings.get("permissions") or {}).get("deny") or []
    found = []
    for rule in rules:
        match = re.fullmatch(r"\s*Read\((.*)\)\s*", str(rule), re.S)
        if match:
            found.append(match.group(1).strip())
    return found


def absolute_pattern(spec, project, home):
    """The absolute pattern of a rule specifier: ``//abs``, ``~/home``, else relative to the project."""
    if spec.startswith("//"):
        return spec[1:]
    if spec.startswith("~/"):
        return f"{home}/{spec[2:]}"
    if spec.startswith("./"):
        spec = spec[2:]
    elif spec.startswith("/"):
        spec = spec[1:]
    return f"{project}/{spec}"


def _regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[":
            end = pattern.find("]", i + 2)
            if end == -1:
                out.append(re.escape(c))
            else:
                body = pattern[i + 1:end]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append(f"[{body}]")
                i = end + 1
                continue
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("".join(out) + r"/?")


def rule_covers(spec, path, project, home):
    """Whether a Read deny rule keeps the file tools from ``path``: it matches the path or a folder above it."""
    pattern = _regex(absolute_pattern(spec, str(project), str(home)))
    path = os.path.normpath(str(path))
    candidates = [path]
    parent = os.path.dirname(path)
    while parent and parent != "/":
        candidates.append(parent)
        parent = os.path.dirname(parent)
    return any(pattern.fullmatch(candidate) for candidate in candidates)


def covering_read_rules(settings, project, home, path):
    return [spec for spec in read_deny_specs(settings) if rule_covers(spec, path, project, home)]


def _strings(entries):
    if isinstance(entries, list):
        return [str(e) for e in entries]
    return [str(entries)] if entries else []


def sandbox_read_denials(settings):
    """The read denials of the settings' sandbox block.

    Every list under ``sandbox.filesystem`` that denies reads: ``denyRead``, or a
    ``read`` block's ``denyOnly`` / ``deny``, the name the CLI's own runtime
    configuration of the commands' sandbox uses (``filesystem.read.denyOnly``).
    """
    block = (settings.get("sandbox") or {}).get("filesystem") or {}
    found = []
    if not isinstance(block, dict):
        return found
    for key, value in block.items():
        if "read" not in str(key).lower():
            continue
        if isinstance(value, dict):
            for inner, entries in value.items():
                if "deny" in str(inner).lower():
                    found += _strings(entries)
        elif "deny" in str(key).lower():
            found += _strings(value)
    return found


def _sandbox_entry_covers(entry, path, project, home):
    """A sandbox entry covers ``path`` if it does read as a rule specifier or as an absolute path (``/abs``)."""
    if rule_covers(entry, path, project, home):
        return True
    return entry.startswith("/") and not entry.startswith("//") and rule_covers("/" + entry, path, project, home)


def read_denials_covering(settings, project, home, path):
    """Every OS-level or file-tool read denial of the settings that covers ``path``: its ``Read`` deny rules (which
    the CLI also turns into read denials of the session's own commands, P-W2-58-1) and its sandbox read denials."""
    found = [f"Read({spec})" for spec in covering_read_rules(settings, project, home, path)]
    found += [f"sandbox read denial {entry}" for entry in sandbox_read_denials(settings)
              if _sandbox_entry_covers(entry, path, project, home)]
    return found


def read_denial_faults(settings, project, home, rels):
    """DEC-873 item 2: the read denials of the settings that cover any of ``rels``; empty when none does.

    The launcher adds no OS-level Read rule for (c) or (d), because running a
    test means reading it: the CLI turns every ``Read`` deny rule that matches
    existing files into a read denial of the session's own commands, whatever its
    form (``<folder>/**``, ``<file>*``, ``W2-5[8]/**``; P-W2-58-1), so no ``Read``
    deny rule and no sandbox read denial may cover these files. The guard alone
    refuses them.
    """
    faults = []
    for rel in rels:
        covering = read_denials_covering(settings, project, home, Path(project) / rel)
        if covering:
            faults.append(f"{rel} is covered by {covering}")
    return faults


HELD_OUT_SAMPLES = ("answers.md", "cases/test_hidden.py")


def held_out_faults(settings, sandbox, project):
    """DEC-873 item 2: the held-out material's ``Read`` rules (b) stay; the files of the stand-in material it misses."""
    specs = read_deny_specs(settings)
    return [str(sandbox.held_out / rel) for rel in HELD_OUT_SAMPLES
            if not any(rule_covers(spec, sandbox.held_out / rel, project, sandbox.home) for spec in specs)]


def tracked_files(project):
    return [rel for rel in git(project, "ls-files", "-z").split("\0") if rel]


# --------------------------------------------------------------------------
# The path-map schema
# --------------------------------------------------------------------------

def schema_validator():
    import jsonschema

    store = {}
    for path in SCHEMAS.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        store[path.name] = document
        if isinstance(document, dict) and "$id" in document:
            store[document["$id"]] = document
    schema = store[PATH_MAP_SCHEMA.name]
    resolver = jsonschema.RefResolver(base_uri=schema.get("$id", ""), referrer=schema, store=store)
    return jsonschema.Draft202012Validator(schema, resolver=resolver)
