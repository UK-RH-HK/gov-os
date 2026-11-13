"""S3 (DEC-1165 (3), CAP-15.d): the mandatory part is never shortened, and a packet whose budget leaves under 6,000
tokens of room is unchanged: the same items and the same hash as before the change.

The hashes below were recorded on the base commit d36c268c1 (the code before W2-183), with these stand-ins built from
fixed text (no clock, no randomness; the same hash in two builds in two folders), by ``gov context <ticket> --json
[--budget N]``. They guard what must not change, so they are green today and stay green. Mandatory part: a ticket whose
mandatory part passes its ceiling is still refused ``CONTEXT_OVER_CEILING``, named, and a mandatory part of any size is
served whole when the ceiling holds it.
"""

from __future__ import annotations

import pytest

import w2_183_support as s

# ---- recorded on d36c268c1 (the base of W2-183), default budget 6000
SMALL_HASH = "fb62b2a3336d535f42f74b9a6818b3066a4e93a6d3b013709155558c81f9e721"
SMALL_TOKENS = 131
LEDGER_HASH = "0a79ea578679db90bdecbb0b5b7adc94c3520cf01bf5da1fe44e907561b42b15"
LEDGER_PAGES_AT_DEFAULT = [f"docs/ledger/page-{n:02d}.md" for n in range(20)]   # 20 items, 5,620 tokens
LEDGER_SUPPLEMENTARY_TOKENS = 5620
LEDGER_MANDATORY_TOKENS = 134
# ---- recorded on d36c268c1, budgets that leave 3,000 and 6,000 tokens of room over the 134 of the mandatory part
LEDGER_AT_ROOM = {3134: ("0e0b95be578abc835e7c4f6b14c9f4fe919dda829809437064a5e6912f435cf7", 10),
                  6134: ("7ac263407c3ea7b14573e3338717ab2c1eda7d7fece4542e821a62253d287aa6", 21)}


def test_a_small_tickets_packet_at_the_default_budget_is_what_it_was(api, small):
    packet = api.gov(small.root, s.SMALL_TICKET).packet
    assert packet[s.K_HASH] == SMALL_HASH, f"the packet's hash changed: {packet[s.K_HASH]}"
    assert packet[s.K_TOKENS] == SMALL_TOKENS and packet["budget"] == {"limit": 6000, "used": SMALL_TOKENS}
    assert s.mandatory_ids(packet) == [s.CHARTER_ID] and packet[s.K_SUPPLEMENTARY] == []
    s.assert_mandatory_whole(small, packet, s.SMALL_TICKET, [s.CHARTER_REL])


def test_the_ledgers_packet_at_the_default_budget_is_what_it_was(api, ledger):
    """Room under 6,000 (the default ceiling less the mandatory part), filled with evidence: same hash, same items."""
    packet = api.gov(ledger.root, s.LEDGER_TICKET).packet
    assert packet[s.K_HASH] == LEDGER_HASH, f"the packet's hash changed: {packet[s.K_HASH]}"
    assert [path for _, path in s.supplementary_ids(packet)] == LEDGER_PAGES_AT_DEFAULT
    assert s.supplementary_tokens(packet) == LEDGER_SUPPLEMENTARY_TOKENS
    assert s.mandatory_tokens(packet) == LEDGER_MANDATORY_TOKENS and s.mandatory_ids(packet) == [s.CHARTER_ID]
    s.assert_mandatory_whole(ledger, packet, s.LEDGER_TICKET, [s.CHARTER_REL])


@pytest.mark.parametrize("budget", sorted(LEDGER_AT_ROOM))
def test_a_budget_that_leaves_6000_or_less_of_room_is_unchanged(api, ledger, budget):
    expected_hash, count = LEDGER_AT_ROOM[budget]
    packet = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet
    assert len(packet[s.K_SUPPLEMENTARY]) == count, f"--budget {budget}: {len(packet[s.K_SUPPLEMENTARY])} items"
    assert packet[s.K_HASH] == expected_hash, f"--budget {budget}: the packet's hash changed"


def test_the_close_with_no_setting_gives_the_small_packet_it_gave(api, small):
    with small.setting(facts="no file"):
        packet = api.close_step(small.root, s.SMALL_TICKET).packet
    assert packet[s.K_HASH] == SMALL_HASH


