"""Support code for W2-77's acceptance tests: the nightly's clean-up removes only its own clone, by its exact path.

How the tests run (README, "How the suite runs"):

- **Through public interfaces only:** the nightly command ``python3 -m gov.close.nightly <branch> --root <project>
  --json`` (its API-0002 envelope, its exit code, its standard error and its record under ``docs/close/nightly/``),
  the batch command ``python3 -m gov.close.batch run <ticket>`` (W2-68's support, imported), and git's own view of
  the repository: ``git worktree list --porcelain``, the administrative folders under the common git directory, and
  the index a worktree holds. Every process runs this worktree's ``src/`` (``PYTHONPATH``, DEC-732).
- **The git commands a night runs** are seen through a stand-in ``git`` first on ``PATH``: it writes one line per
  call (its arguments) to a log of the case's own and hands the call to the real git unchanged. With
  ``fail_remove`` it refuses ``git worktree remove`` alone, so that the clone's removal fails.
- **The clone a night adds is told by the night's own suite:** the tiny suite's probe test writes its worktree's top
  folder and its git directory (the clone's administrative entry) to a file outside the project; with ``lock`` it
  also runs ``git worktree lock`` on the worktree it runs in, so that the nightly's single ``--force`` removal fails.
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under the
  case's own temporary folder; a hidden folder's permissions are restored in a ``finally``.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_W2_66 = str(_HERE.parent / "W2-66")
if _W2_66 not in sys.path:
    sys.path.insert(0, _W2_66)

import w2_66_support as nightly_support  # noqa: E402

close_support = nightly_support.close_support
cli_support = nightly_support.cli_support

REPO_ROOT = nightly_support.REPO_ROOT
SRC = nightly_support.SRC

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

NIGHTLY_MODULE = "gov.close.nightly"
NIGHTLY_DIR_REL = nightly_support.NIGHTLY_DIR_REL
COMMAND = "nightly"
EXIT_OK, EXIT_RED = 0, 3
NIGHTLY_RED = "NIGHTLY_RED"
GREEN, RED = "green", "red"
FULL = "full"

# The night's record as it is today (``src/gov/close/nightly.py`` on the base, without ``--coverage``): every key,
# and no other. The ``cleanup`` key is added only when the clone's removal by its path did not succeed.
RECORD_KEYS = frozenset({"branch", "head", "tree", "base", "scope", "verdict", "junit_xml", "failures", "packages",
                         "tests_run", "findings", "per_test_timeout", "distribution", "tmp_path_retention_policy",
                         "created"})
CLEANUP_KEY = "cleanup"
CLEANUP_FIELDS = ("ok", "clone", "entry", "entry_removed", "error")

NIGHTLY_TIMEOUT_S = 600

# --------------------------------------------------------------------------
# git, with no configuration of the machine's
# --------------------------------------------------------------------------


def git_run(cwd, *args):
    """``git -C <cwd> <args>`` with no global or system configuration: the completed process, never raised."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path(cwd).parent), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)


def same_path(one, other):
    return os.path.realpath(str(one)) == os.path.realpath(str(other))


def registered(root):
    """The worktrees ``git worktree list --porcelain`` of the main repository names: ``{real path: its lines}``."""
    done = git_run(root, "worktree", "list", "--porcelain")
    assert done.returncode == 0, f"git worktree list failed in {root}:\n{done.stderr}"
    found, current = {}, None
    for line in done.stdout.splitlines():
        if line.startswith("worktree "):
            current = os.path.realpath(line[len("worktree "):])
            found[current] = []
        elif current is not None and line:
            found[current].append(line)
    return found


def is_registered(root, path):
    return os.path.realpath(str(path)) in registered(root)


def admin_entries(root):
    """The administrative entries under the common git directory's ``worktrees/``: ``{name: path}``."""
    folder = Path(root) / ".git" / "worktrees"
    return {p.name: p for p in sorted(folder.iterdir())} if folder.is_dir() else {}


# --------------------------------------------------------------------------
# The stand-in git: a log of every call, and a removal that fails
# --------------------------------------------------------------------------

_SEP = "\x1f"


