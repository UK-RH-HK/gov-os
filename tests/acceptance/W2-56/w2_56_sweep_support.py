"""Support for the R3 follow-up (S1; DEC-1112 (3), DEC-1114): nested test runs, their folders, the places they share.

The cases start real runs of this repository's pytest on a planted one-case suite (``w2_56_sweep_probe.py``), from
the repository's root, so ``tests/conftest.py`` applies to each as to any run. Each run learns its own folders from
inside and writes them down: its daemon folders' folder (``CODEINTEL_DAEMON_BASE``) and the ``gov-path-*`` folders on
its ``PATH`` (the links folder for the code-graph tool off ``PATH``, where the run made one). A run can be held in its
case until a file appears, killed with SIGKILL to its process group (it leads a session of its own), or let end.

**Where the runs make their folders (the place)** is never assumed: it is read from the run (the folder that holds
its ``CODEINTEL_DAEMON_BASE``; its temp root for the links folders). Three settings of the environment:

- ``session``: inside a launched session. A planted session temp folder of the launcher's form (``gov-launch-`` and
  8 letters, mode 0700) under the case's short folder, with ``TMPDIR`` and ``CLAUDE_CODE_TMPDIR`` both
  ``<that folder>/claude-<uid>``, as the CLI sets them for a launched session's commands (W2-56 README, S1).
- ``temp-root``: outside a launched session, ``CLAUDE_CODE_TMPDIR`` removed, ``TMPDIR`` a folder of the case's own.
- ``real-tmp``: outside a launched session with no ``TMPDIR`` at all, so the temp root is the real ``/tmp`` (the
  ordinary run from a shell). Needs a writable ``/tmp``: skipped where it is read-only (the launch sandbox).

**Each run's environment** is the one this test run was started with (``/proc/self/environ``: before any conftest
changed ``os.environ``), so a nested run starts as the next run from the same shell would, with the tool on ``PATH``
where it was; ``PYTEST_*``, ``CODEINTEL_DAEMON_BASE`` and the temp variables are dropped, then the place's set.

**Plants** need no knowledge of a run's owner record: a link, a regular file, a folder of another name, a folder
with no record (a killed run's folder emptied in place, at its own path, so the name is the code's own), each with
its modification time set back where the case says.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import pytest

import w2_56_support as s
import w2_56_sandbox_support as sb

PROBE = s.HERE / "w2_56_sweep_probe.py"
UID = os.getuid()
HOUR = 3600
OLD_S = 25 * HOUR       # past DEC-902's line: last modified more than 24 hours ago
YOUNG_S = 23 * HOUR     # inside it
START_S = 120.0         # a run's start until its case has written its record
RUN_S = 240.0           # a run's whole life
HOLD_S = 200            # a held case lets go by itself after this, and never fails on it
SLACK_S = 15.0          # how much longer than an ordinary run a run with a stuck folder may take
REAL_TMP = Path("/tmp")
SHARED = REAL_TMP / f"gov-cbm-{UID}"   # the default daemon place, which live sessions outside a test run use
PLACES = ("session", "temp-root", "real-tmp")
TEMP_VARIABLES = ("TMPDIR", "TEMP", "TMP", "CLAUDE_CODE_TMPDIR")


# --------------------------------------------------------------------------
# The environment a next run starts with
# --------------------------------------------------------------------------

def initial_environment() -> dict:
    """The environment this process was started with, before any conftest changed ``os.environ``."""
    try:
        raw = Path("/proc/self/environ").read_bytes()
    except OSError:
        return dict(os.environ)
    env = {}
    for item in raw.split(b"\0"):
        key, sep, value = item.partition(b"=")
        if sep and key:
            env[os.fsdecode(key)] = os.fsdecode(value)
    return env or dict(os.environ)


def run_environment(extra: dict) -> dict:
    env = {key: value for key, value in initial_environment().items()
           if not key.startswith("PYTEST_") and key != "CODEINTEL_DAEMON_BASE" and key not in TEMP_VARIABLES}
    env.update(PYTHONPATH=s.python_path(), PYTHONDONTWRITEBYTECODE="1")
    env.update(extra)
    return env


# --------------------------------------------------------------------------
# Nested runs
# --------------------------------------------------------------------------

@dataclass
class Run:
    label: str
    process: subprocess.Popen
    record: Path
    output: Path
    began: float
    ended: float | None = None

    def note(self) -> dict | None:
        try:
            return json.loads(self.record.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def text(self) -> str:
        try:
            return self.output.read_text(encoding="utf-8", errors="replace")[-2500:]
        except OSError:
            return ""

    @property
    def seconds(self) -> float:
        return (self.ended or time.monotonic()) - self.began


class Runs:
    """The nested runs of one case; every one still running when the case ends is killed by its process group."""

    def __init__(self, base: Path, env: dict):
        self.base, self.env, self.all = base, env, []

    def start(self, label: str, *, hold=None, watch=(), prefix=()) -> Run:
        record, output = self.base / f"{label}.json", self.base / f"{label}.out"
        env = dict(self.env, W2_56_SWEEP_RECORD=str(record), W2_56_SWEEP_WATCH=json.dumps([str(p) for p in watch]))
        if hold is not None:
            env.update(W2_56_SWEEP_HOLD=str(hold), W2_56_SWEEP_HOLD_S=str(HOLD_S))
        argv = [*prefix, sys.executable, "-m", "pytest", str(PROBE), f"--rootdir={s.REPO_ROOT}", "-q",
                "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"]
        with output.open("w", encoding="utf-8") as handle:
            process = subprocess.Popen(argv, cwd=str(s.REPO_ROOT), env=env, stdin=subprocess.DEVNULL, stdout=handle,
                                       stderr=subprocess.STDOUT, start_new_session=True)
        run = Run(label, process, record, output, time.monotonic())
        self.all.append(run)
        return run

    def wait_note(self, run: Run, timeout: float = START_S) -> dict:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            note = run.note()
            if note is not None:
                return note
            if run.process.poll() is not None:
                break
            time.sleep(0.05)
        note = run.note()
        assert note is not None, (f"the test run {run.label!r} did not reach its case (exit {run.process.poll()}):\n"
                                  f"{run.text()}")
        return note

    def kill(self, run: Run) -> None:
        """SIGKILL to the run's process group (by its leader's pid, which is the group's id), then reaped."""
        if run.process.poll() is None:
            try:
                os.killpg(run.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        run.process.wait(timeout=30)
        run.ended = run.ended or time.monotonic()

    def finish(self, run: Run, timeout: float = RUN_S) -> int:
        try:
            code = run.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.kill(run)
            raise AssertionError(f"the test run {run.label!r} did not end within {timeout:.0f} s:\n"
                                 f"{run.text()}") from None
        run.ended = time.monotonic()
        return code

    def finished(self, run: Run, timeout: float = RUN_S) -> dict:
        """The run's record, once it has ended with exit 0 (its one case passed)."""
        code = self.finish(run, timeout)
        note = run.note()
        assert code == 0 and note is not None, (f"the test run {run.label!r} did not start or run its case "
                                                f"(exit {code}):\n{run.text()}")
        return note

    def close(self) -> None:
        for run in self.all:
            if run.process.poll() is None:
                self.kill(run)


# --------------------------------------------------------------------------
# A run's folders
# --------------------------------------------------------------------------

def own_folders(note: dict) -> list[str]:
    """The run's daemon folders' folder, then its links folders (where it made any)."""
    assert note.get("daemon_base") and note.get("daemon_base_exists"), (
        f"premise (S1): the run named no daemon folder of its own in CODEINTEL_DAEMON_BASE: {note}")
    return [note["daemon_base"], *note.get("links", [])]


def place_of(note: dict) -> Path:
    """Where the run makes its daemon folders' folder."""
    return Path(note["daemon_base"]).parent


def there(paths) -> list[str]:
    return [str(path) for path in paths if os.path.lexists(path)]


def in_real_tmp(path) -> bool:
    return os.path.realpath(path) == str(REAL_TMP)


# --------------------------------------------------------------------------
# Plants
# --------------------------------------------------------------------------

def age(path, seconds: float) -> None:
    """Set the modification time of ``path`` and everything under it ``seconds`` back (a link: the link's own)."""
    when = time.time() - seconds
    path = Path(path)
    if path.is_dir() and not path.is_symlink():
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files + dirs:
                os.utime(os.path.join(root, name), (when, when), follow_symlinks=False)
    os.utime(path, (when, when), follow_symlinks=False)


def open_up(path) -> None:
    """Give the owner back every folder under ``path`` (a plant may have taken its write bit)."""
    path = Path(path)
    if not path.is_dir() or path.is_symlink():
        return
    for root, dirs, _ in os.walk(path):
        for name in dirs:
            folder = os.path.join(root, name)
            if not os.path.islink(folder):
                try:
                    os.chmod(folder, stat.S_IRWXU)
                except OSError:
                    pass
    try:
        os.chmod(path, stat.S_IRWXU)
    except OSError:
        pass


def remove_own(path) -> None:
    """Remove what this case or its runs made at ``path``: a link as a link, a folder whole, a file."""
    path = Path(path)
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        open_up(path)
        shutil.rmtree(path, ignore_errors=True)


def bare(path, seconds: float = 0.0) -> Path:
    """A folder with no owner record at ``path`` (a killed run's folder emptied in place): one file inside."""
    path = Path(path)
    remove_own(path)
    path.mkdir(mode=0o700)
    (path / "older-code.txt").write_text("no owner record\n", encoding="utf-8")
    if seconds:
        age(path, seconds)
    return path


def stuck(path) -> Path:
    """A folder with no owner record, more than 24 hours old, that its owner cannot simply remove: it and a folder
    inside it have lost their write bit (as a module cache leaves them), the inner one holding a file."""
    path = bare(path)
    inner = path / "stuck"
    inner.mkdir()
    (inner / "kept.txt").write_text("x\n", encoding="utf-8")
    age(path, OLD_S)
    inner.chmod(0o500)
    path.chmod(0o500)
    return path


def link_to_outside(path, target_root: Path) -> tuple[Path, Path]:
    """A link at ``path`` to a folder outside the place holding one file; the link's own time set 25 hours back."""
    path = Path(path)
    remove_own(path)
    target = Path(tempfile.mkdtemp(prefix="target-", dir=target_root))
    (target / "kept.txt").write_text("kept\n", encoding="utf-8")
    age(target, OLD_S)
    os.symlink(target, path)
    age(path, OLD_S)
    return path, target


def plant_folder(where, *, name: str | None = None, prefix: str = "w56-") -> Path:
    """A folder of another name in ``where`` holding one file, 25 hours old: by ``name``, or a fresh name."""
    where = Path(where)
    if name is None:
        path = Path(tempfile.mkdtemp(prefix=prefix, dir=where))
    else:
        path = where / name
        path.mkdir(mode=0o700)
    (path / "kept.txt").write_text("kept\n", encoding="utf-8")
    age(path, OLD_S)
    return path


def plant_file(path) -> Path:
    """A regular file at ``path``, 25 hours old."""
    path = Path(path)
    remove_own(path)
    path.write_text("a file, not a folder\n", encoding="utf-8")
    age(path, OLD_S)
    return path


def kind(path) -> str:
    path = Path(path)
    if path.is_symlink():
        return f"link -> {os.readlink(path)}"
    if path.is_dir():
        return "folder: " + ",".join(sorted(entry.name for entry in path.iterdir()))
    if path.is_file():
        return "file"
    return "missing" if not os.path.lexists(path) else "other"


# --------------------------------------------------------------------------
# The places
# --------------------------------------------------------------------------

@dataclass
class Place:
    name: str
    base: Path
    temp_root: Path
    session: Path | None
    runs: Runs
    planted: list = field(default_factory=list)   # what the case planted outside its base (real /tmp): removed

    def leftovers_in_real_tmp(self) -> list[str]:
        """What this case's runs made in the real /tmp and may have left (killed runs on today's code)."""
        found = []
        for run in self.runs.all:
            note = run.note()
            if not note:
                continue
            for path in [note.get("daemon_base"), *note.get("links", [])]:
                if path and Path(path).parent == REAL_TMP:
                    found.append(path)
            if Path(note.get("temp_root") or "") == REAL_TMP and note.get("pid") is not None:
                for lock in REAL_TMP.glob(f"gov-rebuild-{note['pid']}-*.lock"):
                    try:
                        if lock.stat().st_mtime >= time.time() - (time.monotonic() - run.began) - 5:
                            found.append(str(lock))
                    except OSError:
                        pass
        return found


def real_tmp_refused() -> str | None:
    """Why this case cannot use the real /tmp here, or None."""
    if REAL_TMP.is_symlink() or not REAL_TMP.is_dir():
        return "/tmp is not a folder here"
    try:
        probe = tempfile.mkdtemp(prefix="w56r-probe-", dir=REAL_TMP)
    except OSError as error:
        return (f"the real /tmp cannot be written here ({error.strerror}): the launch sandbox keeps it read-only; "
                "the CTO's lead runs this case outside the sandbox")
    os.rmdir(probe)
    return None


@contextmanager
def place(name: str):
    base = sb.short_base("w56r")
    assert base is not None, "no short folder of the case's own can be made (under /tmp or the temp root)"
    runs = None
    made: Place | None = None
    try:
        session = None
        if name == "session":
            session = Path(tempfile.mkdtemp(prefix=s.TEMP_PREFIX, dir=base))   # the launcher's form, mode 0700
            temp_root = session / f"claude-{UID}"
            temp_root.mkdir(mode=0o700)
            extra = {"TMPDIR": str(temp_root), "CLAUDE_CODE_TMPDIR": str(temp_root)}
        elif name == "temp-root":
            temp_root = base / "t"
            temp_root.mkdir(mode=0o700)
            extra = {"TMPDIR": str(temp_root)}
        elif name == "real-tmp":
            why = real_tmp_refused()
            if why:
                pytest.skip(why)
            temp_root, extra = REAL_TMP, {}
        else:
            raise ValueError(name)
        runs = Runs(base, run_environment(extra))
        made = Place(name, base, temp_root, session, runs)
        yield made
    finally:
        if runs is not None:
            runs.close()
        if made is not None:
            for path in [*made.planted, *made.leftovers_in_real_tmp()]:
                remove_own(path)
        open_up(base)
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------
# A pid namespace of its own (two commands of one sandboxed session each run in one)
# --------------------------------------------------------------------------

def namespace_prefix(spin: int) -> list[str]:
    """``bwrap`` with a pid namespace of its own around a run, the rest of the machine as it is. ``spin`` short
    processes run first inside it, so the run's own pid there is past ``spin``, a pid another namespace that has just
    started does not hold."""
    bwrap = shutil.which("bwrap") or "/usr/bin/bwrap"
    loop = f'i=0; while [ "$i" -lt {int(spin)} ]; do /bin/true; i=$((i+1)); done; "$@"'
    return [bwrap, "--dev-bind", "/", "/", "--proc", "/proc", "--unshare-pid", "--die-with-parent", "--",
            "/bin/sh", "-c", loop, "w56"]


def namespaces_refused() -> str | None:
    """Why a run cannot be put in a pid namespace of its own here, or None."""
    if not shutil.which("bwrap"):
        return "no bwrap on PATH here"
    try:
        done = subprocess.run([*namespace_prefix(0), "/bin/true"], capture_output=True, text=True, timeout=30,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"bwrap cannot be run here: {error}"
    if done.returncode != 0:
        return (f"bwrap cannot make a pid namespace here (the launch sandbox refuses nested namespaces; the CTO's "
                f"lead runs this case outside it): {done.stderr.strip()[:300]}")
    return None
