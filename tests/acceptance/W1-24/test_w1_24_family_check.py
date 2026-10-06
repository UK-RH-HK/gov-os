"""S6: registers the context-reproducibility family check: the same ticket and commit give the same packet
hash [CAP-38.b].

Red reason: the check declaration file does not exist yet (nothing matches
``template/governance/kernel/checks/context-reproducibility*``).
"""

from __future__ import annotations

import w1_24_support as S


def test_the_context_reproducibility_check_is_registered(family_check):
    """``gov check --list --json`` lists exactly one check whose family is ``context-reproducibility``."""
    assert family_check["family"] == S.FAMILY


def test_the_check_declaration_has_the_required_fields(family_check):
    """The check YAML has the fields the check runner needs: id, family, tier, severity, command."""
    for field in S.CHECK_FIELDS:
        assert field in family_check, f"the check declaration lacks the field {field!r}"
        assert isinstance(family_check[field], str) and family_check[field], \
            f"the field {field!r} is empty or not a string"


def test_the_same_ticket_and_commit_give_the_same_packet_hash(api, project):
    """The context-reproducibility invariant: same ticket, same commit, same packet hash (CAP-38.b).
    Tested by calling twice and comparing the hashes."""
    h1 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    h2 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    assert h1 == h2, f"same ticket, same commit, different hash: {h1} vs {h2}"