def git_stand_in(folder, log, fail_remove=False):
    """Write a stand-in ``git`` into ``folder``: each call adds one line (its arguments) to ``log``, then runs the
    real git with the same arguments; with ``fail_remove`` a ``git worktree remove`` is refused (exit 1, a message
    on standard error) and nothing else is."""
    real = shutil.which("git")
    assert real, "git is not on PATH"
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    text = (
        f"#!{sys.executable} -I\n"
        "import os\nimport sys\n"
        "args = sys.argv[1:]\n"
        f"line = {_SEP!r}.join(args) + '\\n'\n"
        f"fd = os.open({str(log)!r}, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)\n"
        "os.write(fd, line.encode('utf-8', 'surrogateescape'))\n"
        "os.close(fd)\n"
    )
    if fail_remove:
        text += (
            "for at, word in enumerate(args[:-1]):\n"
            "    if word == 'worktree' and args[at + 1] == 'remove':\n"
            "        sys.stderr.write('fatal: W2-77 stand-in: git worktree remove refused\\n')\n"
            "        sys.exit(1)\n"
        )
    text += f"os.execv({real!r}, [{real!r}] + args)\n"
    script = folder / "git"
    script.write_text(text, encoding="utf-8")
    script.chmod(0o755)
    return script


def git_calls(log):
    """Every call the stand-in logged: a list of argument lists."""
    path = Path(log)
    if not path.is_file():
        return []
    return [line.split(_SEP) for line in path.read_text(encoding="utf-8").splitlines() if line]


def worktree_command(call):
    """The ``git worktree`` subcommand of a call (``add``, ``remove``, ``prune``, ...); None for any other call."""
    for at, word in enumerate(call[:-1]):
        if word == "worktree":
            return call[at + 1]
    return None


def worktree_calls(calls, subcommand):
    return [call for call in calls if worktree_command(call) == subcommand]


def added_path(call):
    """The path of a ``git worktree add`` call: its first argument after ``add`` that is no option."""
    rest = call[call.index("add") + 1:]
    paths = [word for word in rest if not word.startswith("-")]
    return paths[0] if paths else None


# --------------------------------------------------------------------------
# The tiny project
# --------------------------------------------------------------------------

PROBE_CASE = "test_w2_77_probe"
PLAIN_CASE = "test_w2_77_plain"
RED_CASE = "test_w2_77_reads_the_data"
PROBE_REL = f"tests/{PROBE_CASE}.py"
PLAIN_REL = f"tests/{PLAIN_CASE}.py"
RED_REL = "tests/test_w2_77_red.py"
RED_TEST = f"{RED_REL}::{RED_CASE}"
DATA_REL = "data.txt"
BROKEN = "BROKEN"
LOCK_REASON = "W2-77: a planted lock, so that the clone's removal by its path fails"


def probe_test(told_clone, lock):
    """The suite's probe: tells the worktree it runs in (its top folder and its git directory) and, with ``lock``,
    locks that worktree. It always passes."""
    return (
        "import os\nimport subprocess\n\n\n"
        f"def {PROBE_CASE}():\n"
        "    here = os.path.dirname(os.path.abspath(__file__))\n\n"
        "    def git(*args):\n"
        "        return subprocess.run(['git', *args], cwd=here, capture_output=True, text=True)\n\n"
        "    top = git('rev-parse', '--show-toplevel').stdout.strip()\n"
        "    entry = git('rev-parse', '--absolute-git-dir').stdout.strip()\n"
        f"    with open({str(told_clone)!r}, 'a', encoding='utf-8') as out:\n"
        "        out.write(top + '\\t' + entry + '\\n')\n"
        f"    if {bool(lock)!r}:\n"
        f"        git('worktree', 'lock', '--reason', {LOCK_REASON!r}, top)\n"
    )


def red_test(told):
    """A telling test that reads ``data.txt`` and fails where it holds ``BROKEN``."""
    return close_support.telling_test(
        RED_CASE, told,
        body=("data = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "
              f"{DATA_REL!r}), encoding='utf-8').read()\n"
              f"    assert {BROKEN!r} not in data, 'the data is broken: ' + data"))


class Worktree:
    """A second worktree of the project: its folder, its administrative entry (from its own ``.git`` file) and
    the paths staged in its index."""

    def __init__(self, path, entry, staged):
        self.path, self.entry, self.staged = Path(path), Path(entry), tuple(staged)


