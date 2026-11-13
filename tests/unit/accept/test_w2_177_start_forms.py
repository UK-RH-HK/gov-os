"""W2-177 (DAEO-1k7y): the two causes of the six W2-96 signal reds, one case each (docs/changes/W2-177-evidence.md).

(A) ``gov accept``'s child is given the caller's ``PYTHONUSERBASE`` (pytest is found through it under an empty HOME);
    no other ``PYTHON*`` variable of the caller's reaches it.
(B) the test launcher ``w2_96_reap.launch_gov`` starts gov with SIGINT, SIGTERM and SIGHUP at their default unless
    the case names them to be ignored: a test process started as a background job (SIGINT ignored) must not pass
    that on, or the signal cases test the start form, not gov.
"""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

import pytest

from gov.accept import runner
from w2_96_reap import launch_gov

PROBE = (
    "import signal\n"
    "print(' '.join(str(int(signal.getsignal(s) == signal.SIG_IGN))"
    " for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)))\n"
    "sys.exit(0)\n"
)
HANDLED = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


def _child_env(monkeypatch, tmp_path: Path) -> dict[str, str]:
    """The environment ``runner._run`` gives its child: a harmless child stands in for pytest, the env is recorded."""
    root, folder, seen = tmp_path / "root", tmp_path / "root" / "tests", {}
    folder.mkdir(parents=True)
    real = subprocess.Popen

    class Spy(real):
        def __init__(self, command, **kwargs):
            seen.update(kwargs["env"])
            report = next(arg.partition("=")[2] for arg in command if arg.startswith("--junitxml="))
            super().__init__([sys.executable, "-c", "import sys; open(sys.argv[1], 'w').write('<testsuites/>')", report],
                             **kwargs)

    monkeypatch.setattr(runner.subprocess, "Popen", Spy)
    runner._run(root, folder, 30)
    assert seen, "the run started no child"
    return seen


def test_w2_177_the_child_is_given_the_callers_pythonuserbase(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTHONUSERBASE", "/the/callers/user/base")
    env = _child_env(monkeypatch, tmp_path)
    assert env.get("PYTHONUSERBASE") == "/the/callers/user/base"


def test_w2_177_no_user_base_is_made_up_and_no_other_python_variable_passes(monkeypatch, tmp_path):
    monkeypatch.delenv("PYTHONUSERBASE", raising=False)
    monkeypatch.setenv("PYTHONSTARTUP", "/the/callers/startup.py")
    monkeypatch.setenv("PYTHONHOME", "/the/callers/home")
    env = _child_env(monkeypatch, tmp_path)
    assert "PYTHONUSERBASE" not in env
    assert "PYTHONSTARTUP" not in env and "PYTHONHOME" not in env
    assert env["PYTHONDONTWRITEBYTECODE"] == "1" and env["PYTHONPATH"].startswith(str(tmp_path / "root" / "src"))


def _states(tmp_path: Path, ignore: tuple = ()) -> list[int]:
    """Whether SIGINT, SIGTERM, SIGHUP are ignored in a planted gov's process at its start (its wrapper's head)."""
    folder, temp = tmp_path / "launch", tmp_path / "temp"
    folder.mkdir()
    temp.mkdir()
    gov = launch_gov(tmp_path, temp, folder, head="import signal\n" + PROBE, ignore=ignore)
    out, _ = gov.communicate(timeout=60)
    assert gov.returncode == 0, out
    return [int(word) for word in out.split()]


@pytest.fixture
def all_ignored():
    """The test process started as a background job does: SIGINT (and here SIGTERM, SIGHUP) ignored; restored after."""
    before = {signum: signal.getsignal(signum) for signum in HANDLED}
    try:
        for signum in HANDLED:
            signal.signal(signum, signal.SIG_IGN)
        yield
    finally:
        for signum, handler in before.items():
            signal.signal(signum, handler)


def test_w2_177_the_launcher_does_not_pass_on_the_test_processs_ignored_signals(all_ignored, tmp_path):
    assert _states(tmp_path) == [0, 0, 0]


def test_w2_177_the_launcher_ignores_exactly_the_signals_it_is_given(all_ignored, tmp_path):
    # a loop, not a parametrisation: the repository's opt-in lists keep only a parametrised case's first row
    for named in HANDLED:
        expected = [int(signum == named) for signum in HANDLED]
        (tmp_path / f"case-{int(named)}").mkdir()
        assert _states(tmp_path / f"case-{int(named)}", ignore=(named,)) == expected, f"named: {named!r}"


def test_w2_177_the_launcher_ignores_all_three_when_all_are_given(all_ignored, tmp_path):
    assert _states(tmp_path, ignore=HANDLED) == [1, 1, 1]
