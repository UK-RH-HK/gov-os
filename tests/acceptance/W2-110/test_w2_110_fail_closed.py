"""KPI success 2 (fail closed) and failure 3 ("A missing or unreadable coordination-ticket key read as 'ask
everyone'").

The coordination ticket is named in the project's own configuration, one key set at adoption: the top-level
``coordination_ticket`` of ``governance/project/roster.yaml`` (DEC-971 item 4). With no roster, no such key, an
empty or non-text value, a roster that cannot be read or parsed, or a key that names no ticket of the project, every
session's install is refused, the CTO's included, and the refusal says how to set it: it names the file and the key.
Never an ``ask`` and never a pass-through.
"""

from __future__ import annotations

import pytest

import w2_110_support as support
from w2_110_support import (AUDITOR, COORDINATION, ENGINEER, ENGINEERING, MISSING_TICKET_ID, MISSING_WBS_ID,
                            ORCHESTRATOR, PRODUCT_SPEC, RESEARCH, TEST_DESIGNER, TICKET_LEAD, OWN_TICKET, Session,
                            cto)
from w1_04_support import command_id


def assert_fail_closed(answer, command, who, configuration):
    assert answer.decision == "deny", (
        f"with the configuration {configuration}, `{command}` by {who} was {answer.decision}: a coordination-ticket "
        f"key that cannot be read refuses every session's install, the CTO's included (DEC-971 item 4): "
        f"{answer.describe()}")
    assert support.says_how_to_set_the_key(answer.reason), (
        f"with the configuration {configuration}, the refusal of `{command}` by {who} does not say how to set the "
        f"coordination ticket: it must name {support.ROSTER_REL} and the key {support.KEY}: {answer.reason!r}")


@pytest.mark.parametrize("configuration", list(support.FAIL_CLOSED))
def test_the_cto_s_install_is_refused_when_the_key_cannot_be_read(ask, configuration):
    """The orchestrator on the ticket every working configuration names (``DAEO-c0rd``)."""
    assert_fail_closed(ask(configuration, cto()), support.INSTALL, "the orchestrator on DAEO-c0rd", configuration)


# The orchestrator whose GOV_TICKET is what the key holds, word for word: a key that names no ticket is not matched
# by the same words, and an empty or missing key by an empty or missing ticket.
SAME_WORDS = [
    ("names-no-ticket-by-id", MISSING_TICKET_ID),
    ("names-no-ticket-by-wbs", MISSING_WBS_ID),
    ("empty-value", ""),
    ("blank-value", "   "),
    ("number-value", "7"),
    ("null-value", None),
    ("no-key", None),
    ("no-roster", None),
    ("as-generated", None),
]


@pytest.mark.parametrize("configuration,ticket", SAME_WORDS,
                         ids=[f"{c}-GOV_TICKET-{'unset' if t is None else repr(t)}" for c, t in SAME_WORDS])
def test_an_orchestrator_whose_ticket_is_what_the_key_holds_is_refused(ask, configuration, ticket):
    answer = ask(configuration, cto(ticket))
    assert_fail_closed(answer, support.INSTALL, f"the orchestrator with GOV_TICKET={ticket!r}", configuration)


EVERY_SESSION = [
    cto(COORDINATION.wbs, "cto-by-wbs-id"),
    Session("cto-orchestrator-subagent", ORCHESTRATOR, COORDINATION.id, ORCHESTRATOR),
    Session("lead-on-an-engineer-s-ticket", ORCHESTRATOR, ENGINEERING.id),
    Session("orchestrator-without-a-ticket", ORCHESTRATOR, None),
    *[Session(f"{role}-on-its-own-ticket", role, OWN_TICKET[role].id)
      for role in (ENGINEER, TEST_DESIGNER, PRODUCT_SPEC, AUDITOR, RESEARCH, TICKET_LEAD)],
    Session("no-role-on-the-coordination-ticket", None, COORDINATION.id),
    Session("orchestrator-subagent-in-an-engineer-s-session", ENGINEER, ENGINEERING.id, ORCHESTRATOR),
]


@pytest.mark.parametrize("configuration", ["no-roster", "unparsable"])
@pytest.mark.parametrize("session", EVERY_SESSION, ids=str)
def test_every_session_s_install_is_refused_and_told_how_to_set_the_key(ask, configuration, session):
    assert_fail_closed(ask(configuration, session), support.INSTALL, session.name, configuration)


@pytest.mark.parametrize("command", support.INSTALLS, ids=[command_id(c) for c in support.INSTALLS])
def test_without_a_roster_every_install_of_the_cto_is_refused(ask, command):
    assert_fail_closed(ask("no-roster", cto(), command), command, "the orchestrator on DAEO-c0rd", "no-roster")


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_without_a_roster_the_cto_is_refused_in_every_permission_mode(ask, mode):
    """Never an ``ask``, whatever the mode: the prompt the owner would see in Auto mode is not raised either."""
    assert_fail_closed(ask("no-roster", cto(), support.INSTALL, mode), support.INSTALL,
                       f"the orchestrator on DAEO-c0rd in mode {mode}", "no-roster")


def test_the_product_as_generated_names_no_coordination_ticket(generated):
    """The template ships no key that names a ticket: the coordination ticket is the project's, set at adoption."""
    import yaml

    path = generated / support.ROSTER_REL
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        value = data.get(support.KEY) if isinstance(data, dict) else None
        assert not (isinstance(value, str) and value.strip()), (
            f"the template's {support.ROSTER_REL} sets {support.KEY} to {value!r}: a product's coordination ticket "
            f"would be written in the template, not set at adoption")
