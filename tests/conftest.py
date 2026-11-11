"""The suites' temp-folder rules (DEC-898, DEC-907 item 2).

- A run given a per-run ``--basetemp`` is refused at the start: a base folder
  of its own skips pytest's clean-up of old ones. ``GOV_ALLOW_BASETEMP=1``
  opens it for a measured trial; no other value does. An xdist worker is
  not refused: pytest-xdist gives each worker a base folder of its own.
- pytest keeps three base folders under ``pytest-of-<user>``, but never
  removes one whose ``.lock`` is younger than three days, and a killed run
  leaves its ``.lock`` behind. At the end of a run, the controlling process
  removes the numbered base folders past pytest's own retention whose run is
  shown to be over. A folder whose run cannot be shown to be over is kept;
  pytest's own three-day rule removes it later.
- Each Bash command of a sandboxed session runs in a PID namespace of its own,
  so a ``.lock``'s pid cannot show whether a run in another command is over:
  the pid may name another process, or a live one the sweeper cannot see.
  The controlling process of a run of these suites therefore holds a shared
  ``flock`` on its own ``.lock`` from the moment its base folder is made, and
  then writes ``.lock-held`` beside it. A run is over when its folder has no
  ``.lock``; when its ``.lock`` is not held but ``.lock-held`` is there (the
  run that held it is gone); or when its ``.lock`` names a pid no namespace
  can have (``pid_max`` or above). Any other folder is kept, whatever its pid.
- ``gov rebuild`` takes a machine-wide lock (W2-76), and the suites' rebuilds
  in throwaway repositories must not queue behind real rebuilds. Each process
  of a run (the controller and every xdist worker) therefore sets
  ``GOV_REBUILD_LOCK`` at configure time, before any test runs and before
  xdist starts its workers, to a lock file of its own in the session's temp
  folder (``tempfile.gettempdir()``); a worker replaces the controller's. At
  the end the file is removed and the variable's former state restored
  (DEC-956 item 2).
- The machine-wide vector cache (W2-126) is shared by every process that
  embeds, so each test gets a ``GOV_VECTOR_CACHE_DIR`` of its own, under the
  run's base folder and named by the test's id (DEC-1042): no test is served
  another's stand-in vectors, and none writes the user's own cache. The folder
  is made only when the test uses the cache; a test may set or unset the
  variable itself.

- The opt-in suites (DEC-1061, D-4's cut; T-10): every ``tests/optin-lifted*.txt``
  lists cases left out of a run unless the run opts in to the list's suite
  with ``--optin=<name>`` or ``GOV_TESTS_OPTIN=<name>`` (several:
  ``lifted,breadth`` or the option given twice). Each ``optin-lifted*breadth*.txt``
  is ``breadth`` (tier 2's cap and the representatives' other rows; the CTO's
  P-1 (b)); every other ``optin-lifted*.txt`` is ``lifted`` (the switched-off
  features' cases, run report-only in D-10's window). One entry a line: a path
  (a folder or a test file, from the repository's root) or a node id
  (``file::name``, ``file::Class::name``, ``file::name[row]``), then ``#`` and
  why. ``rep: <path or file::name>`` keeps, of every parametrised function
  under it, only its first collected row in a run that does not opt in (the
  representative); its other rows are the opt-in's. A case an opted-in list
  names is collected whole, whatever another list's ``rep:`` says, and a case
  the run names by its node id on the command line is always run. An entry
  that names no collected case deselects nothing. The cases left out are
  reported as deselected; nothing is skipped or deleted, and a run that opts
  in to both suites collects every case as before.

- The code graph (W2-56 S1, DEC-799 item 1, T-8): the controlling process of a
  run makes one folder for the run's code-graph daemon folders
  (``gov.codeintel.make_session_base``), names it in ``CODEINTEL_DAEMON_BASE`` before
  xdist starts its workers, and removes it at the end (made under ``/tmp``
  when ``gov`` cannot be imported yet). Each process of the run also names it
  in a mark in its pytest temp base (``gov.codeintel.MARK``, removed at its
  end), so a ``gov`` process a case starts with an environment built anew, on
  a repository under that base, lands its daemon folder there too. The real tool
  (``codebase-memory-mcp``) is on ``PATH`` only while a case of ``_CBM_SUITES``
  runs (W1-16, W1-20, W1-41, W2-69, W2-92, W1-06's digests file); for every other case each ``PATH`` folder that held it when the
  outermost run started (``CODEINTEL_OFF_PATH``, kept by a run started inside
  it) is replaced by a folder of this process's own with links to the rest of
  its entries. A stand-in a case puts on a nested run's ``PATH`` stays.
- A killed run's folders (W2-56 R3, S1): the run's daemon folder and each
  ``gov-path-*`` links folder hold their owner's record inside them
  (``.gov-owner``), a file the process that made the folder holds an
  exclusive ``flock`` on (close-on-exec) for its life; the record appears
  only once held. The kernel lets the lock go when that process dies, in
  whatever pid namespace the next run sees it from, so a pid is never read.
  The controlling process of the next run, at configure (before its first
  case), removes the folders of the run folder's names in the place where it
  made its own (``c???`` in a launched session's temp folder, else
  ``gov-cbm-<uid>-XXXXXXXX``), and the ``gov-path-XXXXXXXX`` folders in its
  temp root, whose record no process holds; a folder with no record only when
  it and its entries were last modified more than 24 hours ago (DEC-902). A
  link, a regular file, another user's folder and any other name are never
  touched, nor is anything inside the shared ``/tmp/gov-cbm-<uid>``; what
  cannot be opened or removed is left, and never fails or holds up the run.

- git's repository-local variables (DEC-1074 (8), DEC-1083; W2-05's R4-1): ``git bisect run`` and git's hooks
  export ``GIT_DIR`` and others to what they start, and a case's ``git init`` in a folder of its own then acts on
  the repository they name (``core.bare = true`` in the project's config, 2026-11-04). Each process of a run (the
  controller before xdist starts its workers, and every worker) removes them from ``os.environ`` when this file is
  imported: the names ``git rev-parse --local-env-vars`` prints, joined with a fixed list (git 2.43's) used alone
  when git cannot answer, and every ``GIT_CONFIG_KEY_<n>`` / ``GIT_CONFIG_VALUE_<n>``. Nothing is restored at the
  end: the run's process is the run's. A case may set one itself (``monkeypatch``).

The conftest sets no base folder and changes no retention count or policy.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import time
from pathlib import Path

import pytest
from _pytest.pathlib import maybe_delete_a_numbered_dir
from _pytest.tmpdir import get_user

# git's repository-local variables as git 2.43 prints them (``git rev-parse --local-env-vars``): used with git's own
# answer, and alone when git cannot answer (DEC-1074 (8)).
_GIT_LOCAL_FALLBACK = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
    "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE", "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE",
    "GIT_INDEX_FILE", "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX", "GIT_SHALLOW_FILE",
    "GIT_COMMON_DIR",
)
_GIT_CONFIG_PAIR = re.compile(r"GIT_CONFIG_(?:KEY|VALUE)_\d+")


def git_local_env_vars() -> set[str]:
    """The names of git's repository-local variables: git's own answer (a newer git may add names) joined with the
    fixed list, so an older git or one that cannot answer still leaves none of git 2.43's behind. git is asked from
    ``/`` with the fixed list's names already out of its environment: the question needs no repository."""
    names = set(_GIT_LOCAL_FALLBACK)
    env = {key: value for key, value in os.environ.items()
           if key not in names and not _GIT_CONFIG_PAIR.fullmatch(key)}
    try:
        done = subprocess.run(["git", "rev-parse", "--local-env-vars"], cwd="/", env=env, capture_output=True,
                              text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return names
    if done.returncode == 0:
        names.update(line.strip() for line in done.stdout.splitlines()
                     if re.fullmatch(r"GIT_[A-Z0-9_]+", line.strip()))
    return names


def drop_git_local_env() -> list[str]:
    """Remove git's repository-local variables from ``os.environ``; return the names removed (DEC-1074 (8))."""
    names = git_local_env_vars()
    gone = sorted(key for key in os.environ if key in names or _GIT_CONFIG_PAIR.fullmatch(key))
    for key in gone:
        del os.environ[key]
    return gone


# At import, in every process of a run: before any hook, fixture or case, and before xdist starts its workers.
drop_git_local_env()

_ALLOW = "GOV_ALLOW_BASETEMP"
_HELD = ".lock-held"
_NUMBERED = re.compile(r"pytest-(\d+)")
_REBUILD_LOCK = "GOV_REBUILD_LOCK"
_VECTOR_CACHE = "GOV_VECTOR_CACHE_DIR"
_refused = False
_held = None
_rebuild_lock = None  # this process's own lock file and the variable's former value


def _is_worker(config) -> bool:
    return hasattr(config, "workerinput")


@pytest.fixture(autouse=True)
def _own_vector_cache(request, tmp_path_factory, monkeypatch):
    """Each test's own machine-wide vector cache folder (W2-126, DEC-1042); made only when used."""
    name = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:16]
    monkeypatch.setenv(_VECTOR_CACHE, str(tmp_path_factory.getbasetemp() / "vector-cache" / name))


