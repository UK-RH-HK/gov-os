"""KPI 1, the record graph: a decision change raises a CIT-P that lists the affected specifications, decisions,
tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].

These cases run with ``git`` alone on PATH: the code tool is not there, so the code graph cannot be read. They hold
the record side; ``test_w2_37_code_graph.py`` holds the code side, and ``test_w2_37_incomplete.py`` what the report
says about the code graph here.
"""

from __future__ import annotations

import pytest

import w2_37_support as support

ONE_HOP = [
    (support.SPEC, "specifications"),
    (support.CAP, "specifications"),
    (support.OTHER_DECISION, "decisions"),
    (support.TICKET, "tickets"),
    (support.TEST_RECORD, "tests"),
]


@pytest.mark.parametrize("record_id,kind", ONE_HOP, ids=[f"{i}-{k}" for i, k in ONE_HOP])
def test_a_decision_change_lists_each_linked_record_once_under_its_kind_from_the_record_graph(asked, record_id,
                                                                                              kind):
    """Edges both ways: DEC-001 constrains SPEC-001; CAP-901 and DEC-002 depend on it; PROJ-ab01 implements it;
    TR-0001 tests it."""
    found = asked(support.CHANGED)
    assert support.where(found, record_id) == [(kind, "record")], \
        f"{record_id} is not listed once under `{kind}` from the record graph: {support.where(found, record_id)}"


def test_the_change_is_named_as_the_stated_change(asked):
    found = asked(support.CHANGED)
    assert [entry["id"] for entry in found["change"]] == [support.CHANGED], f"`change`: {found['change']}"
    assert found["change"][0].get("graph") == "record", f"`change`: {found['change']}"


def test_a_decision_that_is_an_entry_of_the_register_is_a_stated_change(asked):
    """Decisions are register entries (W2-03): the ticket that implements DEC-070 is affected."""
    found = asked(support.ENTRY_DECISION)
    assert support.where(found, support.ENTRY_TICKET) == [("tickets", "record")], \
        f"the ticket of the register entry: {support.where(found, support.ENTRY_TICKET)}"


def test_nothing_the_graphs_do_not_link_is_listed(asked):
    found = asked(support.CHANGED)
    listed = set(support.ids_of(found))
    stray = sorted(listed & set(support.UNRELATED + (support.WIDE, support.SOLO, support.NAMING, support.PROSE)))
    assert not stray, f"records no edge links to {support.CHANGED} are listed: {stray}"


def test_no_list_is_cut_short(asked):
    """Thirty specifications and thirty tickets link DEC-003: every one is listed."""
    found = asked(support.WIDE)
    missing_specs = sorted(set(support.WIDE_SPECS) - set(support.ids_of(found, "specifications")))
    missing_tickets = sorted(set(support.WIDE_TICKETS) - set(support.ids_of(found, "tickets")))
    assert not missing_specs and not missing_tickets, \
        f"dropped: specifications {missing_specs}, tickets {missing_tickets}"


def test_two_changes_together_list_what_each_lists(asked):
    both = asked([support.CHANGED, support.WIDE])
    for alone in (asked(support.CHANGED), asked(support.WIDE)):
        dropped = sorted(set(support.ids_of(alone)) - set(support.ids_of(both)))
        assert not dropped, f"asked together, the changes drop {dropped}"


def test_the_radius_gives_the_depth_gov_closure_gives_for_it(asked, graph, box):
    """The CIT-P carries a radius (R0 to R3, DEC-035) and the depth it implies, as ``gov closure --radius`` maps it
    (DEC-391)."""
    found = asked(support.CHANGED)
    number = int(found["radius"].lstrip("R").rstrip("+"))
    by_closure = support.closure(graph, [support.CHANGED], box, radius=number)
    assert found["depth"] == by_closure["depth"], \
        f"radius {found['radius']} gives depth {found['depth']}; gov closure --radius {number} gives " \
        f"{by_closure['depth']}"


def test_the_list_holds_every_record_gov_closure_reaches_at_that_depth(asked, graph, box):
    """No record that the record graph links within the depth is dropped."""
    found = asked(support.CHANGED)
    reached = support.closure(graph, [support.CHANGED], box, depth=found["depth"])
    records = sorted(entry["id"] for entry in reached["closure"]
                     if entry["kind"] == "record" and entry["id"] != support.CHANGED)
    dropped = sorted(set(records) - set(support.ids_of(found)))
    assert not dropped, f"gov closure reaches {dropped} at depth {found['depth']}; gov impact does not list them"


def test_an_item_beyond_the_depth_is_a_gap_and_the_report_is_not_complete(asked):
    """SPEC-002 is two hops from DEC-001: listed when the depth reaches it, else named as a gap."""
    found = asked(support.CHANGED)
    if found["depth"] >= 2:
        assert support.where(found, support.FAR_SPEC) == [("specifications", "record")], \
            f"depth {found['depth']} reaches {support.FAR_SPEC}, which is not listed"
    else:
        assert support.in_gaps(found, support.FAR_SPEC) and found["complete"] is False, \
            f"depth {found['depth']} does not reach {support.FAR_SPEC}, and it is not named as a gap"


def test_the_assessment_is_a_change_impact_proposal(asked):
    """The result carries the CIT-P's frontmatter: the shared frontmatter and type change-impact-proposal."""
    found = asked(support.CHANGED)
    proposal = found.get("proposal")
    assert isinstance(proposal, dict), f"the result carries no `proposal`: {sorted(found)}"
    support.check_frontmatter(proposal, support.CITP_TYPE)


def test_the_same_change_gives_the_same_assessment(graph, box):
    first = support.ask(graph, support.CHANGED, box)
    second = support.ask(graph, support.CHANGED, box)
    assert first == second, "two runs over the same commit give different assessments"


def test_out_writes_the_proposal_as_a_cit_p_record(repo, box):
    """``--out`` writes the CIT-P as a record file: frontmatter valid for change-impact-proposal, with the change,
    the radius, the depth and the five lists the result gives (reading R3)."""
    out = repo / "docs" / "changes" / "CITP-900.md"
    found = support.assessment(support.impact(repo, support.CHANGED, box, out=out))
    front, _ = support.read_frontmatter(out)
    support.check_frontmatter(front, support.CITP_TYPE)
    assert front.get("change") == [support.CHANGED], f"the CIT-P's `change`: {front.get('change')!r}"
    assert front.get("radius") == found["radius"] and front.get("depth") == found["depth"], \
        f"the CIT-P's radius and depth {front.get('radius')!r}, {front.get('depth')!r} are not the result's"
    affected = front.get("affected")
    assert isinstance(affected, dict) and sorted(affected) == sorted(support.KINDS), \
        f"the CIT-P's `affected` is not grouped by the five kinds: {affected!r}"
    for kind in support.KINDS:
        assert sorted(affected[kind] or []) == support.ids_of(found, kind), \
            f"the CIT-P's `affected.{kind}` is not the result's: {affected[kind]!r}"
