"""Builder tests for the query-vector cache of the semantic route (W2-54 rounds 2 and 3; DEC-773, DEC-782).

Regression evidence only (DEC-136). The embedder and the model list are replaced by recorders, so no test needs
Ollama or ``sqlite_vec``; each project is a temporary folder.
"""
from __future__ import annotations

import hashlib
import sqlite3
import struct
import sys
import zlib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import semantic  # noqa: E402

DIGEST, OTHER = "a" * 64, "b" * 64
I = semantic.INSTRUCTION


def vector(own: str, before: str | None) -> bytes:
    """1024 float32 numbers: the text's own, and the one it follows unless that is itself or nothing."""
    drift = 0 if before in (None, own) else zlib.crc32(before.encode())
    return struct.pack("1024f", zlib.crc32(own.encode()), drift, *[0.0] * 1022)


@pytest.fixture()
def embedder(tmp_path, monkeypatch):
    """A project with a runtime folder, and an embedder whose vector for a text depends on the text embedded just
    before it, as the real one's does; ``state["revision"]`` is what the model list reports."""
    (tmp_path / ".gov-runtime").mkdir()
    state = {"revision": DIGEST, "calls": [], "options": [], "fail": False, "previous": None}

    def embed(texts, options=None):
        state["calls"].append(texts)
        state["options"].append(options)
        if state["fail"]:
            return None
        vectors = []
        for text in texts:
            vectors.append(vector(text, state["previous"]))
            state["previous"] = text
        return vectors

    monkeypatch.setattr(semantic, "_embed", embed)
    monkeypatch.setattr(semantic, "_revision", lambda: state["revision"])
    return tmp_path, state


def cache(root: Path) -> Path:
    return root / semantic.QUERY_VECTORS_REL


def test_the_question_is_sent_after_the_bare_instruction_in_one_request_and_that_vector_is_used(embedder):
    root, state = embedder
    assert semantic.query_vector(root, "who fires the bowls") == vector(I + "who fires the bowls", I)
    assert state["calls"] == [[I, I + "who fires the bowls"]]
    assert state["options"] == [{"num_gpu": 0}]


def test_a_question_s_request_asks_for_the_cpu_and_a_chunk_s_request_asks_for_nothing(monkeypatch):
    """The request bodies: the question's names ``num_gpu: 0`` (on the CPU its vector is one vector, §5.5 of the
    change record); the index's chunks are embedded with the runner as it is loaded, as before."""
    bodies = []

    def ask(path, body=None):
        bodies.append(body)
        return {"embeddings": [[0.5] * 4 for _ in body["input"]]}

    monkeypatch.setattr(semantic, "_ask", ask)
    assert semantic._embed(["a chunk"]) == [struct.pack("4f", *[0.5] * 4)]
    assert semantic._embed([I, I + "q"], semantic.QUERY_OPTIONS) is not None
    assert bodies == [{"model": semantic.MODEL, "input": ["a chunk"]},
                      {"model": semantic.MODEL, "input": [I, I + "q"], "options": {"num_gpu": 0}}]


def test_a_vector_is_computed_again_to_the_same_bytes_with_the_same_request(embedder):
    """Without the cache, the vector is the computation's: the same request each time, never one that depends on
    the cache's state (DEC-782)."""
    root, state = embedder
    first = semantic.query_vector(root, "q")
    cache(root).unlink()
    (root / ".gov-runtime").chmod(0o555)
    try:
        semantic._embed(["something else"])
        again = semantic.query_vector(root, "q")
    finally:
        (root / ".gov-runtime").chmod(0o755)
    assert again == first and not cache(root).exists()
    assert state["calls"] == [[I, I + "q"], ["something else"], [I, I + "q"]]
    assert state["options"] == [{"num_gpu": 0}, None, {"num_gpu": 0}]


@pytest.mark.parametrize("cache_state", ["cold", "warm", "deleted", "folder unwritable", "file unwritable",
                                         "no folder", "not a cache"])
def test_one_text_gets_one_vector_whatever_came_before_and_whatever_the_cache_s_state(embedder, cache_state):
    root, state = embedder
    first = semantic.query_vector(root, "q")
    semantic._embed(["something else"])
    semantic.query_vector(root, "another text")
    if cache_state == "cold":
        cache(root).unlink()
        semantic._embed(["q"])
    elif cache_state == "deleted":
        cache(root).unlink()
    elif cache_state == "folder unwritable":
        cache(root).unlink()
        (root / ".gov-runtime").chmod(0o555)
    elif cache_state == "file unwritable":
        cache(root).chmod(0o444)
    elif cache_state == "no folder":
        cache(root).unlink()
        (root / ".gov-runtime").rmdir()
    elif cache_state == "not a cache":
        cache(root).write_bytes(b"not a database")
    try:
        assert semantic.query_vector(root, "q") == first
    finally:
        if (root / ".gov-runtime").is_dir():
            (root / ".gov-runtime").chmod(0o755)
    if cache_state in ("folder unwritable", "no folder"):
        assert not cache(root).exists()


