"""W2-96 (DAEO-ouet): builder tests of ``gov accept``'s clean-up after review 3 (DEC-970): the removal of the
private folder tolerates a process that changes it meanwhile or removes it first (R14), and its time grows with
the entries, not their square (R15).

Each test plants a tiny project, or a tree, in a temporary folder; the signal test starts ``gov accept`` as its
own process. Nothing runs against this repository's own acceptance folders.
"""

from __future__ import annotations

import errno
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

from gov.accept import runner
from gov.cli.main import main

MARK = "PLANTED-LEAK-91d4"  # planted in assertions, output and names: must never reach the caller
ONE_LINE = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n"


def _plant(root: Path, tests: dict[str, str]) -> None:
    (root / ".tickets").mkdir(parents=True, exist_ok=True)
    (root / ".tickets" / "DAEO-t001.md").write_text(
        "---\nid: DAEO-t001\nwbs_id: W9-01\nacceptance_tests:\n  path: tests/acceptance/T1/\n---\n# t\n")
    folder = root / "tests" / "acceptance" / "T1"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(ONE_LINE)
    for name, text in tests.items():
        (folder / name).write_text(text)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root, temp = tmp_path / "proj", tmp_path / "tmpdir"
    root.mkdir()
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    monkeypatch.setenv("TMPDIR", str(temp))
    return root, temp


def _tree(top: Path, folders: int = 5, files: int = 20) -> None:
    top.mkdir()
    for i in range(folders):
        inner = top / f"d{i}" / "e"
        inner.mkdir(parents=True)
        for j in range(files):
            (inner / f"f{j}").write_text("x")
            (top / f"d{i}" / f"g{j}").write_text("x")


def _gone(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] == "Z"
    except OSError:
        return True


# --- R14: the removal itself ------------------------------------------------------------------------------------------

def test_w2_96_r14_an_entry_removed_by_another_process_is_passed_over(tmp_path, monkeypatch):
    top = tmp_path / "top"
    _tree(top)
    unlink, rmdir = os.unlink, os.rmdir

    def first_unlink(name, *, dir_fd=None):  # another process removes each file just before the removal does
        unlink(name, dir_fd=dir_fd)
        unlink(name, dir_fd=dir_fd)

    def first_rmdir(name, *, dir_fd=None):
        rmdir(name, dir_fd=dir_fd)
        rmdir(name, dir_fd=dir_fd)

    monkeypatch.setattr(os, "unlink", first_unlink)
    monkeypatch.setattr(os, "rmdir", first_rmdir)
    runner._remove(str(top))
    monkeypatch.undo()
    assert not os.path.lexists(top)


def test_w2_96_r14_a_listed_entry_already_gone_is_passed_over(tmp_path, monkeypatch):
    top = tmp_path / "top"
    _tree(top)
    listdir = os.listdir
    monkeypatch.setattr(os, "listdir", lambda fd: ["ghost-file", "ghost-dir"] + listdir(fd))
    runner._remove(str(top))
    monkeypatch.undo()
    assert not os.path.lexists(top)


def test_w2_96_r14_a_folder_refilled_meanwhile_is_emptied_again(tmp_path, monkeypatch):
    top = tmp_path / "top"
    _tree(top)
    rmdir, refilled = os.rmdir, []

    def refilling_rmdir(name, *, dir_fd=None):  # another process writes in each folder once, just before its rmdir
        if name not in refilled:
            refilled.append(name)
            inner = os.open(name, os.O_RDONLY | os.O_DIRECTORY, dir_fd=dir_fd)
            try:
                os.mkdir("late", dir_fd=inner)
                os.close(os.open("late/f", os.O_CREAT | os.O_WRONLY, 0o600, dir_fd=inner))
            finally:
                os.close(inner)
        rmdir(name, dir_fd=dir_fd)

    monkeypatch.setattr(os, "rmdir", refilling_rmdir)
    runner._remove(str(top))
    monkeypatch.undo()
    assert len(refilled) > 1
    assert not os.path.lexists(top)


def test_w2_96_r14_a_folder_another_process_removed_first_is_no_error(tmp_path):
    runner._remove(str(tmp_path / "never-there"))
    top = tmp_path / "top"
    _tree(top)
    shutil.rmtree(top)
    runner._remove(str(top))


