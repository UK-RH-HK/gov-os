"""KPI success 2 [CAP-08.a, CAP-09.b]: queries return the exact ACTIVE set, the IMPLEMENTS, VALIDATES, SUPERSEDES
and DEPENDS_ON edges, and dangling references by id.
"""

from __future__ import annotations

import pytest

import w1_10_support as support


def _edges(api, graph, **filters):
    return support.record_edges(api.edges(graph.root, **filters), graph.commits.values())


def _expected(edge_type=None, source=None, target=None):
    return [edge for edge in support.EXPECTED_EDGES
            if edge_type in (None, edge[0]) and source in (None, edge[1]) and target in (None, edge[2])]


# ---- the ACTIVE set (CAP-08's acceptance line)

def test_the_active_decisions_are_exactly_those_active_and_not_superseded(api, graph):
    assert sorted(api.active(graph.root, type="decision")) == support.ACTIVE_DECISIONS


def test_a_record_another_record_supersedes_is_not_active(api, graph):
    """ADR-0003 says ACTIVE in its own frontmatter; ADR-0002 lists it under ``supersedes``."""
    assert "ADR-0003" not in api.active(graph.root, type="decision")


def test_a_record_that_names_its_own_successor_is_not_active(api, graph):
    """ADR-0007 says ACTIVE and carries ``superseded_by``; its successor does not name it."""
    assert "ADR-0007" not in api.active(graph.root, type="decision")


def test_the_active_set_without_a_type_covers_every_record_type(api, graph):
    assert sorted(api.active(graph.root)) == support.ACTIVE_ALL


def test_the_active_set_of_a_type_without_active_records_is_empty(api, graph):
    assert api.active(graph.root, type="task") == []


# ---- exact structured queries (CAP-08.a)

def test_records_by_type_and_status_are_exact(api, graph):
    """The frontmatter status alone, which differs from the ACTIVE set by the two superseded decisions."""
    assert api.ids(graph.root, type="decision", status="ACTIVE") == support.STATUS_ACTIVE_DECISIONS


def test_records_by_type_are_exact(api, graph):
    assert api.ids(graph.root, type="decision") == [f"ADR-000{number}" for number in range(1, 8)]
    assert api.ids(graph.root, type="lesson") == ["L-0001"]


def test_records_by_status_are_exact(api, graph):
    assert api.ids(graph.root, status="FINAL") == ["RR-0001", "TR-0001"]


def test_a_query_that_matches_nothing_returns_nothing(api, graph):
    assert api.records(graph.root, type="decision", status="FINAL") == []
    assert api.records(graph.root, type="no-such-type") == []


# ---- edges (CAP-09's acceptance line)

@pytest.mark.parametrize("edge_type", ["IMPLEMENTS", "VALIDATES", "SUPERSEDES", "DEPENDS_ON"])
def test_the_edges_of_a_type_are_exact(api, graph, edge_type):
    assert _edges(api, graph, type=edge_type) == _expected(edge_type)


def test_every_implements_and_validates_edge_of_a_requirement_is_returned(api, graph):
    assert _edges(api, graph, type="IMPLEMENTS", target="REQ-0001") == _expected("IMPLEMENTS", target="REQ-0001")
    assert _edges(api, graph, type="VALIDATES", target="REQ-0001") == [("VALIDATES", "TR-0001", "REQ-0001")]


def test_the_edges_of_one_source_are_exact(api, graph):
    assert _edges(api, graph, source="ADR-0002") == _expected(source="ADR-0002")


def test_a_record_without_links_has_no_edges(api, graph):
    assert _edges(api, graph, source="L-0001") == []
    assert _edges(api, graph, target="L-0001") == []


def test_a_link_named_from_both_sides_is_one_edge(api, graph):
    """ADR-0005 ``supersedes`` ADR-0004, and ADR-0004 is ``superseded_by`` ADR-0005."""
    edges = support.triples(api.edges(graph.root, type="SUPERSEDES", target="ADR-0004"))
    assert edges == [("SUPERSEDES", "ADR-0005", "ADR-0004")]


def test_superseded_by_gives_a_supersedes_edge_from_the_successor(api, graph):
    assert _edges(api, graph, type="SUPERSEDES", target="ADR-0007") == [("SUPERSEDES", "ADR-0005", "ADR-0007")]


# ---- dangling references (CAP-09.b)

def test_dangling_references_are_reported_by_id(api, graph):
    assert support.record_edges(api.dangling(graph.root), graph.commits.values()) == support.EXPECTED_DANGLING


def test_a_dangling_reference_is_still_an_edge(api, graph):
    """CAP-09's outcome: links are traversed "including broken ones"."""
    assert ("DEPENDS_ON", "ADR-0005", "ADR-0099") in _edges(api, graph, type="DEPENDS_ON")


def test_a_reference_that_resolves_is_not_dangling(api, graph):
    targets = {target for _, _, target in support.triples(api.dangling(graph.root))}
    assert not targets & set(support.RECORD_IDS)


def test_a_dangling_reference_goes_once_its_target_is_committed(api, repo):
    support.write(repo.root, "docs/adr/ADR-0099-late.md", support.record("ADR-0099", "decision", "ACTIVE", "Late"))
    support.commit(repo.root, "the missing decision", support.LATER)
    api.load(repo.root)
    assert support.record_edges(api.dangling(repo.root), support.all_commits(repo.root)) == \
        [("VALIDATES", "RR-0001", "REQ-0404")]


def test_a_trailer_that_names_no_record_is_reported_by_id(api, repo):
    """Depends on package DP-5: an unresolved ``Implements:`` id is a dangling reference."""
    support.write(repo.root, "src/app.py", "print('three')\n")
    support.commit(repo.root, "work under a decision that is not there", support.LATER,
                   trailers=[f"Task: {support.TICKET}", "Implements: ADR-0777"])
    api.load(repo.root)
    targets = {target for _, _, target in support.triples(api.dangling(repo.root))}
    assert "ADR-0777" in targets
    assert support.TICKET not in targets
