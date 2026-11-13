"""S1 (DEC-1165 (1), DEC-1027 H): ``gov close`` builds the ticket's context packet at the project's setting
``budgets.close_context_tokens`` in ``governance/project/facts.yaml``, not at ``gov context``'s default of 6,000; with no
setting the default applies as today.

The stand-in's ticket (its own text and its one mandatory source) comes to about 10,000 tokens: it passes the close's
context step with the setting at 65536 and is refused ``CONTEXT_FAILED`` (``context_error`` ``CONTEXT_OVER_CEILING``)
with the setting at 8000 or absent. ``gov context`` with no ``--budget`` still refuses it at 6,000 (the default is
unchanged). The close's step is called as ``gov.close.command._build_context(root, ticket)`` on a real stand-in; nothing
of ``gov.context`` is mocked.

Red today: the close ignores the setting (cases that need the setting to apply). Green today and kept green: every
refusal that is the default's.
"""

from __future__ import annotations

import pytest

import w2_183_support as s

ABSENT_FORMS = ("no key", "no budgets", "no file")


def _mandatory(api, big):
    """The big ticket's own text and mandatory inputs in tokens, as ``gov context``'s refusal names them."""
    details = s.assert_refused_over_ceiling(api.gov(big.root, s.BIG_TICKET), s.BIG_TICKET, s.DEFAULT_CEILING)
    assert 9000 <= details["mandatory_tokens"] <= 11500, f"the fixture is wrong: {details}"
    return details["mandatory_tokens"]


def test_the_close_builds_the_packet_at_the_setting_65536(api, big):
    _mandatory(api, big)
    with big.setting(s.CLOSE_VALUE):
        step = api.close_step(big.root, s.BIG_TICKET)
    packet = step.packet
    assert packet["budget"]["limit"] == s.CLOSE_VALUE, f"the packet's ceiling is not the setting: {packet['budget']}"
    assert packet[s.K_TOKENS] > s.DEFAULT_CEILING, f"the packet is not the whole ~10,000-token mandatory part: {packet[s.K_TOKENS]}"
    assert packet[s.K_TOKENS] <= s.CLOSE_VALUE
    assert packet[s.K_SUPPLEMENTARY] == [], "the stand-in holds no index, yet the packet has supplementary items"
    assert s.BIG_SOURCE_ID in s.mandatory_ids(packet) and s.CHARTER_ID in s.mandatory_ids(packet)


@pytest.mark.parametrize("facts", ABSENT_FORMS, ids=ABSENT_FORMS)
def test_with_no_setting_the_close_refuses_at_the_default(api, big, facts):
    """No key in ``budgets:``, no ``budgets:``, no facts.yaml: today's refusal, at 6,000."""
    with big.setting(facts=facts):
        step = api.close_step(big.root, s.BIG_TICKET)
    error = s.assert_close_refused(step, s.CONTEXT_FAILED, s.OVER_CEILING)
    assert error["details"].get("limit") == s.DEFAULT_CEILING, f"the ceiling is not the default: {error['details']}"
    assert s.BIG_TICKET in error["message"]


def test_a_setting_of_8000_refuses_the_ten_thousand_token_ticket(api, big):
    with big.setting(8000):
        step = api.close_step(big.root, s.BIG_TICKET)
    s.assert_close_refused(step, s.CONTEXT_FAILED, s.OVER_CEILING)


def test_the_refusal_at_8000_is_made_at_the_setting_not_at_the_default(api, big):
    """The refusal's ceiling is the setting's own 8000: a close that ignored the setting would say 6000."""
    with big.setting(8000):
        step = api.close_step(big.root, s.BIG_TICKET)
    error = s.assert_close_refused(step, s.CONTEXT_FAILED, s.OVER_CEILING)
    assert error["details"].get("limit") == 8000, f"the refusal's ceiling is not the setting: {error['details']}"


def test_the_setting_is_the_ceiling_to_the_token(api, big):
    """A setting equal to the mandatory part passes; one token fewer refuses (nothing of the mandatory part is cut)."""
    mandatory = _mandatory(api, big)
    with big.setting(mandatory):
        packet = api.close_step(big.root, s.BIG_TICKET).packet
    assert packet[s.K_TOKENS] == mandatory and packet["budget"]["limit"] == mandatory, packet["budget"]
    with big.setting(mandatory - 1):
        step = api.close_step(big.root, s.BIG_TICKET)
    error = s.assert_close_refused(step, s.CONTEXT_FAILED, s.OVER_CEILING)
    assert error["details"].get("limit") == mandatory - 1 and error["details"].get("mandatory_tokens") == mandatory, \
        error["details"]


def test_gov_context_with_no_budget_still_refuses_at_6000_whatever_the_setting(api, big):
    """The default of ``gov context`` is unchanged: facts.yaml's close setting is for the close only."""
    with big.setting(s.CLOSE_VALUE):
        answer = api.gov(big.root, s.BIG_TICKET)
    s.assert_refused_over_ceiling(answer, s.BIG_TICKET, s.DEFAULT_CEILING)


def test_gov_context_with_a_budget_of_65536_gives_the_whole_mandatory_part(api, big):
    mandatory = _mandatory(api, big)
    packet = api.gov(big.root, s.BIG_TICKET, "--budget", s.CLOSE_VALUE).packet
    assert packet[s.K_TOKENS] == mandatory and packet["budget"]["limit"] == s.CLOSE_VALUE


def test_close_budget_reads_the_setting(api, big):
    with big.setting(s.CLOSE_VALUE):
        step = api.close_budget(big.root)
    assert step.error is None, f"gov.context.close_budget does not read the setting\n{step.describe()}"
    assert step.out["value"] == s.CLOSE_VALUE, step.describe()
    with big.setting(8000):
        assert api.close_budget(big.root).out.get("value") == 8000


@pytest.mark.parametrize("facts", ABSENT_FORMS, ids=ABSENT_FORMS)
def test_close_budget_is_the_default_with_no_setting(api, big, facts):
    with big.setting(facts=facts):
        step = api.close_budget(big.root)
    assert step.error is None, f"gov.context.close_budget refuses with no setting\n{step.describe()}"
    assert step.out["value"] == s.DEFAULT_CEILING == api.constants()["default"], step.describe()


def test_with_no_setting_the_close_packet_is_what_it_was(api, small):
    """A ticket that fits the default: the close's packet with no setting is ``gov context``'s own default packet."""
    packet = api.gov(small.root, s.SMALL_TICKET).packet
    with small.setting(facts="no file"):
        closed = api.close_step(small.root, s.SMALL_TICKET).packet
    assert closed[s.K_HASH] == packet[s.K_HASH] and closed["budget"] == packet["budget"]
