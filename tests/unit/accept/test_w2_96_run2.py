"""W2-96 (DAEO-ouet): builder tests of ``gov accept``'s run 2 (DEC-970): any failed case fails the run, signals
held back during the clean-up and ended as 128 plus the signal, a clean-up without recursion, an inherited
"ignore" kept, and ``accept`` recorded.

Each test plants a tiny project in a temporary folder; the signal tests start ``gov accept`` as its own process.
Nothing runs against this repository's own acceptance folders. Every planted ``gov accept`` and the pytest it
starts are reaped however the case ends (``w2_96_reap``: ``_planted``, the ``launch`` fixture; incident
2026-11-10 00:43).
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
from w2_96_reap import REAP_BOUND, REAP_GRACE, group_alive, launch_fixture, planted

MARK = "PLANTED-LEAK-5c1e"  # planted in assertions, output and names: must never reach the caller
ONE_LINE = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n"


def _plant(root: Path, readme: str, tests: dict[str, str]) -> None:
    (root / ".tickets").mkdir(parents=True, exist_ok=True)
    (root / ".tickets" / "DAEO-t001.md").write_text(
        "---\nid: DAEO-t001\nwbs_id: W9-01\nacceptance_tests:\n  path: tests/acceptance/T1/\n---\n# t\n")
    folder = root / "tests" / "acceptance" / "T1"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(readme)
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


def _accept(root: Path, capsys) -> tuple[int, dict, str]:
    code = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    out, err = capsys.readouterr()
    return code, json.loads(out), out + err


def _gone(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] == "Z"
    except OSError:
        return True


# --- R8: any failed case fails the run --------------------------------------------------------------------------------

@pytest.mark.parametrize("unmapped", [
    f"def test_x():\n    assert False, '{MARK}'\n",
    f"import pytest\n\n@pytest.fixture\ndef broken():\n    raise RuntimeError('{MARK}')\n\n"
    "def test_x(broken):\n    pass\n",
])
def test_w2_96_r8_an_unmapped_failed_or_errored_case_fails_the_run(project, capsys, unmapped):
    root, temp = project
    _plant(root, ONE_LINE, {"test_a.py": "def test_a():\n    pass\n", "test_other.py": unmapped})
    code, envelope, text = _accept(root, capsys)
    assert code == 3
    result = envelope["result"]
    assert result["outcome"] == "fail" and result["error_kind"] is None
    assert result["lines"] == [{"kpi": "success-1", "outcome": "pass", "passed": 1, "failed": 0, "skipped": 0}]
    assert result["unmapped"] == {"passed": 0, "failed": 1, "skipped": 0}
    assert MARK not in text and "test_other" not in text and "test_x" not in text
    assert list(temp.iterdir()) == []


def test_w2_96_r8_unmapped_passed_and_skipped_cases_keep_a_pass(project, capsys):
    root, _ = project
    other = "import pytest\n\ndef test_x():\n    pass\n\ndef test_y():\n    pytest.skip('s')\n"
    _plant(root, ONE_LINE, {"test_a.py": "def test_a():\n    pass\n", "test_other.py": other})
    code, envelope, _ = _accept(root, capsys)
    assert code == 0 and envelope["result"]["outcome"] == "pass"
    assert envelope["result"]["unmapped"] == {"passed": 1, "failed": 0, "skipped": 1}


# --- R10: the clean-up without recursion ------------------------------------------------------------------------------

DEPTH = 1150
DEEP = ("import os\n\ndef test_a(tmp_path):\n    home = os.getcwd()\n    os.chdir(tmp_path)\n"
        f"    for _ in range({DEPTH}):\n        os.mkdir('dddd')\n        os.chdir('dddd')\n"
        f"    open('f', 'w').write('{MARK}')\n    os.chmod('f', 0)\n"
        f"    for level in range({DEPTH}):\n        os.chdir('..')\n"
        "        if level % 97 == 0:\n            os.chmod('dddd', 0)\n    os.chdir(home)\n")


@pytest.mark.parametrize("tail, code", [("", 0), ("    assert False\n", 3)])
def test_w2_96_r10_a_deep_tree_is_removed_without_a_crash(project, capsys, tail, code):
    root, temp = project
    _plant(root, ONE_LINE, {"test_a.py": DEEP + tail})
    got, envelope, text = _accept(root, capsys)
    assert got == code, envelope
    assert envelope["result"]["error_kind"] is None
    assert MARK not in text
    assert list(temp.iterdir()) == []


def test_w2_96_r10_remove_needs_no_recursion_and_no_long_paths(tmp_path):
    top = tmp_path / "top"
    top.mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "kept").write_text("x")
    fd = os.open(top, os.O_RDONLY)
    try:
        for level in range(1500):  # 1500 levels of 9 characters: a path far beyond PATH_MAX
            os.mkdir("ddddddddd", dir_fd=fd)
            child = os.open("ddddddddd", os.O_RDONLY, dir_fd=fd)
            os.close(fd)
            fd = child
            if level % 300 == 0:
                os.symlink(str(tmp_path / "outside"), "link", dir_fd=fd)
        os.close(os.open("f", os.O_CREAT | os.O_WRONLY, 0, dir_fd=fd))
    finally:
        os.close(fd)
    os.chmod(top, 0)
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(200)
    try:
        runner._remove(str(top))
    finally:
        sys.setrecursionlimit(limit)
    assert not top.exists()
    assert (tmp_path / "outside" / "kept").read_text() == "x"  # a link is removed, never followed


# --- R9, R11, R12: signals --------------------------------------------------------------------------------------------

GATED = ("import os, time\n\ndef test_a():\n    open({started!r}, 'w').write(str(os.getpid()))\n"
         "    while not os.path.exists({go!r}):\n        time.sleep(0.05)\n")

# the planted gov's own head: with W296_SLOW set, the clean-up's removal waits once it has begun, so that a signal
# is sent while the clean-up runs. Every planted gov is reaped by ``w2_96_reap`` (its recording and its reaper).
HEAD = """from gov.accept import runner
slow = os.environ.get("W296_SLOW")
if slow:
    remove = runner._remove
    def _slow(folder):
        open(slow, "w").write("x")
        time.sleep(2)
        remove(folder)
    runner._remove = _slow