@pytest.fixture(autouse=True)
def _own_guard_calls(request, tmp_path_factory, monkeypatch):
    """Each test's own guard call-log folder (ACT-GUARD-CALLLOG-1; DEC-1108 (5), DEC-1109 (2)); made only when used."""
    name = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:16]
    monkeypatch.setenv("GOV_GUARD_CALLS_DIR", str(tmp_path_factory.getbasetemp() / "guard-calls" / name))


def _own_rebuild_lock() -> tuple[str, str | None]:
    """Point ``GOV_REBUILD_LOCK`` at a new lock file of this process's own; return it and the former value."""
    fd, path = tempfile.mkstemp(prefix=f"gov-rebuild-{os.getpid()}-", suffix=".lock", dir=tempfile.gettempdir())
    os.close(fd)
    former = os.environ.get(_REBUILD_LOCK)
    os.environ[_REBUILD_LOCK] = path
    return path, former


def _drop_rebuild_lock(path: str, former: str | None) -> None:
    if former is None:
        os.environ.pop(_REBUILD_LOCK, None)
    else:
        os.environ[_REBUILD_LOCK] = former
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


_OPTIN_ENV = "GOV_TESTS_OPTIN"
_OPTIN_NAMES = ("lifted", "breadth")
_OPTIN_GLOB = "optin-lifted*.txt"
_TESTS = Path(__file__).resolve().parent
_ROOT = _TESTS.parent


