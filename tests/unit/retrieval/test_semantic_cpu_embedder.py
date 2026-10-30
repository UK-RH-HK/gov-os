"""Builder tests for the CPU-only query embedder (W2-54 round 4; DEC-798, DEC-261 as amended).

Regression evidence only (DEC-136). No process is started and no Ollama is needed: the start, the requests and the
device listing are replaced by recorders; each project is a temporary folder.
"""
from __future__ import annotations

import hashlib
import sqlite3
import struct
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import ollama, semantic  # noqa: E402

I = semantic.INSTRUCTION
DIGEST = "a" * 64


def test_the_query_address_is_the_setting_else_the_shared_default_port_plus_one():
    assert ollama.query_host({}) == "127.0.0.1:11435" == ollama.QUERY_DEFAULT_HOST
    assert ollama.query_host({"GOV_QUERY_OLLAMA_HOST": "http://127.0.0.1:9", "OLLAMA_HOST": "x:1"}) == \
        "http://127.0.0.1:9"


def test_the_cpu_embedder_is_started_at_its_own_address_with_the_gpu_hidden(monkeypatch):
    seen = []
    monkeypatch.setattr(ollama, "ensure_available", lambda **kwargs: seen.append(kwargs) or {"available": True})
    env = {"OLLAMA_HOST": "127.0.0.1:11434", "GOV_QUERY_OLLAMA_HOST": "127.0.0.1:7", "PATH": "/bin",
           "CUDA_VISIBLE_DEVICES": "0"}
    assert ollama.ensure_query_available(timeout_s=3, env=env) == {"available": True}
    assert seen == [{"timeout_s": 3, "env": {**env, "OLLAMA_HOST": "127.0.0.1:7", "CUDA_VISIBLE_DEVICES": "-1"}}]
    assert env["OLLAMA_HOST"] == "127.0.0.1:11434"  # the caller's environment is not changed


def _listing(models):
    def ask(path, body=None, host=None):
        assert path == "/api/ps" and host == "h:1"
        return models if models is None else {"models": models}
    return ask


def _model(name=semantic.MODEL, size=2371270737, vram=0):
    return {"name": name, "model": name, "size": size, "size_vram": vram}


@pytest.mark.parametrize("models, on_cpu", [
    ([_model()], True),
    ([_model(vram=2371270737)], False),
    ([_model(vram=1185635368)], False),
    ([], False),
    ([_model(name="nomic-embed-text:latest")], False),
    ([_model(size=0)], False),
    ([{"name": semantic.MODEL, "size": 5}], False),
    (None, False),
])
def test_only_the_model_listed_wholly_on_the_cpu_counts(monkeypatch, models, on_cpu):
    monkeypatch.setattr(semantic, "_ask", _listing(models))
    assert semantic._on_cpu("h:1") is on_cpu


@pytest.fixture()
def recorded(tmp_path, monkeypatch):
    (tmp_path / ".gov-runtime").mkdir()
    state = {"order": [], "on_cpu": True}

    def embed(texts, host=None):
        state["order"].append(("embed", host))
        return [struct.pack("2f", len(text), 1.0) for text in texts]

    def on_cpu(host):
        state["order"].append(("ps", host))
        return state["on_cpu"]

    monkeypatch.setenv(ollama.QUERY_HOST_SETTING, "h:1")
    monkeypatch.setattr(semantic, "_embed", embed)
    monkeypatch.setattr(semantic, "_revision", lambda host=None: DIGEST)
    monkeypatch.setattr(semantic, "_on_cpu", on_cpu)
    return tmp_path, state


def test_the_device_is_read_after_the_vector_is_computed_and_a_vector_off_the_cpu_is_not_used(recorded):
    root, state = recorded
    state["on_cpu"] = False
    assert semantic.query_vector(root, "q") == (None, semantic.NOT_ON_CPU)
    assert state["order"] == [("embed", "h:1"), ("ps", "h:1")]
    assert not (root / semantic.QUERY_VECTORS_REL).exists()
    state["on_cpu"] = True
    assert semantic.query_vector(root, "q")[0] == struct.pack("2f", len(I + "q"), 1.0)
    assert (root / semantic.QUERY_VECTORS_REL).exists()


def test_round_3_s_entries_are_never_served_and_are_dropped_at_the_next_write(recorded):
    root, state = recorded
    path = root / semantic.QUERY_VECTORS_REL
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE query_vector (model TEXT NOT NULL, revision TEXT NOT NULL, text_sha256 TEXT "
                           "NOT NULL, embedding BLOB NOT NULL, PRIMARY KEY (model, revision, text_sha256))")
        connection.execute("INSERT INTO query_vector VALUES (?, ?, ?, ?)",
                           (semantic.MODEL, DIGEST, hashlib.sha256((I + "q").encode()).hexdigest(), b"\0" * 8))
    assert semantic.query_vector(root, "q") == (struct.pack("2f", len(I + "q"), 1.0), None)
    assert state["order"][0] == ("embed", "h:1")
    with sqlite3.connect(path) as connection:
        tables = {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert tables == {"device_query_vector"}
    assert list((root / ".gov-runtime").iterdir()) == [path]


def test_a_search_makes_the_cpu_embedder_answer_and_not_the_shared_runner(tmp_path, monkeypatch):
    """A search with ``refresh=False`` makes the CPU embedder answer (started if needed); the shared runner is the
    build's alone. Unavailable, the facet says so and gives no hit."""
    ensured = []
    monkeypatch.setattr(semantic, "_status", lambda root: None)
    monkeypatch.setattr(semantic, "_open", lambda root: sqlite3.connect(":memory:"))
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: ensured.append(ensure) or ollama.WARNING)
    answer = semantic.search(tmp_path, "q", refresh=False)
    assert ensured == [ollama.ensure_query_available]
    assert answer["available"] is False and answer["reason"] == ollama.WARNING and answer["hits"] == []