"""


def _planted(folder: Path):
    """``w2_96_reap.planted`` with this file's head; yields ``launch(root, temp, env=None, ignore=())``."""
    return planted(folder, HEAD)


launch = launch_fixture(HEAD)  # the r9/r11/r12 cases' planted gov: reaped, with the pytest it started


def _slow(slow: Path) -> dict[str, str]:
    return {"W296_SLOW": str(slow)}


def _wait_for(path: Path, seconds: float = 60) -> None:
    deadline = time.monotonic() + seconds
    while not (path.exists() and path.read_text()) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert path.exists()


@pytest.mark.parametrize("signals", [(2,), (15,), (1,), (2, 15, 1)])  # SIGINT, SIGTERM, SIGHUP, all three
def test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back(project, tmp_path, launch, signals):
    root, temp = project
    started, go, slow = tmp_path / "started", tmp_path / "go", tmp_path / "slow"
    go.write_text("x")
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go)) + f"    print('{MARK}')\n"})
    gov = launch(root, temp, env=_slow(slow))
    _wait_for(slow)
    for signum in signals:
        gov.send_signal(signum)
        time.sleep(0.1)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 128 + signals[0]  # an ordinary exit, never a death by the signal
    assert MARK.encode() not in out and b"Traceback" not in out
    assert list(temp.iterdir()) == []


@pytest.mark.parametrize("first, more", [(2, (15, 1)), (15, (2,)), (1, (2,))])
def test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up(project, tmp_path, launch, first, more):
    root, temp = project
    started, slow = tmp_path / "started", tmp_path / "slow"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(tmp_path / "never"))})
    gov = launch(root, temp, env=_slow(slow))
    _wait_for(started)
    child = int(started.read_text())
    gov.send_signal(first)
    _wait_for(slow)
    for signum in more:
        gov.send_signal(signum)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 128 + first
    assert b"Traceback" not in out and MARK.encode() not in out
    assert list(temp.iterdir()) == []
    assert _gone(child)


