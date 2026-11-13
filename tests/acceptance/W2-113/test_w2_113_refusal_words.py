"""KPI success 2: when the rule cannot run (no key, or a key naming no ticket) the refusal names ``GOV_TICKET``, says
how to set the key, in words that are true in that case, and stays a refusal (W2-110's review F5).

Planted products are W2-110's generator's (adoption is not needed): (a) a roster without the key, (b) no roster file
(and the product as generated), (c) a key naming no ticket in ``.tickets/``. In each, the orchestrator (the would-be
CTO) and another role (an engineer) attempt an install.

The predicates (``w2_113_support``): *names GOV_TICKET*: the text holds ``GOV_TICKET``. *Says how to set the key*:
W2-110's: the text names ``governance/project/roster.yaml`` and ``coordination_ticket``. *Claims a key was set*:
``claims_a_key_was_set``, narrow (README, "Success 2: the words").
"""

from __future__ import annotations

import pytest

import w2_113_support as support
from w2_113_support import w110

# configuration (W2-110's names), the case it stands for, whether a key exists in it
CONFIGURATIONS = [
    ("no-key", "a-roster-without-the-key", False),
    ("no-roster", "b-no-roster-file", False),
    ("as-generated", "b-the-product-as-generated", False),
    ("names-no-ticket-by-id", "c-key-names-no-ticket-id", True),
    ("names-no-ticket-by-wbs", "c-key-names-no-ticket-wbs", True),
]
SESSIONS = [w110.cto(w110.COORDINATION.id, "orchestrator"),
            w110.Session("engineer", w110.ENGINEER, w110.ENGINEERING.id)]
PARAMS = [pytest.param(name, case, exists, id=case) for name, case, exists in CONFIGURATIONS]


@pytest.mark.parametrize("session", SESSIONS, ids=str)
@pytest.mark.parametrize("configuration,case,key_exists", PARAMS)
def test_the_install_stays_refused_when_the_rule_cannot_run(ask, configuration, case, key_exists, session):
    answer = ask(configuration, session)
    assert answer.decision == "deny", (
        f"{session}'s install in {case} must stay refused (fail closed), never asked or let through: {answer.describe()}")


@pytest.mark.parametrize("session", SESSIONS, ids=str)
@pytest.mark.parametrize("configuration,case,key_exists", PARAMS)
def test_the_refusal_names_gov_ticket(ask, configuration, case, key_exists, session):
    answer = ask(configuration, session)
    assert answer.decision == "deny", f"{session}'s install in {case} was {answer.decision}: {answer.describe()}"
    assert support.names_the_variable(answer.reason), (
        f"the refusal of {session}'s install in {case} must name {support.NAMES_THE_VARIABLE} (the variable that "
        f"names the CTO's ticket): {answer.reason!r}")


@pytest.mark.parametrize("session", SESSIONS, ids=str)
@pytest.mark.parametrize("configuration,case,key_exists", PARAMS)
def test_the_refusal_says_how_to_set_the_key(ask, configuration, case, key_exists, session):
    answer = ask(configuration, session)
    assert answer.decision == "deny", f"{session}'s install in {case} was {answer.decision}: {answer.describe()}"
    assert support.says_how_to_set_the_key(answer.reason), (
        f"the refusal of {session}'s install in {case} must say how to set the key: name "
        f"{support.ROSTER_REL} and {support.KEY}: {answer.reason!r}")


@pytest.mark.parametrize("session", SESSIONS, ids=str)
@pytest.mark.parametrize("configuration,case,key_exists", PARAMS)
def test_the_refusal_does_not_claim_a_key_was_set(ask, configuration, case, key_exists, session):
    answer = ask(configuration, session)
    assert answer.decision == "deny", f"{session}'s install in {case} was {answer.decision}: {answer.describe()}"
    claims = support.claims_a_key_was_set(answer.reason, key_exists)
    assert not claims, (
        f"in {case} the key cannot do its work (a key is present: {key_exists}), and nothing set it at adoption, but "
        f"the refusal of {session}'s install claims {claims}: {answer.reason!r}")
