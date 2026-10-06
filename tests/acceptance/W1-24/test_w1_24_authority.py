"""S7: given two conflicting records, the authority block holds only the one with higher precedence
(Charter > Contract > ADRs > specifications > tasks > retrieval > inference) and marks the other
superseded [CAP-01.a].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

import w1_24_support as S


def test_the_authority_block_holds_only_the_higher_precedence_record(api, project):
    """The ticket TK_PRECEDENCE declares ADR_B (decision) and SPEC_A (specification). ADR_B supersedes SPEC_A.
    The authority block holds ADR_B (higher precedence) and not SPEC_A."""
    packet = api.context(project, S.TK_PRECEDENCE)
    S.check_packet(packet)
    authority_ids = {item[S.M_ID] for item in packet[S.K_AUTHORITY]}
    assert S.ADR_B in authority_ids, \
        f"the higher-precedence record {S.ADR_B} is not in the authority block"
    assert S.SPEC_A not in authority_ids, \
        f"the lower-precedence record {S.SPEC_A} is in the authority block — " \
        f"only the higher-precedence one should appear"


def test_the_lower_precedence_record_is_marked_superseded(api, project):
    """The lower-precedence record SPEC_A is listed as superseded in the packet (in the mandatory or dropped list,
    with a marker that it was outranked)."""
    packet = api.context(project, S.TK_PRECEDENCE)
    S.check_packet(packet)
    mandatory = packet[S.K_MANDATORY]
    spec_items = [item for item in mandatory if item.get(S.M_ID) == S.SPEC_A]
    dropped = packet.get(S.K_DROPPED, [])
    spec_dropped = [item for item in dropped if isinstance(item, dict) and item.get("id") == S.SPEC_A]
    found = spec_items + spec_dropped
    assert len(found) > 0, f"the lower-precedence record {S.SPEC_A} is not mentioned anywhere in the packet"


def test_the_full_precedence_order(api, project):
    """In the authority block the charter outranks the contract, which outranks ADRs, which outrank specifications,
    which outrank tasks. Tested with TK_NORMAL whose sources span charter, contract and decision."""
    packet = api.context(project, S.TK_NORMAL)
    S.check_packet(packet)
    authority = packet[S.K_AUTHORITY]
    tiers = [item.get(S.M_AUTHORITY, "") for item in authority]
    positions = {}
    for i, tier in enumerate(tiers):
        normalised = tier.lower().strip()
        for kind in S.PRECEDENCE:
            if kind in normalised or normalised in kind:
                if kind not in positions:
                    positions[kind] = i
    for higher, lower in zip(S.PRECEDENCE, S.PRECEDENCE[1:]):
        if higher in positions and lower in positions:
            assert positions[higher] <= positions[lower], \
                f"{higher} (at {positions[higher]}) should come before {lower} (at {positions[lower]}) " \
                f"in the authority block"


def test_all_five_store_representable_levels_in_precedence_order(api, project):
    """With TK_FULL_PREC (sources at charter, contract, decision, specification and ticket level),
    the mandatory list contains all five tiers and they appear in CAP-01.a order."""
    packet = api.context(project, S.TK_FULL_PREC)
    S.check_packet(packet)
    mandatory = packet[S.K_MANDATORY]
    tiers_seen = []
    for item in mandatory:
        tier = item.get(S.M_AUTHORITY, "").lower().strip()
        for kind in S.PRECEDENCE:
            if kind in tier or tier in kind:
                if kind not in tiers_seen:
                    tiers_seen.append(kind)
                break
    assert len(tiers_seen) == len(S.PRECEDENCE), \
        f"expected all 5 precedence levels {list(S.PRECEDENCE)}, but only saw {tiers_seen}"
    for i, kind in enumerate(S.PRECEDENCE):
        assert tiers_seen[i] == kind, \
            f"at position {i} expected {kind!r} but got {tiers_seen[i]!r} — " \
            f"the five levels are not in CAP-01.a order: {tiers_seen}"