def pytest_addoption(parser):
    parser.addoption("--optin", action="append", default=[], metavar="NAME[,NAME]",
                     help=f"run the opt-in suite(s) NAME too ({', '.join(_OPTIN_NAMES)}: the cases of "
                          f"tests/optin-NAME*.txt, DEC-1061); also {_OPTIN_ENV}=NAME[,NAME]")


def optin_name(listing: Path) -> str:
    """The opt-in suite a list belongs to, by its file name: every ``optin-lifted*breadth*.txt`` is ``breadth``
    (``optin-lifted-breadth.txt``, ``optin-lifted-guard-breadth.txt``), every other ``optin-lifted*.txt`` is
    ``lifted`` (``optin-lifted.txt``, ``optin-lifted-guard.txt``)."""
    return "breadth" if "breadth" in Path(listing).name else "lifted"


def optin_entries(folder: Path = _TESTS, skip=()) -> list[tuple[str, str, str]]:
    """Every entry of ``folder``'s opt-in lists but those of the suites in ``skip``: ``(kind, target, list file
    name)``, kind ``case`` or ``rep``."""
    entries = []
    for listing in sorted(folder.glob(_OPTIN_GLOB)):
        if optin_name(listing) in skip:
            continue
        for raw in listing.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            kind = "case"
            if line.startswith("rep:"):
                kind, line = "rep", line[len("rep:"):].strip()
            if line:
                entries.append((kind, line, listing.name))
    return entries


