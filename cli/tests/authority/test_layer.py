"""The persisted authority/graph layer (ARCHITECTURE.md section 8.1, orchestrator clarification on node B5):
- the digest ensures its own schema first, so a bare connection that never built this layer does not crash;
- a persisted class_lifecycle row equals a fresh, live govbridge.authority.lifecycle.classify() call (the ONE
  function used both ways, by construction);
- two from-clean builds of the fixture repo give an identical digest;
- resolver.py never touches the store (kept out of scope here; enforced by resolver.py's own import boundary and
  by the fact that resolver.resolve() takes no store/conn argument at all).
"""
import sqlite3

from govbridge.authority import layer, lifecycle, records, registry
from govbridge.core import view as viewmod


def _build_fresh(fixture_repo, view_path):
    conn = sqlite3.connect(":memory:")
    vc = viewmod.load_view(view_path)
    resolved_view = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    rules = None
    stats = layer.build(conn, resolved_view, rules, str(fixture_repo.root), from_clean=True,
                         view_path=view_path,
                         registry_path="tests/fixtures/authority/fixture-authority-registry.yaml")
    return conn, stats


def test_bare_connection_digest_never_crashes():
    conn = sqlite3.connect(":memory:")  # never built: no record_def/authority_edge/class_lifecycle tables yet
    d = layer.digest(conn)
    assert d.rows == 0
    assert d.digest == layer.digest(sqlite3.connect(":memory:")).digest  # two empty stores hash identically


def test_build_populates_all_three_tables(fixture_repo, view_path):
    conn, stats = _build_fresh(fixture_repo, view_path)
    assert stats["record_defs"] > 0
    assert stats["class_lifecycle_rows"] == stats["record_defs"]
    assert stats["edges"] >= stats["record_defs"]  # at least one DEFINES edge per definition, plus SUPERSEDES
    counts = {
        "record_def": conn.execute("SELECT COUNT(*) FROM record_def").fetchone()[0],
        "class_lifecycle": conn.execute("SELECT COUNT(*) FROM class_lifecycle").fetchone()[0],
    }
    assert counts["record_def"] == stats["record_defs"]
    assert counts["class_lifecycle"] == stats["class_lifecycle_rows"]


def test_persisted_class_lifecycle_row_equals_live_classify(fixture_repo, view_path):
    conn, _ = _build_fresh(fixture_repo, view_path)
    row = conn.execute(
        "SELECT unit, cls, lifecycle, derivation, path, commit_id, line_start, line_end FROM class_lifecycle "
        "WHERE unit = 'OA-FX-06'"
    ).fetchone()
    assert row is not None
    unit, cls, lc, derivation, path, commit_id, line_start, line_end = row

    reg = registry.load("tests/fixtures/authority/fixture-authority-registry.yaml", verify_commit="records",
                         view_path=view_path, repo=str(fixture_repo.root))
    live = lifecycle.classify(unit, reg=reg, repo=str(fixture_repo.root), view_path=view_path)
    assert (cls, lc, derivation) == (live.cls, live.lifecycle, live.derivation)
    assert (path, commit_id) == (live.path, live.commit)


def test_two_from_clean_builds_give_identical_digest(fixture_repo, view_path):
    conn1, _ = _build_fresh(fixture_repo, view_path)
    conn2, _ = _build_fresh(fixture_repo, view_path)
    d1, d2 = layer.digest(conn1), layer.digest(conn2)
    assert d1.digest == d2.digest
    assert d1.rows == d2.rows


def test_resolver_module_has_no_store_dependency():
    """W10 (outage property): the mandatory-input resolver reads Git directly, never the persisted layer -- it
    takes no sqlite3.Connection anywhere in its public API."""
    import inspect
    from govbridge.authority import resolver as resolvermod
    src = inspect.getsource(resolvermod)
    assert "sqlite3" not in src
    assert "govbridge.authority.layer" not in src and "from govbridge.authority import layer" not in src
