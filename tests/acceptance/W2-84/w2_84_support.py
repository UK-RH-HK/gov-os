"""Support code for the W2-84 acceptance tests (standard library and PyYAML only).

W2-84 makes the guard's refusal of an evaluation set's hidden part (DEC-820 (d))
cover every tree of the repository: the main tree, every worktree that
``git worktree list`` names, and every run clone under ``~/gov-os-runs/``
(DEC-950 item 1, row W2-H063). The tests drive one public interface: **the
guard**, the kernel's PreToolUse hook
(``template/governance/kernel/hooks/pretooluse.py``), committed into the planted
repository at ``governance/kernel/hooks/`` and run as the harness runs it, with
the call on stdin and the session's identity in ``GOV_ROLE`` and ``GOV_TICKET``
(the form of W2-58's acceptance cases).

**The code under test** is this worktree's ``src/``: every child gets
``PYTHONPATH``, the runner's own value when it has one (DEC-732 sets it per
command), else the ``src`` folder of the worktree that holds this file.

**Everything is planted** in pytest's temporary folders, under a temporary
``HOME`` used for every call. Nothing here reads, lists or plants anything in
this repository's ``fixtures/evaluation/**/hidden/**`` or in the real
``~/gov-os-runs/``: the runs root the guard sees is ``<tmp>/home/gov-os-runs``.

The layout of one world (``make_world``)::

    <base>/home/                         HOME of every call
      repo/                              the planted repository's main tree (branch main)
      gov-os-worktrees/W2-81/            a worktree (branch w2/W2-81: the engineer's own, with its acceptance tests)
      gov-os-worktrees/W2-82/            a worktree (branch w2/W2-82)
      gov-os-worktrees/W2-85/            a worktree whose branch removes the hidden part ("clean")
      gov-os-runs/W2-83/                 an own folder, its marker naming repo's git common directory
      gov-os-runs/W2-83/clone/           a run clone (git clone of repo)
      gov-os-runs/W2-00/a/b/repo/        a clone made by hand, deeper, in a folder with no marker
      held-out-material/                 the stand-in held-out material (W2-58's form)
      outside/                           symbolic links outside every tree
    <base>/systmp/  <base>/elsewhere/  <base>/pycache/  <base>/bin/
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
GUARD_SOURCE = REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
PATH_MAP_REL = "governance/project/path-map.yaml"
RUNS_NAME = "gov-os-runs"                 # the runs root's name in HOME (W2-50, DEC-728)
OWN_MARKER = ".gov-os-repository"         # the own folder's marker (DEC-751 1)

ENGINEER = "engineer"
RESEARCH = "research"
ORCHESTRATOR = "orchestrator"
AUDITOR = "independent-auditor"

COMMAND_TIMEOUT_S = 60.0

# Words only these tests write, so that an output or a decision can be traced to them.
WORD = "zqxw84"                          # in ordinary files
HIDDEN_WORD = "zqxw84hiddenanswer"       # only in the hidden part of the evaluation set
HELD_WORD = "zqxw84heldoutanswer"        # only in the stand-in held-out material
SECRET_WORD = "zqxw84secretvalue"        # only in the stand-in secret
TEST_WORD = "zqxw84testsource"           # only in the engineer's own acceptance tests


def held_out_list():
    """Where the guard reads the held-out list, and its key: the guard's own public constants (DEC-162, DEC-218).

    Taken from the code under test, never written out here.
    """
    path = python_path()
    if path and path not in sys.path:
        sys.path.insert(0, path)
    from gov.guard import heldout
    return heldout.CONFIG_REL, heldout.CONFIG_KEY


def python_path():
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


# --------------------------------------------------------------------------
# The tickets and the evaluation set
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    tk: str
    role: str
    wbs: str
    allowed: tuple

    @property
    def acceptance(self):
        return f"tests/acceptance/{self.wbs}"


# The engineer's ticket: measured by its role (engineer). Its acceptance tests are (c) to it.
ENG = Ticket("DAEO-zz84", ENGINEER, "W2-81", ("src/app/**",))
# A research ticket measured by its ticket id, not by its role.
MEASURED_TK = Ticket("DAEO-zz86", RESEARCH, "W2-86", ("experiments/spikes/exp-984/**",))
# A research ticket no set measures.
FREE_TK = Ticket("DAEO-zz87", RESEARCH, "W2-87", ("experiments/spikes/exp-985/**",))
TICKETS = (ENG, MEASURED_TK, FREE_TK)


def ticket_text(ticket):
    return "\n".join([
        "---",
        f"id: {ticket.tk}",
        "status: in_progress",
        "deps: []",
        "links: []",
        "created: 2026-10-30T07:00:00Z",
        "type: task",
        "priority: 1",
        f"assignee: {ticket.role}",
        f"external-ref: {ticket.wbs}",
        "tags: [wave-2, implementation, standard]",
        f"wbs_id: {ticket.wbs}",
        "title: W2-84 fixture ticket",
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
        f"# {ticket.wbs} W2-84 fixture ticket",
        "",
    ])


EVAL_SET = "fixture-questions"
HIDDEN_FILE = "eval/memory/hidden/answers.yaml"           # under the hidden glob eval/memory/hidden/**
HIDDEN_EXTRA = "eval/memory/answers-extra.yaml"           # matched by the one-folder glob eval/memory/answers-*.yaml
HIDDEN_FOLDER = "eval/memory/hidden"
VISIBLE_FILE = "eval/memory/visible/questions.yaml"
VISIBLE_FOLDER = "eval/memory/visible"
HIDDEN_FILES = {
    HIDDEN_FILE: f"q1: {HIDDEN_WORD}-one\nq2: {HIDDEN_WORD}-two\n",
    HIDDEN_EXTRA: f"q3: {HIDDEN_WORD}-three\n",
}
VISIBLE_FILES = {VISIBLE_FILE: f"- q1 {WORD}\n- q2 {WORD}\n"}


def evaluation_block():
    """The planted set: it measures the role ``engineer`` and the ticket ``DAEO-zz86``."""
    return {EVAL_SET: {
        "visible": [f"{VISIBLE_FOLDER}/**"],
        "hidden": [f"{HIDDEN_FOLDER}/**", "eval/memory/answers-*.yaml"],
        "measures": {"roles": [ENGINEER], "tickets": [MEASURED_TK.tk]},
    }}


def path_map_text():
    """The kernel template's path map with the planted ``evaluation_sets`` block (W2-58's form)."""
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document["evaluation_sets"] = evaluation_block()
    return yaml.safe_dump(document, sort_keys=False)


SECRET_REL = ".env"
OWN_TEST_REL = f"{ENG.acceptance}/test_feature.py"
HELD_SAMPLE = "answers.md"


# --------------------------------------------------------------------------
# The sandbox
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path
    tmpdir: Path
    elsewhere: Path
    pycache: Path
    bin: Path

    @property
    def runs(self):
        """``~/gov-os-runs`` as the guard sees it."""
        return self.home / RUNS_NAME

    @property
    def worktrees_parent(self):
        return self.home / "gov-os-worktrees"

    @property
    def held_out(self):
        return self.home / "held-out-material"

    @property
    def outside(self):
        return self.home / "outside"


def make_sandbox(base):
    base = Path(base).resolve()
    box = Sandbox(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache", base / "bin")
    for directory in (box.home, box.tmpdir, box.elsewhere, box.pycache, box.bin):
        directory.mkdir(parents=True, exist_ok=True)
    return box


def base_environment(sandbox, role=None, ticket=None, project=None, path_first=None):
    path = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    if path_first is not None:
        path = f"{path_first}{os.pathsep}{path}"
    env = {
        "PATH": path,
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
        "GIT_AUTHOR_NAME": "W2-84 acceptance", "GIT_AUTHOR_EMAIL": "w2-84@example.invalid",
        "GIT_COMMITTER_NAME": "W2-84 acceptance", "GIT_COMMITTER_EMAIL": "w2-84@example.invalid",
    }
    if project is not None:
        env["CLAUDE_PROJECT_DIR"] = str(project)
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return env


def git(sandbox, directory, *args):
    """A git command of the fixture (never through the guard), with the sandbox's HOME and no user config."""
    proc = subprocess.run(["git", "-C", str(directory), "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=COMMAND_TIMEOUT_S,
                          env=base_environment(sandbox), stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# The planted repository
# --------------------------------------------------------------------------

OWN_TEST_TEXT = f"# {TEST_WORD} {WORD}\ndef test_the_feature():\n    assert True\n"


def base_files(sandbox, hidden=True):
    """The files of the planted repository's first commit; ``hidden`` False leaves the hidden part out.

    The engineer's own acceptance tests are not among them: they are committed
    on its own branch only (``make_world``), so that a tree's (c) part (DEC-820
    (c)) refuses nothing in the other trees and in the store world, and a
    refusal there is (d)'s.
    """
    held_rel, held_key = held_out_list()
    files = {
        "README.md": f"# W2-84 planted repository {WORD}\n",
        ".gitignore": ".gov-runtime/\n__pycache__/\n.pytest_cache/\n",
        "src/app/main.py": f"VALUE = 1  # {WORD}\n",
        "docs/notes.md": f"notes {WORD}\n",
        SECRET_REL: f"STAND_IN={SECRET_WORD}\n",
        PATH_MAP_REL: path_map_text(),
        held_rel: yaml.safe_dump({held_key: [str(sandbox.held_out)]}, sort_keys=False),
        **VISIBLE_FILES,
    }
    for ticket in TICKETS:
        files[f".tickets/{ticket.tk}.md"] = ticket_text(ticket)
    if hidden:
        files.update(HIDDEN_FILES)
    return files


def make_held_out(sandbox):
    """The stand-in held-out material (W2-58's form), under the temporary HOME."""
    write(sandbox.held_out / HELD_SAMPLE, f"{HELD_WORD}\n")
    write(sandbox.held_out / "cases" / "test_hidden.py", f"# {HELD_WORD}\n")


def init_repository(sandbox, repo, files):
    for rel, text in files.items():
        write(repo / rel, text)
    (repo / GUARD_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GUARD_SOURCE, repo / GUARD_REL)
    git(sandbox, repo, "init", "-q", "-b", "main")
    git(sandbox, repo, "add", "-A")
    git(sandbox, repo, "commit", "-q", "-m", "W2-84 fixture: the base")


def common_dir(repo):
    """The real path of a repository's git common directory, as the own folder's marker names it (DEC-751 1)."""
    return os.path.realpath(os.path.join(str(repo), ".git"))


def make_own_folder(sandbox, name, repo):
    """An own folder under the runs root, with its marker naming ``repo``'s git common directory."""
    own = sandbox.runs / name
    own.mkdir(parents=True, exist_ok=True)
    (own / OWN_MARKER).write_text(common_dir(repo) + "\n", encoding="utf-8")
    return own


@dataclass
class World:
    """A sandbox and the trees of its planted repository."""
    sandbox: Sandbox
    trees: dict                                   # name -> root (Path)
    revs: dict = field(default_factory=dict)      # name -> commit id (12 digits) or branch

    def tree(self, name):
        return self.trees[name]

    def ask(self, call, role, ticket, root, path_first=None, agent_type=None):
        return ask_guard(self.sandbox, call, role, ticket, root, path_first=path_first, agent_type=agent_type)


# The names of the trees of ``make_world``.
MAIN = "main-tree"
WT_OWN = "worktree-W2-81"
WT_OTHER = "worktree-W2-82"
CLONE = "run-clone"
DEEP = "deep-clone"
CLEAN = "clean-worktree-W2-85"
# The trees that hold the hidden part.
TREE_NAMES = (MAIN, WT_OWN, WT_OTHER, CLONE, DEEP)
# The trees a session runs in.
SESSION_ROOTS = (MAIN, WT_OWN, CLONE)


def make_world(base, links=True):
    """The planted repository, three worktrees, a marked run clone and a deeper clone made by hand.

    - ``main``: the first commit, which holds the hidden part; the main tree,
      the worktree W2-82, and both clones are on it;
    - ``w2/W2-81``: the engineer's own branch, which adds its acceptance tests
      (``tests/acceptance/W2-81/``); the worktree W2-81 is on it;
    - ``w2/W2-85``: a branch that removes the hidden part; the worktree W2-85
      (``clean``) is on it and holds neither a hidden file nor the engineer's
      tests, so that a search from above it is refused today for no part of
      its own: what refuses it is the other trees' hidden part.

    ``links`` plants the symbolic links of the link cases: in each session's
    root, ``peek`` to W2-82's hidden folder; outside every tree,
    ``answers-link`` to W2-82's hidden file, ``tree-link`` to W2-82 itself and
    ``clone-link`` to the run clone.
    """
    sandbox = make_sandbox(base)
    make_held_out(sandbox)
    repo = sandbox.home / "repo"
    init_repository(sandbox, repo, base_files(sandbox))
    wt_own = sandbox.worktrees_parent / "W2-81"
    wt_other = sandbox.worktrees_parent / "W2-82"
    clean = sandbox.worktrees_parent / "W2-85"
    git(sandbox, repo, "worktree", "add", "-q", "-b", "w2/W2-81", str(wt_own))
    write(wt_own / OWN_TEST_REL, OWN_TEST_TEXT)
    git(sandbox, wt_own, "add", "-A")
    git(sandbox, wt_own, "commit", "-q", "-m", "W2-84 fixture: the engineer's acceptance tests")
    git(sandbox, repo, "worktree", "add", "-q", "-b", "w2/W2-82", str(wt_other))
    git(sandbox, repo, "worktree", "add", "-q", "-b", "w2/W2-85", str(clean))
    git(sandbox, clean, "rm", "-r", "-q", HIDDEN_FOLDER, HIDDEN_EXTRA)
    git(sandbox, clean, "commit", "-q", "-m", "W2-84 fixture: a branch without the hidden part")
    own = make_own_folder(sandbox, "W2-83", repo)
    clone = own / "clone"
    git(sandbox, sandbox.home, "clone", "-q", str(repo), str(clone))
    deep = sandbox.runs / "W2-00" / "a" / "b" / "repo"
    deep.parent.mkdir(parents=True, exist_ok=True)
    git(sandbox, sandbox.home, "clone", "-q", str(repo), str(deep))
    world = World(sandbox, {MAIN: repo, WT_OWN: wt_own, WT_OTHER: wt_other, CLONE: clone, DEEP: deep,
                            CLEAN: clean})
    for name in TREE_NAMES:
        assert (world.tree(name) / HIDDEN_FILE).is_file(), f"the {name} does not hold the hidden part"
    assert not (clean / "eval" / "memory" / "hidden").exists() and not (clean / HIDDEN_EXTRA).exists()
    assert (wt_own / OWN_TEST_REL).is_file() and not (repo / OWN_TEST_REL).exists()
    if links:
        for name in SESSION_ROOTS:
            os.symlink(wt_other / HIDDEN_FOLDER, world.tree(name) / "peek")
        sandbox.outside.mkdir(parents=True, exist_ok=True)
        os.symlink(wt_other / HIDDEN_FILE, sandbox.outside / "answers-link")
        os.symlink(wt_other, sandbox.outside / "tree-link")
        os.symlink(clone, sandbox.outside / "clone-link")
    return world


# The branch of the store world whose one commit adds the hidden part.
HIDDEN_BRANCH = "w2/W2-88"
STORE_MAIN = "main-tree"
STORE_WT = "worktree-W2-81"


def make_store_world(base):
    """A repository whose trees hold no hidden file, while a commit on another branch holds the hidden part.

    - ``main``: the base (no hidden part), then ``unrelated``: a commit that
      changes ``docs/notes.md`` only;
    - ``w2/W2-88``: from the base, ``hidden``: a commit that adds the hidden
      part (and changes the visible file), then ``after``: a commit that
      changes ``docs/notes.md`` only;
    - the main tree on ``main`` and a worktree on ``w2/W2-81`` (from
      ``main``): neither holds a hidden file.

    ``revs`` gives each commit's id in 12 digits.
    """
    sandbox = make_sandbox(base)
    make_held_out(sandbox)
    repo = sandbox.home / "repo"
    init_repository(sandbox, repo, base_files(sandbox, hidden=False))
    git(sandbox, repo, "checkout", "-q", "-b", HIDDEN_BRANCH)
    for rel, text in HIDDEN_FILES.items():
        write(repo / rel, text)
    write(repo / VISIBLE_FILE, f"- q1 {WORD}\n- q2 {WORD}\n- q3 {WORD}\n")
    git(sandbox, repo, "add", "-A")
    git(sandbox, repo, "commit", "-q", "-m", "W2-84 fixture: the hidden part")
    hidden = git(sandbox, repo, "rev-parse", "--short=12", "HEAD").strip()
    write(repo / "docs/notes.md", f"notes, after the hidden part {WORD}\n")
    git(sandbox, repo, "commit", "-q", "-am", "W2-84 fixture: after the hidden part")
    after = git(sandbox, repo, "rev-parse", "--short=12", "HEAD").strip()
    git(sandbox, repo, "checkout", "-q", "main")
    write(repo / "docs/notes.md", f"notes, unrelated {WORD}\n")
    git(sandbox, repo, "commit", "-q", "-am", "W2-84 fixture: an unrelated change")
    unrelated = git(sandbox, repo, "rev-parse", "--short=12", "HEAD").strip()
    wt = sandbox.worktrees_parent / "W2-81"
    git(sandbox, repo, "worktree", "add", "-q", "-b", "w2/W2-81", str(wt))
    for root in (repo, wt):
        assert not (root / HIDDEN_FOLDER).exists() and not (root / HIDDEN_EXTRA).exists(), (
            f"the store world's tree {root} holds a hidden file")
    return World(sandbox, {STORE_MAIN: repo, STORE_WT: wt},
                 {"hidden": hidden, "after": after, "unrelated": unrelated})


# --------------------------------------------------------------------------
# Stand-ins for git, first on PATH
# --------------------------------------------------------------------------

_GIT_STAND_IN = r'''#!@PYTHON@
"""Stand-in for git (W2-84 acceptance tests): @MODE@ on the worktree command, the real git for everything else."""
import json, os, sys, time

args = sys.argv[1:]
mode = @MODE_VALUE@
log = @LOG@
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(args) + "\n")
if "worktree" in args:
    if mode == "fail":
        sys.stderr.write("fatal: the W2-84 stand-in refuses to list the worktrees\n")
        sys.exit(128)
    if mode == "sleep":
        time.sleep(@SLEEP@)
os.execv(@REAL@, [@REAL@, *args])
'''


@dataclass(frozen=True)
class GitStandIn:
    folder: Path        # put first on PATH
    log: Path | None

    def calls(self):
        if self.log is None or not self.log.is_file():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def worktree_calls(self):
        return [call for call in self.calls() if "worktree" in call]

    def clear(self):
        if self.log is not None and self.log.exists():
            self.log.unlink()


# The guard's git timeout is 5 seconds (DEC-950's design note, item 1): the stand-in sleeps well past it, then
# answers as the real git, so that a guard without the timeout would get a good answer and let the call through.
SLEEP_S = 12


def install_git_stand_in(sandbox, mode, name):
    """A ``git`` in a folder of its own: ``mode`` is ``fail`` (the worktree command fails), ``sleep`` (it sleeps past
    the guard's timeout, then answers) or ``record`` (every call is recorded, and passed on)."""
    real = shutil.which("git")
    assert real, "git is not on PATH"
    folder = sandbox.bin / name
    folder.mkdir(parents=True, exist_ok=True)
    log = sandbox.elsewhere / f"git-calls-{name}.jsonl" if mode == "record" else None
    text = (_GIT_STAND_IN.replace("@PYTHON@", sys.executable).replace("@MODE@", mode)
            .replace("@MODE_VALUE@", repr(mode)).replace("@LOG@", repr(str(log) if log else ""))
            .replace("@SLEEP@", str(SLEEP_S)).replace("@REAL@", repr(os.path.realpath(real))))
    path = folder / "git"
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return GitStandIn(folder, log)


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


@dataclass(frozen=True)
class Call:
    """One tool call: its tool and its input. ``label`` is what a failure message shows."""
    tool: str
    input: dict
    label: str

    def __str__(self):
        return self.label


def ask_guard(sandbox, call, role, ticket, root, path_first=None, agent_type=None):
    """Run the guard committed in ``root`` once, as the harness does before a call of a session rooted there."""
    root = Path(root)
    data = {
        "session_id": "w2-84-acceptance-session",
        "transcript_path": str(sandbox.elsewhere / "transcript.jsonl"),
        "cwd": str(root),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": call.tool,
        "tool_input": call.input,
        "tool_use_id": f"toolu_w2_84_{next(_CALLS):06d}",
    }
    if agent_type is not None:
        data["agent_type"] = agent_type
    tk = ticket.tk if isinstance(ticket, Ticket) else ticket
    try:
        proc = subprocess.run([sys.executable, str(root / GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(root),
                              env=base_environment(sandbox, role, tk, root, path_first=path_first),
                              timeout=COMMAND_TIMEOUT_S)
        returncode, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        returncode, stdout, stderr = None, "", "timed out"
    decision, reason = _decision(returncode, stdout, stderr)
    return Decision(decision, reason, returncode, stdout, stderr)


def read(path):
    return Call("Read", {"file_path": str(path)}, f"Read {path}")


def grep(path, pattern=WORD):
    return Call("Grep", {"pattern": pattern, "path": str(path), "output_mode": "content"},
                f"Grep {pattern!r} in {path}")


def glob_call(pattern, path):
    return Call("Glob", {"pattern": pattern, "path": str(path)}, f"Glob {pattern!r} in {path}")


def bash(command):
    return Call("Bash", {"command": command, "description": "W2-84 acceptance call"}, f"Bash `{command}`")


def q(path):
    return shlex.quote(str(path))


def assert_allowed(result, call, who=""):
    assert result.decision == "allow", f"{who}{call} was not allowed: {result.describe()}"


def assert_refused(result, call, who=""):
    assert result.decision == "deny", f"{who}{call} was not refused: {result.describe()}"
    assert result.reason.strip(), f"{who}{call} was refused without a reason: {result.describe()}"


# Today's rendering of a refusal the guard cannot work out (``PolicyError``), which the design note keeps for the
# new causes (item 7): "<cause>: the call is refused (fail closed, DEC-820)".
FAIL_CLOSED = "fail closed"


def assert_refused_closed(result, call, who=""):
    """Refused because what the session is refused cannot be worked out (fail closed), with a cause."""
    assert_refused(result, call, who)
    assert FAIL_CLOSED in result.reason, (
        f"{who}{call} was refused, but not as a fail-closed refusal with its cause: {result.describe()}")


# --------------------------------------------------------------------------
# File modes, restored for pytest's clean-up
# --------------------------------------------------------------------------

class Modes:
    """Folders made unreadable for one case; ``restore`` gives them back their mode."""

    def __init__(self):
        self.changed: list[tuple[Path, int]] = []

    def lock(self, path):
        path = Path(path)
        self.changed.append((path, path.stat().st_mode & 0o7777))
        path.chmod(0o000)

    def restore(self):
        while self.changed:
            path, mode = self.changed.pop()
            try:
                path.chmod(mode)
            except OSError:
                pass


def unreadable(path):
    """Whether this process (the same user as the guard) is refused a listing of ``path``."""
    try:
        os.listdir(path)
    except PermissionError:
        return True
    return False
