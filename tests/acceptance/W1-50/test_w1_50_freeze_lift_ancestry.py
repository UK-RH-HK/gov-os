"""KPI success 4 and 7 (DEC-409, rule 1): who may lift a freeze, and who may still set one.

"gov pause --off refuses when any ancestor process is a Claude Code session,
wherever it was started, the operator console included" and "Setting a freeze
stays open to the owner, from a terminal or the operator console, and to the
orchestrator".

Two ways in, both described in ``w1_50_freeze_README.md``:

- **the internal function** ``gov.pause.command.lift(root, ancestry=None,
  terminal=None)``, called in a new process with a planted ancestry and a
  planted terminal (``w1_50_freeze_lift``). This is the one place where a test
  goes below the command line: by design the command line cannot be made to
  lift from under an agent session, and every suite runs under one;
- **the real command line**, ``python3 -m gov.cli.main pause --off``, with the
  ancestry the suite really has. Under an agent session that ancestry holds a
  Claude Code session (or, inside a launched session's sandbox, cannot be
  read); from a plain terminal the test's pipes are no terminal. So "refused
  and nothing changes" holds wherever the suite runs, and the reason is pinned
  only where the test plants it.

Every project is this test's own temporary repository.
"""

from __future__ import annotations

import os
import re

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_frozen, freeze_interface, freeze_project, freeze_sandbox,
)

lift = support.lift_support
pause_support = support.pause_support

NAMES_A_SESSION = re.compile(r"claude", re.IGNORECASE)
NAMES_THE_READING = re.compile(r"ancest|process|cannot be read|unreadable|not readable", re.IGNORECASE)


def _assert_refused(run, what):
    assert run.status == lift.REFUSED, f"{what}: the lift was not refused: {run.describe()}"
    assert run.message.strip(), f"{what}: the refusal says nothing: {run.describe()}"


# --------------------------------------------------------------------------
# A Claude Code session among the ancestors
# --------------------------------------------------------------------------



@pytest.mark.parametrize("shape", sorted(lift.UNREADABLE_ANCESTRIES))
def test_an_ancestry_that_cannot_be_read_refuses_the_lift(freeze_frozen, freeze_sandbox, shape):
    """Not being able to read the chain up to the system's first process refuses (the stricter reading)."""
    before = support.flag_state(freeze_frozen)

    run = lift.lift(freeze_frozen, freeze_sandbox, ancestry=lift.UNREADABLE_ANCESTRIES[shape])

    _assert_refused(run, shape)
    assert NAMES_THE_READING.search(run.message), \
        f"{shape}: the refusal does not say that the ancestry could not be read: {run.message!r}"
    support.assert_nothing_changed(freeze_frozen, before, shape)


@pytest.mark.parametrize("role", ["", "owner", "orchestrator", "engineer"])
def test_gov_role_does_not_turn_a_session_into_the_owner(freeze_frozen, freeze_sandbox, role):
    """DEC-407, DEC-409: "whatever GOV_ROLE says". Unset is every other case of this file."""
    before = support.flag_state(freeze_frozen)

    run = lift.lift(freeze_frozen, freeze_sandbox, ancestry=lift.SESSION_ANCESTRIES["headless-p"], role=role)

    _assert_refused(run, f"GOV_ROLE={role!r}")
    support.assert_nothing_changed(freeze_frozen, before, f"GOV_ROLE={role!r}")


# --------------------------------------------------------------------------
# The real command line
# --------------------------------------------------------------------------

def _assert_the_command_line_refused(run, project, before, interface, what):
    error = pause_support.failed(run, interface)
    assert error["message"].strip()
    support.assert_nothing_changed(project, before, what)
    return error


# Names an implementer might give a way round the checks. None may be one.
SWITCHES = {
    "GOV_PAUSE_ANCESTRY": "[]", "GOV_ANCESTRY": "[]", "GOV_PAUSE_SKIP_ANCESTRY": "1", "GOV_SKIP_ANCESTRY": "1",
    "GOV_PAUSE_NO_ANCESTRY_CHECK": "1", "GOV_PAUSE_TERMINAL": "0,1", "GOV_PAUSE_NO_TTY": "1", "GOV_NO_TTY": "1",
    "GOV_PAUSE_FORCE": "1", "GOV_FORCE": "1", "GOV_PAUSE_YES": "1", "GOV_ASSUME_YES": "1",
    "GOV_PAUSE_CODE": "LIFT-0000", "GOV_LIFT_CODE": "LIFT-0000", "GOV_OWNER": "1", "GOV_IS_OWNER": "1",
    "GOV_ALLOW_LIFT": "1", "GOV_TEST": "1", "GOV_TESTING": "1", "GOV_TEST_MODE": "1", "GOV_DEBUG": "1",
    "PYTEST_CURRENT_TEST": "tests/acceptance/W1-50/test_x.py::test_y (call)", "CI": "true",
}
ENVIRONMENTS = {
    "gov-role-empty": ("", {}),
    "gov-role-owner": ("owner", {}),
    "the-session-s-own-marks-cleared": (None, {"CLAUDECODE": "", "CLAUDE_CODE_ENTRYPOINT": "", "CLAUDE_PROJECT_DIR": "",
                                               "GOV_TICKET": ""}),
    "every-switch-name-at-once": (None, SWITCHES),
}


@pytest.mark.parametrize("name", sorted(ENVIRONMENTS))
def test_no_environment_variable_turns_the_checks_off(freeze_frozen, freeze_sandbox, freeze_interface, name):
    """The seam of the tests is a parameter of an internal function: nothing in the environment reaches it."""
    role, extra = ENVIRONMENTS[name]
    before = support.flag_state(freeze_frozen)

    run = support.run_cli(freeze_frozen, freeze_sandbox, "pause", "--off", "--json", role=role, extra_env=extra)

    _assert_the_command_line_refused(run, freeze_frozen, before, freeze_interface, name)


def test_no_option_turns_the_checks_off(freeze_frozen, freeze_sandbox):
    """An option that is not one of the command's is a usage error, and the flag stays."""
    before = support.flag_state(freeze_frozen)
    for extra in (["--force"], ["--yes"], ["-y"], ["--no-tty"], ["--code", "LIFT-0000"], ["--ancestry", "[]"],
                  ["--terminal", "0,1"], ["--owner"], ["--i-am-the-owner"]):
        run = support.run_cli(freeze_frozen, freeze_sandbox, "pause", "--off", *extra, "--json")
        assert run.returncode == 2, f"gov pause --off {' '.join(extra)} is not a usage error\n{run.describe()}"
        support.assert_nothing_changed(freeze_frozen, before, f"gov pause --off {' '.join(extra)}")


def test_the_help_shows_no_option_for_the_checks(freeze_project, freeze_sandbox):
    """``gov pause --help`` names the options of W1-28 and the shared ones, and no other."""
    run = support.run_cli(freeze_project, freeze_sandbox, "pause", "--help")
    assert run.returncode == 0, run.describe()
    options = set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", run.stdout))
    assert options == {"--help", "--off", "--cancel-agents", "--rollback", "--json", "--root", "--session", "--role"}, \
        f"gov pause --help names other options than the command's own: {sorted(options)}\n{run.stdout}"


# --------------------------------------------------------------------------
# Setting a freeze stays open (KPI success 7)
# --------------------------------------------------------------------------