def _target(entry: str, root: Path = _ROOT) -> tuple[Path, str]:
    """An entry's path (absolute) and its node part after the first ``::`` (empty for a path)."""
    path, _, rest = entry.partition("::")
    return (root / path.rstrip("/")).resolve(), rest


class _Targets:
    """A set of entries' targets, looked up per item: whole paths (folders or files) and node parts per file."""

    def __init__(self, targets):
        self.paths, self.parts = set(), {}
        for path, rest in targets:
            if rest:
                self.parts.setdefault(path, []).append(rest)
            else:
                self.paths.add(path)

    def names(self, here: Path, part: str) -> bool:
        if here in self.paths or not self.paths.isdisjoint(here.parents):
            return True
        return any(part == rest or part.startswith(rest + "[") or part.startswith(rest + "::")
                   for rest in self.parts.get(here, ()))


def optin_left_out(items, entries) -> list:
    """The items a run that does not opt in leaves out, in collection order."""
    cases = _Targets(_target(target) for kind, target, _ in entries if kind == "case")
    reps = _Targets(_target(target) for kind, target, _ in entries if kind == "rep")
    resolved, seen, out = {}, set(), []
    for item in items:
        key = str(item.path)
        here = resolved.get(key) or resolved.setdefault(key, Path(key).resolve())
        part = item.nodeid.partition("::")[2]
        if cases.names(here, part):
            out.append(item)
            continue
        if getattr(item, "callspec", None) is not None and reps.names(here, part):
            function = (key, part.partition("[")[0])
            if function in seen:
                out.append(item)
            else:
                seen.add(function)
    return out


def _opted_in(config) -> set[str]:
    """The opt-in suites the run names, by option or variable, each comma-separated."""
    given = [*(config.getoption("optin") or []), os.environ.get(_OPTIN_ENV, "")]
    return {name.strip() for value in given for name in value.split(",") if name.strip()}


def pytest_collection_modifyitems(config, items):
    opted = _opted_in(config)
    entries = optin_entries(skip=opted)
    if not entries:
        return
    left = optin_left_out(items, entries)
    asked = [arg.split(" ")[0] for arg in config.args if "::" in arg]
    if left and asked:
        # A case the run names by its node id on the command line is run: the caller asked for it by name.
        here = Path(str(config.invocation_params.dir))
        targets = [("case", str((here / arg.partition("::")[0]).resolve().relative_to(_ROOT)) + "::" +
                    arg.partition("::")[2], "") for arg in asked
                   if (here / arg.partition("::")[0]).resolve().is_relative_to(_ROOT)]
        kept = {id(item) for item in optin_left_out(left, targets)}
        left = [item for item in left if id(item) not in kept]
    if left and opted:
        # A case an opted-in suite's list names is collected whole, whatever another suite's ``rep:`` says.
        named = [(kind, target, name) for kind, target, name in optin_entries()
                 if kind == "case" and optin_name(Path(name)) in opted]
        if named:
            kept = {id(item) for item in optin_left_out(left, named)}
            left = [item for item in left if id(item) not in kept]
    if left:
        gone = {id(item) for item in left}
        items[:] = [item for item in items if id(item) not in gone]
        config.hook.pytest_deselected(items=left)