@pytest.mark.parametrize("kinds", [(2,), (15,), (2, 15, 1)])
def test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it(project, tmp_path, launch, kinds):
    root, temp = project
    started, go, slow = tmp_path / "started", tmp_path / "go", tmp_path / "slow"
    go.write_text("x")
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go))})
    gov = launch(root, temp, env=_slow(slow))
    _wait_for(slow)
    sent = 0
    while gov.poll() is None and sent < 2000:  # through the clean-up and after it, until gov has ended
        try:
            gov.send_signal(kinds[sent % len(kinds)])
        except ProcessLookupError:
            break
        sent += 1
        time.sleep(0.005)
    gov.communicate(timeout=60)
    assert gov.returncode == 128 + kinds[0]  # an ordinary exit, never a death by a later signal
    assert list(temp.iterdir()) == []


def test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it(project, tmp_path, launch):
    root, temp = project
    started = tmp_path / "started"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(tmp_path / "never"))})
    gov = launch(root, temp)
    _wait_for(started)
    child = int(started.read_text())
    gov.send_signal(signal.SIGINT)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 130
    assert b"Traceback" not in out and b"KeyboardInterrupt" not in out
    assert list(temp.iterdir()) == []
    assert _gone(child)


# a case's process that uses the reaping and is then killed outright: it plants gov, waits for the run to block,
# writes "<gov pid> <pytest group> <reaper pid>" and sleeps until it is killed
HOLDER = """import importlib.util, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).parent))  # the shared w2_96_reap beside the case's file
spec = importlib.util.spec_from_file_location("w296_case", sys.argv[1])
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)
root, temp, folder, started, out = map(Path, sys.argv[2:7])
with case._planted(folder) as launch:
    gov = launch(root, temp)
    case._wait_for(started)
    out.with_suffix(".part").write_text(f"{gov.pid} {int(started.read_text())} {launch.reaper}")
    os.replace(out.with_suffix(".part"), out)
    time.sleep(600)
"""


def _blocking(project, tmp_path) -> tuple[Path, Path, Path]:
    root, temp = project
    started = tmp_path / "started"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(tmp_path / "never"))})
    return root, temp, started


def _nothing_left(seen: dict[str, int]) -> None:
    """Neither the planted gov nor anything in its group, the pytest group it started or the reaper is alive."""
    deadline = time.monotonic() + REAP_GRACE + REAP_BOUND + 10
    while time.monotonic() < deadline and not (
            _gone(seen["gov"]) and not group_alive(seen["gov"]) and not group_alive(seen["group"])
            and _gone(seen["reaper"])):
        time.sleep(0.05)
    assert _gone(seen["gov"]) and not group_alive(seen["gov"])  # the planted gov and anything in its group
    assert not group_alive(seen["group"])  # the pytest group gov started
    assert _gone(seen["reaper"])


def test_w2_96_r9_r12_a_case_whose_body_ends_early_leaves_no_planted_process(project, tmp_path):
    """DEC-866 rewrite (incident 2026-11-10 00:43): a planted gov whose run blocks, and a helper using the reaping
    whose body ends early by ``pytest.fail``: afterwards neither the planted gov nor the pytest group it started
    has a live process, nor does the reaper. Checked by pid only."""
    root, temp, started = _blocking(project, tmp_path)
    seen: dict[str, int] = {}

    def body(launch):
        gov = launch(root, temp)
        _wait_for(started)
        seen.update(gov=gov.pid, group=int(started.read_text()), reaper=launch.reaper)
        assert gov.poll() is None and group_alive(seen["group"])  # the run blocks: both are alive here
        pytest.fail("the case's body ends early")

    with pytest.raises(pytest.fail.Exception, match="ends early"):
        with _planted(tmp_path / "w296_reap") as launch:
            body(launch)
    _nothing_left(seen)


