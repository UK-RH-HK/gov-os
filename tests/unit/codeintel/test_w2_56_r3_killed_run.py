"""W2-56 R3 (S1) unit tests: a killed test run's folders are removed by the next run (``tests/conftest.py``).

Regression evidence only (MR-3). Each run folder and links folder holds its owner's record, a file its maker holds
``flock``'d for its life; the next run removes the folders of those names whose record no process holds, and a folder
with no record only when it is more than 24 hours old (DEC-902). Links, regular files, other users' folders and other
names are never touched; a folder that cannot be removed is left without failing. The real runs, killed, in the real
``/tmp`` and across pid namespaces are the acceptance cases'.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from gov import codeintel

CONFTEST = Path(__file__).resolve().parents[2] / "conftest.py"
HOUR = 3600


def _load():
    spec = importlib.util.spec_from_file_location("_root_conftest_for_w2_56_r3", CONFTEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conftest = _load()


def _age(path: Path, hours: float) -> None:
    when = time.time() - hours * HOUR
    for top, folders, files in os.walk(path, topdown=False):
        for name in (*folders, *files):
            os.utime(os.path.join(top, name), (when, when), follow_symlinks=False)
    os.utime(path, (when, when), follow_symlinks=False)


@pytest.fixture()
def place(tmp_path):
    """A launched session's temp folder (``gov-launch-`` and 8 letters) and the CLI's folder in it."""
    launched = tmp_path / "gov-launch-w56abcde"
    (launched / f"claude-{os.getuid()}").mkdir(parents=True, mode=0o700)
    return launched


def _run_folder(place: Path, name: str = "cq7z", *, hours: float | None = None, record: bool = False) -> Path:
    folder = place / name
    folder.mkdir(mode=0o700)
    (folder / "older-code.txt").write_text("a daemon folder of a killed run\n", encoding="utf-8")
    if record:
        (folder / conftest._OWNER).write_text('{"pid": 4}', encoding="utf-8")  # nobody holds it: its owner is gone
    if hours is not None:
        _age(folder, hours)
    return folder


def _sweep(place: Path) -> None:
    conftest._sweep_killed(place, conftest._LAUNCHED_NAMES)


# -- the names --------------------------------------------------------------------------------------------------------

def test_the_names_swept_are_the_names_the_code_makes(place):
    made = codeintel.make_session_base({"CLAUDE_CODE_TMPDIR": str(place / f"claude-{os.getuid()}")})
    assert made.parent == place and conftest._run_names(made) is conftest._LAUNCHED_NAMES
    elsewhere = codeintel.make_session_base({})
    try:
        names = conftest._run_names(elsewhere)
        assert names is not None and names.pattern == f"gov-cbm-{os.getuid()}-[a-z0-9_]{{8}}"
    finally:
        shutil.rmtree(elsewhere)
    links = Path(tempfile.mkdtemp(prefix="gov-path-", dir=place))
    assert conftest._LINKS_NAMES.fullmatch(links.name)
    assert conftest._run_names(place / "cbm") is None and conftest._run_names(Path("/tmp/cq7z")) is None


# -- the owner's record -----------------------------------------------------------------------------------------------

def test_a_folder_whose_owner_holds_its_record_is_kept_and_removed_once_the_owner_is_killed(place):
    folder = _run_folder(place, hours=25)
    (folder / "older-code.txt").unlink()
    code = ("import importlib.util, sys, time\n"
            "spec = importlib.util.spec_from_file_location('c', sys.argv[1])\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "m._own(sys.argv[2]); print('held', flush=True); time.sleep(120)\n")
    owner = subprocess.Popen([sys.executable, "-c", code, str(CONFTEST), str(folder)], stdout=subprocess.PIPE,
                             text=True, env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    try:
        assert owner.stdout.readline().strip() == "held"
        assert sorted(os.listdir(folder)) == [conftest._OWNER]  # the record appears only once held
        _sweep(place)
        assert folder.is_dir()  # held, at any age, whatever pid the record names
    finally:
        owner.send_signal(signal.SIGKILL)
        owner.wait(timeout=30)
        owner.stdout.close()
    _sweep(place)
    assert not folder.exists()


def test_a_record_held_by_this_process_keeps_the_folder_and_ends_with_it(place):
    folder = _run_folder(place)
    conftest._own(folder)
    try:
        _sweep(place)
        assert (folder / conftest._OWNER).is_file()
    finally:
        shutil.rmtree(folder)
        conftest._disown(folder)
    assert str(folder) not in conftest._owners


def test_a_record_no_process_holds_means_the_owner_is_gone_at_any_age(place):
    fresh = _run_folder(place, "c001", record=True)
    _sweep(place)
    assert not fresh.exists()


@pytest.mark.parametrize("hours,kept", [(None, True), (23, True), (25, False)])
def test_a_folder_with_no_record_is_kept_for_24_hours(place, hours, kept):
    folder = _run_folder(place, hours=hours)
    _sweep(place)
    assert folder.exists() is kept


def test_a_newer_entry_keeps_an_old_folder_with_no_record(place):
    folder = _run_folder(place, hours=25)
    (folder / "newer.txt").write_text("x", encoding="utf-8")  # an entry written an hour ago would keep it too
    os.utime(folder, (time.time() - 25 * HOUR,) * 2)
    _sweep(place)
    assert folder.exists()


def test_a_staged_record_alone_is_no_record(place):
    folder = _run_folder(place, record=False)
    (folder / f"{conftest._OWNER}.4").write_text("", encoding="utf-8")
    _sweep(place)
    assert folder.exists()


def test_a_record_that_is_a_link_or_a_folder_keeps_the_folder(place, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("keep", encoding="utf-8")
    linked = _run_folder(place, "c002", hours=25)
    (linked / conftest._OWNER).symlink_to(outside / "keep.txt")
    folded = _run_folder(place, "c003", hours=25)
    (folded / conftest._OWNER).mkdir()
    _age(linked, 25)
    _age(folded, 25)
    _sweep(place)
    assert linked.is_dir() and folded.is_dir() and (outside / "keep.txt").read_text() == "keep"


# -- never touched ----------------------------------------------------------------------------------------------------

def test_links_files_and_other_names_are_never_touched(place, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("keep", encoding="utf-8")
    (place / "c004").symlink_to(outside, target_is_directory=True)
    (place / "c005").write_text("a file", encoding="utf-8")
    others = ["cbm", "cc-socks", f"gov-cbm-{os.getuid()}", "gov-launch-w56abcdefgh", "w56-other-abcdefgh", "cq7z9",
              "C001"]
    for name in others:
        _run_folder(place, name, record=True)
    for name in ("c004", "c005", *others):
        os.utime(place / name, (time.time() - 25 * HOUR,) * 2, follow_symlinks=False)
    _sweep(place)
    assert (place / "c004").is_symlink() and (outside / "keep.txt").read_text() == "keep"
    assert (place / "c005").read_text() == "a file"
    assert all((place / name).is_dir() for name in others)


def test_only_links_folders_of_the_code_s_form_are_swept_in_the_temp_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    names = ["gov-path-abcd1234", "gov-pathology-abcd1234", "w56-gov-path-abcd1234", "gov-path-abc", "gov-launch-x"]
    for name in names:
        _run_folder(root, name, record=True)
    conftest._sweep_killed(root, conftest._LINKS_NAMES)
    assert sorted(os.listdir(root)) == sorted(names[1:])


def test_another_users_folder_is_never_removed(place, monkeypatch):
    folder = _run_folder(place, record=True)
    real = os.getuid()
    monkeypatch.setattr(conftest.os, "getuid", lambda: real + 1)  # the folder reads as another user's
    _sweep(place)
    monkeypatch.undo()
    assert folder.is_dir()


# -- what cannot be removed -------------------------------------------------------------------------------------------

def test_a_0500_folder_never_fails_or_holds_up_the_sweep(place):
    folder = _run_folder(place, hours=25)
    inner = folder / "inner"
    inner.mkdir()
    (inner / "file.txt").write_text("x", encoding="utf-8")
    _age(folder, 25)
    inner.chmod(0o500)
    folder.chmod(0o500)
    try:
        started = time.monotonic()
        _sweep(place)
        assert time.monotonic() - started < 5
    finally:
        for path in (folder, inner):
            if path.is_dir():
                path.chmod(0o700)
    assert not folder.exists()  # opened to its owner and removed; leaving it would also be right


def test_a_place_that_cannot_be_read_or_written_is_left_without_failing(tmp_path):
    conftest._sweep_killed(tmp_path / "missing", conftest._LAUNCHED_NAMES)
    shut = tmp_path / "gov-launch-shut1234"
    shut.mkdir()
    _run_folder(shut, record=True)
    shut.chmod(0o500)
    try:
        conftest._sweep_killed(shut, conftest._LAUNCHED_NAMES)
        assert (shut / "cq7z").is_dir()  # its entry cannot be unlinked: left
    finally:
        shut.chmod(0o700)


def test_the_conftest_wires_the_record_and_the_sweep_into_the_run():
    """This run's own folder holds a record this process holds, and is named in CODEINTEL_DAEMON_BASE."""
    base = os.environ.get("CODEINTEL_DAEMON_BASE")
    if not base:
        pytest.skip("this run has no daemon folder of its own")
    record = Path(base) / conftest._OWNER
    assert stat.S_ISREG(os.lstat(record).st_mode)
    gone, fd = conftest._owner_gone(base)
    assert gone is False and fd is None  # held by this run's controlling process
    assert re.fullmatch(r'\{"pid": \d+\}', record.read_text())
