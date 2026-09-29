import sqlite3

import numpy as np
import pytest

from govbridge.semantic import vectors


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    vectors.create_table(c)
    return c


def _v(*xs):
    return np.asarray(xs, dtype="<f4")


def test_put_and_search_ranks_by_cosine(conn):
    vectors.put_vector(conn, "c1", "sha1", "pinA", 3, vectors.vec_to_bytes(_v(1, 0, 0)))
    vectors.put_vector(conn, "c2", "sha2", "pinA", 3, vectors.vec_to_bytes(_v(0, 1, 0)))
    vectors.put_vector(conn, "c3", "sha3", "pinA", 3, vectors.vec_to_bytes(_v(0.9, 0.1, 0)))
    hits = vectors.search(conn, _v(1, 0, 0), k=2, pin_id="pinA")
    assert [h[0] for h in hits] == ["c1", "c3"]
    assert hits[0][1] > hits[1][1]


def test_search_is_scoped_to_pin_id(conn):
    vectors.put_vector(conn, "c1", "sha1", "pinA", 2, vectors.vec_to_bytes(_v(1, 0)))
    vectors.put_vector(conn, "c2", "sha2", "pinB", 2, vectors.vec_to_bytes(_v(1, 0)))
    hits = vectors.search(conn, _v(1, 0), k=10, pin_id="pinA")
    assert [h[0] for h in hits] == ["c1"]


def test_digest_is_deterministic_and_order_independent(conn):
    vectors.put_vector(conn, "c2", "sha2", "pinA", 2, vectors.vec_to_bytes(_v(0, 1)))
    vectors.put_vector(conn, "c1", "sha1", "pinA", 2, vectors.vec_to_bytes(_v(1, 0)))
    d1 = vectors.digest_for_pin(conn, "pinA")

    conn2 = sqlite3.connect(":memory:")
    vectors.create_table(conn2)
    vectors.put_vector(conn2, "c1", "sha1", "pinA", 2, vectors.vec_to_bytes(_v(1, 0)))
    vectors.put_vector(conn2, "c2", "sha2", "pinA", 2, vectors.vec_to_bytes(_v(0, 1)))
    d2 = vectors.digest_for_pin(conn2, "pinA")
    assert d1 == d2


def test_digest_changes_if_a_vector_changes(conn):
    vectors.put_vector(conn, "c1", "sha1", "pinA", 2, vectors.vec_to_bytes(_v(1, 0)))
    d1 = vectors.digest_for_pin(conn, "pinA")
    vectors.put_vector(conn, "c1", "sha1", "pinA", 2, vectors.vec_to_bytes(_v(0, 1)))
    d2 = vectors.digest_for_pin(conn, "pinA")
    assert d1 != d2


def test_reuse_vector_looks_up_by_text_sha256_and_pin(conn):
    assert vectors.reuse_vector(conn, "sha1", "pinA") is None
    vb = vectors.vec_to_bytes(_v(1, 0))
    vectors.put_vector(conn, "c1", "sha1", "pinA", 2, vb)
    assert vectors.reuse_vector(conn, "sha1", "pinA") == vb
    assert vectors.reuse_vector(conn, "sha1", "pinB") is None  # scoped to the pin


def test_embed_and_store_dedupes_identical_text_without_a_second_model_call(conn, monkeypatch):
    calls = []

    def fake_embed(texts, mode="passage", dimensions=None, pin_id=None, **kw):
        calls.append(list(texts))
        return {"vectors": [[1.0, 0.0] for _ in texts], "dim": 2}

    monkeypatch.setattr("govbridge.semantic.vectors.runner.embed", fake_embed)

    class FakePin:
        dimensions = 2

    rows = [("c1", "shaX", "same text"), ("c2", "shaX", "same text"), ("c3", "shaY", "different text")]
    stats = vectors.embed_and_store(conn, rows, FakePin(), "pinA", batch_texts=10)
    assert stats["chunks_seen"] == 3
    assert stats["chunks_embedded"] == 2  # one call embeds shaX once and shaY once
    assert stats["chunks_reused"] == 1  # c2 reused c1's vector (same text_sha256, in-batch)
    # both distinct texts were embedded in ONE subprocess call (batched), not one call per chunk
    assert len(calls) == 1
    assert sorted(calls[0]) == ["different text", "same text"]
    assert vectors.count_for_pin(conn, "pinA") == 3


def test_embed_and_store_reuses_across_calls_via_existing_vector_rows(conn, monkeypatch):
    calls = []

    def fake_embed(texts, mode="passage", dimensions=None, pin_id=None, **kw):
        calls.append(list(texts))
        return {"vectors": [[1.0, 0.0] for _ in texts], "dim": 2}

    monkeypatch.setattr("govbridge.semantic.vectors.runner.embed", fake_embed)

    class FakePin:
        dimensions = 2

    vectors.embed_and_store(conn, [("c1", "shaX", "same text")], FakePin(), "pinA")
    assert len(calls) == 1
    # a second, later build (a new chunk, same underlying text) must not call the model again
    stats2 = vectors.embed_and_store(conn, [("c2", "shaX", "same text")], FakePin(), "pinA")
    assert len(calls) == 1  # no new subprocess call
    assert stats2["chunks_reused"] == 1
    assert stats2["chunks_embedded"] == 0
