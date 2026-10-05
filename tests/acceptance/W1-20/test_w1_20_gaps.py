"""KPI success 2 (DEPTH_LIMIT_REACHED lists the gaps) and KPI failure 2 (an unresolved id is omitted) [CAP-57.a].

Every test here runs with ``git`` alone on ``PATH``: the code tool is not there.

- The target of a record's edge is a record id (CAP-09.b). When no record has it, it is unresolved, and the code
  facet is not asked (package DP-4): these tests hold its gap to the reason UNRESOLVED on any machine, and the
  stopping reason to UNRESOLVED_IDS when such ids are the only gaps (DEC-396) and to DEPTH_LIMIT_REACHED when a
  gap also lies beyond the depth (DEC-393).
- An id given on the command line that is no record could still be a symbol, and the tool is not there to say:
  these tests hold that gap to its id and to "not CLOSURE_COMPLETE". Its reason with both facets answering is
  held by ``test_w1_20_code.py``, without the code facet by ``test_w1_20_facets_and_no_model.py``.
"""

from __future__ import annotations

import w1_20_support as support


def test_every_id_beyond_the_depth_is_a_gap(graph, box):
    """The start record at depth 0: each of the eight ids it names was not followed, and each is listed."""
    found = support.ask(graph, [support.HUB], box, depth=0)
    assert support.ids(found) == [support.HUB]
    assert found["stopping_reason"] == support.DEPTH_LIMIT
    assert support.gap_ids(found) == sorted(support.HUB_TARGETS.values())


def test_a_gap_beyond_the_depth_says_so(graph, box):
    """Package DP-5: a gap carries its reason, and beyond the depth it is DEPTH_LIMIT_REACHED."""
    found = support.ask(graph, [support.CHAIN[0]], box, depth=2)
    assert support.gap_reasons(found, support.CHAIN[3]) == [support.GAP_DEPTH]


def test_an_id_already_in_the_closure_is_no_gap(graph, box):
    """At depth 0 the other record of the cycle is the gap; at depth 1 the way back to the start is none."""
    assert support.gap_ids(support.ask(graph, [support.CYCLE[0]], box, depth=0)) == [support.CYCLE[1]]
    assert support.ask(graph, [support.CYCLE[0]], box, depth=1)["gaps"] == []


def test_an_edge_to_no_record_is_in_the_gap_list(graph, box):
    """Failure 2: both dangling targets are within the depth, neither is a record, and both are listed."""
    found = support.ask(graph, [support.DANGLING_START], box, depth=5)
    assert support.ids(found) == [support.DANGLING_START, support.DANGLING_NEXT]
    assert support.gap_ids(found) == [support.MISSING_NEAR, support.MISSING_FAR]
    for missing in (support.MISSING_NEAR, support.MISSING_FAR):
        assert support.gap_reasons(found, missing) == [support.GAP_UNRESOLVED]
    # Unresolved ids are the only gaps and the code facet is not asked for a record's edge: DEC-396.
    assert found["stopping_reason"] == support.UNRESOLVED_IDS


def test_a_start_id_that_names_nothing_is_in_the_gap_list(graph, box):
    """Failure 2: an id given on the command line that resolves to nothing is listed, next to what did resolve."""
    found = support.ask(graph, [support.SOLO, support.UNKNOWN], box, depth=5)
    assert support.ids(found) == [support.SOLO]
    assert support.gap_ids(found) == [support.UNKNOWN]
    assert found["stopping_reason"] != support.COMPLETE


def test_only_unresolved_start_ids_give_an_answer_with_gaps(graph, box):
    """Nothing resolves: an empty closure with the gap listed, as a result and not as an error."""
    found = support.ask(graph, [support.UNKNOWN], box, depth=1)
    assert found["closure"] == []
    assert support.gap_ids(found) == [support.UNKNOWN]
    assert found["stopping_reason"] != support.COMPLETE


def test_an_unresolved_id_is_told_from_one_beyond_the_depth(graph, box):
    """Depth 1: the dangling target one hop away was looked for and not found; the one two hops away was not reached.

    Both are in the gap list, each with its own reason (package DP-5).
    """
    found = support.ask(graph, [support.DANGLING_START], box, depth=1)
    assert support.gap_ids(found) == [support.MISSING_NEAR, support.MISSING_FAR]
    assert support.gap_reasons(found, support.MISSING_NEAR) == [support.GAP_UNRESOLVED]
    assert support.gap_reasons(found, support.MISSING_FAR) == [support.GAP_DEPTH]
    assert found["stopping_reason"] != support.COMPLETE


def test_a_depth_cut_together_with_an_unresolved_id_stops_on_the_depth(graph, box):
    """DEC-393: a gap beyond the depth decides the stopping reason before an unresolved id does.

    A closure of records, so the code facet is not asked and cannot decide it. The reason on each gap carries
    the rest: the unresolved id is still told from the one that was not reached.
    """
    found = support.ask(graph, [support.DANGLING_START], box, depth=1)
    assert found["stopping_reason"] == support.DEPTH_LIMIT
    assert {entry["id"]: entry["reason"] for entry in found["gaps"]} == \
        {support.MISSING_NEAR: support.GAP_UNRESOLVED, support.MISSING_FAR: support.GAP_DEPTH}