def test_a_cached_vector_is_used_without_asking_the_embedder(embedder):
    root, state = embedder
    first = semantic.query_vector(root, "q")
    semantic.query_vector(root, "another text")
    assert semantic.query_vector(root, "q") == first
    assert len(state["calls"]) == 2


def test_the_key_is_a_hash_of_the_text_and_the_text_is_kept_nowhere(embedder):
    root, _ = embedder
    semantic.query_vector(root, "who fires the bowls")
    with sqlite3.connect(cache(root)) as connection:
        rows = connection.execute("SELECT model, revision, text_sha256 FROM query_vector").fetchall()
    assert rows == [(semantic.MODEL, DIGEST, hashlib.sha256((I + "who fires the bowls").encode()).hexdigest())]
    assert b"fires" not in cache(root).read_bytes()


@pytest.mark.parametrize("other", ["Who fires the bowls", "who fires the  bowls", "who fires the bowls\n",
                                   " who fires the bowls"])
def test_the_key_is_the_exact_text(embedder, other):
    root, state = embedder
    first = semantic.query_vector(root, "who fires the bowls")
    assert semantic.query_vector(root, other) != first
    assert len(state["calls"]) == 2


def test_another_revision_is_another_key_and_the_first_comes_back_with_its_revision(embedder):
    root, state = embedder
    first = semantic.query_vector(root, "q")
    state["revision"] = OTHER
    semantic.query_vector(root, "q")
    state["revision"] = DIGEST
    assert semantic.query_vector(root, "q") == first
    assert len(state["calls"]) == 2
    with sqlite3.connect(cache(root)) as connection:
        assert connection.execute("SELECT count(*) FROM query_vector").fetchone() == (2,)


def test_a_failed_embedding_caches_nothing_and_the_next_search_asks_again(embedder):
    root, state = embedder
    state["fail"] = True
    assert semantic.query_vector(root, "q") is None
    assert not cache(root).exists()
    state["fail"] = False
    assert semantic.query_vector(root, "q") == vector(I + "q", I)
    assert len(state["calls"]) == 2


def test_without_a_revision_the_embedder_s_vector_is_used_and_nothing_is_cached(embedder):
    root, state = embedder
    state["revision"] = None
    assert semantic.query_vector(root, "q") == vector(I + "q", I)
    assert not cache(root).exists()


def test_the_cache_never_passes_its_bound_and_keeps_the_newest_entries(embedder, monkeypatch):
    root, state = embedder
    monkeypatch.setenv(semantic.CACHE_BOUND_SETTING, str(256 * 1024))
    texts = [f"question {n}" for n in range(120)]
    vectors = {}
    for text in texts:
        vectors[text] = semantic.query_vector(root, text)
        assert cache(root).stat().st_size <= 256 * 1024
        assert list((root / ".gov-runtime").iterdir()) == [cache(root)]
    asked = len(state["calls"])
    assert semantic.query_vector(root, texts[-1]) == vectors[texts[-1]] and len(state["calls"]) == asked
    for text in texts[:10]:
        assert semantic.query_vector(root, text) == vectors[text]
    assert len(state["calls"]) > asked


def test_an_entry_larger_than_the_bound_is_not_kept(embedder, monkeypatch):
    root, state = embedder
    monkeypatch.setenv(semantic.CACHE_BOUND_SETTING, "4096")
    first = semantic.query_vector(root, "q")
    assert semantic.query_vector(root, "q") == first and len(state["calls"]) == 2
    assert cache(root).stat().st_size <= 4096


def test_the_default_bound_is_used_when_the_setting_is_not_a_number(monkeypatch):
    monkeypatch.setenv(semantic.CACHE_BOUND_SETTING, "a lot")
    assert semantic._bound() == semantic.CACHE_BOUND
    monkeypatch.delenv(semantic.CACHE_BOUND_SETTING)
    assert semantic._bound() == semantic.CACHE_BOUND == 64 * 1024 * 1024


def test_a_search_without_an_index_writes_nothing(embedder):
    root, state = embedder
    answer = semantic.search(root, "q", refresh=False)
    assert answer["available"] is False and answer["hits"] == []
    assert state["calls"] == [] and list((root / ".gov-runtime").iterdir()) == []
