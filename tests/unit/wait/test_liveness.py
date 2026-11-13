"""The shared liveness function of gov.wait: asked of a pid alone (os.kill 0), a zombie counts as gone."""

from __future__ import annotations

import os
import subprocess
import sys
import time

from gov.wait import liveness


def test_a_running_process_is_not_gone():
    assert liveness.gone(os.getpid()) is False


def test_an_exited_and_reaped_process_is_gone():
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    assert liveness.gone(child.pid) is True


def test_a_zombie_counts_as_gone():
    child = subprocess.Popen([sys.executable, "-c", "pass"])  # not reaped: it stays a zombie
    deadline = time.time() + 5
    while time.time() < deadline and liveness._state(child.pid) != "Z":
        time.sleep(0.02)
    try:
        assert liveness._state(child.pid) == "Z"
        assert liveness.gone(child.pid) is True
    finally:
        child.wait()


def test_pid_file_reading(tmp_path):
    file = tmp_path / "job.pid"
    assert liveness.read_pid(file) is None            # no file
    file.write_text("")
    assert liveness.read_pid(file) is None            # empty
    file.write_text("pid=1234\n")
    assert liveness.read_pid(file) == 1234            # digits only, as the script took them
    file.write_text("0\n")
    assert liveness.read_pid(file) is None            # 0 would signal the process group
    file.write_text("9" * 19)
    assert liveness.read_pid(file) is None            # beyond any pid: not asked
