"""KPI success 1, its CTO half, and failure 2 ("The CTO's install refused when the coordination ticket is set").

In a product generated from the template, an install by the orchestrator on the coordination ticket (the CTO) is
asked of the owner, with the owner's prompt as it is today (DEC-971 item 4, DEC-957, DEC-083). The coordination
ticket is the one the top-level ``coordination_ticket`` of ``governance/project/roster.yaml`` names, by id or by WBS
id, and the session's ``GOV_TICKET`` may name it either way (README, KPI success 2).
"""

from __future__ import annotations

import pytest

import w2_110_support as support
from w2_110_support import COORDINATION, ORCHESTRATOR, OTHER_ORCHESTRATION, Session, cto
from w1_04_support import command_id


def assert_asked(answer, command, who):
    assert answer.settings_rule is None, (
        f"the generated settings refuse `{command}` before the hook ({answer.settings_rule}): the case would not "
        f"reach the install rule")
    assert answer.decision == "ask", (
        f"`{command}` by {who} was {answer.decision}, not asked of the owner (DEC-957, DEC-971 item 4): "
        f"{answer.describe()}")
    expected = support.owner_prompt(command)
    assert expected in answer.reason, (
        f"the owner's prompt for `{command}` is not as before (DEC-083: the approval names that a tool-registry "
        f"record is required): expected {expected!r} in {answer.reason!r}")


@pytest.mark.parametrize("command", support.INSTALLS, ids=[command_id(c) for c in support.INSTALLS])
def test_the_cto_s_install_is_asked_of_the_owner(ask, command):
    assert_asked(ask("key-by-id", cto(), command), command, "the CTO (the orchestrator on the coordination ticket)")


CTO_FORMS = [
    ("key-by-id", COORDINATION.id),
    ("key-by-id", COORDINATION.wbs),
    ("key-by-wbs", COORDINATION.id),
    ("key-by-wbs", COORDINATION.wbs),
    ("key-only", COORDINATION.id),
    ("key-quoted-after-roles", COORDINATION.wbs),
]


@pytest.mark.parametrize("configuration,ticket", CTO_FORMS,
                         ids=[f"{c}-GOV_TICKET-{t}" for c, t in CTO_FORMS])
def test_the_key_and_the_session_s_ticket_each_name_the_ticket_by_id_or_by_wbs_id(ask, configuration, ticket):
    answer = ask(configuration, cto(ticket), support.INSTALL)
    assert_asked(answer, support.INSTALL, f"the orchestrator with GOV_TICKET={ticket} in {configuration}")


def test_an_orchestrator_subagent_in_the_cto_s_session_is_asked(ask):
    session = Session("orchestrator-subagent-in-the-cto-s-session", ORCHESTRATOR, COORDINATION.id, ORCHESTRATOR)
    assert_asked(ask("key-by-id", session), support.INSTALL, "an orchestrator subagent in the CTO's session")


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_the_cto_is_asked_in_every_permission_mode(ask, mode):
    """DEC-083's KPI: the approval prompt appears even in Auto mode; nothing of it changes."""
    assert_asked(ask("key-by-id", cto(), support.INSTALL, mode), support.INSTALL, f"the CTO in mode {mode}")


@pytest.mark.parametrize("ticket", [OTHER_ORCHESTRATION.id, OTHER_ORCHESTRATION.wbs])
def test_the_key_not_the_code_decides_which_orchestrator_is_the_cto(ask, ticket):
    """The key names another ticket: that ticket's orchestrator is the CTO (its refused counterpart, the first
    ticket's orchestrator, is in ``test_w2_110_others_refused.py``)."""
    answer = ask("key-names-another-ticket", cto(ticket), support.INSTALL)
    assert_asked(answer, support.INSTALL, f"the orchestrator on {ticket}, the ticket the key names")
