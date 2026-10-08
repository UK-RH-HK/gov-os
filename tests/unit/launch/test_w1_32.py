"""Builder tests for the launcher changes of W1-32 (DEC-392).

Regression evidence only (DEC-136). No CLI and no process is started: ``subprocess.Popen`` is replaced by a
stand-in object, the project is a temporary directory, and a signal is raised by the test in its own process
while the launcher's handler is installed (checked first), never sent to another process. They cover the paths
the acceptance tests cannot reach from outside: a signal before the session is started, during the clean-up, a
second signal, and a session that does not end when asked.
"""
from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.launch import launcher  # noqa: E402

HANDLED = (*launcher.END_SIGNALS, signal.SIGALRM)


def _raise(number):
    """Raise ``number`` in this process, only while the launcher handles it."""
    assert signal.getsignal(number) not in (signal.SIG_DFL, signal.SIG_IGN, signal.default_int_handler), \
        f"the launcher does not handle {signal.Signals(number).name} here"
    signal.raise_signal(number)


class Session:
    """In place of ``subprocess.Popen``: ``plan(session)`` runs in ``wait``; a session that obeys ends when asked."""
    made: list = []
    plan, obeys = None, True

    def __init__(self, argv, cwd, env):
        self.folder, self.returncode, self.calls = Path(env["TMPDIR"]), None, []
        assert self.folder.is_dir()
        Session.made.append(self)

    def wait(self):
        if self.returncode is not None:
            return self.returncode
        code = Session.plan(self)
        deadline = time.monotonic() + 10
        while code is None and self.returncode is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.returncode = code if self.returncode is None else self.returncode
        return self.returncode

    def poll(self):
        return self.returncode

    def terminate(self):
        self.calls.append("terminate")
        if Session.obeys:
            self.returncode = -signal.SIGTERM

    def kill(self):
        self.calls.append("kill")
        self.returncode = -signal.SIGKILL


@pytest.fixture
def launch(tmp_path, monkeypatch):
    """``launch(plan, obeys=True)`` launches with a stand-in session; the temp directory is ``launch.temp``."""
    home, temp, project = tmp_path / "home", tmp_path / "temp", tmp_path / "project"
    for folder in (home / ".local" / "bin", temp, project):
        folder.mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_ticket", lambda *args: None)
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    monkeypatch.setattr(launcher, "END_WAIT_S", 1)
    before = {number: signal.signal(number, signal.SIG_DFL) for number in HANDLED}  # a runner may ignore some
    before[signal.SIGINT] = signal.signal(signal.SIGINT, signal.default_int_handler)
    Session.made = []

    def _launch(plan, obeys=True):
        Session.plan, Session.obeys = staticmethod(plan), obeys
        return launcher.launch(project, "engineer", "TST-a001", [])

    _launch.temp = temp
    yield _launch
    assert [signal.getsignal(number) for number in HANDLED] == \
        [signal.SIG_DFL if number != signal.SIGINT else signal.default_int_handler for number in HANDLED], \
        "the launcher left a handler of its own"
    assert signal.alarm(0) == 0, "the launcher left an alarm set"
    for number, handler in before.items():
        signal.signal(number, handler if handler is not None else signal.SIG_DFL)


@pytest.mark.parametrize("number", launcher.END_SIGNALS, ids=lambda number: signal.Signals(number).name)
def test_a_signal_ends_the_session_removes_the_folder_and_gives_130(launch, number):
    assert launch(lambda session: _raise(number)) == launcher.INTERRUPT_EXIT == 130
    assert [session.calls for session in Session.made] == [["terminate"]]
    assert os.listdir(launch.temp) == []


def test_a_session_that_does_not_end_when_asked_is_killed(launch):
    assert launch(lambda session: _raise(signal.SIGTERM), obeys=False) == launcher.INTERRUPT_EXIT
    assert Session.made[0].calls == ["terminate", "kill"] and os.listdir(launch.temp) == []