def test_the_small_packet_at_the_setting_has_the_same_mandatory_items(api, small):
    """A close at 65536 of a ticket that fits the default: the same mandatory items, the ticket's text whole."""
    before = api.gov(small.root, s.SMALL_TICKET).packet
    with small.setting(s.CLOSE_VALUE):
        packet = api.close_step(small.root, s.SMALL_TICKET).packet
    assert packet["mandatory"] == before["mandatory"] and packet["authority"] == before["authority"]
    assert packet[s.K_SUPPLEMENTARY] == before[s.K_SUPPLEMENTARY] == []
    s.assert_mandatory_whole(small, packet, s.SMALL_TICKET, [s.CHARTER_REL])


def test_a_mandatory_part_over_its_ceiling_is_still_refused_named(api, big):
    """~10,000 tokens against 6,000: ``CONTEXT_OVER_CEILING`` naming the ticket, the ceiling and the size."""
    details = s.assert_refused_over_ceiling(api.gov(big.root, s.BIG_TICKET), s.BIG_TICKET, s.DEFAULT_CEILING)
    assert details["mandatory_tokens"] > s.DEFAULT_CEILING


def test_a_mandatory_part_over_a_big_budget_is_still_refused_named(api, big):
    """The cap is of the supplementary block only: a budget under the mandatory part refuses, whatever it is."""
    mandatory = s.assert_refused_over_ceiling(api.gov(big.root, s.BIG_TICKET), s.BIG_TICKET,
                                              s.DEFAULT_CEILING)["mandatory_tokens"]
    s.assert_refused_over_ceiling(api.gov(big.root, s.BIG_TICKET, "--budget", mandatory - 1), s.BIG_TICKET,
                                  mandatory - 1)


def test_the_mandatory_part_is_served_whole_when_the_budget_holds_it(api, big):
    """Never shortened: with a budget of 65536 the ~10,000-token mandatory part (past the 6,000 cap) is whole."""
    packet = api.gov(big.root, s.BIG_TICKET, "--budget", s.CLOSE_VALUE).packet
    assert packet[s.K_TOKENS] > s.DEFAULT_CEILING and packet[s.K_SUPPLEMENTARY] == []
    assert s.mandatory_ids(packet) == [s.CHARTER_ID, s.BIG_SOURCE_ID] or \
        sorted(s.mandatory_ids(packet)) == sorted([s.CHARTER_ID, s.BIG_SOURCE_ID])
    s.assert_mandatory_whole(big, packet, s.BIG_TICKET, [s.CHARTER_REL, s.BIG_SOURCE_REL])


def test_the_mandatory_part_is_not_shortened_by_a_big_budget_with_evidence_to_spare(api, ledger):
    """With room for 24,000 tokens of evidence and a cap of 6,000 on it, the mandatory part is the same as at the
    default budget: the same items by sha256, the ticket's own text whole, the same tokens."""
    default = api.gov(ledger.root, s.LEDGER_TICKET).packet
    big = api.gov(ledger.root, s.LEDGER_TICKET, "--budget", 60000).packet
    assert big["mandatory"] == default["mandatory"] and big["authority"] == default["authority"]
    assert s.mandatory_tokens(big) == s.mandatory_tokens(default) == LEDGER_MANDATORY_TOKENS
    s.assert_mandatory_whole(ledger, big, s.LEDGER_TICKET, [s.CHARTER_REL])


def test_the_close_packet_of_the_big_ticket_is_whole_at_the_setting(api, big):
    """The close's packet at 65536 carries the ~10,000-token mandatory part whole, by sha256 (CAP-15.d)."""
    with big.setting(s.CLOSE_VALUE):
        packet = api.close_step(big.root, s.BIG_TICKET).packet
    s.assert_mandatory_whole(big, packet, s.BIG_TICKET, [s.CHARTER_REL, s.BIG_SOURCE_REL])
    direct = api.gov(big.root, s.BIG_TICKET, "--budget", s.CLOSE_VALUE).packet
    assert packet["mandatory"] == direct["mandatory"] and packet[s.K_TOKENS] == direct[s.K_TOKENS]
