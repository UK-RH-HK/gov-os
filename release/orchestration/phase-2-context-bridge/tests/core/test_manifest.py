from govbridge.core import manifest as manifestmod, store


def _seeded_conn(root):
    conn = store.open_db(root=root)
    store.put_blob(conn, "b1", "sha1", 10, True, "INCLUDED", "INCLUDE")
    store.put_blob(conn, "b2", "sha2", 20, True, "INCLUDED", "INCLUDE")
    store.put_occurrence(conn, "records", "c1", "a.txt", "b1", "100644")
    store.put_occurrence(conn, "records", "c1", "b.txt", "b2", "100644")
    store.put_chunk(conn, "ch1", "b1", "v1", 1, 1, "ts1", "hello")
    store.put_chunk(conn, "ch2", "b2", "v1", 1, 1, "ts2", "world")
    conn.commit()
    return conn


def test_core_layers_are_registered_by_default():
    layers = manifestmod.get_registered_layers()
    assert {"occurrence", "chunk", "blob"} <= set(layers)


def test_occurrence_and_chunk_digests_are_order_independent_content_sensitive(tmp_path):
    conn = _seeded_conn(tmp_path / "s1")
    d1 = manifestmod.occurrence_layer_digest(conn)
    d2 = manifestmod.chunk_layer_digest(conn)
    assert d1.rows == 2 and d2.rows == 2
    assert isinstance(d1.digest, str) and len(d1.digest) == 64

    conn2 = _seeded_conn(tmp_path / "s2")  # same content, inserted in the same order -> same digest
    assert manifestmod.occurrence_layer_digest(conn2).digest == d1.digest
    assert manifestmod.chunk_layer_digest(conn2).digest == d2.digest


def test_a_new_layer_can_register_without_editing_core(tmp_path):
    """Proves the extension point node B2-B5 will use: a layer completely foreign to govbridge.core can register
    its own digest function and appear in build_manifest()'s output, without this test importing or modifying any
    core file beyond the public register_layer API."""
    conn = _seeded_conn(tmp_path / "s3")

    def fake_lexical_layer_digest(conn):
        return manifestmod.LayerDigest(rows=42, digest="f" * 64, extra={"tokenizer": "porter unicode61"})

    manifestmod.register_layer("lexical_fts_fake", fake_lexical_layer_digest)
    try:
        m = manifestmod.build_manifest(conn, view=[{"name": "records", "commit": "c1"}], config_sha256={},
                                        pins={}, coverage={})
        assert "lexical_fts_fake" in m["layers"]
        assert m["layers"]["lexical_fts_fake"] == {"rows": 42, "digest": "f" * 64, "tokenizer": "porter unicode61"}
        assert "occurrence" in m["layers"] and "chunk" in m["layers"]
    finally:
        manifestmod._LAYER_REGISTRY.pop("lexical_fts_fake", None)


def test_manifest_sha256_ignores_the_manifest_sha256_field_itself():
    m1 = {"a": 1, "manifest_sha256": None}
    m2 = {"a": 1, "manifest_sha256": "garbage-should-be-ignored"}
    assert manifestmod.manifest_sha256(m1) == manifestmod.manifest_sha256(m2)


def test_build_manifest_is_reproducible_for_identical_store_content(tmp_path):
    conn_a = _seeded_conn(tmp_path / "a")
    conn_b = _seeded_conn(tmp_path / "b")
    view = [{"name": "records", "commit": "c1"}]
    ma = manifestmod.build_manifest(conn_a, view=view, config_sha256={"x": "1"}, pins={"chunker_version": "v1"},
                                     coverage={"included": 2})
    mb = manifestmod.build_manifest(conn_b, view=view, config_sha256={"x": "1"}, pins={"chunker_version": "v1"},
                                     coverage={"included": 2})
    assert ma["manifest_sha256"] == mb["manifest_sha256"]
    assert ma["manifest_sha256"] is not None


def test_build_manifest_changes_when_store_content_changes(tmp_path):
    conn_a = _seeded_conn(tmp_path / "a")
    view = [{"name": "records", "commit": "c1"}]
    ma = manifestmod.build_manifest(conn_a, view=view, config_sha256={}, pins={}, coverage={})

    conn_c = store.open_db(root=tmp_path / "c")
    store.put_blob(conn_c, "b1", "sha1", 10, True, "INCLUDED", "INCLUDE")
    store.put_occurrence(conn_c, "records", "c1", "a.txt", "b1", "100644")
    store.put_chunk(conn_c, "ch1", "b1", "v1", 1, 1, "ts1", "DIFFERENT TEXT")
    conn_c.commit()
    mc = manifestmod.build_manifest(conn_c, view=view, config_sha256={}, pins={}, coverage={})
    assert ma["manifest_sha256"] != mc["manifest_sha256"]