def test_w2_96_r14_a_removal_racing_another_removal_ends_and_raises_nothing(tmp_path):
    for attempt in range(6):
        top = tmp_path / f"top{attempt}"
        _tree(top, folders=30, files=100)
        other = threading.Thread(target=shutil.rmtree, args=(top,), kwargs={"ignore_errors": True})
        other.start()
        runner._remove(str(top))
        other.join()
        assert not os.path.lexists(top)


def test_w2_96_r14_an_error_that_stays_is_passed_over_after_a_bounded_number_of_passes(tmp_path, monkeypatch):
    top = tmp_path / "top"
    _tree(top, folders=2, files=2)
    calls = []

    def stuck(name, *, dir_fd=None):
        calls.append(name)
        raise OSError(errno.EBUSY, "busy")

    monkeypatch.setattr(os, "rmdir", stuck)
    began = time.monotonic()
    runner._remove(str(top))  # never raises
    took = time.monotonic() - began
    monkeypatch.undo()
    assert took < 10 and len(calls) < 200
    shutil.rmtree(top)


def test_w2_96_r14_the_removal_never_leaves_the_tree(tmp_path, monkeypatch):
    """A folder moved elsewhere during the removal: going up never lands outside the private folder."""
    top, outside = tmp_path / "top", tmp_path / "outside"
    outside.mkdir()
    (outside / "kept").write_text("x")
    (top / "a" / "b").mkdir(parents=True)
    (top / "a" / "b" / "f").write_text("x")
    unlink, moved = os.unlink, []

    def moving_unlink(name, *, dir_fd=None):  # another process moves the folder being emptied out of the tree
        if not moved and dir_fd is not None and name == "f":
            moved.append(1)
            os.rename(top / "a" / "b", outside / "b")
        unlink(name, dir_fd=dir_fd)

    monkeypatch.setattr(os, "unlink", moving_unlink)
    runner._remove(str(top))
    monkeypatch.undo()
    assert moved and not os.path.lexists(top)
    assert (outside / "kept").read_text() == "x"


# --- R14: through gov accept ------------------------------------------------------------------------------------------

# a planted test starts, in a session of its own, a writer that keeps writing and removing files in the test's own
# temporary folder (as a nested gov accept does), and records its pid outside
WRITER = ("import os, sys, time\nhome, stop = sys.argv[1], time.monotonic() + 2.5\ni = 0\n"
          "while time.monotonic() < stop:\n    try:\n        d = os.path.join(home, f'w{i % 40}')\n"
          "        if not os.path.isdir(d):\n            os.mkdir(d)\n        open(os.path.join(d, f'f{i}'), 'w').write('x')\n"
          "        if i % 3 == 0:\n            for n in os.listdir(d)[:5]:\n                os.unlink(os.path.join(d, n))\n"
          "    except OSError:\n        if not os.path.isdir(home):\n            break\n    i += 1\n")
RACER = ("import os, subprocess, sys, time\n\ndef test_a(tmp_path):\n"
         "    writer = subprocess.Popen([sys.executable, {writer!r}, str(tmp_path)], start_new_session=True)\n"
         "    open({pid!r}, 'w').write(str(writer.pid))\n    time.sleep(0.3)\n{tail}")


def _racer(tmp_path: Path, tail: str = "") -> tuple[str, Path]:
    writer, pid = tmp_path / "w296_writer.py", tmp_path / "writer.pid"
    writer.write_text(WRITER)
    return RACER.format(writer=str(writer), pid=str(pid), tail=tail), pid


