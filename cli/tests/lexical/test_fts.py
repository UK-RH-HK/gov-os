from govbridge.core import freshness, manifest as manifestmod, store


def test_lexical_registers_itself_at_import_time():
    """The extension point core.manifest/core.freshness document: importing this package alone (nothing in core
    edited) must make both registries know about it."""
    import govbridge.lexical  # noqa: F401

    assert "lexical" in freshness.get_layer_builders()
    assert "lexical" in manifestmod.get_registered_layers()


def test_full_build_indexes_every_chunk_core_produced(built_store):
    fixture_repo, view_path, rules_path = built_store
    conn = store.open_db()
    core_chunks = conn.execute("SELECT COUNT(*) FROM chunk").fetchone()[0]
    lexical_rows = conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0]
    indexed_blobs = conn.execute("SELECT COUNT(*) FROM lexical_indexed_blob").fetchone()[0]
    assert core_chunks > 0
    assert lexical_rows == core_chunks
    distinct_blobs = conn.execute("SELECT COUNT(DISTINCT blob_id) FROM chunk").fetchone()[0]
    assert indexed_blobs == distinct_blobs


def test_two_from_clean_builds_give_identical_lexical_digest(fixture_repo, view_path, rules_path):
    import govbridge.lexical  # noqa: F401

    r1 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root), from_clean=True)
    m1 = freshness.load_previous_manifest()["manifest"]
    r2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root), from_clean=True)
    m2 = freshness.load_previous_manifest()["manifest"]

    assert r1["manifest_sha256"] == r2["manifest_sha256"]
    assert m1["layers"]["lexical"] == m2["layers"]["lexical"]
    assert m1["layers"]["lexical"]["rows"] > 0
    assert m1["layers"]["lexical"]["tokenize"] == "porter unicode61 tokenchars '_'"


def test_incremental_build_only_adds_new_blobs_chunks(built_store, fixture_repo, view_path, rules_path):
    import repobuilder

    conn = store.open_db()
    before = conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0]
    before_ids = {r[0] for r in conn.execute("SELECT chunk_id FROM lexical_fts").fetchall()}
    conn.close()

    repobuilder.write(fixture_repo.root, "docs/incremental-marker.md", "unique_incremental_marker_token here\n")
    repobuilder._commit(fixture_repo.root, "c5: incremental addition")

    r2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert r2["trigger"] == "INCREMENTAL"

    conn = store.open_db()
    after = conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0]
    after_ids = {r[0] for r in conn.execute("SELECT chunk_id FROM lexical_fts").fetchall()}
    conn.close()

    assert after == before + 1
    assert before_ids <= after_ids  # every previously-indexed chunk is still there, untouched
    assert len(after_ids - before_ids) == 1  # exactly one new chunk landed


def test_rebuild_is_idempotent_no_duplicate_rows(built_store):
    from govbridge.lexical import fts as ftsmod

    conn = store.open_db()
    before = conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0]
    stats = ftsmod.build(conn, from_clean=False)  # nothing new: every blob is already indexed
    after = conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0]
    assert stats["blobs"] == 0
    assert after == before


def test_ensure_schema_is_idempotent(tmp_path):
    from govbridge.lexical import fts as ftsmod

    conn = store.open_db(root=tmp_path / "s")
    ftsmod.ensure_schema(conn)
    ftsmod.ensure_schema(conn)  # must not raise on a second call
    assert conn.execute("SELECT COUNT(*) FROM lexical_fts").fetchone()[0] == 0
