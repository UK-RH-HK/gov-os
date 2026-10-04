"""W1-47 -- without a session role there is no wide scope.

KPI success 7: "The guard function that resolves a role's allowed paths fails
closed when its session-role argument is missing: without that argument the
orchestrator gets no wide scope (DEC-178), and a builder test in
tests/unit/guard/ shows it (DEC-179)".

The KPI names a builder test as its evidence: the function is internal, and its
one caller, the hook, always passes the argument. An acceptance test can show
two things through public interfaces.

- What the hook does when the session's own role is missing or is not
  orchestrator: an ``orchestrator`` subagent gets no wide scope. This is the
  behaviour DEC-178 fixed, and the change must not loosen it.
- That the builder tests in ``tests/unit/guard/`` pass. Whether one of them
  calls the function without the argument is for the reviewer to read; this
  suite does not import the guard.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

import w1_47_support as support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
ENGINEER_TICKET = support.TICKET_OF[ENGINEER]
ORCHESTRATOR_TICKET = support.TICKET_OF[ORCHESTRATOR]

# name: environment of a session whose own role is missing. The ticket is declared all the same.
MISSING = {
    "GOV_ROLE-not-set": {},
    "GOV_ROLE-empty": {"GOV_ROLE": ""},
    "GOV_ROLE-blank": {"GOV_ROLE": "   "},
}
# A file outside every fixture ticket's paths: only the wide scope would allow it.
OUTSIDE = "README.md"


def _write(project, relpath):
    return support.write_input("Write", project / relpath)


@pytest.mark.parametrize("case", sorted(MISSING))
@pytest.mark.parametrize("ticket", (ORCHESTRATOR_TICKET, ENGINEER_TICKET, None), ids=("its-ticket", "another", "none"))
def test_an_orchestrator_subagent_has_no_wide_scope_when_the_session_role_is_missing(project, guard, case, ticket):
    """KPI success 7 (DEC-178, DEC-179): a file write."""
    result = guard(project, "Write", _write(project, OUTSIDE), (None, ticket, ORCHESTRATOR), environment=MISSING[case])
    assert result.decision == "deny", (
        f"Write on {OUTSIDE} by an orchestrator subagent in a session with {case}: {result.describe()}"
    )


@pytest.mark.parametrize("case", sorted(MISSING))
def test_an_orchestrator_subagent_has_no_wide_scope_through_bash_either(project, guard, case):
    """KPI success 7: a Bash write."""
    command = f"echo changed > {OUTSIDE}"
    result = guard(project, "Bash", support.bash_input(command), (None, ORCHESTRATOR_TICKET, ORCHESTRATOR),
                   environment=MISSING[case])
    assert result.decision == "deny", (
        f"Bash `{command}` by an orchestrator subagent in a session with {case}: {result.describe()}"
    )


@pytest.mark.parametrize("session_role", (ENGINEER, support.TEST_DESIGNER, support.AUDITOR, "owner"))
def test_an_orchestrator_subagent_in_another_role_s_session_has_no_wide_scope(project, guard, session_role):
    """DEC-178: the wide scope holds only when the session's own role is orchestrator."""
    result = guard(project, "Write", _write(project, OUTSIDE), (session_role, ENGINEER_TICKET, ORCHESTRATOR))
    assert result.decision == "deny", (
        f"Write on {OUTSIDE} by an orchestrator subagent in a {session_role} session: {result.describe()}"
    )


def test_the_orchestrator_s_own_session_keeps_the_wide_scope(project, guard):
    """Failing closed takes nothing from the orchestrator's own session (DEC-156)."""
    for who in ((ORCHESTRATOR, ORCHESTRATOR_TICKET, None), (ORCHESTRATOR, ORCHESTRATOR_TICKET, ORCHESTRATOR)):
        result = guard(project, "Write", _write(project, OUTSIDE), who)
        support.assert_allowed(result, f"Write on {OUTSIDE} in the orchestrator's own session, as {who}")


def test_the_builder_tests_of_the_guard_pass():
    """KPI success 7: "a builder test in tests/unit/guard/ shows it": the builder suite is green."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/guard", "-q", "-p", "no:cacheprovider"],
        cwd=str(support.REPO_ROOT), env=env, capture_output=True, text=True, timeout=300, check=False,
    )
    assert proc.returncode == 0, f"tests/unit/guard does not pass:\n{proc.stdout[-2000:]}\n{proc.stderr[-1000:]}"
