"""Fifth batch: the wrapper turns the tool's loopback UI off (DEC-362) [CAP-12].

Tests added after implementation, reason "owner decision":

- **DEC-362.** The tool's daemon serves an HTTP graph view on ``127.0.0.1:9749`` unless the setting ``ui_enabled``
  of its home says ``false``. Every call the wrapper makes leaves the UI off: the tool, asked in the repository's
  home, says so; the daemon the call started did not serve it (no ``ui.serving`` line in the home's daemon log);
  and nothing listened on the port. That holds for the first call in a fresh repository, for a second
  ``index(root)``, and whatever the caller's environment, the name of the repository or a setting left in the
  home say.

How the wrapper turns it off is not held: no test looks for an argument of the tool's command line.

Every command that can start a daemon runs in a user and network namespace of its own, in which the UI port is
that command's alone: the port is one for the whole machine, and another session may run the tool. A machine that
gives no such namespace skips the cases.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

HELPER, ENTRY = "ui_helper", "ui_entry"
FILES = {
    "app/panel.py": f"def {HELPER}(value):\n    return value + 1\n\n\n"
                    f"def {ENTRY}(value):\n    return {HELPER}(value)\n",
    "README.md": "# Panel\n\nA small repository.\n",
}
# The binary reads none of these (it has CBM_UI_MAX_RENDER_NODES only); a caller may still set them.
UI_VARIABLES = {"CBM_UI": "true", "CBM_UI_ENABLED": "true", "CBM_UI_PORT": str(support.UI_PORT),
                "UI_ENABLED": "true", "UI_PORT": str(support.UI_PORT), "CBM_UI_MAX_RENDER_NODES": "1000"}
SWITCH_ON = "--ui=true"
LIST_PROJECTS = ("cli", "--quiet", "--json", "list_projects", '{"format":"json"}')


@pytest.fixture(scope="module")
def port(cbm):
    """Whether a command can have the UI port to itself (``support.port_watched``); else the test is skipped."""
    probe = support.make_sandbox()
    try:
        done = subprocess.run([*support.port_watched(probe.tmpdir / "probe.json", 0), sys.executable, "-c", "pass"],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
    finally:
        support.remove_sandbox(probe)
    if done.returncode != 0:
        pytest.skip(f"this machine gives a command no UI port of its own ({done.stderr.strip()[-200:]})")
    return support.port_watched


def _repository(base):
    repo = support.Repo(base)
    for rel, text in FILES.items():
        repo.write(rel, text)
    return repo.commit("first")


def _home(repo, sandbox):
    return Path(support.one(repo.root, "home", [], sandbox))


def _asked(repo, calls, sandbox, record, env=None):
    """Calls of the wrapper in one child, with the UI port watched while they run and shortly after."""
    return support.run_calls("gov.codeintel", repo.root, calls, sandbox, env=env,
                             launcher=support.port_watched(record))


def _ui_on(home, record, sandbox, served_before=0, setting=True):
    """What shows the UI on after a command: nothing when it is off."""
    shown = []
    served = support.ui_served(home) - served_before
    if served > 0:
        shown.append(f"the daemon log of the home holds {served} new line(s) with {support.UI_SERVING}")
    opened, looks = support.port_looks(record)
    if opened:
        shown.append(f"{support.UI_HOST}:{support.UI_PORT} was open at {opened} of {looks} looks")
    if setting:
        said = support.ui_setting(home, sandbox)
        if said != "false":
            shown.append(f"the tool says {support.UI_SETTING} = {said} in the home")
    return shown


def _callers_are_right(run, result):
    assert (("app/panel.py", ENTRY) in support.entries(result, f"callers({HELPER})")), \
        f"the answer changed: {ENTRY} is no caller of {HELPER}\n{run.describe()}"


# --------------------------------------------------------------------------
# The premise: the tool alone
# --------------------------------------------------------------------------

def _tool_alone(home, sandbox, record):
    env = support.child_env(sandbox) | {"CBM_CACHE_DIR": str(home)}
    env.pop("PYTHONPATH")
    done = subprocess.run([*support.port_watched(record), support.TOOL, *LIST_PROJECTS],
                          cwd=str(sandbox.elsewhere), env=env, capture_output=True, text=True,
                          timeout=support.TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"{support.TOOL} list_projects (home {home}) failed:\n{done.stdout}\n{done.stderr}"


def test_the_tool_alone_serves_its_ui_unless_the_setting_of_its_home_says_false(port, sandbox):
    """So the other cases pass only through the wrapper, and the three signs they read tell on from off."""
    left, off = sandbox.tmpdir / "left", sandbox.tmpdir / "off"
    for home in (left, off):
        home.mkdir()
    _tool_alone(left, sandbox, sandbox.tmpdir / "left.json")
    assert support.daemon_log(left), "the tool's daemon left no log in its home"
    assert support.ui_served(left) >= 1, \
        f"the tool alone did not say it served its UI:\n{support.daemon_log(left)[-2000:]}"
    opened, looks = support.port_looks(sandbox.tmpdir / "left.json")
    assert opened, f"the tool alone did not listen on {support.UI_HOST}:{support.UI_PORT} ({looks} looks)"
    assert support.ui_setting(left, sandbox) == "true", "the tool alone does not say its UI is enabled"

    support.tool_config(off, sandbox, "set", support.UI_SETTING, "false")
    _tool_alone(off, sandbox, sandbox.tmpdir / "off.json")
    assert support.daemon_log(off), "the tool's daemon left no log in its home"
    shown = _ui_on(off, sandbox.tmpdir / "off.json", sandbox)
    assert not shown, f"the setting of the home did not turn the UI off: {'; '.join(shown)}"


# --------------------------------------------------------------------------
# Every call of the wrapper, and a second index
# --------------------------------------------------------------------------

STEPS = {
    "index": [("index", [])],
    "projects": [("projects", [])],
    "callers": [("callers", [HELPER])],
    "index-again": [("index", []), ("callers", [HELPER])],
}


@pytest.fixture(scope="module")
def sequence(module, port, module_sandbox, tmp_path_factory):
    """One fresh repository: indexed, listed, asked and indexed again. ``step -> (run, daemon log there, UI signs)``."""
    tmp_path = tmp_path_factory.mktemp("w1-16-ui")
    repo = _repository(tmp_path / "panel")
    home = _home(repo, module_sandbox)
    seen = {}
    for step, calls in STEPS.items():   # one indexing job at a time
        record = tmp_path / f"{step}.json"
        before = 0 if calls[0][0] == "index" else support.ui_served(home)   # an index builds the home anew
        run = _asked(repo, calls, module_sandbox, record)
        seen[step] = (run, bool(support.daemon_log(home)), _ui_on(home, record, module_sandbox, before))
    return seen


@pytest.mark.parametrize("step", ["index", "projects", "callers"])
def test_a_call_of_the_wrapper_leaves_the_ui_off(sequence, step):
    """The first call in a fresh repository (``index``), ``projects`` and an answer function."""
    run, logged, shown = sequence[step]
    assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
    if step == "projects":
        assert isinstance(run.results[0], list) and len(run.results[0]) == 1, \
            f"the answer changed: expected one project name\n{run.describe()}"
    if step == "callers":
        _callers_are_right(run, run.results[0])
    assert logged, "the home holds no daemon log after the call: nothing tells whether a daemon served the UI"
    assert not shown, f"after {step}(root) the UI is on: {'; '.join(shown)}"


def test_a_second_index_keeps_the_ui_off(sequence):
    """``index(root)`` removes the home and builds it anew: the setting does not go with it."""
    run, logged, shown = sequence["index-again"]
    assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
    _callers_are_right(run, run.results[1])
    assert logged, "the home holds no daemon log after the call: nothing tells whether a daemon served the UI"
    assert not shown, f"after a second index(root) the UI is on: {'; '.join(shown)}"


def test_a_first_call_that_builds_no_index_does_not_serve_the_ui(module, port, tmp_path, sandbox):
    """``projects(root)`` in a repository that was never indexed. Whether it answers or is refused is not held."""
    repo = _repository(tmp_path / "never")
    home = _home(repo, sandbox)
    _asked(repo, [("projects", [])], sandbox, tmp_path / "projects.json")
    shown = _ui_on(home, tmp_path / "projects.json", sandbox, setting=False)   # the home may not exist: not asked
    assert not shown, f"projects(root) as the first call served the UI: {'; '.join(shown)}"


# --------------------------------------------------------------------------
# A caller cannot turn it back on
# --------------------------------------------------------------------------

def test_ui_variables_of_the_callers_environment_do_not_turn_the_ui_on(module, port, tmp_path, sandbox):
    repo = _repository(tmp_path / "env")
    home = _home(repo, sandbox)
    run = _asked(repo, [("index", []), ("callers", [HELPER])], sandbox, tmp_path / "env.json",
                 env=support.child_env(sandbox) | UI_VARIABLES)
    assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
    _callers_are_right(run, run.results[1])
    shown = _ui_on(home, tmp_path / "env.json", sandbox)
    assert not shown, f"with UI variables in the caller's environment the UI is on: {'; '.join(shown)}"


def test_a_repository_and_a_symbol_named_like_the_switch_do_not_turn_the_ui_on(module, port, tmp_path, sandbox):
    """The root's path is the one thing of a caller that stands on the tool's command line; a name is asked too."""
    repo = _repository(tmp_path / SWITCH_ON)
    home = _home(repo, sandbox)
    run = _asked(repo, [("index", []), ("callers", [HELPER]), ("callers", [SWITCH_ON])], sandbox,
                 tmp_path / "switch.json")
    assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
    _callers_are_right(run, run.results[1])
    assert run.results[2] == [], f"a name that is no symbol has callers\n{run.describe()}"
    shown = _ui_on(home, tmp_path / "switch.json", sandbox)
    assert not shown, f"in a repository named {SWITCH_ON} the UI is on: {'; '.join(shown)}"


def test_a_setting_left_in_the_home_is_turned_off_by_the_next_call(module, port, tmp_path, sandbox):
    """Someone sets ``ui_enabled`` to ``true`` with the tool, in the repository's home; then the wrapper is called."""
    repo = _repository(tmp_path / "left")
    home = _home(repo, sandbox)
    first = _asked(repo, [("index", [])], sandbox, tmp_path / "index.json")
    assert first.results is not None, f"gov.codeintel did not answer\n{first.describe()}"
    for function, args in (("projects", []), ("callers", [HELPER])):
        # A daemon that still runs is not the case here: the next call starts one. Its end is waited for, three
        # seconds at most (the time the case slept before; DEC-561).
        support.wait_for_daemon_end(home)
        support.tool_config(home, sandbox, "set", support.UI_SETTING, "true")
        assert support.ui_setting(home, sandbox) == "true", "the premise does not hold: the setting was not left on"
        record, before = tmp_path / f"{function}.json", support.ui_served(home)
        run = _asked(repo, [(function, args)], sandbox, record)
        assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
        if function == "callers":
            _callers_are_right(run, run.results[0])
        shown = _ui_on(home, record, sandbox, before)
        assert not shown, f"after a setting left on in the home, {function}(root) leaves the UI on: {'; '.join(shown)}"
