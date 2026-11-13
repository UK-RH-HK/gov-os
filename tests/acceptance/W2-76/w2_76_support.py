"""Support code for the W2-76 acceptance tests: the rebuild's timings, its watchdog and its machine lock (DEC-939
item 2, rows W2-L451 and W2-M408).

The interface under test is public only: ``gov rebuild [--json] [--no-embeddings]``, run as
``sys.executable -m gov.cli.main rebuild ...`` in a temporary repository built from scratch, its standard output (the
API envelope), its standard error, its exit code, the files it leaves under ``.gov-runtime/`` and the project file
``governance/project/rebuild.yaml`` that sets ``slow_after_s`` and ``lock``.

The code under test is this worktree's ``src/``: every child gets the runner's ``PYTHONPATH`` (DEC-732), else this
worktree's ``src/``. A bare ``gov`` is never run.

Every repository these tests rebuild carries a ``rebuild.yaml`` whose ``lock`` is a temporary path: no case takes the
machine's real rebuild lock, and no case waits for the default threshold.

The outside programs the rebuild runs are stood in for through ``PATH`` only:

- the code-graph tool is left off ``PATH`` (the code index then reports itself not recreated, inside a sandbox and
  outside it alike, and no daemon starts);
- the semantic stage's endpoint (``OLLAMA_HOST``) is a closed loopback port: the stage reports itself as it does when
  no endpoint answers;
- ``gitleaks`` is the real one, or a stand-in first on ``PATH`` that sleeps on its first call and then hands on to the
  real one (the planted slow stage: the secrets filter inside the lexical stage).
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import site
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = REPO_ROOT / "src"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
HOLDER_SCRIPT = HERE / "w2_76_holder.py"

REAL_GITLEAKS = shutil.which("gitleaks")
GIT = shutil.which("git")
FLOCK = shutil.which("flock")
TIMEOUT = shutil.which("timeout")

SETTINGS_REL = "governance/project/rebuild.yaml"
RECORD_REL = ".gov-runtime/rebuild/record.json"
RECORD_DIR_REL = ".gov-runtime/rebuild"
MACHINE_LOCK = "/tmp/gov-os-rebuild.lock"

STAGE_KEYS = ("record_s", "lexical_s", "secrets_s", "semantic_s", "codeintel_s", "compaction_s", "total_s")
LOCK_KEYS = ("path", "wait_s", "holder", "held_by_caller", "taken_at", "released_at")
STAGE_NAMES = ("record", "lexical", "secrets", "semantic", "codeintel", "compaction")
ISO_UTC_MICRO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}(Z|\+00:00)$")
LONG_HEX = re.compile(r"[0-9A-Fa-f]{13,}")

# The watchdog's record names its parts in words only in the ticket's design; these are the names a case accepts for
# each part, the first being the recommended one (README, "The record's parts").
PROCESSES_KEYS = ("processes", "procs", "process_tree")
PARENT_KEYS = ("ppid", "parent", "parent_pid")
WCHAN_KEYS = ("wchan", "wait_channel")
CMDLINE_KEYS = ("cmdline", "command_line", "command", "cmd")
LOAD_KEYS = ("load", "loadavg", "load_average")
WRITTEN_KEYS = ("written_at", "write_time", "updated_at", "time", "at", "now")
RUNNING_KEYS = ("stage_running", "running", "current_stage", "running_stage")
RUNNING_FOR_KEYS = ("stage_running_s", "running_s", "running_for_s", "elapsed_s")
DONE_KEYS = ("stages_done", "done", "completed", "stages")

# How long a case waits for one rebuild before it gives up: a wait, not a time the ticket promises. A tiny rebuild
# takes one to three seconds alone; the wait is generous for a loaded machine.
COMMAND_TIMEOUT_S = 120.0
# The bound within which a rebuild under its caller's own hold must end (no deadlock): a stated bound, asserted.
WRAPPED_BOUND_S = 120.0

try:
    import pytest as _pytest

    needs_tools = _pytest.mark.skipif(REAL_GITLEAKS is None or GIT is None,
                                      reason="gitleaks or git is not on PATH: the rebuild cannot run its stages")
    needs_flock = _pytest.mark.skipif(FLOCK is None or TIMEOUT is None,
                                      reason="flock(1) or timeout(1) is not on PATH")
except ImportError:   # pragma: no cover - only used under pytest
    needs_tools = needs_flock = None


# --------------------------------------------------------------------------
# The environment of every child
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    base: Path
    home: Path
    tmpdir: Path
    tools: Path
    locks: Path       # the folder of this case's temporary lock paths
    pycache: Path


def make_box(base):
    base = Path(base).resolve()
    box = Box(base, base / "home", base / "systmp", base / "tools", base / "locks", base / "pycache")
    for folder in (box.home, box.tmpdir, box.tools, box.locks, box.pycache):
        folder.mkdir(parents=True, exist_ok=True)
    return box


def python_path():
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's ``src/``."""
    return os.environ.get("PYTHONPATH") or str(SRC)


