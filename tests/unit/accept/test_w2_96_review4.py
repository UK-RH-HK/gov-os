"""W2-96 (DAEO-ouet): builder tests of review 4's W1 (DEC-987, R16): before its clean-up, ``gov accept`` stops and
reaps every process the run started, whatever its session, so that once ``gov`` has ended no process of the run is
alive and nothing of the run appears in the caller's ``TMPDIR`` later.

Each test plants a tiny project in a temporary folder whose test starts processes in sessions of their own (as a
nested ``gov accept`` does); the stop tests start ``gov accept`` as its own process. Nothing runs against this
repository's own acceptance folders.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from gov.accept import runner
from gov.cli.main import main

pytestmark = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the subreaper is Linux only")

MARK = "PLANTED-LEAK-3e7a"  # planted in assertions: must never reach the caller
ONE_LINE = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n"

# the orphan: records its pid, then, 2 s later, recreates a folder under the planted test's temporary folder (as an
# orphaned nested pytest's report writer does)
ORPHAN = ("import os, sys, time\nopen(sys.argv[2], 'w').write(str(os.getpid()))\ntime.sleep(float(sys.argv[3]))\n"
          "os.makedirs(os.path.join(sys.argv[1], 'given-1'), exist_ok=True)\n"
          "open(os.path.join(sys.argv[1], 'given-1', 'f'), 'w').write('x')\n")
# the planted test starts, in a session of its own, a middle process that starts the orphan in another session of
# its own and ends at once, so the orphan outlives its parent; the test never waits for it
PLANTED = ("import os, subprocess, sys, time\n\ndef test_a(tmp_path):\n"
           "    middle = ('import subprocess, sys; '\n"
           "              'subprocess.Popen([sys.executable] + sys.argv[1:], start_new_session=True)')\n"
           "    subprocess.Popen([sys.executable, '-c', middle, {orphan!r}, str(tmp_path), {pid!r}, {wait!r}],\n"
           "                     start_new_session=True).wait()\n"
           "    stop = time.monotonic() + 20\n"
           "    while not (os.path.exists({pid!r}) and open({pid!r}).read()) and time.monotonic() < stop:\n"
           "        time.sleep(0.02)\n{tail}")
# a process that keeps forking: "hop" forks and ends, again and again; "breed" keeps forking children that stay
FORKER = {"hop": ("import os, sys, time\nstop = time.monotonic() + 20\nwhile time.monotonic() < stop:\n"
                  "    open(sys.argv[1], 'a').write(f'{os.getpid()}\\n')\n    if os.fork():\n        os._exit(0)\n"
                  "    time.sleep(0.005)\n"),
          "breed": ("import os, sys, time\nopen(sys.argv[1], 'a').write(f'{os.getpid()}\\n')\nfor i in range(300):\n"
                    "    if os.fork() == 0:\n        open(sys.argv[1], 'a').write(f'{os.getpid()}\\n')\n"
                    "        time.sleep(20)\n        os._exit(0)\n    time.sleep(0.005)\ntime.sleep(20)\n")}
FORKING = ("import os, subprocess, sys, time\n\ndef test_a():\n"
           "    subprocess.Popen([sys.executable, {forker!r}, {pids!r}], start_new_session=True)\n"
           "    time.sleep(0.5)\n{tail}")
WRAPPER = "import sys\nfrom gov.cli.main import main\nsys.exit(main(sys.argv[1:]))\n"


def _plant(root: Path, test: str) -> None:
    (root / ".tickets").mkdir(parents=True, exist_ok=True)
    (root / ".tickets" / "DAEO-t001.md").write_text(
        "---\nid: DAEO-t001\nwbs_id: W9-01\nacceptance_tests:\n  path: tests/acceptance/T1/\n---\n# t\n")
    folder = root / "tests" / "acceptance" / "T1"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(ONE_LINE)
    (folder / "test_a.py").write_text(test)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root, temp = tmp_path / "proj", tmp_path / "tmpdir"
    root.mkdir()
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    monkeypatch.setenv("TMPDIR", str(temp))
    return root, temp


def _orphan(tmp_path: Path, tail: str = "", wait: float = 2) -> tuple[str, Path]:
    orphan, pid = tmp_path / "w296_orphan.py", tmp_path / "orphan.pid"
    orphan.write_text(ORPHAN)
    return PLANTED.format(orphan=str(orphan), pid=str(pid), wait=str(wait), tail=tail), pid


def _alive(pid: int) -> bool:
    """Whether the pid is a live process of the planted run (its command line names a planted script)."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[-1].split()[0]
        return state != "Z" and b"w296_" in Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False


