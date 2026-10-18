"""Builder tests for the stored query vectors of the semantic route (W2-54 round 2; DEC-773).

Regression evidence only (DEC-136). The embedder and the model list are replaced by recorders, so no test needs
Ollama or ``sqlite_vec``; each project is a temporary folder.
"""
from __future__ import annotations

import sqlite3
import struct
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import semantic  # noqa: E402

DIGEST, OTHER = "a" * 64, "b" * 64


@pytest.fixture()
def embedder(tmp_path, monkeypatch):
    """A project with a runtime folder, and an embedder whose every call gives a new vector, as the real one does
    after a different text; ``state["revision"]`` is what the model list reports."""
    (tmp_path / ".gov-runtime").mkdir()
    state = {"revision": DIGEST, "calls": [], "fail": False}

    def embed(texts):
        state["calls"].append(texts)
        return None if state["fail"] else [struct.pack("2f", len(state["calls"]), 0.5) for _ in texts]

    monkeypatch.setattr(semantic, "_embed", embed)
    monkeypatch.setattr(semantic, "_revision", lambda: state["revision"])
    return tmp_path, state


def test_one_text_gets_one_vector_and_the_first_is_the_embedder_s(embedder):
    root, state = embedder
    first = semantic._query_vector(root, "who fires the bowls")
    assert first == struct.pack("2f", 1, 0.5)
    semantic._query_vector(root, "another text")
    assert semantic._query_vector(root, "who fires the bowls") == first
    assert state["calls"] == [["who fires the bowls"], ["another text"]]
    assert (root / semantic.QUERY_VECTORS_REL).is_file()


@pytest.mark.parametrize("other", ["Who fires the bowls", "who fires the  bowls", "who fires the bowls\n",
                                   " who fires the bowls"])
def test_the_key_is_the_exact_text(embedder, other):
    root, state = embedder
    first = semantic._query_vector(root, "who fires the bowls")
    assert semantic._query_vector(root, other) != first
    assert len(state["calls"]) == 2


def test_another_revision_is_another_key_and_the_first_comes_back_with_its_revision(embedder):
    root, state = embedder
    first = semantic._query_vector(root, "q")
    state["revision"] = OTHER
    assert semantic._query_vector(root, "q") != first
    state["revision"] = DIGEST
    assert semantic._query_vector(root, "q") == first
    assert len(state["calls"]) == 2


def test_a_failed_embedding_stores_nothing_and_the_next_search_asks_again(embedder):
    root, state = embedder
    state["fail"] = True
    assert semantic._query_vector(root, "q") is None
    state["fail"] = False
    assert semantic._query_vector(root, "q") == struct.pack("2f", 2, 0.5)
    assert len(state["calls"]) == 2


def test_without_a_revision_the_embedder_s_vector_is_used_and_nothing_is_stored(embedder):
    root, state = embedder
    state["revision"] = None
    assert semantic._query_vector(root, "q") == struct.pack("2f", 1, 0.5)
    assert not (root / semantic.QUERY_VECTORS_REL).exists()


def test_a_write_that_loses_keeps_the_vector_that_won(embedder):
    root, _ = embedder
    path, key = root / semantic.QUERY_VECTORS_REL, (semantic.MODEL, DIGEST, "q")
    assert semantic._stored(path, key, b"won") == b"won"
    assert semantic._stored(path, key, b"lost") == b"won"
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM query_vector").fetchone() == (1,)


def test_a_write_that_fails_gives_the_embedder_s_vector_and_raises_nothing(embedder):
    root, state = embedder
    (root / ".gov-runtime").rmdir()
    assert semantic._query_vector(root, "q") == struct.pack("2f", 1, 0.5)
    assert not (root / ".gov-runtime").exists()


def test_a_search_without_an_index_writes_nothing(embedder):
    root, state = embedder
    answer = semantic.search(root, "q", refresh=False)
    assert answer["available"] is False and answer["hits"] == []
    assert state["calls"] == [] and list((root / ".gov-runtime").iterdir()) == []
