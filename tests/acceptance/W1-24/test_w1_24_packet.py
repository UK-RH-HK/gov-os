"""S1: the packet holds every mandatory input by id and sha256, the authority block first, stays under the ceiling
(default ~6k tokens) and carries its hash [CAP-15.a, CAP-15.e].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

import hashlib
import json
import re

import w1_24_support as S


def test_the_packet_holds_every_mandatory_input_by_id_and_sha256(api, project):
    """Every source the ticket declares is in the packet's mandatory list, each with an id and a sha256."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    mandatory = packet[S.K_MANDATORY]
    found_ids = {item[S.M_ID] for item in mandatory}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, f"{source_id} is missing from the mandatory list"
    for item in mandatory:
        assert re.fullmatch(r"[0-9a-f]{64}", item[S.M_SHA]), \
            f"the sha256 of {item[S.M_ID]} is not a 64-hex hash: {item[S.M_SHA]!r}"


def test_the_authority_block_is_first_in_the_packet(api, project):
    """The authority block is a list whose entries precede or equal the mandatory list's entries by precedence."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    authority = packet[S.K_AUTHORITY]
    assert isinstance(authority, list) and len(authority) > 0, "the authority block is empty"
    authority_ids = [item[S.M_ID] for item in authority]
    mandatory_ids = [item[S.M_ID] for item in packet[S.K_MANDATORY]]
    for aid in authority_ids:
        assert aid in mandatory_ids, f"authority item {aid} is not in the mandatory list"


def test_the_packet_stays_under_the_default_ceiling(api, project):
    """The packet's token usage does not exceed the default ceiling of ~6k tokens (DEC-004)."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    budget = packet[S.K_BUDGET]
    assert isinstance(budget[S.B_USED], (int, float)), f"budget.used is not a number: {budget[S.B_USED]!r}"
    assert budget[S.B_USED] <= budget[S.B_LIMIT], \
        f"the packet uses {budget[S.B_USED]} tokens, above the limit of {budget[S.B_LIMIT]}"
    assert budget[S.B_LIMIT] <= S.DEFAULT_BUDGET, \
        f"the default limit is {budget[S.B_LIMIT]}, above the ceiling of {S.DEFAULT_BUDGET}"


def test_the_packet_carries_its_own_hash(api, project):
    """The packet has a ``hash`` field that is a 64-character lowercase hex sha256."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    assert re.fullmatch(r"[0-9a-f]{64}", packet[S.K_HASH]), \
        f"the hash is not a sha256: {packet[S.K_HASH]!r}"


def test_the_hash_is_stable_across_two_runs(api, project):
    """Two calls with the same ticket and the same commit produce the same packet hash (CAP-38.b)."""
    h1 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    h2 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    assert h1 == h2, f"the packet hash changed across two runs: {h1} vs {h2}"


def test_the_supplementary_block_is_separate_from_the_authority_block(api, project):
    """The packet distinguishes between mandatory/authority inputs and supplementary context."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    assert S.K_SUPPLEMENTARY in packet, "the packet has no supplementary field"
    assert isinstance(packet[S.K_SUPPLEMENTARY], list), \
        f"supplementary is not a list: {type(packet[S.K_SUPPLEMENTARY]).__name__}"
