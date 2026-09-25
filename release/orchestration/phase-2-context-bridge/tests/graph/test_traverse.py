"""Generic bounded traversal over persisted authority_edge rows (govbridge.authority.layer)."""
import sqlite3

from govbridge.authority import layer
from govbridge.core import view as viewmod
from govbridge.graph import traverse


def _build(fixture_repo, view_path):
    conn = sqlite3.connect(":memory:")
    vc = viewmod.load_view(view_path)
    resolved_view = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    layer.build(conn, resolved_view, None, str(fixture_repo.root), from_clean=True, view_path=view_path,
                registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    return conn


def test_persisted_edges_to_and_from(fixture_repo, view_path):
    conn = _build(fixture_repo, view_path)
    to_oa = traverse.persisted_edges_to(conn, "OD-FX-07")
    assert any(e.dst == "OA-FX-06" for e in to_oa)
    from_oa = traverse.persisted_edges_from(conn, "OA-FX-06")
    assert any(e.src == "OD-FX-07" for e in from_oa)


def test_neighbours_both_directions(fixture_repo, view_path):
    conn = _build(fixture_repo, view_path)
    neigh = traverse.neighbours(conn, "OA-FX-06")
    assert len(neigh) >= 1


def test_bfs_bounded_depth(fixture_repo, view_path):
    conn = _build(fixture_repo, view_path)
    visited = traverse.bfs(conn, ["OD-FX-07"], max_depth=1)
    assert "OA-FX-06" in visited
    assert "OD-FX-07" in visited


def test_no_store_returns_empty():
    assert traverse.persisted_edges_from(None, "anything") == []
    assert traverse.persisted_edges_to(None, "anything") == []
    assert traverse.neighbours(None, "anything") == []
