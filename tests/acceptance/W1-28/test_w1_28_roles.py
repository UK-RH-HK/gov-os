"""KPI success 4, first clause [CAP-05.d, "owner-gated"].

"Pause, cancel and rollback run only on the owner's or the orchestrator's
invocation."

- A worker role's call, and a call under a role nobody knows, is refused by
  the command and changes nothing: no flag, no released claim, no commit.
- The owner's call runs: every other file of this suite.
- The orchestrator's call runs. For ``--cancel-agents`` and ``--rollback``
  that agrees with DEC-292 (releasing a dead session's claim is the main
  orchestrator's job) and DEC-156. For the plain pause it follows the KPI
  line as written, against DEC-176 ("setting or lifting a freeze is the
  owner's action"): decision package DP-2, option (a) or (b). No case here
  has the orchestrator lift a pause.

How the role reaches the command is DP-3: ``w1_28_support.pause`` gives it as
``--role`` and as ``GOV_ROLE``, with the same value. A call with no role, and
a call whose two values differ, are not tested.
"""

from __future__ import annotations

import pytest

import w1_28_support as support


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_worker_cannot_pause(project, pause, interface, role):
    support.refused(pause(role=role), interface)
    assert not support.is_paused(project), f"the call of {role} was refused and the flag is set"


def test_a_role_nobody_knows_cannot_pause(project, pause, interface):
    support.refused(pause(role="developer"), interface)
    assert not support.is_paused(project), "the call was refused and the flag is set"


def test_a_worker_cannot_lift_a_pause(paused, pause, interface):
    support.refused(pause("--off", role=support.ENGINEER), interface)
    assert support.is_paused(paused), "a worker's gov pause --off cleared the flag"


def test_a_worker_cannot_cancel_agents(project, sandbox, pause, interface, claims):
    support.refused(pause("--cancel-agents", role=support.ENGINEER), interface)
    for ticket, holder in claims.items():
        assert support.tasks(project, sandbox, "holder", ticket) == holder, \
            f"a worker's gov pause --cancel-agents released the claim on {ticket}"


def test_a_worker_cannot_roll_back(project, pause, interface, history):
    before = support.head(project)
    support.refused(pause("--rollback", support.TICKET, role=support.ENGINEER), interface)
    assert support.head(project) == before, "a worker's gov pause --rollback made a commit"
    assert support.porcelain(project) == "", f"it left changes:\n{support.porcelain(project)}"


def test_the_orchestrator_can_pause(project, pause, interface):
    """Follows the KPI line as written (DP-2, option (a) or (b))."""
    support.succeeded(pause(role=support.ORCHESTRATOR), interface)
    assert support.is_paused(project), f"the orchestrator's gov pause did not set {support.FREEZE_FLAG_REL}"


def test_the_orchestrator_can_cancel_agents(project, pause, interface, claims):
    support.succeeded(pause("--cancel-agents", role=support.ORCHESTRATOR), interface)
    assert support.locks(project) == [], f"claims are still held: {support.locks(project)}"


def test_the_orchestrator_can_roll_back(project, pause, interface, history):
    support.succeeded(pause("--rollback", support.TICKET, role=support.ORCHESTRATOR), interface)
    support.assert_rolled_back(project)