def _wait_gone(pid_file: Path, seconds: float = 30) -> None:
    deadline = time.monotonic() + seconds
    while not (pid_file.exists() and pid_file.read_text()) and time.monotonic() < deadline:
        time.sleep(0.05)
    pid = int(pid_file.read_text())
    while not _gone(pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert _gone(pid)


@pytest.mark.parametrize("tail, code, outcome", [("", 0, "pass"), (f"    assert False, '{MARK}'\n", 3, "fail")])
def test_w2_96_r14_an_unstopped_run_is_reported_as_its_results_say(project, tmp_path, capsys, tail, code, outcome):
    root, temp = project
    test, pid = _racer(tmp_path, tail)
    _plant(root, {"test_a.py": test})
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    out, err = capsys.readouterr()
    result = json.loads(out)["result"]
    assert got == code and result["outcome"] == outcome and result["error_kind"] is None, result
    assert MARK not in out + err
    _wait_gone(pid)
    assert list(temp.iterdir()) == []


def test_w2_96_r14_an_unstopped_run_whose_entries_vanish_is_never_a_crash(project, capsys, monkeypatch):
    root, temp = project
    _plant(root, {"test_a.py": "def test_a(tmp_path):\n    for i in range(50):\n"
                               "        (tmp_path / f'f{i}').write_text('x')\n"})
    unlink, rmdir = os.unlink, os.rmdir

    def first_unlink(name, *, dir_fd=None):
        unlink(name, dir_fd=dir_fd)
        if dir_fd is not None:  # the removal's own call: another process got there first
            unlink(name, dir_fd=dir_fd)

    def first_rmdir(name, *, dir_fd=None):
        rmdir(name, dir_fd=dir_fd)
        if dir_fd is not None:
            rmdir(name, dir_fd=dir_fd)

    monkeypatch.setattr(os, "unlink", first_unlink)
    monkeypatch.setattr(os, "rmdir", first_rmdir)
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    monkeypatch.undo()
    result = json.loads(capsys.readouterr().out)["result"]
    assert got == 0 and result["outcome"] == "pass" and result["error_kind"] is None, result
    assert list(temp.iterdir()) == []


# gov accept as its own process; with W296_VANISH set, every entry the removal takes is removed just before it by
# "another process", so that each of its own calls meets "file not found"
WRAPPER = """import os, sys
from gov.cli.main import main
if os.environ.get("W296_VANISH"):
    unlink, rmdir = os.unlink, os.rmdir
    def first_unlink(name, *, dir_fd=None):
        unlink(name, dir_fd=dir_fd)
        if dir_fd is not None:
            unlink(name, dir_fd=dir_fd)
    def first_rmdir(name, *, dir_fd=None):
        rmdir(name, dir_fd=dir_fd)
        if dir_fd is not None:
            rmdir(name, dir_fd=dir_fd)
    os.unlink, os.rmdir = first_unlink, first_rmdir
sys.exit(main(sys.argv[1:]))
"""


@pytest.mark.parametrize("signum", [2, 15, 1])
@pytest.mark.parametrize("vanish", [True, False])
def test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal(project, tmp_path, signum, vanish):
    root, temp = project
    started = tmp_path / "started"
    test, pid = _racer(tmp_path, f"    open({str(started)!r}, 'w').write('x')\n    time.sleep(60)\n")
    _plant(root, {"test_a.py": test})
    script = tmp_path / "w296_gov.py"
    script.write_text(WRAPPER)
    env = dict(os.environ, PYTHONPATH=str(Path(runner.__file__).parents[2]), TMPDIR=str(temp))
    env.pop("W296_VANISH", None)
    if vanish:
        env["W296_VANISH"] = "1"
    gov = subprocess.Popen([sys.executable, str(script), "accept", "DAEO-t001", "--json", "--root", str(root)],
                           env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    deadline = time.monotonic() + 60
    while not started.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert started.exists()
    gov.send_signal(signum)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 128 + signum, out
    assert MARK.encode() not in out and b"Traceback" not in out
    _wait_gone(pid)
    assert list(temp.iterdir()) == []


# --- R15: linear in the entries ---------------------------------------------------------------------------------------

def test_w2_96_r15_eight_thousand_sibling_folders_go_in_a_few_seconds(tmp_path):
    top = tmp_path / "top"
    top.mkdir()
    for i in range(8000):
        (top / f"d{i:05d}").mkdir()
    (top / "d00007" / "f").write_text("x")
    began = time.monotonic()
    runner._remove(str(top))
    took = time.monotonic() - began
    assert not os.path.lexists(top)
    assert took < 5, took


def test_w2_96_r15_r10_a_wide_and_deep_tree_together(tmp_path):
    top = tmp_path / "top"
    top.mkdir()
    for i in range(2000):
        (top / f"s{i}").mkdir()
    fd = os.open(top / "s0", os.O_RDONLY)
    try:
        for _ in range(1200):  # beyond PATH_MAX, under one of the siblings
            os.mkdir("dddddddd", dir_fd=fd)
            child = os.open("dddddddd", os.O_RDONLY, dir_fd=fd)
            os.close(fd)
            fd = child
    finally:
        os.close(fd)
    os.chmod(top / "s1", 0)
    runner._remove(str(top))
    assert not os.path.lexists(top)


def test_w2_96_r14_signals_stay_untouched_by_the_removal(tmp_path):
    before = {signum: signal.getsignal(signum) for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    top = tmp_path / "top"
    _tree(top, folders=2, files=2)
    runner._remove(str(top))
    assert {signum: signal.getsignal(signum) for signum in before} == before