_CBM_TOOL = "codebase-memory-mcp"
_CBM_MARK = ".gov-cbm-base"  # gov.codeintel.MARK
# The suites (and the one file) that run the real code-graph tool (T-8); every other case runs without it, so none starts
# a daemon outside the run's own folder. W1-41's adopt stage A3, W2-69's rebuild, W2-92's code-graph route and W1-06's digest check need it (D-10).
_CBM_SUITES = frozenset({"W1-16", "W1-20", "W1-41", "W2-69", "W2-92", "test_w1_06_digests.py"})
_cbm_base = None  # this run's daemon folder and CODEINTEL_DAEMON_BASE's former value (the controlling process only)
_off_path: dict = {"folder": None, "links": {}}  # this process's folders of links, per PATH folder that has the tool

# W2-56 R3 (S1): a killed run's folders, removed by the next run.
_OWNER = ".gov-owner"  # the owner's record inside a run folder or a links folder: a file its maker holds flock'd
_STALE_S = 24 * 3600  # a folder with no owner's record is removed only when older than this (DEC-902)
_MKDTEMP = "[a-z0-9_]{8}"  # tempfile.mkdtemp's eight letters
_LAUNCHED_NAMES = re.compile(r"c[a-z0-9]{3}")  # gov.codeintel.make_session_base, in a launched session's temp folder
_LINKS_NAMES = re.compile(f"gov-path-{_MKDTEMP}")  # _without_tool's links folder, in the temp root
_owners: dict = {}  # folder -> the descriptor of its owner's record, held by this process


def _run_names(made: Path):
    """The names of run folders in the place ``made`` (this run's folder) stands in: the form ``made`` itself has
    (``make_session_base``'s short ``c???`` in a launched session's temp folder, else ``gov-cbm-<uid>-XXXXXXXX``); None
    when it has neither."""
    forms = [re.compile(f"gov-cbm-{os.getuid()}-{_MKDTEMP}")]
    if made.parent.name.startswith("gov-launch-"):
        forms.insert(0, _LAUNCHED_NAMES)
    return next((form for form in forms if form.fullmatch(made.name)), None)


def _own(folder) -> None:
    """Put this process's owner's record in ``folder``, held (``flock``, close-on-exec) until ``_disown``. Staged under
    another name and renamed once held, so no other run ever sees the record free while its owner lives."""
    staged = os.path.join(folder, f"{_OWNER}.{os.getpid()}")
    try:
        fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    except OSError:
        return  # no record: the folder is kept by the next run for 24 hours
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, json.dumps({"pid": os.getpid()}).encode())  # for a reader only: the lock decides
        os.rename(staged, os.path.join(folder, _OWNER))
    except OSError:
        os.close(fd)
        try:
            os.unlink(staged)
        except OSError:
            pass
        return
    _owners[str(folder)] = fd


def _disown(folder) -> None:
    fd = _owners.pop(str(folder), None)
    if fd is not None:
        os.close(fd)


