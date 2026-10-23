"""W2-67, KPI 4 (DEC-898): the suites keep pytest's own retention of three base folders, nothing passes a per-run
``--basetemp``, and a full run leaves at most three base folders behind.

Two kinds of case:

- **What the repository says** (no run): the pytest configuration and the Python sources of round 1's folders
  pass no ``--basetemp``, set no base folder and change no retention count.
- **What a run leaves behind**: a nested pytest, bounded to one worker and one tiny case (``w2_67_tmp_probe.py``),
  started from the repository root with the repository's own configuration and a ``TMPDIR`` of the case's own.
  The case first plants older base folders under ``TMPDIR/pytest-of-<user>/``, as earlier runs leave them, then
  counts pytest's base folders (``pytest-<n>``) once the run has ended. The nested run passes no ``--basetemp``.

pytest keeps a base folder whose ``.lock`` is younger than three days: it takes it for a run still going. A run
that is killed (a timeout, a stopped session) never removes its lock, so its folder stays for three days whatever
the retention count; that is how ``/tmp/pytest-of-usain`` came to hold 61 run folders (W2-67's card). A folder
whose lock names a process that is still running is another run's, and stays.
"""

from __future__ import annotations

import ast
import configparser
import getpass
import os
import re
import site
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PROBE = HERE / "w2_67_tmp_probe.py"
KEEP = 3                                  # pytest's own retention (tmp_path_retention_count's default)
OLD_RUNS = 5                              # older base folders a case plants before its run
RUN_TIMEOUT_S = 300
BASETEMP = "--" + "basetemp"              # built, so that this file's own text holds no such argument
RETENTION_KEY = "tmp_path_retention_count"
CONFIG_FILES = ("pyproject.toml", "pytest.ini", "tox.ini", "setup.cfg")
# Round 1's folders (DEC-904 item 5): the root conftest and the folders this round may touch.
ROUND_1 = ("tests/conftest.py", "tests/acceptance/W1-07", "tests/acceptance/W1-25", "tests/acceptance/W1-26",
           "tests/acceptance/W1-27", "tests/acceptance/W2-02", "tests/unit/guard")
NUMBERED = re.compile(r"^pytest-(\d+)$")


# --------------------------------------------------------------------------
# What the repository says
# --------------------------------------------------------------------------

def _ini_options():
    """Every pytest option the repository's configuration files set: (file, key, value)."""
    found = []
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.is_file():
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        pytest_table = data.get("tool", {}).get("pytest", {})
        for table in (pytest_table.get("ini_options", {}), pytest_table):
            for key, value in table.items():
                if key != "ini_options":
                    found.append(("pyproject.toml", key, value))
    for name in CONFIG_FILES[1:]:
        path = REPO_ROOT / name
        if not path.is_file():
            continue
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path, encoding="utf-8")
        for section in ("pytest", "tool:pytest"):
            if parser.has_section(section):
                found.extend((name, key, value) for key, value in parser.items(section))
    return found


def test_the_pytest_configuration_passes_no_basetemp_and_keeps_three_base_folders():
    """Green on the head: a guard."""
    wrong = []
    for name, key, value in _ini_options():
        text = " ".join(value) if isinstance(value, (list, tuple)) else str(value)
        if key == "addopts" and BASETEMP in text:
            wrong.append(f"{name}: addopts passes {BASETEMP} ({text})")
        if key == RETENTION_KEY and str(value).strip() != str(KEEP):
            wrong.append(f"{name}: {RETENTION_KEY} = {value} (pytest's own is {KEEP})")
    assert not wrong, "the configuration changes pytest's base folders (DEC-898):\n" + "\n".join(wrong)


def _round_1_sources():
    for rel in ROUND_1:
        path = REPO_ROOT / rel
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from (item for item in sorted(path.rglob("*.py")) if "__pycache__" not in item.parts)


