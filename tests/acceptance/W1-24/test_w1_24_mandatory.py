"""S4: mandatory inputs are resolved deterministically from the ticket's declared ids, never by retrieval rank;
each lists its authority and lifecycle state, its version or hash constraint, and the reason it is required
[CAP-15.b, CAP-01.d].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

import re

import w1_24_support as S


def test_mandatory_inputs_are_resolved_from_the_tickets_declared_ids(api, project):
    """Every id in the ticket's ``sources`` field appears in the packet's mandatory list."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    found_ids = {item[S.M_ID] for item in packet[S.K_MANDATORY]}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, \
            f"{source_id} is declared in the ticket's sources but missing from mandatory"


def test_mandatory_inputs_are_not_ranked_by_retrieval(api, project):
    """The mandatory list is ordered by precedence, not by retrieval score. The charter (highest) comes first."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    mandatory = packet[S.K_MANDATORY]
    ids = [item[S.M_ID] for item in mandatory]
    assert S.CHARTER_ID in ids, f"the charter {S.CHARTER_ID} is not in the mandatory list"
    charter_pos = ids.index(S.CHARTER_ID)
    for source_id in (S.CONTRACT_ID, S.ADR_A):
        if source_id in ids:
            other_pos = ids.index(source_id)
            assert charter_pos <= other_pos, \
                f"the charter is at position {charter_pos} but {source_id} is at {other_pos} — " \
                f"mandatory inputs should be ordered by precedence, not retrieval rank"


def test_each_mandatory_input_lists_its_authority_tier(api, project):
    """Every mandatory input carries an ``authority`` field naming its precedence tier."""
    packet = api.context(project, S.TK_NORMAL)
    for item in packet[S.K_MANDATORY]:
        assert isinstance(item.get(S.M_AUTHORITY), str) and item[S.M_AUTHORITY], \
            f"mandatory input {item.get(S.M_ID)} has no authority tier"


def test_each_mandatory_input_lists_its_lifecycle_state(api, project):
    """Every mandatory input carries a ``lifecycle`` field naming its status."""
    packet = api.context(project, S.TK_NORMAL)
    for item in packet[S.K_MANDATORY]:
        assert isinstance(item.get(S.M_LIFECYCLE), str) and item[S.M_LIFECYCLE], \
            f"mandatory input {item.get(S.M_ID)} has no lifecycle state"


def test_each_mandatory_input_lists_its_version_or_hash_constraint(api, project):
    """Every mandatory input carries a ``constraint`` field: a version, a sha256 or a marker."""
    packet = api.context(project, S.TK_NORMAL)
    for item in packet[S.K_MANDATORY]:
        assert S.M_CONSTRAINT in item, \
            f"mandatory input {item.get(S.M_ID)} has no constraint field"


def test_each_mandatory_input_lists_the_reason_it_is_required(api, project):
    """Every mandatory input carries a ``reason`` field explaining why it is required."""
    packet = api.context(project, S.TK_NORMAL)
    for item in packet[S.K_MANDATORY]:
        assert isinstance(item.get(S.M_REASON), str) and item[S.M_REASON], \
            f"mandatory input {item.get(S.M_ID)} has no reason"


def test_the_resolution_is_deterministic(api, project):
    """Two calls with the same ticket produce the same mandatory list in the same order."""
    m1 = api.context(project, S.TK_NORMAL)[S.K_MANDATORY]
    m2 = api.context(project, S.TK_NORMAL)[S.K_MANDATORY]
    ids1 = [item[S.M_ID] for item in m1]
    ids2 = [item[S.M_ID] for item in m2]
    assert ids1 == ids2, f"the mandatory order is not deterministic: {ids1} vs {ids2}"
    shas1 = [item[S.M_SHA] for item in m1]
    shas2 = [item[S.M_SHA] for item in m2]
    assert shas1 == shas2, "the sha256 values changed across two runs"