def add_worktree(root, path, staged=None):
    """A second worktree of the repository at ``root``, at ``path`` (detached at HEAD), with ``staged``
    (``{rel: text}``) staged in its index."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    close_support.git(root, "worktree", "add", "-q", "--detach", str(path), "HEAD")
    pointer = (path / ".git").read_text(encoding="utf-8").strip()
    assert pointer.startswith("gitdir: "), f"the worktree's .git file is not a pointer: {pointer!r}"
    for rel, text in (staged or {}).items():
        close_support.write(path, rel, text)
        close_support.git(path, "add", "--", rel)
    return Worktree(path, pointer[len("gitdir: "):], (staged or {}).keys())


class Project:
    """A temporary project the nightly runs on in seconds: a git repository on ``main`` with a tiny suite (the
    probe, a telling test, and with ``red`` a test that reads ``data.txt``), a ``.gitignore`` for
    ``.gov-runtime/``, and nothing else (no test map, no path map: the nightly's defaults).

    With ``red``: the initial commit is green, a green night's record names it, and a later commit breaks
    ``data.txt`` (the culprit), so that the night is red and bisects. ``lock``: the probe locks the clone.
    ``bare``: a branch ``bare`` names a first commit without ``tests/``.
    """

    def __init__(self, base, lock=False, red=False, fail_remove=False):
        self.base = Path(base)
        self.root = self.base / "project"
        self.told = self.base / "told"
        self.probe = self.base / "probe"
        self.log = self.base / "git-calls.log"
        for folder in (self.root, self.told, self.probe):
            folder.mkdir(parents=True, exist_ok=True)
        self.sandbox = cli_support.make_sandbox(self.base / "sandbox")
        self.stand_in = git_stand_in(self.base / "stand-in", self.log, fail_remove=fail_remove)
        self._minute = 0
        close_support.git(self.root, "init", "-q", "-b", "main")
        self._write({"README.md": "# A tiny project\n", ".gitignore": ".gov-runtime/\n", DATA_REL: "fine\n"})
        self.bare = self._commit("a first commit, without tests")
        close_support.git(self.root, "branch", "bare", self.bare)
        files = {PROBE_REL: probe_test(self.probe / "clone", lock),
                 PLAIN_REL: close_support.telling_test(PLAIN_CASE, self.told)}
        if red:
            files[RED_REL] = red_test(self.told)
        self._write(files)
        self.initial = self._commit("the tiny suite")
        self.culprit = None
        if red:
            self.plant_green_night(self.initial)
            self._write({DATA_REL: f"{BROKEN}\n"})
            self.culprit = self._commit("the culprit")

    # -- files and commits ----------------------------------------------------

    def _write(self, files):
        for rel, text in files.items():
            close_support.write(self.root, rel, text)

    def _commit(self, message):
        self._minute += 1
        close_support.commit_all(self.root, message, minute=self._minute)
        return self.head()

    def head(self, ref="HEAD"):
        return close_support.git(self.root, "rev-parse", ref).strip()

    def plant_green_night(self, head):
        """A green night's record naming ``head``, committed (as W2-66's fixture plants one)."""
        tree = close_support.git(self.root, "rev-parse", f"{head}^{{tree}}").strip()
        record = {"branch": "main", "head": head, "tree": tree, "scope": FULL, "verdict": GREEN, "base": None,
                  "junit_xml": [], "failures": [], "packages": []}
        self._write({f"{NIGHTLY_DIR_REL}/NR-20261001T000000Z-{head[:12]}.json": json.dumps(record, indent=2) + "\n"})
        return self._commit("a green night's record")

    def records(self):
        folder = self.root / NIGHTLY_DIR_REL
        return sorted(p.relative_to(self.root).as_posix() for p in folder.glob("NR-*.json")) if folder.is_dir() else []

    # -- other worktrees of the repository ----------------------------------------

    def add_worktree(self, path, staged=None):
        return add_worktree(self.root, path, staged)

    def plant_stale(self, path):
        """A stale registration: a worktree added, then its folder deleted (git's ``prune`` would drop it)."""
        worktree = self.add_worktree(path)
        shutil.rmtree(worktree.path)
        return worktree

    # -- the night ----------------------------------------------------------------

    def env(self):
        env = close_support.sandbox_env(self.sandbox)
        env["PATH"] = str(self.stand_in.parent) + os.pathsep + env["PATH"]
        return env

    def nightly(self, branch="main", *args):
        """``python3 -m gov.close.nightly <branch> --root <project> --json``, this worktree's ``src/``, with the
        stand-in git first on ``PATH``."""
        cmd = [sys.executable, "-m", NIGHTLY_MODULE, branch, *args, "--root", str(self.root), "--json"]
        try:
            done = subprocess.run(cmd, cwd=str(self.root), env=self.env(), capture_output=True, text=True,
                                  timeout=NIGHTLY_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"the nightly command did not end within {NIGHTLY_TIMEOUT_S} s") from None
        return cli_support.Run(tuple(cmd[2:]), done.returncode, done.stdout, done.stderr, 0.0)

    def git_calls(self):
        return git_calls(self.log)

    def clone(self):
        """``(top folder, administrative entry)`` of the clone the night ran its suite in, as its probe told."""
        path = self.probe / "clone"
        assert path.is_file(), "the night's suite did not run its probe: the clone is not known"
        told = {tuple(line.split("\t")) for line in path.read_text(encoding="utf-8").splitlines() if line}
        assert len(told) == 1, f"the probe ran in more than one worktree: {sorted(told)}"
        top, entry = next(iter(told))
        assert not same_path(top, self.root), "the night's suite ran in the project's own working tree, not a clone"
        return Path(top), Path(entry)

    def added_clone(self):
        """The path of the one ``git worktree add`` the night ran (the stand-in's log)."""
        adds = worktree_calls(self.git_calls(), "add")
        assert len(adds) == 1, f"the night ran {len(adds)} git worktree add calls: {adds}"
        return Path(added_path(adds[0]))

    def told_runs(self):
        return close_support.told_by(self.told)


# --------------------------------------------------------------------------
# Hiding a worktree's folder while the night runs (W2-68's F1)
# --------------------------------------------------------------------------

@contextmanager
def moved_aside(path):
    """The folder moved aside (standing for an unmounted or moved folder), and put back afterwards."""
    path = Path(path)
    aside = path.with_name(path.name + ".aside")
    path.rename(aside)
    try:
        yield
    finally:
        aside.rename(path)


@contextmanager
def unreadable(path):
    """The folder made unreadable (permission denied), and its permissions restored afterwards."""
    path = Path(path)
    mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(0)
    try:
        yield
    finally:
        path.chmod(mode)


HIDDEN = {"moved_aside": moved_aside, "unreadable": unreadable}

# --------------------------------------------------------------------------
# Reading what the night left
# --------------------------------------------------------------------------


def envelope(run):
    return run.envelope()


def green(run):
    """The envelope of a green night: ``ok: true``, exit 0; its result."""
    data = run.envelope()
    assert data.get("ok") is True and run.returncode == EXIT_OK, f"the night is not green (exit 0)\n{run.describe()}"
    return data.get("result") or {}


def red(run):
    """The envelope of a red night: ``ok: false``, exit 3, ``NIGHTLY_RED``; its error."""
    data = run.envelope()
    assert data.get("ok") is False and run.returncode == EXIT_RED, f"the night is not red (exit 3)\n{run.describe()}"
    error = data.get("error") or {}
    assert error.get("code") == NIGHTLY_RED, f"a red night's error is not {NIGHTLY_RED}\n{run.describe()}"
    return error


def record_of(project, run):
    """The night's record: the file the envelope names under ``record``, read as JSON; and its path."""
    data = run.envelope()
    body = data.get("result") if data.get("ok") else (data.get("error") or {}).get("details")
    rel = (body or {}).get("record")
    assert isinstance(rel, str) and rel.startswith(NIGHTLY_DIR_REL + "/NR-"), \
        f"the night names no record under {NIGHTLY_DIR_REL}/\n{run.describe()}"
    path = project.root / rel
    assert path.is_file(), f"the night's record {rel} does not exist\n{run.describe()}"
    return json.loads(path.read_text(encoding="utf-8")), rel


def assert_kept(project, worktree, what):
    """``worktree`` keeps its registration, its administrative folder and its staged index."""
    listed = registered(project.root)
    assert os.path.realpath(str(worktree.path)) in listed, \
        f"{what}: {worktree.path} is no longer registered (git worktree list --porcelain: {sorted(listed)})"
    assert worktree.entry.is_dir(), f"{what}: its administrative folder {worktree.entry} is gone"
    inside = git_run(worktree.path, "diff", "--cached", "--name-only")
    assert inside.returncode == 0, f"{what}: git no longer works inside {worktree.path}:\n{inside.stderr}"
    staged = set(inside.stdout.split())
    assert set(worktree.staged) <= staged, \
        f"{what}: its staged change {sorted(worktree.staged)} is gone from its index (staged now: {sorted(staged)})"


def stderr_lines_naming(run, path, also=None):
    """The lines of the night's standard error that name ``path`` (or ``also``, the form the record gives)."""
    names = {str(path), os.path.realpath(str(path))}
    if also:
        names |= {str(also), os.path.realpath(str(also))}
    return [line for line in run.stderr.splitlines() if any(name in line for name in names)]
