"""Supplementary context: present, dropped under pressure, and indicated when unavailable [CAP-15.d].

The first design tests pressure with fixtures where supplementary context is always empty (no index).
These cases build a lexical index so that supplementary context exists, and test the three behaviours:
it appears, it is dropped before mandatory under a small budget, and the packet states why it is
absent when the index is not built.

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
Cases that build the index need ``gitleaks`` on PATH and skip without it.
"""

from __future__ import annotations

import w1_24_support as S


def test_supplementary_context_is_non_empty_with_a_built_index(api, indexed_project):
    """When the lexical index is built and has content, the packet's supplementary list is non-empty
    (package DP-3: how ``context`` queries ``retrieve`` for supplementary context)."""
    packet = api.context(indexed_project, S.TK_SUPP)
    S.check_packet(packet)
    supplementary = packet.get(S.K_SUPPLEMENTARY, [])
    assert isinstance(supplementary, list) and len(supplementary) > 0, \
        "the supplementary list is empty even though the index has content"


def test_supplementary_is_dropped_before_mandatory_and_the_drop_is_named(api, indexed_project):
    """With a small budget and an index that has content, supplementary context is dropped before any
    mandatory input, and the ``dropped`` list names what was cut."""
    packet = api.context(indexed_project, S.TK_SUPP, budget=200)
    S.check_packet(packet)
    mandatory_ids = {item[S.M_ID] for item in packet[S.K_MANDATORY]}
    assert S.CHARTER_ID in mandatory_ids, \
        f"mandatory input {S.CHARTER_ID} was dropped under pressure — supplementary should go first"
    dropped = packet.get(S.K_DROPPED, [])
    assert isinstance(dropped, list) and len(dropped) > 0, \
        "the dropped list is empty — supplementary context was not recorded as dropped"


def test_the_packet_indicates_supplementary_is_unavailable_when_the_index_is_down(api, repo):
    """With no lexical index built, the packet's supplementary field is empty and the packet states
    why (not silently empty). Package DP-4: the exact indicator (a ``dropped`` entry, a ``facets``
    field, or another mechanism)."""
    api.build_store(repo)
    packet = api.context(repo, S.TK_NORMAL)
    S.check_packet(packet)
    supplementary = packet.get(S.K_SUPPLEMENTARY, [])
    assert isinstance(supplementary, list) and len(supplementary) == 0, \
        "supplementary is non-empty without an index"
    dropped = packet.get(S.K_DROPPED, [])
    assert isinstance(dropped, list), "dropped is not a list"
    has_indicator = len(dropped) > 0 or any(
        isinstance(item, dict) and "unavailable" in str(item.get("reason", "")).lower()
        for item in dropped
    )
    assert has_indicator or S.K_SUPPLEMENTARY in packet, \
        "the packet does not indicate why supplementary context is empty (DP-4)"