def test_w2_96_r9_r12_a_case_whose_process_is_killed_leaves_no_planted_process(project, tmp_path):
    """DEC-866 rewrite (incident 2026-11-10 00:43, the run's worker gone): the same, with the case's process killed
    by SIGKILL while the run blocks, so that no finaliser of its own runs; the reaper alone stops what it planted."""
    root, temp, started = _blocking(project, tmp_path)
    script, out = tmp_path / "w296_holder.py", tmp_path / "holder_pids"
    script.write_text(HOLDER)
    env = dict(os.environ, PYTHONPATH=str(Path(runner.__file__).parents[2]))
    holder = subprocess.Popen([sys.executable, str(script), __file__, str(root), str(temp),
                               str(tmp_path / "w296_reap"), str(started), str(out)], env=env, stdin=subprocess.DEVNULL)
    try:
        _wait_for(out)
        seen = dict(zip(("gov", "group", "reaper"), map(int, out.read_text().split())))
        assert not _gone(seen["gov"]) and group_alive(seen["group"])  # the run blocks: both are alive here
    finally:
        holder.kill()  # SIGKILL by its pid: the case's process ends with no finaliser of its own
        holder.wait()
    _nothing_left(seen)


# the planted test starts A in a session of its own, A (which ignores SIGTERM, so that B stays its child until the
# end) starts B in another and both stay; A records "<A> <B>"
NESTED = ("import os, subprocess, sys, time\n\ndef test_a():\n"
          "    inner = ('import os, signal, subprocess, sys, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); '\n"
          "             'b = subprocess.Popen([sys.executable, \"-c\", \"import time; time.sleep(120)\"], '\n"
          "             'start_new_session=True); '\n"
          "             'open(sys.argv[1] + \".part\", \"w\").write(f\"{{os.getpid()}} {{b.pid}}\"); '\n"
          "             'os.replace(sys.argv[1] + \".part\", sys.argv[1]); time.sleep(120)')\n"
          "    subprocess.Popen([sys.executable, '-c', inner, {nested!r}], start_new_session=True)\n"
          "    open({started!r}, 'w').write(str(os.getpid()))\n    time.sleep(120)\n")


def test_w2_96_r9_r12_a_planted_tests_own_sessions_are_reaped_once_gov_can_no_longer(project, tmp_path):
    """DEC-866 rewrite, round 2: a planted test's processes in sessions of their own, one under the other, while
    gov is stopped (SIGSTOP) so that it can neither end nor reap its run; the case's body ends early. Afterwards no
    group of theirs has a live process: the reaper finds them as descendants of what it recorded."""
    root, temp = project
    started, nested = tmp_path / "started", tmp_path / "nested"
    _plant(root, ONE_LINE, {"test_a.py": NESTED.format(nested=str(nested), started=str(started))})
    seen: dict[str, int] = {}
    with pytest.raises(pytest.fail.Exception, match="ends early"):
        with _planted(tmp_path / "w296_reap") as launch:
            gov = launch(root, temp)
            _wait_for(started)
            _wait_for(nested)
            seen["gov"] = gov.pid
            seen["a"], seen["b"] = map(int, nested.read_text().split())
            assert group_alive(seen["a"]) and group_alive(seen["b"])
            os.kill(gov.pid, signal.SIGSTOP)  # gov can no longer stop or reap its run itself
            pytest.fail("the case's body ends early")
    assert _gone(seen["gov"])
    assert not group_alive(seen["a"]) and not group_alive(seen["b"])


@pytest.mark.parametrize("signum", [2, 15, 1])
def test_w2_96_r11_an_inherited_ignore_is_kept(project, tmp_path, launch, signum):
    root, temp = project
    started, go = tmp_path / "started", tmp_path / "go"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go))})
    gov = launch(root, temp, ignore=(signum,))
    _wait_for(started)
    gov.send_signal(signum)
    time.sleep(0.5)
    assert gov.poll() is None
    go.write_text("x")
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 0, out
    assert json.loads(out)["result"]["outcome"] == "pass"
    assert list(temp.iterdir()) == []


# --- R13: the command is recorded -------------------------------------------------------------------------------------

def test_w2_96_r13_accept_is_a_recorded_command():
    from gov.check.commands import GOV_COMMANDS, RECORDED_GOV_COMMANDS

    assert "accept" in RECORDED_GOV_COMMANDS and "accept" in GOV_COMMANDS