def test_a_second_signal_kills_the_session_at_once(launch):
    def plan(session):
        _raise(signal.SIGTERM)
        _raise(signal.SIGHUP)

    started = time.monotonic()
    assert launch(plan, obeys=False) == launcher.INTERRUPT_EXIT
    assert Session.made[0].calls == ["terminate", "kill"] and time.monotonic() - started < 0.9
    assert os.listdir(launch.temp) == []


def test_a_signal_before_the_session_is_started_starts_none_and_leaves_no_folder(launch, monkeypatch):
    make = launcher.tempfile.mkdtemp

    def mkdtemp(**keys):
        _raise(signal.SIGHUP)
        return make(**keys)

    monkeypatch.setattr(launcher.tempfile, "mkdtemp", mkdtemp)
    assert launch(lambda session: 0) == launcher.INTERRUPT_EXIT
    assert Session.made == [] and os.listdir(launch.temp) == []


def test_a_signal_during_the_removal_keeps_the_sessions_exit_code_and_the_removal(launch, monkeypatch):
    remove = launcher.shutil.rmtree

    def rmtree(folder):
        _raise(signal.SIGTERM)
        _raise(signal.SIGINT)
        remove(folder)

    monkeypatch.setattr(launcher.shutil, "rmtree", rmtree)
    assert launch(lambda session: 7) == 7
    assert Session.made[0].calls == [] and os.listdir(launch.temp) == []


@pytest.mark.parametrize("code", (0, 7))
def test_a_failed_removal_keeps_the_exit_code_and_names_the_folder_in_one_line(launch, monkeypatch, capsys, code):
    def rmtree(folder):
        raise PermissionError(13, "Permission denied", str(folder))

    monkeypatch.setattr(launcher.shutil, "rmtree", rmtree)
    assert launch(lambda session: code) == code
    lines = capsys.readouterr().err.splitlines()
    assert len(lines) == 1 and str(Session.made[0].folder) in lines[0]


@pytest.mark.parametrize("way", ("no-stderr", "reader-gone", "closed"))
@pytest.mark.parametrize("code", (0, 7))
def test_a_failed_removal_keeps_the_exit_code_when_stderr_cannot_be_written(launch, monkeypatch, way, code):
    """Nothing of the line stays in the stream's buffer: what stays there fails the interpreter's last flush."""
    monkeypatch.setattr(launcher.shutil, "rmtree", lambda folder: (_ for _ in ()).throw(OSError(39, "not empty")))
    reader, writer = os.pipe()
    os.close(reader)
    stream = os.fdopen(writer, "w", encoding="utf-8")  # a pipe nobody reads: every write to it fails
    if way != "reader-gone":
        stream.close()
    monkeypatch.setattr(sys, "stderr", None if way == "no-stderr" else stream)
    assert launch(lambda session: code) == code
    stream.close()  # raises when the line was left in the buffer


def test_a_failed_removal_after_a_signal_still_gives_130(launch, monkeypatch, capsys):
    monkeypatch.setattr(launcher.shutil, "rmtree", lambda folder: (_ for _ in ()).throw(OSError(39, "not empty")))
    assert launch(lambda session: _raise(signal.SIGTERM)) == launcher.INTERRUPT_EXIT
    assert Session.made[0].calls == ["terminate"] and len(capsys.readouterr().err.splitlines()) == 1


def test_an_error_while_the_session_runs_leaves_no_session_and_no_folder(launch):
    def plan(session):
        raise RuntimeError("an error of the launcher's own")

    with pytest.raises(RuntimeError):
        launch(plan)
    assert Session.made[0].calls == ["kill"] and os.listdir(launch.temp) == []


def test_a_signal_the_caller_ignores_stays_ignored(launch):
    """``nohup gov launch``: the session is not ended by a hangup, and its exit code is the launcher's."""
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    try:
        def plan(session):
            assert signal.getsignal(signal.SIGHUP) is signal.SIG_IGN
            return 4

        assert launch(plan) == 4 and Session.made[0].calls == []
    finally:
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
