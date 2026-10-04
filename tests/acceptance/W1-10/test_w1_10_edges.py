"""KPI success 4 [CAP-09.a]: the graph stores all eight typed edges: EVIDENCE_FOR, CONSTRAINS, IMPLEMENTS, TESTS,
GENERATES, VALIDATES, SUPERSEDES, DEPENDS_ON.

The frontmatter key of an edge is its name in lower case; the edge goes from the record that carries the key to each
id listed (package DP-5 for ``evidence_for``, ``tests``, ``generates`` and ``validates``; DEC-012 names the others).
"""

from __future__ import annotations

import pytest

import w1_10_support as support


@pytest.mark.parametrize("edge_type", support.EDGE_TYPES)
def test_the_graph_stores_the_typed_edge(api, graph, edge_type):
    expected = [edge for edge in support.EXPECTED_EDGES if edge[0] == edge_type]
    assert expected, f"the fixture has no {edge_type} edge"
    assert support.record_edges(api.edges(graph.root, type=edge_type), graph.commits.values()) == expected


def test_the_edges_between_records_are_exactly_those_of_the_frontmatter(api, graph):
    """No edge is missing, none is doubled, and a key that is not an edge (``consumers``, ``decisions``) gives none."""
    edges = [edge for edge in support.triples(api.edges(graph.root)) if edge[1] not in graph.commits.values()]
    assert sorted(edges) == support.EXPECTED_EDGES
    assert len(edges) == len(set(edges)), "an edge is stored twice"


def test_every_edge_has_one_of_the_eight_types(api, graph):
    edges = support.record_edges(api.edges(graph.root), graph.commits.values())
    assert {edge_type for edge_type, _, _ in edges} == set(support.EDGE_TYPES)


def test_an_edge_type_outside_the_eight_has_no_edges(api, graph):
    assert api.edges(graph.root, type="RELATES_TO") == []
