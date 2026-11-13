"""S5 and F3 (second half): a launched session gets a cleaned process environment.

S5: PATH, HOME, the locale, what the CLI needs to sign in, its identity and the launcher's own values (TMPDIR,
CLAUDE_CODE_TMPDIR) reach the session; none of the parent's CLAUDE* and GOV* variables (its session id, messaging
socket and token, child-session mark, effort, compaction window, subagent model, GOV_DEV_TIERS) and no PYTHONPATH,
shown by a test that starts the launcher with each set [DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, W2-M393].
F3: a parent's CLAUDE*, GOV* or PYTHONPATH value in a launched session.

Both the session's process environment (what the stand-in CLI records) and the ``env`` block of its ``--settings``
value (which the CLI applies to its own process and its commands) are read. The names the launcher sets from its
own values (CLAUDE_CODE_TMPDIR, GOV_ROLE, GOV_TICKET) may be there, never with the parent's value. A planted value
that turns up under any name fails too (each planted value holds the word ``zqxw56parent``).
"""

from __future__ import annotations

import os

import pytest

import w2_56_support as s


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    s.make_project(box)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return box


def _planted(names) -> dict:
    return {name: s.parent_value(name) for name in names}


def _launch_with(box, planted: dict, role=s.ENGINEER, extra=None):
    env = s.base_environment(box)
    env.update(planted)
    env.update(extra or {})
    launch = s.run_launch(box, role, s.TICKET_OF[role].tk, env=env)
    assert launch.returncode == 0 and launch.started, f"the launch did not start one session\n{launch.describe()}"
    return launch


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s5_no_parent_claude_gov_or_pythonpath_value_reaches_the_session(box, role):
    planted = _planted(s.PARENT_VARIABLES)
    launch = _launch_with(box, planted, role)
    process = s.leaks(launch.call["env"], planted)
    settings = s.leaks(launch.settings().get("env") or {}, planted)
    assert not process, f"{role}: the parent's values reached the session's process environment: {process}"
    assert not settings, f"{role}: the parent's values reached the env block of --settings: {settings}"


@pytest.mark.parametrize("name", sorted(s.PARENT_VARIABLES))
def test_s5_each_parent_variable_set_alone_is_kept_from_the_session(box, name):
    planted = _planted([name])
    launch = _launch_with(box, planted)
    process = s.leaks(launch.call["env"], planted)
    settings = s.leaks(launch.settings().get("env") or {}, planted)
    assert not process and not settings, (f"the parent's {name} reached the session: process {process}, "
                                          f"--settings env {settings}")


def test_s5_the_session_keeps_path_home_the_locale_and_its_identity(box):
    planted = _planted(s.PARENT_VARIABLES)
    parent = s.base_environment(box)
    env = _launch_with(box, planted).call["env"]
    missing = [entry for entry in parent["PATH"].split(os.pathsep) if entry and entry not in
               env.get("PATH", "").split(os.pathsep)]
    assert env.get("PATH") and not missing, f"PATH lost the parent's entries {missing}: {env.get('PATH')!r}"
    for name in ("HOME", "LANG", "LC_ALL", "USER", "LOGNAME"):
        assert env.get(name) == parent[name], f"{name} is {env.get(name)!r}, the parent's is {parent[name]!r}"


def test_s5_tmpdir_and_claude_code_tmpdir_are_the_launchers_own_temp_folder(box):
    planted = _planted(s.PARENT_VARIABLES)
    parent = s.base_environment(box)
    launch = _launch_with(box, planted)
    env, settings_env = launch.call["env"], launch.settings().get("env") or {}
    tmpdir = env.get("TMPDIR")
    assert tmpdir and env.get("CLAUDE_CODE_TMPDIR") == tmpdir, (
        f"TMPDIR {tmpdir!r} and CLAUDE_CODE_TMPDIR {env.get('CLAUDE_CODE_TMPDIR')!r} are not one folder")
    assert tmpdir != parent["TMPDIR"] and s.MARK not in tmpdir, f"TMPDIR {tmpdir!r} is the parent's, not the launcher's"
    for name in ("TMPDIR", "CLAUDE_CODE_TMPDIR"):
        assert settings_env.get(name, tmpdir) == tmpdir, f"--settings env {name} is {settings_env.get(name)!r}"


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s5_the_launched_role_and_ticket_replace_the_parents(box, role):
    planted = _planted(["GOV_ROLE", "GOV_TICKET"])
    launch = _launch_with(box, planted, role)
    ticket = s.TICKET_OF[role].tk
    settings_env = launch.settings().get("env") or {}
    assert settings_env.get("GOV_ROLE") == role and settings_env.get("GOV_TICKET") == ticket, (
        f"--settings env names {settings_env.get('GOV_ROLE')!r} / {settings_env.get('GOV_TICKET')!r}")
    env = launch.call["env"]
    for name, value in (("GOV_ROLE", role), ("GOV_TICKET", ticket)):
        assert env.get(name, value) == value, f"the process environment's {name} is {env.get(name)!r}, not {value!r}"


def test_s5_an_unrelated_parent_variable_is_not_passed(box):
    """S5 names what the session gets (PATH, HOME, the locale, the sign-in, its identity, the launcher's values):
    read as the list of what passes, a variable of the parent that is none of these does not reach the session."""
    launch = _launch_with(box, {}, extra={"W2_56_UNRELATED_PARENT_VALUE": "zqxw56unrelated"})
    env = launch.call["env"]
    held = [name for name, value in env.items() if "zqxw56unrelated" in value]
    assert not held, f"an unrelated variable of the parent reached the session: {held}"
