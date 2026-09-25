from govbridge.core import store


def test_store_root_prefers_govbridge_store_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "explicit-store"))
    assert store.store_root() == tmp_path / "explicit-store"
    assert store.store_root(view_id="whatever") == tmp_path / "explicit-store"  # env always wins


def test_store_root_default_includes_view_id(monkeypatch, tmp_path):
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    assert store.store_root(view_id="my-view") == tmp_path / "home" / "store" / "my-view"
    assert store.store_root() == tmp_path / "home" / "store" / "default"


def test_open_db_creates_schema_and_is_idempotent(tmp_path):
    root = tmp_path / "s1"
    conn = store.open_db(root=root)
    store.put_blob(conn, "b1", "sha", 10, True, "INCLUDED", "INCLUDE")
    store.put_occurrence(conn, "records", "c1", "a/b.txt", "b1", "100644")
    store.put_chunk(conn, "ch1", "b1", "v1", 1, 2, "tsha", "hello")
    conn.commit()
    conn.close()

    # re-opening must not wipe existing rows (schema uses CREATE TABLE IF NOT EXISTS)
    conn2 = store.open_db(root=root)
    counts = store.counts(conn2)
    assert counts == {"blob": 1, "occurrence": 1, "chunk": 1}
    conn2.close()


def test_clear_layer_tables_empties_everything(tmp_path):
    root = tmp_path / "s2"
    conn = store.open_db(root=root)
    store.put_blob(conn, "b1", "sha", 10, True, "INCLUDED", "INCLUDE")
    store.put_occurrence(conn, "records", "c1", "a/b.txt", "b1", "100644")
    store.put_chunk(conn, "ch1", "b1", "v1", 1, 2, "tsha", "hello")
    conn.commit()
    store.clear_layer_tables(conn)
    assert store.counts(conn) == {"blob": 0, "occurrence": 0, "chunk": 0}


def test_move_store_aside_renames_rather_than_deletes(tmp_path):
    root = tmp_path / "s3"
    root.mkdir()
    (root / "marker.txt").write_text("x")
    dest = store.move_store_aside(root=root)
    assert dest is not None
    assert not root.exists()
    assert dest.exists()
    assert (dest / "marker.txt").read_text() == "x"
    assert store.move_store_aside(root=root) is None  # nothing left to move


def test_chunks_exist_for_blob_is_scoped_to_chunker_version(tmp_path):
    root = tmp_path / "s4"
    conn = store.open_db(root=root)
    store.put_blob(conn, "b1", "sha", 10, True, "INCLUDED", "INCLUDE")
    store.put_chunk(conn, "ch1", "b1", "v1", 1, 2, "tsha", "hello")
    conn.commit()
    assert store.chunks_exist_for_blob(conn, "b1", "v1") is True
    assert store.chunks_exist_for_blob(conn, "b1", "v2") is False
    assert store.has_blob(conn, "b1") is True
    assert store.has_blob(conn, "nope") is False
