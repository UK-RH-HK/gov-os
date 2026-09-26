"""BR-DAG-AMEND-R1-17 item 5 regression test.

``govbridge.code.symbols.ensure_indexed`` used to be called from EVERY query entry point
(``stats``/``definitions``/``callers``/``reads_key``, and ``govbridge.route.real_routes``'s code route, and every
external caller: ``govbridge.code.history``, ``govbridge.graph.code_bridge``, ``govbridge.graph.symbol_history``,
``govbridge.compile.codeseeds``, ``govbridge.demo.grade``) against a read-write connection (``_open_conn()``) -- so
a query against a commit the eager code-layer builder (``govbridge.code.build.code_layer_builder``, run at BUILD
time) had not already reached silently classified, parsed and persisted it on the spot, a genuine write at query
time.

Reopening (BR-DAG-AMEND-R1-17 item 5, second pass): ``ensure_indexed`` is now BUILD-ONLY -- its only legitimate
caller is ``code_layer_builder``. Every query, INCLUDING this module's own ``stats``/``definitions``/``callers``/
``reads_key``, now goes through :func:`govbridge.code.symbols.ensure_indexed_readonly` -- READ-ONLY, by
construction (``_open_conn_readonly`` -> ``store.open_db_readonly()``) -- which raises the typed
:class:`govbridge.code.symbols.StoreNeedsRebuild` for any blob the eager build never reached, rather than building
it there. There are no more separate ``*_readonly`` duplicates of ``definitions``/``callers``: those functions
themselves are the read-only ones now, converted rather than duplicated (this run's own `decisions`).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from govbridge.code import build as codebuild
from govbridge.code import symbols as codesymbols
from govbridge.core import store as corestore
from govbridge.core.view import Partition, RefSpec, ResolvedRef, ResolvedView, ViewConfig

import _repobuilder as rb


def _view(refs: list) -> ViewConfig:
    return ViewConfig(view_id="test-view", refs=refs, partitions=[Partition(name="all", owner="records",
                                                                             fallback=[], paths=["**"])], raw={})


def _resolved(view: ViewConfig, named: dict, repo=None) -> ResolvedView:
    return ResolvedView(
        view_id=view.view_id, config=view,
        named={n: ResolvedRef(name=n, commit=c, status="OK") for n, c in named.items()},
        history=[], repo=repo,
    )


def _eager_view_for(root, commit) -> ResolvedView:
    view = _view([
        RefSpec(name="records", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=None),
    ])
    return _resolved(view, {"records": commit}, repo=str(root))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ensure_indexed_readonly_matches_ensure_indexed_once_eager_built(repo, tmp_path):
    """Once the eager builder has already reached a commit's .rs blobs, the read-only path returns EXACTLY the
    same (path, blob_id) entries the lazy path would -- same content, only the connection and the write-avoidance
    differ."""
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    c1 = rb.commit(repo, "v1")

    store_root = tmp_path / "store"
    conn = corestore.open_db(root=store_root)
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    conn.close()

    conn_ro = corestore.open_db_readonly(root=store_root)
    got = codesymbols.ensure_indexed_readonly(conn_ro, c1, repo=str(repo))
    assert sorted(got) == [("runtime/src/mod_a.rs", codesymbols._rs_tree_entries(c1, repo=str(repo))[0].oid)]


def test_ensure_indexed_readonly_raises_store_needs_rebuild_when_the_code_layer_never_built(repo, tmp_path):
    """A store whose code layer was NEVER built at all (no code_blob table): the typed error, never a silent
    build, never a raw sqlite3 traceback."""
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    c1 = rb.commit(repo, "v1")

    store_root = tmp_path / "store"
    conn = corestore.open_db(root=store_root)  # core layer only -- codestore.ensure_schema() never called
    conn.close()

    conn_ro = corestore.open_db_readonly(root=store_root)
    with pytest.raises(codesymbols.StoreNeedsRebuild) as exc_info:
        codesymbols.ensure_indexed_readonly(conn_ro, c1, repo=str(repo))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "code_blob" in str(exc_info.value)


def test_ensure_indexed_readonly_raises_store_needs_rebuild_for_a_blob_the_eager_build_never_reached(repo, tmp_path):
    """The eager builder reached commit c1's blobs; a LATER commit c2 adds a new .rs file the eager build never
    saw (this repo's own "records" ref is still pinned at c1 in the resolved view passed to the builder) -- a
    read-only query at c2 must raise, never silently parse the new blob."""
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    c1 = rb.commit(repo, "v1")

    store_root = tmp_path / "store"
    conn = corestore.open_db(root=store_root)
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    conn.close()

    rb.write(repo, "runtime/src/mod_b.rs", "pub fn never_eager_indexed() {}\n")
    c2 = rb.commit(repo, "v2: a blob the eager build at c1 never reached")

    conn_ro = corestore.open_db_readonly(root=store_root)
    with pytest.raises(codesymbols.StoreNeedsRebuild) as exc_info:
        codesymbols.ensure_indexed_readonly(conn_ro, c2, repo=str(repo))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "runtime/src/mod_b.rs" in str(exc_info.value)


def test_ensure_indexed_readonly_never_writes_against_a_file_and_directory_read_only_store(repo, tmp_path):
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    c1 = rb.commit(repo, "v1")

    store_root = tmp_path / "store"
    conn = corestore.open_db(root=store_root)
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    conn.close()

    db_path = corestore.db_path(store_root)
    before_sha = _sha256_file(db_path)
    os.chmod(db_path, 0o444)
    os.chmod(store_root, 0o555)
    try:
        conn_ro = corestore.open_db_readonly(root=store_root)
        got = codesymbols.ensure_indexed_readonly(conn_ro, c1, repo=str(repo))
        assert got
    finally:
        os.chmod(store_root, 0o755)
        os.chmod(db_path, 0o644)
    assert _sha256_file(db_path) == before_sha


def test_definitions_and_callers_work_once_eager_built_and_raise_when_not(repo, tmp_path, monkeypatch):
    """``definitions``/``callers`` themselves are the read-only implementations now (no separate ``*_readonly``
    duplicate): they return real results once the eager builder has reached the commit, and raise the typed
    StoreNeedsRebuild -- never a silent lazy build -- when it has not."""
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn target_fn() {}\n")
    rb.write(repo, "runtime/src/mod_b.rs", "fn caller() {\n    target_fn();\n}\n")
    c1 = rb.commit(repo, "v1")

    store_root = tmp_path / "store"
    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_root))
    # a store that EXISTS (the core layer built) but whose code layer specifically was never built -- the real
    # failure shape StoreNeedsRebuild names; a store that does not exist AT ALL is a different, one-layer-up error
    # (open_db_readonly's own docstring), not this function's concern.
    corestore.open_db(root=store_root).close()

    with pytest.raises(codesymbols.StoreNeedsRebuild):
        codesymbols.definitions("target_fn", c1, repo=str(repo))
    with pytest.raises(codesymbols.StoreNeedsRebuild):
        codesymbols.callers("target_fn", c1, repo=str(repo))
    with pytest.raises(codesymbols.StoreNeedsRebuild):
        codesymbols.stats(c1, repo=str(repo))
    with pytest.raises(codesymbols.StoreNeedsRebuild):
        codesymbols.reads_key("no_such_key", c1, repo=str(repo))

    conn = corestore.open_db(root=store_root)
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    conn.close()

    defs = codesymbols.definitions("target_fn", c1, repo=str(repo))
    assert defs["definitions"]

    callers = codesymbols.callers("target_fn", c1, repo=str(repo))
    assert callers["callers"]

    stats = codesymbols.stats(c1, repo=str(repo))
    assert stats["rs_files"] == 2

    reads = codesymbols.reads_key("no_such_key", c1, repo=str(repo))
    assert reads["reads"] == []
