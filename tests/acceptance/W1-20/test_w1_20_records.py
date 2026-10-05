"""KPI success 1, the record side: referenced ids are resolved through the record graph to a depth [CAP-57.a].

Every test here runs with ``git`` alone on ``PATH``: the code tool is not there. A closure whose ids are all
records does not need it (package DP-4), so these tests run on any machine.

The fixture's components do not name each other, and each test starts from a record nothing else names, so the
tests hold whether or not a closure also follows edges backwards (package DP-2). The one test of the backward
direction says so.
"""

from __future__ import annotations

import pytest

import w1_20_support as support

CHAIN = support.CHAIN
LAST_HOP = len(CHAIN) - 1   # nine hops from the first record of the chain to the last


@pytest.mark.parametrize("depth", [0, 1, 8, LAST_HOP, 50])
def test_a_chain_is_followed_to_the_depth_and_no_further(graph, box, depth):
    """Depth N holds the records at most N hops away; the next one is the gap, and the reason says so."""
    found = support.ask(graph, [CHAIN[0]], box, depth=depth)
    assert support.ids(found) == CHAIN[:depth + 1]
    assert support.ids(found, "record") == CHAIN[:depth + 1], "a record's entry does not say kind `record`"
    if depth < LAST_HOP:
        assert found["stopping_reason"] == support.DEPTH_LIMIT
        assert support.gap_ids(found) == [CHAIN[depth + 1]]
    else:
        assert found["stopping_reason"] == support.COMPLETE
        assert found["gaps"] == []


def test_every_one_of_the_eight_typed_edges_is_followed(graph, box):
    """CAP-09.a's edges, one of each type from one record: all eight targets are one hop away."""
    found = support.ask(graph, [support.HUB], box, depth=1)
    missing = sorted(edge_type for edge_type, target in support.HUB_TARGETS.items()
                     if target not in support.ids(found))
    assert not missing, f"the closure does not follow the edges of type {missing}"
    assert support.ids(found) == sorted([support.HUB, *support.HUB_TARGETS.values()])
    assert found["stopping_reason"] == support.COMPLETE and found["gaps"] == []


def test_a_cycle_ends_and_is_complete(graph, box):
    """Two records that depend on each other: each is listed once, and the way back is no gap."""
    for depth in (1, 50):
        found = support.ask(graph, [support.CYCLE[0]], box, depth=depth)
        assert support.ids(found) == support.CYCLE
        assert found["stopping_reason"] == support.COMPLETE and found["gaps"] == []


def test_several_start_ids_give_the_closure_of_all_of_them(graph, box):
    found = support.ask(graph, [support.SOLO, support.CYCLE[0]], box, depth=1)
    assert support.ids(found) == sorted([support.SOLO, *support.CYCLE])
    assert found["stopping_reason"] == support.COMPLETE


def test_the_result_names_the_depth_it_ran_at(graph, box):
    """CAP-57's acceptance compares runs "over the same commit and depth": the depth is in the output."""
    assert support.ask(graph, [CHAIN[0]], box, depth=2)["depth"] == 2


def test_a_record_that_names_the_start_record_is_in_its_closure(graph, box):
    """Package DP-2 (both directions): what implements or validates a requirement belongs to its closure."""
    found = support.ask(graph, [support.REQUIREMENT], box, depth=1)
    assert support.ids(found) == sorted([support.REQUIREMENT, support.IMPLEMENTER, support.VALIDATOR])
    assert found["stopping_reason"] == support.COMPLETE


@pytest.mark.parametrize("radius, depth", [(0, 1), (1, 1), (2, 3), (3, 8)])
def test_the_depth_scales_with_the_impact_radius(graph, box, radius, depth):
    """Package DP-3: ``--radius`` gives the depth of DEC-035's table (R0-R1: 1, R2: 3, R3+: 8)."""
    found = support.ask(graph, [CHAIN[0]], box, radius=radius)
    assert found["depth"] == depth
    assert support.ids(found) == CHAIN[:depth + 1]
    assert found["stopping_reason"] == support.DEPTH_LIMIT and support.gap_ids(found) == [CHAIN[depth + 1]]