def _mine() -> set[int]:
    """This process's children, from the kernel."""
    found = set()
    for task in os.listdir("/proc/self/task"):
        found.update(int(pid) for pid in Path(f"/proc/self/task/{task}/children").read_text().split())
    return found


def _subreaper() -> int:
    import ctypes
    value = ctypes.c_int()
    ctypes.CDLL(None).prctl(37, ctypes.byref(value), 0, 0, 0)  # PR_GET_CHILD_SUBREAPER
    return value.value


def _launch(root: Path, temp: Path, tmp_path: Path) -> subprocess.Popen:
    script = tmp_path / "w296_gov.py"
    script.write_text(WRAPPER)
    env = dict(os.environ, PYTHONPATH=str(Path(runner.__file__).parents[2]), TMPDIR=str(temp))
    return subprocess.Popen([sys.executable, str(script), "accept", "DAEO-t001", "--json", "--root", str(root)],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def _wait_for(path: Path, seconds: float = 60) -> None:
    deadline = time.monotonic() + seconds
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert path.exists()


# --- R16: an own-session orphan is stopped and reaped before the clean-up ---------------------------------------------

@pytest.mark.parametrize("tail, code, outcome", [("", 0, "pass"), (f"    assert False, '{MARK}'\n", 3, "fail")])
def test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_finished_run_cleans_up(project, tmp_path, capsys,
                                                                                    tail, code, outcome):
    root, temp = project
    test, pid_file = _orphan(tmp_path, tail)
    _plant(root, test)
    before = _mine()
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    out, err = capsys.readouterr()
    result = json.loads(out)["result"]
    assert got == code and result["outcome"] == outcome and result["error_kind"] is None, result  # the child's status
    assert MARK not in out + err
    pid = int(pid_file.read_text())
    assert not os.path.exists(f"/proc/{pid}"), "the orphan is alive, or left unreaped, after gov returned"
    assert _mine() <= before
    assert list(temp.iterdir()) == []
    time.sleep(3)  # past the moment the orphan would have written
    assert list(temp.iterdir()) == []


@pytest.mark.parametrize("signum", [2, 15, 1])
def test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up(project, tmp_path, signum):
    root, temp = project
    started = tmp_path / "started"
    test, pid_file = _orphan(tmp_path, f"    open({str(started)!r}, 'w').write('x')\n    time.sleep(60)\n")
    _plant(root, test)
    gov = _launch(root, temp, tmp_path)
    _wait_for(started)
    gov.send_signal(signum)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 128 + signum, out
    assert MARK.encode() not in out and b"Traceback" not in out
    assert not _alive(int(pid_file.read_text())), "the orphan outlived gov"
    time.sleep(3)
    assert list(temp.iterdir()) == []


# --- R16: a process that keeps forking is still ended within the bound ------------------------------------------------

@pytest.mark.parametrize("kind", ["hop", "breed"])
@pytest.mark.parametrize("stop", [None, 15])
def test_w2_96_r16_a_process_that_keeps_forking_is_ended_within_the_bound(project, tmp_path, kind, stop):
    root, temp = project
    forker, pids, started = tmp_path / "w296_forker.py", tmp_path / "forked.pids", tmp_path / "started"
    forker.write_text(FORKER[kind])
    tail = "" if stop is None else f"    open({str(started)!r}, 'w').write('x')\n    time.sleep(60)\n"
    _plant(root, FORKING.format(forker=str(forker), pids=str(pids), tail=tail))
    began = time.monotonic()
    gov = _launch(root, temp, tmp_path)
    if stop is not None:
        _wait_for(started)
        gov.send_signal(stop)
    out, _ = gov.communicate(timeout=60)
    took = time.monotonic() - began
    assert gov.returncode == (0 if stop is None else 128 + stop), out
    assert took < 15 + runner.REAP_SECONDS, took
    recorded = {int(line) for line in pids.read_text().split()}
    assert recorded and not [pid for pid in recorded if _alive(pid)]
    time.sleep(0.5)  # a fork in flight when gov ended would show up now
    assert not [pid for pid in {int(line) for line in pids.read_text().split()} if _alive(pid)]
    assert list(temp.iterdir()) == []


# --- R16: only the run's own processes, and the main child's status stays its own -------------------------------------

def test_w2_96_r16_a_child_gov_had_before_the_run_is_neither_stopped_nor_reaped(project, tmp_path, capsys):
    root, temp = project
    test, pid_file = _orphan(tmp_path)
    _plant(root, test)
    keeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    ended = subprocess.Popen([sys.executable, "-c", "raise SystemExit(7)"])
    deadline = time.monotonic() + 30
    while Path(f"/proc/{ended.pid}/stat").read_text().rsplit(")", 1)[-1].split()[0] != "Z":  # ended, not yet waited
        assert time.monotonic() < deadline
        time.sleep(0.02)
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    capsys.readouterr()
    try:
        assert got == 0
        assert keeper.poll() is None  # never stopped
        assert ended.wait(timeout=5) == 7  # its status never taken
    finally:
        keeper.kill()
        keeper.wait()
    assert not os.path.exists(f"/proc/{int(pid_file.read_text())}")


def test_w2_96_r16_the_subreaper_setting_ends_with_the_run(project, tmp_path, capsys):
    root, _ = project
    _plant(root, "def test_a():\n    pass\n")
    before = _subreaper()
    assert main(["accept", "DAEO-t001", "--json", "--root", str(root)]) == 0
    capsys.readouterr()
    assert _subreaper() == before


def test_w2_96_r16_without_the_subreaper_a_run_keeps_todays_behaviour(project, capsys, monkeypatch):
    root, temp = project
    _plant(root, "def test_a():\n    pass\n")
    monkeypatch.setattr(runner, "_subreaper", lambda on: None)  # not Linux, or the call failed
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    result = json.loads(capsys.readouterr().out)["result"]
    assert got == 0 and result["outcome"] == "pass", result
    assert list(temp.iterdir()) == []


def test_w2_96_r16_a_descendant_that_survives_the_bound_does_not_stop_the_clean_up(project, tmp_path, capsys,
                                                                                    monkeypatch):
    root, temp = project
    test, pid_file = _orphan(tmp_path, wait=60)  # it would write only long after the test ends it
    _plant(root, test)
    kill = os.kill
    monkeypatch.setattr(runner, "REAP_SECONDS", 0.5)
    monkeypatch.setattr(os, "kill", lambda pid, signum: None)  # a descendant no signal ends
    began = time.monotonic()
    got = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    took = time.monotonic() - began
    monkeypatch.undo()
    capsys.readouterr()
    pid = int(pid_file.read_text())
    try:
        assert got == 0 and took < 15, took
        assert list(temp.iterdir()) == []
    finally:
        if pid in _mine():
            kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
    assert _subreaper() == 0


def test_w2_96_r16_reap_is_bounded_and_never_raises(monkeypatch):
    sent = []
    monkeypatch.setattr(runner, "_children", lambda pid: {4194304})  # a "child" that never goes (above pid_max)
    monkeypatch.setattr(os, "kill", lambda pid, signum: sent.append(pid))  # recorded, never sent
    monkeypatch.setattr(runner, "REAP_SECONDS", 0.3)
    began = time.monotonic()
    runner._reap(set())
    assert time.monotonic() - began < 3 and sent and set(sent) == {4194304}
