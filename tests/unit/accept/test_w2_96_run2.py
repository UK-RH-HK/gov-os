"""W2-96 (DAEO-ouet): builder tests of ``gov accept``'s run 2 (DEC-970): any failed case fails the run, signals
held back during the clean-up and ended as 128 plus the signal, a clean-up without recursion, an inherited
"ignore" kept, and ``accept`` recorded.

Each test plants a tiny project in a temporary folder; the signal tests start ``gov accept`` as its own process.
Nothing runs against this repository's own acceptance folders.
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

# gov accept as its own process; with W296_SLOW set, the clean-up's removal waits once it has begun, so that a
# signal is sent while the clean-up runs
WRAPPER = """import os, sys, time
from gov.accept import runner
from gov.cli.main import main
slow = os.environ.get("W296_SLOW")
if slow:
    remove = runner._remove
    def _slow(folder):
        open(slow, "w").write("x")
        time.sleep(2)
        remove(folder)
    runner._remove = _slow
sys.exit(main(sys.argv[1:]))
"""


def _launch(root: Path, temp: Path, tmp_path: Path, slow: Path | None = None, ignore: tuple = ()):
    script = tmp_path / "w296_gov.py"
    script.write_text(WRAPPER)
    env = dict(os.environ, PYTHONPATH=str(Path(runner.__file__).parents[2]), TMPDIR=str(temp))
    env.pop("W296_SLOW", None)
    if slow is not None:
        env["W296_SLOW"] = str(slow)

    def _ignore():
        for signum in ignore:
            signal.signal(signum, signal.SIG_IGN)

    return subprocess.Popen([sys.executable, str(script), "accept", "DAEO-t001", "--json", "--root", str(root)],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=_ignore)


def _wait_for(path: Path, seconds: float = 60) -> None:
    deadline = time.monotonic() + seconds
    while not (path.exists() and path.read_text()) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert path.exists()


@pytest.mark.parametrize("signals", [(2,), (15,), (1,), (2, 15, 1)])  # SIGINT, SIGTERM, SIGHUP, all three
def test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back(project, tmp_path, signals):
    root, temp = project
    started, go, slow = tmp_path / "started", tmp_path / "go", tmp_path / "slow"
    go.write_text("x")
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go)) + f"    print('{MARK}')\n"})
    gov = _launch(root, temp, tmp_path, slow=slow)
    _wait_for(slow)
    for signum in signals:
        gov.send_signal(signum)
        time.sleep(0.1)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 128 + signals[0]  # an ordinary exit, never a death by the signal
    assert MARK.encode() not in out and b"Traceback" not in out
    assert list(temp.iterdir()) == []


@pytest.mark.parametrize("first, more", [(2, (15, 1)), (15, (2,)), (1, (2,))])
def test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up(project, tmp_path, first, more):
    root, temp = project
    started, slow = tmp_path / "started", tmp_path / "slow"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(tmp_path / "never"))})
    gov = _launch(root, temp, tmp_path, slow=slow)
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
def test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it(project, tmp_path, kinds):
    root, temp = project
    started, go, slow = tmp_path / "started", tmp_path / "go", tmp_path / "slow"
    go.write_text("x")
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go))})
    gov = _launch(root, temp, tmp_path, slow=slow)
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


def test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it(project, tmp_path):
    root, temp = project
    started = tmp_path / "started"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(tmp_path / "never"))})
    gov = _launch(root, temp, tmp_path)
    _wait_for(started)
    child = int(started.read_text())
    gov.send_signal(signal.SIGINT)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 130
    assert b"Traceback" not in out and b"KeyboardInterrupt" not in out
    assert list(temp.iterdir()) == []
    assert _gone(child)


@pytest.mark.parametrize("signum", [2, 15, 1])
def test_w2_96_r11_an_inherited_ignore_is_kept(project, tmp_path, signum):
    root, temp = project
    started, go = tmp_path / "started", tmp_path / "go"
    _plant(root, ONE_LINE, {"test_a.py": GATED.format(started=str(started), go=str(go))})
    gov = _launch(root, temp, tmp_path, ignore=(signum,))
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
