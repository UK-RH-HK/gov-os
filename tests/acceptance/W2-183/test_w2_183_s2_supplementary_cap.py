"""S2 (DEC-1165 (2), DEC-860): ``gov context``'s supplementary block holds at most 6,000 tokens whatever ``--budget`` is
passed: its room is the smaller of the budget less the mandatory part, and 6,000. The close's packet is capped the same
way.

The ledger stand-in has 80 matching pages (about 24,000 tokens of supplementary evidence, indexed), a small ticket and
one mandatory source: with ``--budget 60000`` the base's supplementary block holds more than 22,000 tokens. A packet
whose budget leaves under 6,000 tokens of room gets at most that room (and, the evidence being plentiful, nearly all of
it). Stacking stops at the first item that does not fit, so a block with room for 6,000 holds at least 6,000 less one
page (about 300 tokens).

Red today: every case where the room passes 6,000 (the cap does not exist). Green today and kept green: the cases
whose room is under 6,000.
"""

from __future__ import annotations

import pytest

import w2_183_support as s

PAGE = 400   # the most one page of the ledger counts, with room to spare
BIG_BUDGETS = (60000, 20000, 12000)


def _mandatory(api, ledger):
    """The ledger ticket's own text and its mandatory input in tokens, from its default-budget packet."""
    packet = api.gov(ledger.root, s.LEDGER_TICKET).packet
    mandatory = s.mandatory_tokens(packet)
    assert 0 < mandatory < 1000, f"the fixture is wrong: {mandatory}"
    return mandatory


def test_the_stand_in_holds_far_more_evidence_than_the_cap(ledger):
    pages = [ledger.text(f"docs/ledger/page-{n:02d}.md") for n in range(s.LEDGER_PAGES)]
    assert sum(s.tokens(text) for text in pages) > 3 * s.SUPPLEMENTARY_CAP


def test_the_cap_is_6000(api):
    found = api.constants()
    assert found["cap"] == s.SUPPLEMENTARY_CAP == 6000, f"gov.context.SUPPLEMENTARY_CAP is {found['cap']!r}"
    assert found["default"] == s.DEFAULT_CEILING


@pytest.mark.parametrize("budget", BIG_BUDGETS)
def test_a_big_budget_gives_at_most_6000_tokens_of_supplementary(api, ledger, budget):
    packet = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet
    supplementary = s.supplementary_tokens(packet)
    assert supplementary <= s.SUPPLEMENTARY_CAP, (
        f"--budget {budget}: the supplementary block holds {supplementary} tokens, over the cap of "
        f"{s.SUPPLEMENTARY_CAP} ({len(packet[s.K_SUPPLEMENTARY])} items)")
    assert supplementary >= s.SUPPLEMENTARY_CAP - PAGE, \
        f"--budget {budget}: the block holds {supplementary} tokens, far under the room of {s.SUPPLEMENTARY_CAP}"
    assert packet["budget"]["limit"] == budget and packet[s.K_TOKENS] <= budget
    assert packet[s.K_TOKENS] == s.mandatory_tokens(packet) + supplementary


def test_the_block_is_the_same_whatever_budget_is_passed_past_the_cap(api, ledger):
    """Room is ``min(budget - mandatory, 6000)``: every budget with at least 6,000 of room gives one block."""
    mandatory = _mandatory(api, ledger)
    first = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", mandatory + s.SUPPLEMENTARY_CAP).packet
    assert s.supplementary_tokens(first) <= s.SUPPLEMENTARY_CAP
    for budget in (mandatory + s.SUPPLEMENTARY_CAP + 1, mandatory + 3 * s.SUPPLEMENTARY_CAP, 60000):
        packet = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet
        assert s.supplementary_ids(packet) == s.supplementary_ids(first), (
            f"--budget {budget} (room {budget - mandatory}) gives {len(packet[s.K_SUPPLEMENTARY])} items, the budget "
            f"with room 6000 gives {len(first[s.K_SUPPLEMENTARY])}")


@pytest.mark.parametrize("room", (3000, 1000, 5000))
def test_a_room_under_the_cap_gets_at_most_that_room(api, ledger, room):
    mandatory = _mandatory(api, ledger)
    packet = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", mandatory + room).packet
    supplementary = s.supplementary_tokens(packet)
    assert 0 < supplementary <= room, f"room {room}: the supplementary block holds {supplementary} tokens"
    assert supplementary >= room - PAGE, f"room {room}: the block holds {supplementary}, far under the room"
    assert packet[s.K_TOKENS] <= mandatory + room


def test_the_close_packet_at_the_setting_65536_holds_at_most_6000_supplementary(api, ledger):
    """The close's packet is capped the same way: ceiling 65536, supplementary block no more than 6,000."""
    with ledger.setting(s.CLOSE_VALUE):
        packet = api.close_step(ledger.root, s.LEDGER_TICKET).packet
    assert packet["budget"]["limit"] == s.CLOSE_VALUE, f"the close's packet is not built at the setting: {packet['budget']}"
    supplementary = s.supplementary_tokens(packet)
    assert supplementary <= s.SUPPLEMENTARY_CAP, (
        f"the close's supplementary block holds {supplementary} tokens, over the cap of {s.SUPPLEMENTARY_CAP}")
    assert supplementary >= s.SUPPLEMENTARY_CAP - PAGE, f"the close's block holds {supplementary} tokens"


def test_the_close_packet_is_gov_contexts_packet_at_the_same_budget(api, ledger):
    """The close's step adds nothing and takes nothing: its packet is the packet ``gov context --budget <setting>``
    gives (same items, same hash)."""
    with ledger.setting(s.CLOSE_VALUE):
        closed = api.close_step(ledger.root, s.LEDGER_TICKET).packet
    direct = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", s.CLOSE_VALUE).packet
    assert closed[s.K_HASH] == direct[s.K_HASH], "the close's packet is not the context's packet at the setting"
    assert s.supplementary_ids(closed) == s.supplementary_ids(direct)
    assert s.supplementary_tokens(direct) <= s.SUPPLEMENTARY_CAP
