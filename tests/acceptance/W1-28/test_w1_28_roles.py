"""KPI success 3, first clause [CAP-05.d, "owner-gated"].

"Pause, cancel and rollback run only on the owner's or the orchestrator's
invocation." DEC-365:

- The caller is ``GOV_ROLE`` when it is set: ``orchestrator`` is allowed, every
  worker role is refused. When ``GOV_ROLE`` is unset, the caller is the owner.
- The orchestrator may set the freeze. Only the owner lifts it: ``--off`` works
  only with ``GOV_ROLE`` unset.
- There is no ``--role`` flag for this command. ``gov`` gives every command the
  shared ``--role`` option (``src/gov/cli/main.py``), so the option still
  parses; what is tested is that this command does not read it to decide who
  calls.

A refused call ends with the error ``PAUSE_REFUSED`` (named after
``LAUNCH_REFUSED``, ``src/gov/launch/launcher.py``; DEC-378) and changes nothing: no
flag, no released claim, no commit. A ``GOV_ROLE`` that names no role is
neither the owner nor the orchestrator, and is refused like a worker.

The owner's call runs: every other file of this suite.
"""

from __future__ import annotations

import pytest

import w1_28_support as support


# --------------------------------------------------------------------------
# A worker is refused
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_worker_cannot_pause(project, pause, interface, role):
    before = support.head(project)
    support.refused(pause(role=role), interface)
    assert not support.is_paused(project), f"the call of {role} was refused and the flag is set"
    assert support.head(project) == before, "the refused call made a commit"


def test_a_role_nobody_knows_cannot_pause(project, pause, interface):
    support.refused(pause(role="developer"), interface)
    assert not support.is_paused(project), "the call was refused and the flag is set"


def test_a_worker_cannot_lift_a_pause(paused, pause, interface):
    support.refused(pause("--off", role=support.ENGINEER), interface)
    assert support.is_paused(paused), "a worker's gov pause --off cleared the flag"


def test_a_worker_cannot_cancel_agents(project, sandbox, pause, interface, claims):
    before, tickets = support.head(project), support.ticket_files(project)
    support.refused(pause("--cancel-agents", role=support.ENGINEER), interface)
    for ticket, holder in claims.items():
        assert support.tasks(project, sandbox, "holder", ticket) == holder, \
            f"a worker's gov pause --cancel-agents released the claim on {ticket}"
    assert not support.is_paused(project), "a worker's gov pause --cancel-agents set the flag"
    assert support.head(project) == before, "a worker's gov pause --cancel-agents made a commit"
    assert support.ticket_files(project) == tickets, "a worker's gov pause --cancel-agents changed a ticket file"


def test_a_worker_cannot_roll_back(project, pause, interface, history):
    before = support.head(project)
    support.refused(pause("--rollback", support.TICKET, role=support.ENGINEER), interface)
    assert support.head(project) == before, "a worker's gov pause --rollback made a commit"
    assert support.porcelain(project) == "", f"it left changes:\n{support.porcelain(project)}"
    assert not support.is_paused(project), "a worker's gov pause --rollback set the flag"


def test_a_workers_rollback_of_an_unknown_ticket_is_refused_as_a_workers_and_sets_nothing(project, pause, interface):
    """DEC-378: the flag is set "once the caller is allowed". The caller is judged first, so nothing is set here."""
    support.refused(pause("--rollback", support.UNKNOWN_TICKET, role=support.ENGINEER), interface)
    assert not support.is_paused(project), "a refused caller's rollback of an unknown ticket set the flag"


# --------------------------------------------------------------------------
# The orchestrator sets, and does not lift
# --------------------------------------------------------------------------

def test_the_orchestrator_can_pause(project, sandbox, pause, interface):
    support.succeeded(pause(role=support.ORCHESTRATOR), interface)
    assert support.is_paused(project), f"the orchestrator's gov pause did not set {support.FREEZE_FLAG_REL}"
    support.assert_denied(support.guard_write(project, sandbox, support.ORCHESTRATOR),
                          "after its own pause, the orchestrator's write")


def test_the_orchestrator_can_cancel_agents(project, pause, interface, claims):
    support.succeeded(pause("--cancel-agents", role=support.ORCHESTRATOR), interface)
    assert support.locks(project) == [], f"claims are still held: {support.locks(project)}"


def test_the_orchestrator_can_roll_back(project, pause, interface, history):
    support.succeeded(pause("--rollback", support.TICKET, role=support.ORCHESTRATOR), interface)
    support.assert_rolled_back(project)


def test_the_orchestrator_cannot_lift_a_pause(project, sandbox, pause, interface):
    """Only the owner lifts. The orchestrator's ``--off`` is refused, on its own freeze too, and the freeze stays."""
    support.succeeded(pause(role=support.ORCHESTRATOR), interface)
    support.refused(pause("--off", role=support.ORCHESTRATOR), interface)
    assert support.is_paused(project), "the orchestrator's gov pause --off cleared the flag"
    support.assert_denied(support.guard_write(project, sandbox, support.ENGINEER),
                          "after the orchestrator's refused --off, the write")


def test_the_owner_lifts_a_pause_the_orchestrator_set(project, sandbox, pause, lift, interface):
    support.succeeded(pause(role=support.ORCHESTRATOR), interface)
    lift()  # DEC-409: the owner in person
    assert not support.is_paused(project), "the owner's gov pause --off left the orchestrator's freeze"
    support.assert_allowed(support.guard_write(project, sandbox, support.ENGINEER), "after the owner's --off, the write")


# --------------------------------------------------------------------------
# The caller is GOV_ROLE, not --role
# --------------------------------------------------------------------------

def test_the_owner_is_the_call_without_gov_role_whatever_the_session_that_runs_the_tests_has(project, pause, lift,
                                                                                         interface, monkeypatch):
    """The tests run in a worker's session. Its ``GOV_ROLE`` does not reach the command: the call is the owner's."""
    monkeypatch.setenv(support.guard_support.ROLE_ENV, support.ENGINEER)
    support.succeeded(pause(), interface)
    assert support.is_paused(project)
    lift()  # DEC-409: the owner in person; the session's GOV_ROLE does not reach that call either
    assert not support.is_paused(project), "a call with no GOV_ROLE could not lift the pause"


@pytest.mark.parametrize("named", [support.ORCHESTRATOR, support.OWNER_NAME])
def test_a_worker_is_refused_whatever_role_it_names_with_the_role_option(project, pause, interface, named):
    support.refused(pause(role=support.ENGINEER, flag_role=named), interface)
    assert not support.is_paused(project), f"a worker paused the project with --role {named}"


def test_the_orchestrator_cannot_lift_a_pause_by_naming_the_owner(paused, pause, interface):
    support.refused(pause("--off", role=support.ORCHESTRATOR, flag_role=support.OWNER_NAME), interface)
    assert support.is_paused(paused), "the orchestrator lifted the pause with --role owner"


def test_the_owner_is_not_refused_for_a_role_option(project, pause, interface):
    """With ``GOV_ROLE`` unset the caller is the owner, whatever ``--role`` names: the option is not read."""
    support.succeeded(pause(flag_role=support.ENGINEER), interface)
    assert support.is_paused(project), "the owner's gov pause did not set the flag"