def closed_loopback_port():
    """A loopback port nothing listens on (bound, then closed): the semantic stage's endpoint never answers."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def environment(box, tools=None):
    """The rebuild's environment, from scratch: ``tools`` (gitleaks, real or a stand-in) first on PATH, then
    Python's own folder and the system's; no code-graph tool; an endpoint that never answers."""
    tools = Path(tools or box.tools)
    if not (tools / "gitleaks").exists():
        (tools / "gitleaks").symlink_to(REAL_GITLEAKS)
    path = os.pathsep.join([str(tools), str(Path(sys.executable).parent), "/usr/bin", "/bin"])
    host = f"127.0.0.1:{closed_loopback_port()}"
    return {
        "PATH": path,
        "HOME": str(box.home),
        "TMPDIR": str(box.tmpdir),
        "XDG_CACHE_HOME": str(box.home / ".cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONUSERBASE": site.getuserbase(),
        "PYTHONPYCACHEPREFIX": str(box.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OLLAMA_HOST": host,
        "GOV_QUERY_OLLAMA_HOST": host,
        "GOV_OLLAMA_BIN": str(box.base / "no-ollama-here"),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-76 acceptance", "GIT_AUTHOR_EMAIL": "w2-76@example.invalid",
        "GIT_COMMITTER_NAME": "W2-76 acceptance", "GIT_COMMITTER_EMAIL": "w2-76@example.invalid",
    }


def git(directory, *args):
    proc = subprocess.run([GIT, "-C", str(directory), "-c", "user.name=W2-76 acceptance",
                           "-c", "user.email=w2-76@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=60,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# A temporary repository
# --------------------------------------------------------------------------

def path_map_text():
    import yaml

    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document.setdefault("namespaces", {})["docs"] = {
        "paths": ["docs/**", "src/**"],
        "memory_class": "governance",
        "sensitivity": "internal",
        "permitted_roles": ["engineer", "independent-test-designer", "independent-auditor", "orchestrator",
                            "product-spec", "research"],
        "retention": "kept in git history",
        "export_policy": "allowed",
        "embedding_policy": "embedded",
        "provenance": "written by the W2-76 tests",
        "deletion_rebuild": "authoritative; restored from git only",
    }
    return yaml.safe_dump(document, sort_keys=False)


def settings_text(lock, slow_after_s=600):
    return f"slow_after_s: {slow_after_s}\nlock: {json.dumps(str(lock))}\n"


def make_project(box, name, lock, slow_after_s=600, settings=None):
    """A committed repository with an indexed, embedded ``docs/**`` and ``src/**``, the kernel's gitleaks rules, and
    a ``rebuild.yaml`` naming a temporary ``lock`` (or the raw ``settings`` text, for the refusal cases)."""
    project = box.base / name
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    write(project / "governance/project/path-map.yaml", path_map_text())
    write(project / SETTINGS_REL, settings if settings is not None else settings_text(lock, slow_after_s))
    write(project / "docs/notes.md", "# Notes\n\nThe rebuild indexes this text about lanterns and harbours.\n")
    write(project / "docs/more.md", "# More\n\nA second page, about tides.\n")
    write(project / "src/app.py", "def greet(name):\n    return 'hello ' + name\n")
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-76 fixture")
    return project


def set_settings(project, text):
    write(Path(project) / SETTINGS_REL, text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "rebuild.yaml changed")


# --------------------------------------------------------------------------
# The planted slow stage: gitleaks that sleeps on its first call
# --------------------------------------------------------------------------

def slow_gitleaks(box, name, sleep_s):
    """A tools folder whose ``gitleaks`` sleeps ``sleep_s`` on its first call (in this folder), then hands on to the
    real gitleaks; every later call hands on at once. Paths are written into the script: no variable of the
    environment is relied on, so a filter that cleans the environment of gitleaks does not change it."""
    tools = box.base / name
    tools.mkdir(parents=True, exist_ok=True)
    marker = tools / "first-call-taken"
    script = (
        f"#!{sys.executable}\n"
        "import os, sys, time\n"
        "try:\n"
        f"    os.close(os.open({str(marker)!r}, os.O_CREAT | os.O_EXCL | os.O_WRONLY))\n"
        f"    time.sleep({float(sleep_s)!r})\n"
        "except FileExistsError:\n"
        "    pass\n"
        f"os.execv({REAL_GITLEAKS!r}, [{REAL_GITLEAKS!r}] + sys.argv[1:])\n"
    )
    stand_in = write(tools / "gitleaks", script)
    stand_in.chmod(0o755)
    return tools


# --------------------------------------------------------------------------
# Running a rebuild
# --------------------------------------------------------------------------

@dataclass
class Run:
    args: tuple
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float
    pid: int = 0
    started: float = 0.0   # time.time() at the start

    def envelope(self):
        try:
            return json.loads(self.stdout)
        except ValueError:
            return {}

    @property
    def result(self):
        return self.envelope().get("result") or {}

    def describe(self, tail=2500):
        return (f"{' '.join(self.args)}\nexit code: {self.returncode} after {self.seconds:.1f} s\n"
                f"stdout:\n{self.stdout[-tail:]}\nstderr:\n{self.stderr[-tail:]}")


def rebuild_argv(*extra):
    return [sys.executable, "-m", "gov.cli.main", "rebuild", "--json", *extra]


def _kill_group(proc):
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(proc.pid, signal.SIGKILL)


def start(project, env, argv, stdout, stderr):
    return subprocess.Popen(argv, cwd=str(project), env=env, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                            start_new_session=True)


def run(project, env, argv, timeout=COMMAND_TIMEOUT_S):
    """Run ``argv`` in ``project`` to its end (or kill its process group at ``timeout``)."""
    began, wall = time.monotonic(), time.time()
    proc = start(project, env, argv, subprocess.PIPE, subprocess.PIPE)
    try:
        out, err = proc.communicate(timeout=timeout)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        out, err = proc.communicate()
        code = None
    finally:
        _kill_group(proc)
    return Run(tuple(argv), code, out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
               time.monotonic() - began, proc.pid, wall)


def rebuild(project, env, *extra, timeout=COMMAND_TIMEOUT_S):
    return run(project, env, rebuild_argv(*extra), timeout=timeout)


class Background:
    """A rebuild in the background, its output in files, so that a case can read its standard error and its record
    while it runs."""

    def __init__(self, project, env, argv, folder):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.argv = tuple(argv)
        self.out_path, self.err_path = folder / "stdout", folder / "stderr"
        self._out, self._err = open(self.out_path, "wb"), open(self.err_path, "wb")
        self.began, self.started = time.monotonic(), time.time()
        self.proc = start(project, env, argv, self._out, self._err)
        self.pid = self.proc.pid

    def stderr_now(self):
        return self.err_path.read_text(encoding="utf-8", errors="replace")

    def running(self):
        return self.proc.poll() is None

    def finish(self, timeout=COMMAND_TIMEOUT_S):
        try:
            self.proc.wait(timeout=max(1.0, timeout - (time.monotonic() - self.began)))
            code = self.proc.returncode
        except subprocess.TimeoutExpired:
            _kill_group(self.proc)
            self.proc.wait()
            code = None
        finally:
            _kill_group(self.proc)
            self._out.close()
            self._err.close()
        return Run(self.argv, code, self.out_path.read_text(encoding="utf-8", errors="replace"), self.stderr_now(),
                   time.monotonic() - self.began, self.pid, self.started)

    def kill(self):
        _kill_group(self.proc)
        with contextlib.suppress(Exception):
            self.proc.wait(timeout=10)
        self._out.close()
        self._err.close()


def wait_until(predicate, timeout, step=0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(step)
    return predicate()


# --------------------------------------------------------------------------
# A holder of the lock that is not the rebuild's ancestor
# --------------------------------------------------------------------------

class Holder:
    """``w2_76_holder.py``: a sibling process that takes an exclusive flock on ``lock`` and holds it until the case
    creates its release file (or 60 s pass)."""

    def __init__(self, lock, folder):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.release = folder / "release"
        self.proc = subprocess.Popen([sys.executable, str(HOLDER_SCRIPT), str(lock), str(self.release), "60"],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     start_new_session=True)
        line = self.proc.stdout.readline().decode()
        assert line.startswith("held"), f"the stand-in holder did not take {lock}: {line!r}"
        self.pid = self.proc.pid

    def let_go(self):
        self.release.write_text("go", encoding="utf-8")
        with contextlib.suppress(subprocess.TimeoutExpired):
            self.proc.wait(timeout=10)
        _kill_group(self.proc)


def lock_is_free(lock):
    """Whether no one holds ``lock`` (one non-blocking exclusive take by this process, released at once)."""
    with open(lock, "a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        fcntl.flock(handle, fcntl.LOCK_UN)
        return True


# --------------------------------------------------------------------------
# Reading results and records
# --------------------------------------------------------------------------

def read_record(project):
    path = Path(project) / RECORD_REL
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return None, None
    try:
        return json.loads(text), text
    except ValueError:
        return None, text


def first_key(mapping, names):
    """The first of ``names`` that ``mapping`` holds, else None."""
    if not isinstance(mapping, dict):
        return None
    return next((name for name in names if name in mapping), None)


def iso(stamp):
    from datetime import datetime

    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def store_snapshot(project, skip=RECORD_DIR_REL):
    """Every file under ``.gov-runtime/`` but the rebuild's record folder, with its digest."""
    runtime = Path(project) / ".gov-runtime"
    found = {}
    if runtime.is_dir():
        for path in sorted(runtime.rglob("*")):
            rel = path.relative_to(project).as_posix()
            if rel == skip or rel.startswith(skip + "/") or not path.is_file() or path.is_symlink():
                continue
            found[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def error_text(run_):
    """The refusal's code, message and details, as one text."""
    error = run_.envelope().get("error") or {}
    return error.get("code"), json.dumps(error)
