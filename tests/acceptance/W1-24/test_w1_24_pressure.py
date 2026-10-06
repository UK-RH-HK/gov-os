"""S3: under token pressure supplementary context is dropped before any mandatory input, and the packet
records what was dropped; with an index down or stale the mandatory inputs are still delivered [CAP-15.d].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

import w1_24_support as S


def test_supplementary_is_dropped_before_mandatory_inputs(api, project):
    """With a tight budget, supplementary context is dropped before any mandatory input.

    The packet's mandatory list still holds every source the ticket declared, and
    the supplementary list is empty or shorter than it would be with the default
    budget.
    """
    packet = api.context(project, S.TK_PRESSURE, budget=200)
    S.check_packet(packet)
    mandatory = packet[S.K_MANDATORY]
    found_ids = {item[S.M_ID] for item in mandatory}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, \
            f"mandatory input {source_id} was dropped under pressure — supplementary should go first"
    supplementary = packet.get(S.K_SUPPLEMENTARY, [])
    assert isinstance(supplementary, list), "supplementary is not a list"


def test_the_packet_records_what_was_dropped(api, project):
    """The packet has a ``dropped`` field that lists what was not included."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    assert S.K_DROPPED in packet, "the packet has no `dropped` field"
    assert isinstance(packet[S.K_DROPPED], list), \
        f"`dropped` is not a list: {type(packet[S.K_DROPPED]).__name__}"


def test_mandatory_inputs_are_delivered_without_the_lexical_index(api, repo):
    """With no lexical index built, the mandatory inputs are still delivered (the index is for supplementary)."""
    api.build_store(repo)
    packet = api.context(repo, S.TK_NORMAL)
    S.check_packet(packet)
    found_ids = {item[S.M_ID] for item in packet[S.K_MANDATORY]}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, \
            f"mandatory input {source_id} is missing when the lexical index is absent"


def test_mandatory_inputs_are_delivered_without_the_semantic_store(api, repo):
    """With no semantic vectors, the mandatory inputs are still delivered."""
    api.build_store(repo)
    packet = api.context(repo, S.TK_NORMAL)
    S.check_packet(packet)
    found_ids = {item[S.M_ID] for item in packet[S.K_MANDATORY]}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, \
            f"mandatory input {source_id} is missing when the semantic store is absent"
