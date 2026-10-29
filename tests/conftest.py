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

The conftest sets no base folder and changes no retention count or policy.
"""

from __future__ import annotations

import fcntl
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
_refused = False
_held = None


def _is_worker(config) -> bool:
    return hasattr(config, "workerinput")


def pytest_configure(config):
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
    if _refused or _is_worker(config):
        return
    _sweep(config)
