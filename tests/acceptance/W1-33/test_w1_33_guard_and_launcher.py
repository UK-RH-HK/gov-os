"""W1-33 -- what the definitions state is what the guard and the launcher decide.

A role definition grants nothing by itself: the guard decides a role's write
scope and the install rule, the launcher its network profile. These tests ask
both, in a temporary copy of the project, for the decisions the KPI lines state.
No session is started and no call is made.

KPI success 2: "Only the test designer pattern includes tests/acceptance/**; the
auditor is read-only; only the orchestrator may install, and only after owner
approval in chat (DEC-083)".

KPI success 3 [CAP-58.b]: "WRITE_REPO_SCOPED via allowed_paths;
PACKAGE_INSTALL/SYSTEM_INSTALL per DEC-083 ... a launched worker session's
network grant comes from the launcher's network profile ... (empty for engineer,
test designer and auditor ...)".

KPI success 4: "the orchestrator ... write scope, anywhere in the repository
except tests/acceptance/** (DEC-156)".

Every test here is green before implementation: W1-02, W1-04, W1-45 and W1-46
built these decisions. They stay in this suite so that a definition and the
decision it describes are checked together.
"""

from __future__ import annotations

import pytest

import w1_33_support as support

w47 = support.w47
launch_support = support.launch_support
ACCEPTANCE_FILE = "tests/acceptance/W1-90/test_new.py"
INSTALL = "pip install requests"


@pytest.mark.parametrize("role", support.ROLES)
def test_only_the_test_designer_may_write_the_acceptance_tests(guard, project, role):
    result = guard("Write", w47.write_input("Write", project / ACCEPTANCE_FILE), role)
    if role == support.TEST_DESIGNER:
        w47.assert_allowed(result, f"a Write to {ACCEPTANCE_FILE} by the test designer")
    else:
        w47.assert_stopped(result, f"a Write to {ACCEPTANCE_FILE} by {role}")


def test_the_orchestrator_may_write_anywhere_else_in_the_repository(guard, project):
    for rel in ("README.md", "src/gov/guard/decide.py", "docs/notes.md", support.ROSTER_REL):
        w47.assert_allowed(guard("Write", w47.write_input("Write", project / rel), support.ORCHESTRATOR),
                           f"a Write to {rel} by the orchestrator")


def test_the_auditor_writes_only_the_report_path_of_its_own_ticket(guard, project):
    """DEC-112. The fixture ticket of the auditor allows ``docs/audit/**``."""
    report = launch_support.OWN_PATH[support.AUDITOR]
    w47.assert_allowed(guard("Write", w47.write_input("Write", project / report), support.AUDITOR),
                       f"a Write to {report} by the auditor on its own ticket")
    for rel in ("README.md", "src/gov/guard/decide.py", "docs/notes.md"):
        w47.assert_stopped(guard("Write", w47.write_input("Write", project / rel), support.AUDITOR),
                           f"a Write to {rel} by the auditor")
    other = guard("Write", w47.write_input("Write", project / report), support.AUDITOR,
                  w47.TICKET_OF[support.ENGINEER])
    w47.assert_stopped(other, f"a Write to {report} by the auditor on an engineer's ticket")


@pytest.mark.parametrize("role", support.ROLES)
def test_an_install_asks_for_the_orchestrator_and_is_denied_to_every_other_role(guard, role):
    result = guard("Bash", w47.bash_input(INSTALL), role)
    if role == support.ORCHESTRATOR:
        assert result.decision == "ask", f"`{INSTALL}` by the orchestrator did not ask: {result.describe()}"
    else:
        w47.assert_stopped(result, f"`{INSTALL}` by {role}")


@pytest.mark.parametrize("role", support.EMPTY_PROFILE_ROLES)
def test_the_launcher_gives_the_role_an_empty_network_profile(launch, role):
    result = launch(role)
    assert launch_support.allowed_domains(result.settings()) == [], (
        f"the settings built for {role} allow hosts: {launch_support.allowed_domains(result.settings())}"
    )


@pytest.mark.parametrize("role", support.NOT_LAUNCHED)
def test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker(launch, role):
    launch_support.assert_refused(launch(role), "worker role")