def _owner_gone(path: str):
    """``(gone, fd)`` for a run's folder: ``(True, fd)`` with its record locked here when no process holds it (its
    owner is gone); ``(None, None)`` when it holds no record; ``(False, None)`` when the record is held, or is no
    regular file, or cannot be opened."""
    try:
        fd = os.open(os.path.join(path, _OWNER), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    except FileNotFoundError:
        return None, None
    except OSError:
        return False, None
    try:
        if stat.S_ISREG(os.fstat(fd).st_mode):
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True, fd
    except OSError:
        pass
    os.close(fd)
    return False, None


def _stale(path: str, seen: os.stat_result) -> bool:
    """True when the folder and every entry in it were last modified more than ``_STALE_S`` ago."""
    newest = seen.st_mtime
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    newest = max(newest, entry.stat(follow_symlinks=False).st_mtime)
                except OSError:
                    continue
    except OSError:
        pass
    return time.time() - newest > _STALE_S


def _remove_folder(path: str) -> None:
    """Remove a killed run's folder of this user's; its folders are opened to their owner first when that is needed
    (a 0500 folder). Whatever cannot be removed is left."""
    shutil.rmtree(path, ignore_errors=True)
    if not os.path.lexists(path):
        return
    try:
        os.chmod(path, 0o700)
        for top, folders, _files in os.walk(path):
            for name in folders:
                inner = os.path.join(top, name)
                if stat.S_ISDIR(os.lstat(inner).st_mode):  # a link is removed as a link, never followed
                    os.chmod(inner, 0o700)
    except OSError:
        pass
    shutil.rmtree(path, ignore_errors=True)


def _sweep_killed(place, names, keep=()) -> None:
    """W2-56 R3: remove the folders in ``place`` whose names ``names`` matches whole, but those in ``keep``: each that
    is a real folder of this user's whose owner's record no process holds, or that holds no record and is stale
    (``_stale``). Never fails: a place or a folder that cannot be read or removed is left as it is."""
    try:
        with os.scandir(place) as entries:
            found = [entry.path for entry in entries if names.fullmatch(entry.name)]
    except OSError:
        return
    uid = os.getuid()
    for path in found:
        if path in keep:
            continue
        try:
            seen = os.lstat(path)
            if not stat.S_ISDIR(seen.st_mode) or seen.st_uid != uid:
                continue  # a link, a regular file, another user's folder
            gone, fd = _owner_gone(path)
            try:
                if gone or (gone is None and _stale(path, seen)):
                    _remove_folder(path)
            finally:
                if fd is not None:
                    os.close(fd)
        except Exception:  # noqa: BLE001 -- the clean-up never stops the run
            continue


def _own_cbm_base():
    """W2-56 S1: one folder for this run's code-graph daemon folders, named in ``CODEINTEL_DAEMON_BASE``; None without one.
    A run whose ``gov`` cannot be imported at configure time (a nested run whose environment has no ``PYTHONPATH``,
    whose cases put ``src`` on ``sys.path`` themselves) makes the folder under ``/tmp`` all the same."""
    try:
        from gov import codeintel
        made = codeintel.make_session_base()
    except ImportError:
        made = None
        for place in ("/tmp", tempfile.gettempdir()):
            try:
                made = Path(tempfile.mkdtemp(prefix=f"gov-cbm-{os.getuid()}-", dir=place))
                break
            except OSError:
                continue
        if made is None:
            return None
    except Exception:  # noqa: BLE001 -- no place: the code index keeps its own default
        return None
    _own(made)  # W2-56 R3: this run's record first, then a killed run's folders beside it
    names = _run_names(made)
    if names is not None:
        _sweep_killed(made.parent, names, keep={str(made)})
    former = os.environ.get("CODEINTEL_DAEMON_BASE")
    os.environ["CODEINTEL_DAEMON_BASE"] = str(made)
    return made, former


_cbm_marks: list = []  # the marks this process wrote (W2-56 S1), removed at its end


@pytest.fixture(scope="session", autouse=True)
def _cbm_mark(tmp_path_factory):
    """W2-56 S1: the mark naming this run's daemon folder in this process's pytest temp base (``gov.codeintel.MARK``),
    so a ``gov`` process a case starts with an environment built anew, on a repository under that base, finds the
    run's folder too (where the case's own clean-up, in this process, looks for it)."""
    base = os.environ.get("CODEINTEL_DAEMON_BASE") or ""
    if os.path.isabs(base):  # written here, not by gov.codeintel.write_mark: gov may not be importable yet
        try:
            mark = tmp_path_factory.getbasetemp() / _CBM_MARK
            staged = mark.with_name(f"{_CBM_MARK}.{os.getpid()}")
            staged.write_text(json.dumps({"base": base, "pid": os.getpid()}), encoding="utf-8")
            os.replace(staged, mark)
            _cbm_marks.append(mark)
        except OSError:  # no base folder: the variable alone names the folder
            pass
    yield


def _drop_cbm_base(made: Path, former: str | None) -> None:
    if former is None:
        os.environ.pop("CODEINTEL_DAEMON_BASE", None)
    else:
        os.environ["CODEINTEL_DAEMON_BASE"] = former
    shutil.rmtree(made, ignore_errors=True)
    _disown(made)


def _tool_folders(value: str) -> list[str]:
    """The folders of ``value`` (a PATH) that hold the code-graph tool, as real paths, less those in a temp folder
    (a case's stand-in, put on a nested run's PATH: that run may get an environment of the case's own making)."""
    temps = {os.path.realpath(place) for place in ("/tmp", "/var/tmp", tempfile.gettempdir())}
    found = []
    for part in value.split(os.pathsep):
        tool = os.path.join(part, _CBM_TOOL) if part else ""
        if not (tool and os.path.isfile(tool) and os.access(tool, os.X_OK)):
            continue
        real = os.path.realpath(part)
        if not any(real == temp or real.startswith(temp + os.sep) for temp in temps):
            found.append(real)
    return found


def _own_off_path():
    """The folders that held the tool when the outermost run started (``CODEINTEL_OFF_PATH``), kept by a run started
    inside it: a stand-in a case puts on a nested run's PATH stays there. None when the variable was set already."""
    if "CODEINTEL_OFF_PATH" in os.environ:
        return None
    os.environ["CODEINTEL_OFF_PATH"] = os.pathsep.join(_tool_folders(os.environ.get("PATH", "")))
    return True


def _without_tool(value: str) -> str | None:
    """``value`` (a PATH) with each folder that held the code-graph tool when the outermost run started replaced by a
    folder of links to the rest of its entries; None when no such folder is on it."""
    off = {part for part in os.environ.get("CODEINTEL_OFF_PATH", "").split(os.pathsep) if part}
    parts, changed = value.split(os.pathsep), False
    for i, part in enumerate(parts):
        tool = os.path.join(part, _CBM_TOOL) if part else ""
        if not (tool and os.path.isfile(tool) and os.access(tool, os.X_OK)) or os.path.realpath(part) not in off:
            continue
        links = _off_path["links"].get(part)
        if links is None:
            if _off_path["folder"] is None:
                _off_path["folder"] = tempfile.mkdtemp(prefix="gov-path-")
                _own(_off_path["folder"])  # W2-56 R3
            links = tempfile.mkdtemp(dir=_off_path["folder"])
            for name in os.listdir(part):
                if name != _CBM_TOOL:
                    os.symlink(os.path.join(part, name), os.path.join(links, name))
            _off_path["links"][part] = links
        parts[i], changed = links, True
    return os.pathsep.join(parts) if changed else None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """The code-graph tool off PATH for every case but those of ``_CBM_SUITES``, fixtures included (W2-56 S1)."""
    before = os.environ.get("PATH")
    without = None
    if before and _CBM_SUITES.isdisjoint(Path(str(item.path)).parts):
        try:
            without = _without_tool(before)
        except OSError:
            without = None
    if without is not None:
        os.environ["PATH"] = without
    try:
        yield
    finally:
        if without is not None and os.environ.get("PATH") == without:
            os.environ["PATH"] = before


def pytest_configure(config):
    global _rebuild_lock, _cbm_base
    _refuse_basetemp(config)
    if _rebuild_lock is None:
        _rebuild_lock = _own_rebuild_lock()
    if _cbm_base is None and not _is_worker(config):
        _cbm_base = _own_cbm_base()
        _sweep_killed(tempfile.gettempdir(), _LINKS_NAMES, keep=set(_owners))  # W2-56 R3: a killed run's links folders
        _off_path["set"] = _own_off_path()


def _refuse_basetemp(config) -> None:
    global _refused
    if _is_worker(config) or config.option.basetemp is None:
        return
    if os.environ.get(_ALLOW) == "1":
        return
    _refused = True
    raise pytest.UsageError(
        f"a per-run --basetemp ({config.option.basetemp}) is refused (DEC-898, DEC-907 item 2): "
        "a base folder of its own skips pytest's clean-up of old base folders. "
        "Run without --basetemp: pytest keeps its own three base folders under "
        "pytest-of-<user> in the temp folder (add -o tmp_path_retention_policy=failed, DEC-905). "
        f"For a measured trial only, set {_ALLOW}=1."
    )


def _hold(basetemp: Path) -> None:
    """Hold a shared flock on this run's own ``.lock`` while the process lives."""
    global _held
    if _held is not None:
        return
    try:
        fd = os.open(basetemp / ".lock", os.O_RDONLY)
    except OSError:
        return
    fcntl.flock(fd, fcntl.LOCK_SH)
    _held = fd
    try:
        os.close(os.open(basetemp / _HELD, os.O_WRONLY | os.O_CREAT, 0o600))
    except OSError:
        pass  # without the mark the folder is only ever kept


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Hold the ``.lock`` as soon as pytest makes this run's base folder."""
    config = session.config
    factory = getattr(config, "_tmp_path_factory", None)
    if _is_worker(config) or factory is None or factory._given_basetemp is not None:
        return
    make = factory.getbasetemp

    def getbasetemp() -> Path:
        basetemp = make()
        _hold(basetemp)
        return basetemp

    factory.getbasetemp = getbasetemp


def _pid_max() -> int | None:
    try:
        return int(Path("/proc/sys/kernel/pid_max").read_text())
    except (OSError, ValueError):
        return None


def _run_is_over(folder: Path) -> bool:
    """True only when the run that made ``folder`` is shown to be over."""
    lock = folder / ".lock"
    try:
        fd = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False  # a live run holds it
        # Held exclusively here, no run can take the lock and write the mark.
        if os.path.lexists(folder / _HELD):
            return True  # the run that held it is gone
        pid = os.read(fd, 32).decode("ascii", "replace").strip()
    finally:
        os.close(fd)
    limit = _pid_max()
    return pid.isdigit() and limit is not None and int(pid) >= limit


def _pytest_root(factory) -> Path:
    """The ``pytest-of-<user>`` folder pytest's own base folders go in."""
    if factory._basetemp is not None and factory._given_basetemp is None:
        return factory._basetemp.parent
    temproot = Path(os.environ.get("PYTEST_DEBUG_TEMPROOT") or tempfile.gettempdir()).resolve()
    return temproot / f"pytest-of-{get_user() or 'unknown'}"


def _sweep(config) -> None:
    factory = getattr(config, "_tmp_path_factory", None)
    if factory is None:
        return
    root = _pytest_root(factory)
    try:
        st = os.lstat(root)
    except OSError:
        return
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
        return
    own = factory._basetemp
    keep = int(config.getini("tmp_path_retention_count"))
    if config.getini("tmp_path_retention_policy") == "none":
        keep = 0
    numbered = {}
    for entry in os.scandir(root):
        match = _NUMBERED.fullmatch(entry.name)
        if match and entry.is_dir(follow_symlinks=False):
            numbered[int(match.group(1))] = Path(entry.path)
    if not numbered:
        return
    newest = max(numbered)
    for number, folder in sorted(numbered.items()):
        if number > newest - keep or folder == own:
            continue
        if _run_is_over(folder):
            try:
                (folder / ".lock").unlink()
            except FileNotFoundError:
                pass
            except OSError:
                continue
            maybe_delete_a_numbered_dir(folder)


def pytest_unconfigure(config):
    global _rebuild_lock, _cbm_base
    if _rebuild_lock is not None:
        _drop_rebuild_lock(*_rebuild_lock)
        _rebuild_lock = None
    while _cbm_marks:
        try:
            _cbm_marks.pop().unlink()
        except OSError:
            pass
    if _cbm_base is not None:
        _drop_cbm_base(*_cbm_base)
        _cbm_base = None
    if _off_path.pop("set", None):
        os.environ.pop("CODEINTEL_OFF_PATH", None)
    if _off_path["folder"] is not None:
        shutil.rmtree(_off_path["folder"], ignore_errors=True)
        _disown(_off_path["folder"])
        _off_path["folder"], _off_path["links"] = None, {}
    if _refused or _is_worker(config):
        return
    _sweep(config)