def _settings_in(path):
    """Where a source passes ``--basetemp`` in an argument list, sets a base folder, or sets the retention count."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)):
            for item in node.elts:
                if isinstance(item, ast.Constant) and isinstance(item.value, str) and \
                        item.value.split("=", 1)[0] == BASETEMP:
                    found.append(f"line {node.lineno}: an argument list passes {item.value!r}")
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                if isinstance(target, ast.Attribute) and target.attr in ("basetemp", "_basetemp"):
                    found.append(f"line {node.lineno}: sets .{target.attr}")
                if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) and \
                        target.slice.value in (RETENTION_KEY, "basetemp"):
                    found.append(f"line {node.lineno}: sets [{target.slice.value!r}]")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setattr" and \
                len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and \
                node.args[1].value in ("basetemp", "_basetemp", RETENTION_KEY):
            found.append(f"line {node.lineno}: setattr(..., {node.args[1].value!r}, ...)")
    return found


def test_no_source_of_round_1_passes_a_per_run_basetemp_or_changes_the_retention():
    """Green on the head: a guard."""
    wrong = {str(path.relative_to(REPO_ROOT)): found for path in _round_1_sources() if (found := _settings_in(path))}
    assert not wrong, f"a per-run base folder or another retention count (DEC-898): {wrong}"


# --------------------------------------------------------------------------
# What a run leaves behind
# --------------------------------------------------------------------------

def _user_root(tmpdir):
    root = Path(tmpdir) / f"pytest-of-{getpass.getuser()}"
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    return root


def _plant_run(root, number, lock_pid=None):
    """A base folder as an earlier run leaves it; with ``lock_pid``, as a run that never ended or is still going
    (pytest writes its pid into ``.lock`` and removes the file when it exits)."""
    folder = root / f"pytest-{number}"
    (folder / "test_something0").mkdir(parents=True)
    (folder / "test_something0" / "left.txt").write_text("left by an earlier run\n", encoding="utf-8")
    if lock_pid is not None:
        (folder / ".lock").write_text(str(lock_pid), encoding="utf-8")
    return folder


def _dead_pid():
    """A pid no process can hold: above the kernel's largest."""
    try:
        return int(Path("/proc/sys/kernel/pid_max").read_text().strip()) + 1
    except (OSError, ValueError):
        return 2 ** 22 + 1


def _base_folders(root):
    return sorted((path.name for path in Path(root).iterdir()
                   if NUMBERED.match(path.name) and path.is_dir() and not path.is_symlink()),
                  key=lambda name: int(NUMBERED.match(name).group(1)))


def _run_probe(tmpdir, home):
    """The nested run: the repository's configuration, one worker, one case, no per-run base folder."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "USER": getpass.getuser(),
        "LOGNAME": getpass.getuser(),
        "TMPDIR": str(tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(REPO_ROOT / "src"),   # DEC-732: this worktree's code
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUSERBASE": site.getuserbase(),   # where pytest and its plugins are installed
    }
    command = [sys.executable, "-m", "pytest", str(PROBE), "--rootdir", str(REPO_ROOT), "-q", "--no-header",
               "-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly"]
    assert BASETEMP not in " ".join(command)
    done = subprocess.run(command, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
                          timeout=RUN_TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the nested run failed:\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}"
    return done


def test_a_run_after_older_runs_leaves_at_most_three_base_folders(tmp_path):
    """Five finished runs' base folders were there before. Green on the head: a guard (pytest's own retention)."""
    tmpdir, home = tmp_path / "tmp", tmp_path / "home"
    home.mkdir()
    root = _user_root(tmpdir)
    for number in range(OLD_RUNS):
        _plant_run(root, number)
    _run_probe(tmpdir, home)
    left = _base_folders(root)
    assert len(left) <= KEEP, f"{len(left)} base folders left behind, more than {KEEP} (DEC-898): {left}"
    assert f"pytest-{OLD_RUNS}" in left, f"the run's own base folder is not among those left: {left}"


def test_a_run_after_killed_runs_leaves_at_most_three_base_folders(tmp_path):
    """Five runs that were killed left their base folders with their ``.lock``, naming processes that no longer
    exist. A full run leaves at most three base folders behind (DEC-898)."""
    tmpdir, home = tmp_path / "tmp", tmp_path / "home"
    home.mkdir()
    root = _user_root(tmpdir)
    dead = _dead_pid()
    for number in range(OLD_RUNS):
        _plant_run(root, number, lock_pid=dead)
    _run_probe(tmpdir, home)
    left = _base_folders(root)
    assert len(left) <= KEEP, (
        f"{len(left)} base folders left behind, more than {KEEP} (DEC-898): {left}. Each older one holds a .lock "
        f"naming pid {dead}, which no process holds: the runs that wrote them were killed."
    )
    assert f"pytest-{OLD_RUNS}" in left, f"the run's own base folder is not among those left: {left}"


def test_a_base_folder_of_a_run_still_going_is_kept(tmp_path):
    """A base folder whose ``.lock`` names a running process belongs to another run: it stays. Green on the head:
    a guard against a clean-up that would remove a running session's folder."""
    tmpdir, home = tmp_path / "tmp", tmp_path / "home"
    home.mkdir()
    root = _user_root(tmpdir)
    running = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        dead = _dead_pid()
        _plant_run(root, 0, lock_pid=dead)
        _plant_run(root, 1, lock_pid=dead)
        held = _plant_run(root, 2, lock_pid=running.pid)
        time.sleep(0.05)
        _run_probe(tmpdir, home)
        assert running.poll() is None, "the process holding the planted lock ended during the run"
        assert held.is_dir() and (held / "test_something0" / "left.txt").is_file(), (
            f"the base folder of a run still going (pid {running.pid}) was removed: {_base_folders(root)}"
        )
    finally:
        running.kill()
        running.wait()
