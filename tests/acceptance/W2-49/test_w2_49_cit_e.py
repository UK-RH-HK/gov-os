"""KPI success line 4: the CIT-E (``docs/changes/W2-49-CIT-E.md``).

"The CIT-E record matches the CIT-P, or lists the differences" (CAP-33's
acceptance: after apply, the CIT-E record matches the proposal or lists the
differences).  Each change the CIT-P names is either confirmed as made or
listed as a difference, and every covers item Contract v4.2 actually changed
is recorded.
"""

from __future__ import annotations

import pytest

from w2_49_support import (
    CIT_E,
    CIT_P,
    MOVED_ITEMS,
    base_yaml_model,
    covers_ids,
    current_model,
    gate,
    has,
    read_doc,
    require_v42,
    together,
)


def test_cit_e_names_its_proposal_and_source():
    """The CIT-E is the execution record of W2-49's CIT-P, under DEC-722."""
    cit_e = read_doc(CIT_E)
    assert has(r"W2-49-CIT-P", cit_e), "the CIT-E does not name its proposal, W2-49-CIT-P"
    assert has(r"DEC-722", cit_e), "the CIT-E does not cite DEC-722"


@pytest.mark.parametrize(
    "change, pattern",
    [
        ("CAP-44.h (the lite verdict)", r"CAP-44\.h"),
        ("the A7 gate of CAP-44.f", gate("A7")),
        ("the A10 gate of CAP-44.f", gate("A10")),
        ("CAP-43.b (the lite manifest and file hashes)", r"CAP-43\.b"),
        ("the Contract's version 4.2", r"(?<![\d.])4\.2(?![\d])"),
    ],
    ids=["CAP-44.h", "A7", "A10", "CAP-43.b", "v4.2"],
)
def test_cit_e_records_each_change_the_cit_p_names(change, pattern):
    """Each change of the CIT-P is confirmed as made, or listed as a difference."""
    cit_e = read_doc(CIT_E)
    assert has(pattern, cit_e), f"the CIT-E neither confirms nor lists as a difference: {change}"


def test_cit_e_states_its_differences_from_the_cit_p():
    """The CIT-E says what differs from the proposal, or that nothing does."""
    cit_e = read_doc(CIT_E)
    assert together(cit_e, r"differen", r"CIT-P|proposal"), (
        "the CIT-E has no statement of its differences from the CIT-P (or that there are none)"
    )


def test_cit_e_records_every_covers_item_the_contract_changed():
    """Every covers item whose wave or wording changed in v4.2, or that v4.2 added, is in the CIT-E."""
    cit_e = read_doc(CIT_E)
    now = current_model("yaml")
    require_v42(now)
    before = {c.id: c.raw for c in base_yaml_model().covers}
    changed = {c.id for c in now.covers if before.get(c.id) != c.raw}
    assert changed, "Contract v4.2 changed no covers item"
    missing = sorted(i for i in changed if not has(rf"{i.replace('.', r'[.]')}(?![\w])", cit_e))
    assert not missing, f"covers items changed in v4.2 but not recorded in the CIT-E: {missing}"


def test_cit_e_records_every_moved_item_the_cit_p_names():
    """The CIT-P's items among CAP-44.f, CAP-44.h and CAP-43.b each appear in the CIT-E."""
    cit_e = read_doc(CIT_E)
    named = covers_ids(read_doc(CIT_P)) & set(MOVED_ITEMS)
    assert named, "the CIT-P names none of CAP-44.f, CAP-44.h and CAP-43.b"
    missing = sorted(named - covers_ids(cit_e))
    assert not missing, f"items the CIT-P names but the CIT-E neither confirms nor lists: {missing}"


def test_cit_e_records_the_owner_approval_before_the_change():
    """CAP-33: the Contract changes only after independent review and the owner's approval of the CIT-P."""
    cit_e = read_doc(CIT_E)
    assert has(r"CAP-33", cit_e), "the CIT-E does not cite CAP-33"
    assert together(cit_e, r"owner", r"approv|accept"), "the CIT-E does not record the owner's approval"
