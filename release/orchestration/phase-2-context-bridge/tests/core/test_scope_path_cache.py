"""REPAIR_DAG.yaml node R1-GA1, second reopening: "query commands must never write to the store." This module
covers the four scenarios the reopening named explicitly, for the BUILD-time structures that replaced the old,
query-time ``_ensure_scope_indexes()`` (``govbridge.core.store``'s own ``occurrence_distinct_path`` table plus
``govbridge.authority.layer``'s ``record_def_by_path`` index):

(a) ``govbridge gather`` runs at full speed against a store that is genuinely read-only AT THE FILE LEVEL (a real
    ``chmod``, not only ``store.open_db_readonly()``'s own ``mode=ro`` choice), and the store file's sha256 is
    byte-identical before and after.
(b) a store that lacks a build-time structure a scoped query needs raises the typed, named
    ``STORE_NEEDS_REBUILD`` error -- never a silent slow fallback, and never a write.
(c) after a ref moves and the affected layer is rebuilt INCREMENTALLY (``govbridge.core.freshness``, the real
    incremental path -- never a from-clean rebuild), ``occurrence_distinct_path`` holds no stale ``(blob_id,
    path)`` pair: one no surviving ``occurrence`` row backs any more.
(d) two from-clean builds of the SAME source give identical ``occurrence_distinct_path`` content, not just an
    identical overall manifest (``occurrence_distinct_path`` is deliberately NOT itself a registered manifest
    layer -- see ``govbridge.core.store``'s own module-level comment -- so this is the direct proof, not an
    inference from ``occurrence``'s digest alone).

This node's own mutation_scope for this file's purpose is exactly ``tests/core/test_scope_path_cache.py`` (new),
alongside ``govbridge/authority/layer.py`` (the ``record_def_by_path`` index), ``govbridge/core/store.py`` (the
``occurrence_distinct_path`` table and ``prune_stale_distinct_paths``) and ``govbridge/core/freshness.py`` (the
three incremental prune call sites) -- never the class table, the class-table test, or the six invariant tests,
none of which this file touches or imports.

Reuses ``tests/fixtures/gather/gather_repobuilder.py`` (REPAIR_DAG.yaml node R1-GA1's own fixture: a tiny,
hermetic Git repo with one file classified CONTRACT, everything else EVIDENCE) rather than inventing a second
fixture builder -- the same one ``tests/gather/test_engine.py``'s ``built_repo`` fixture already uses for its own
real-view tests, imported the same way (``sys.path`` insertion, since it lives under ``tests/fixtures/``, not a
package). Every test sets ``GOVBRIDGE_STORE``/``GOV_BRIDGE_HOME`` explicitly (``tests/core/conftest.py``'s own
autouse ``_no_env_leak`` fixture only ever deletes the inherited value, by design -- every test in this directory
picks its own), the same convention ``tests/core/test_freshness.py`` already uses.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path

import pytest

from govbridge.core import freshness, store as storemod
from govbridge.lexical import query as lexicalquery
from govbridge.semantic import vectors as vectorsmod

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
sys.path.insert(0, str(FIXTURES_GATHER))
import gather_repobuilder as repobuilder  # noqa: E402

#: tests/gather/test_engine.py's own lexical-only facet registry: "deliberately excludes semantic so these tests
#: never spawn the embedding subprocess... and stay fast" (its own module docstring) -- reused here for exactly the
#: same reason. This sandbox's GOV_BRIDGE_HOME is isolated per test (below), so the real, locally-cached embedding
#: model is never on that path; a real semantic query would need one. ``requirement`` in this registry is still
#: scoped to CONTRACT/FROZEN_GATE_CONTRACT (same as the real config/facets.yaml), so the SQL scope push-down this
#: reopening moved off query-time writes is still fully exercised, over the lexical route.
TEST_FACETS_PATH = str(FIXTURES_GATHER / "test-facets.yaml")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _distinct_path_digest(conn) -> str:
    """A direct content digest over ``occurrence_distinct_path``, independent of the registered build-manifest
    layers (this table is deliberately not one of them -- see ``govbridge.core.store``'s own comment) -- the same
    FIELD_SEP/ROW_SEP row-hashing convention ``govbridge.core.manifest``'s own layer digests use, so this is
    directly comparable in spirit even though it is not itself a manifest layer."""
    rows = conn.execute("SELECT blob_id, path FROM occurrence_distinct_path ORDER BY blob_id, path").fetchall()
    h = hashlib.sha256()
    for blob_id, path in rows:
        h.update(f"{blob_id}\x1f{path}\x1e".encode("utf-8"))
    return h.hexdigest()


def _index_exists(conn, name: str) -> bool:
    return conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (name,)).fetchone() is not None


def _table_exists(conn, name: str) -> bool:
    return conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def _query(text: str, facets: list) -> dict:
    return {"id": "Q1", "text": text, "class": None, "subject": None, "facets": facets}


# --- (a) a genuinely (file-level) read-only store: full speed, byte-identical file -------------------------------

def test_gather_runs_full_speed_against_a_file_level_read_only_store_with_sha256_unchanged(monkeypatch, tmp_path):
    """Exercises the REAL lexical route (``govbridge.route.real_routes`` -> ``govbridge.lexical.query``) through
    ``purpose``/``requirement``, using the SAME lexical-only test registry (``TEST_FACETS_PATH``) ``tests/gather/
    test_engine.py``'s own real-view tests already use for this exact reason: no embedding subprocess, no
    locally-cached model dependency, and still a real, scoped ("requirement" -> CONTRACT/FROZEN_GATE_CONTRACT) SQL
    push-down -- exactly the mechanism this reopening moved off query-time writes. Deliberately excludes the
    ``code``-routed facets too (not in this registry at all): ``govbridge.code.symbols.ensure_indexed`` has its own,
    SEPARATE query-time-write pattern (``govbridge/code/symbols.py``, not a file this node is authorized to touch
    for this purpose) which this pass does not address -- named here rather than silently masked. The semantic
    route's own read-only wiring (``govbridge.semantic.search``/``.vectors``) is proven separately below
    (``test_open_db_readonly_reads_correctly_and_cannot_write``, plus the ``StoreNeedsRebuild`` tests), at the
    connection level rather than through a real embedding call this sandbox cannot always make."""
    from govbridge.gather import engine as enginemod
    from govbridge.route import real_routes

    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = repobuilder.build(tmp_path)
    r1 = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r1["trigger"] == "FULL"

    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    os.chmod(db_path, 0o444)
    try:
        routes = real_routes.build_real_routes(view_path=br.view_path, repo=str(br.root),
                                                registry_path=br.registry_path)
        t0 = time.monotonic()
        result = enginemod.gather(_query(repobuilder.TERM, ["purpose", "requirement"]), routes, batch_size=2,
                                   max_rounds=20, threads=1, facets_path=TEST_FACETS_PATH)
        elapsed = time.monotonic() - t0
    finally:
        os.chmod(db_path, 0o644)

    assert elapsed < 10.0, f"gather took {elapsed}s against a tiny fixture store -- looks like a slow fallback"
    assert result["stop_reason"] in enginemod.STOP_REASONS
    contract_hits = [h for h in result["merged"]
                     if h["occurrences"] and h["occurrences"][0]["path"] == repobuilder.CONTRACT_PATH]
    assert contract_hits, "the requirement facet's SQL scope push-down did not find the CONTRACT item"

    # Deliberately NOT asserting on the store directory's file listing: real_routes.build_real_routes' own
    # classification helper (govbridge.route.real_routes._conn(), feeding authoritylayer.classify_hit) still opens
    # via store.open_db() rather than store.open_db_readonly() -- a documented, deliberate choice (see that
    # function's own comment) because classify_hit's ensure_schema() call would otherwise break on any store whose
    # authority-layer schema was never separately built, which is out of this node's authorized scope to fix. A
    # plain, non-immutable WAL connection to a FILE that is read-only but whose DIRECTORY is not may legitimately
    # create -wal/-shm sibling files (SQLite's own WAL bookkeeping) without ever writing a single byte INTO
    # store.db itself -- which is the actual, literal guarantee required here and the only one this assertion checks.
    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "the store file's bytes changed across a read-only gather run"


def test_open_db_readonly_reads_correctly_and_cannot_write(monkeypatch, tmp_path):
    """The primitive every query path's read-only wiring (``govbridge.lexical.query``, ``govbridge.semantic.
    search``, and ``govbridge.route.real_routes``' own connection where it applies) is built on -- proven directly,
    once, independent of any one route: it reads real data through a genuinely (file-level ``chmod``) read-only
    store, and any attempted write against it raises structurally (``mode=ro&immutable=1``), never merely because
    every write-shaped statement elsewhere happens to be wrapped in a try/except (``store.open_db()``'s own,
    weaker, still-valid-for-BUILD-paths tolerance)."""
    _built_minimal(monkeypatch, tmp_path)
    db_path = storemod.db_path(storemod.store_root())
    before_sha = _sha256_file(db_path)
    os.chmod(db_path, 0o444)
    try:
        conn = storemod.open_db_readonly()
        count = conn.execute("SELECT COUNT(*) FROM occurrence").fetchone()[0]
        assert count > 0
        with pytest.raises(Exception):
            conn.execute("INSERT INTO occurrence_distinct_path(blob_id, path) VALUES ('x', 'y')")
        conn.close()
    finally:
        os.chmod(db_path, 0o644)
    assert _sha256_file(db_path) == before_sha


# --- (b) a missing build-time structure raises the typed, named error --------------------------------------------

def _built_minimal(monkeypatch, tmp_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = repobuilder.build(tmp_path)
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return br


def test_lexical_query_raises_store_needs_rebuild_when_the_dedup_table_is_missing(monkeypatch, tmp_path):
    br = _built_minimal(monkeypatch, tmp_path)
    conn = storemod.open_db()
    assert _table_exists(conn, "occurrence_distinct_path")
    conn.execute("DROP TABLE occurrence_distinct_path")
    conn.commit()
    conn.close()

    with pytest.raises(lexicalquery.StoreNeedsRebuild) as exc_info:
        lexicalquery.query(repobuilder.TERM, scope_classes=("CONTRACT",), view_path=br.view_path, repo=str(br.root))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "occurrence_distinct_path" in str(exc_info.value)


def test_lexical_query_raises_store_needs_rebuild_when_the_record_def_index_is_missing(monkeypatch, tmp_path):
    br = _built_minimal(monkeypatch, tmp_path)
    conn = storemod.open_db()
    assert _index_exists(conn, "record_def_by_path")
    conn.execute("DROP INDEX record_def_by_path")
    conn.commit()
    conn.close()

    with pytest.raises(lexicalquery.StoreNeedsRebuild) as exc_info:
        lexicalquery.query(repobuilder.TERM, scope_classes=("CONTRACT",), view_path=br.view_path, repo=str(br.root))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "record_def_by_path" in str(exc_info.value)


def test_lexical_query_never_writes_when_it_raises_store_needs_rebuild(monkeypatch, tmp_path):
    """The typed error is raised by a read-only lookup against ``sqlite_master`` (``_check_scope_structures``) --
    never by an attempted, failed write -- so the store file must be untouched even in the FAILURE path, not only
    the success path (a)/(a)'s own database already covers."""
    br = _built_minimal(monkeypatch, tmp_path)
    db_path = storemod.db_path(storemod.store_root())
    conn = storemod.open_db()
    conn.execute("DROP TABLE occurrence_distinct_path")
    conn.commit()
    conn.close()
    before_sha = _sha256_file(db_path)

    with pytest.raises(lexicalquery.StoreNeedsRebuild):
        lexicalquery.query(repobuilder.TERM, scope_classes=("CONTRACT",), view_path=br.view_path, repo=str(br.root))

    assert _sha256_file(db_path) == before_sha


def test_semantic_search_raises_store_needs_rebuild_when_the_dedup_table_is_missing(monkeypatch, tmp_path):
    _built_minimal(monkeypatch, tmp_path)
    conn = storemod.open_db()
    conn.execute("DROP TABLE occurrence_distinct_path")
    conn.commit()

    with pytest.raises(vectorsmod.StoreNeedsRebuild) as exc_info:
        vectorsmod.search(conn, [0.0] * 8, k=5, pin_id="any-pin", scope_classes=("CONTRACT",))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "occurrence_distinct_path" in str(exc_info.value)


def test_semantic_search_raises_store_needs_rebuild_when_the_record_def_index_is_missing(monkeypatch, tmp_path):
    _built_minimal(monkeypatch, tmp_path)
    conn = storemod.open_db()
    conn.execute("DROP INDEX record_def_by_path")
    conn.commit()

    with pytest.raises(vectorsmod.StoreNeedsRebuild) as exc_info:
        vectorsmod.search(conn, [0.0] * 8, k=5, pin_id="any-pin", scope_classes=("CONTRACT",))
    assert exc_info.value.CODE == "STORE_NEEDS_REBUILD"
    assert "record_def_by_path" in str(exc_info.value)


# --- (c) an incremental rebuild after a ref moves prunes stale (blob_id, path) pairs ------------------------------

def test_incremental_rebuild_after_a_ref_moves_leaves_no_stale_distinct_path_pair(monkeypatch, tmp_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = repobuilder.build(tmp_path)
    r1 = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r1["trigger"] == "FULL"

    conn = storemod.open_db()
    old_blob_id = conn.execute(
        "SELECT blob_id FROM occurrence WHERE path=? LIMIT 1", (repobuilder.CONTRACT_PATH,)
    ).fetchone()[0]
    assert (old_blob_id, repobuilder.CONTRACT_PATH) in set(
        conn.execute("SELECT blob_id, path FROM occurrence_distinct_path").fetchall()
    )
    conn.close()

    # Move BOTH refs the view resolves (``records``==main, ``product``) off the old commit, so the old
    # (blob_id, path) pair is genuinely orphaned -- no surviving occurrence row backs it from ANY ref. Moving only
    # one would leave the other still legitimately referencing the old blob, and pruning it then would be the
    # exact bug prune_stale_distinct_paths exists to avoid, not a case it should trigger on.
    repobuilder.write(br.root, repobuilder.CONTRACT_PATH, "# updated contract\n\nnew content, a new blob.\n")
    repobuilder._git(br.root, "add", "-A")
    repobuilder._git(br.root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "c2")
    repobuilder._git(br.root, "branch", "-f", "product", "HEAD")

    r2 = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root))
    assert r2["trigger"] != "NOOP"

    conn = storemod.open_db()
    pairs = set(conn.execute("SELECT blob_id, path FROM occurrence_distinct_path").fetchall())
    assert (old_blob_id, repobuilder.CONTRACT_PATH) not in pairs, "a stale (blob_id, path) pair survived"
    new_blob_id = conn.execute(
        "SELECT blob_id FROM occurrence WHERE path=? LIMIT 1", (repobuilder.CONTRACT_PATH,)
    ).fetchone()[0]
    assert new_blob_id != old_blob_id
    assert (new_blob_id, repobuilder.CONTRACT_PATH) in pairs
    # Every remaining pair is still backed by at least one surviving occurrence row -- prune_stale_distinct_paths
    # never removes more than the orphaned ones.
    live_pairs = set(conn.execute("SELECT blob_id, path FROM occurrence").fetchall())
    assert pairs <= live_pairs


# --- (d) two from-clean builds of the same source give identical occurrence_distinct_path content ----------------

def test_two_from_clean_builds_give_identical_distinct_path_content(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = repobuilder.build(tmp_path)

    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-A"))
    ra = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    conn_a = storemod.open_db(root=Path(tmp_path / "store-A"))
    digest_a = _distinct_path_digest(conn_a)
    assert _index_exists(conn_a, "record_def_by_path")
    record_def_rows_a = conn_a.execute("SELECT COUNT(*) FROM record_def").fetchone()[0]

    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-B"))
    rb = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    conn_b = storemod.open_db(root=Path(tmp_path / "store-B"))
    digest_b = _distinct_path_digest(conn_b)
    assert _index_exists(conn_b, "record_def_by_path")
    record_def_rows_b = conn_b.execute("SELECT COUNT(*) FROM record_def").fetchone()[0]

    assert ra["trigger"] == "FULL"
    assert rb["trigger"] == "FULL"
    assert ra["manifest_sha256"] == rb["manifest_sha256"]
    assert digest_a == digest_b
    assert record_def_rows_a == record_def_rows_b
