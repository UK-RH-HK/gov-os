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

- The opt-in suite ``lifted`` (DEC-1061, D-4's cut; T-10): every
  ``tests/optin-lifted*.txt`` lists cases left out of a run unless the run
  opts in with ``--optin=lifted`` or ``GOV_TESTS_OPTIN=lifted``. One entry a
  line: a path (a folder or a test file, from the repository's root) or a
  node id (``file::name``, ``file::Class::name``, ``file::name[row]``), then
  ``#`` and why. ``rep: <path or file::name>`` keeps, of every parametrised
  function under it, only its first collected row in a run that does not opt
  in (the representative); its other rows are the opt-in's. An entry that
  names no collected case deselects nothing. The cases left out are reported
  as deselected; nothing is skipped or deleted, and an opted-in run collects
  every case as before.

The conftest sets no base folder and changes no retention count or policy.
"""

from __future__ import annotations

import fcntl
import hashlib
import os
import re
import stat
import tempfile
from pathlib import Path

import pytest
from _pytest.pathlib import maybe_delete_a_numbered_dir
from _pytest.tmpdir import get_user

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
_OPTIN_NAME = "lifted"
_OPTIN_GLOB = "optin-lifted*.txt"
_TESTS = Path(__file__).resolve().parent
_ROOT = _TESTS.parent


def pytest_addoption(parser):
    parser.addoption("--optin", action="append", default=[], metavar="NAME",
                     help=f"run the opt-in suite NAME too (only '{_OPTIN_NAME}': the cases of "
                          f"tests/{_OPTIN_GLOB}, DEC-1061); also {_OPTIN_ENV}=NAME")


def optin_entries(folder: Path = _TESTS) -> list[tuple[str, str, str]]:
    """Every entry of ``folder``'s opt-in lists: ``(kind, target, list file name)``, kind ``case`` or ``rep``."""
    entries = []
    for listing in sorted(folder.glob(_OPTIN_GLOB)):
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


def _opted_in(config) -> bool:
    names = set(config.getoption("optin") or [])
    names |= {name.strip() for name in os.environ.get(_OPTIN_ENV, "").split(",")}
    return _OPTIN_NAME in names


def pytest_collection_modifyitems(config, items):
    if _opted_in(config):
        return
    entries = optin_entries()
    if not entries:
        return
    left = optin_left_out(items, entries)
    if left:
        gone = {id(item) for item in left}
        items[:] = [item for item in items if id(item) not in gone]
        config.hook.pytest_deselected(items=left)


def pytest_configure(config):
    global _rebuild_lock
    _refuse_basetemp(config)
    if _rebuild_lock is None:
        _rebuild_lock = _own_rebuild_lock()


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
    global _rebuild_lock
    if _rebuild_lock is not None:
        _drop_rebuild_lock(*_rebuild_lock)
        _rebuild_lock = None
    if _refused or _is_worker(config):
        return
    _sweep(config)
