"""Builder tests for the emergency patch DEC-1033 (DAEO-sdxk): a question's vector is used whatever device the query
embedder computed it on, and the query server is started without the GPU hidden (DEC-798's CPU-only rule replaced).

Regression evidence only (DEC-136). Stand-ins only: ``_ask`` answers ``/api/tags``, ``/api/embed`` and ``/api/ps``
from a dict, and ``ensure_available`` is a recorder; no server is started or asked. Each project is a temporary folder.
"""
from __future__ import annotations

import sqlite3
import struct
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import ollama, semantic  # noqa: E402

I = semantic.INSTRUCTION
DIGEST = "d" * 64
HOST = "127.0.0.1:1"
SIZE = 2371270737


def _ps(vram=0, size=SIZE, name=semantic.MODEL):
    return {"models": [{"name": name, "model": name, "size": size, "size_vram": vram}]}


@pytest.fixture()
def server(tmp_path, monkeypatch):
    """A stand-in query embedder: ``state["ps"]`` is what ``/api/ps`` answers, ``state["embed"]`` what ``/api/embed``
    answers (None: the stand-in vectors); every request is recorded in ``state["asked"]``."""
    (tmp_path / ".gov-runtime").mkdir()
    state = {"ps": _ps(), "embed": None, "asked": []}

    def ask(path, body=None, host=None):
        state["asked"].append((path, host))
        assert host == HOST, f"{path} was asked of {host}, not the query embedder"
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "model": semantic.MODEL, "digest": DIGEST}]}
        if path == "/api/ps":
            return state["ps"]
        if path == "/api/embed":
            if state["embed"] is not None:
                return state["embed"]
            return {"embeddings": [[float(len(text)), 1.0, 0.5] for text in body["input"]]}
        raise AssertionError(path)

    monkeypatch.setenv(ollama.QUERY_HOST_SETTING, HOST)
    monkeypatch.setattr(semantic, "_ask", ask)
    return tmp_path, state


def _expected(query="q"):
    return struct.pack("3f", float(len(I + query)), 1.0, 0.5)


def _cached_devices(root):
    with sqlite3.connect(root / semantic.QUERY_VECTORS_REL) as connection:
        return [device for (device,) in connection.execute("SELECT device FROM device_query_vector")]


@pytest.mark.parametrize("vram, device", [(SIZE, "gpu"), (SIZE // 2, "gpu"), (0, "cpu")])
def test_a_question_s_vector_is_used_whatever_device_the_model_is_reported_on(server, vram, device):
    root, state = server
    state["ps"] = _ps(vram=vram)
    assert semantic.query_vector(root, "q") == (_expected(), None)
    assert _cached_devices(root) == [device]
    asked = [path for path, _ in state["asked"]]
    assert asked.index("/api/embed") < asked.index("/api/ps"), "the device is read after the vector is computed"


def test_a_vector_cached_from_either_device_is_served_without_asking_the_embedder(server):
    root, state = server
    state["ps"] = _ps(vram=SIZE)
    first = semantic.query_vector(root, "q")
    state["asked"].clear()
    state["ps"] = _ps(vram=0)
    assert semantic.query_vector(root, "q") == first
    assert [path for path, _ in state["asked"]] == ["/api/tags"]


@pytest.mark.parametrize("ps", [
    {"models": []},
    _ps(name="nomic-embed-text:latest"),
    _ps(size=0),
    {"models": [{"name": semantic.MODEL, "size": SIZE}]},
    {"models": [{"name": semantic.MODEL, "size": SIZE, "size_vram": "big"}]},
    {"models": [{"name": semantic.MODEL, "size": SIZE, "size_vram": -1}]},
    {"models": "not a list"},
    None,
    ["not", "an", "object"],
], ids=["nothing", "other-model", "size-0", "no-size_vram", "size_vram-text", "size_vram-negative", "models-text",
        "no-answer", "answer-a-list"])
def test_a_model_not_reported_loaded_gives_no_vector_named_and_nothing_cached(server, ps):
    root, state = server
    state["ps"] = ps
    assert semantic.query_vector(root, "q") == (None, semantic.NOT_LOADED)
    assert not (root / semantic.QUERY_VECTORS_REL).exists()


@pytest.mark.parametrize("embed, reason", [
    ({"embeddings": [[1.0, 2.0], [1.0, 2.0, 3.0]]}, "MALFORMED"),
    ({"embeddings": [[], []]}, "MALFORMED"),
    ({"embeddings": [[1.0, 2.0], [float("nan"), 2.0]]}, "MALFORMED"),
    ({"embeddings": [[1.0, 2.0], [float("inf"), 2.0]]}, "MALFORMED"),
    ({"embeddings": [[1.0, 2.0], ["a", "b"]]}, "MALFORMED"),
    ({"embeddings": [[1.0, 2.0], 7]}, "MALFORMED"),
    ({"embeddings": [[1.0, 2.0]]}, "NO_EMBEDDING"),
    ({}, "NO_EMBEDDING"),
], ids=["lengths-differ", "empty", "nan", "inf", "text", "not-a-list", "one-vector", "no-embeddings"])
def test_a_malformed_answer_gives_no_vector_named_and_nothing_cached(server, embed, reason):
    root, state = server
    state["ps"], state["embed"] = _ps(vram=SIZE), embed
    assert semantic.query_vector(root, "q") == (None, getattr(semantic, reason))
    assert not (root / semantic.QUERY_VECTORS_REL).exists()


def test_the_cpu_only_reason_is_retired():
    assert not hasattr(semantic, "NOT_ON_CPU") and not hasattr(semantic, "_on_cpu")
    assert semantic.NOT_LOADED and semantic.MALFORMED and semantic.NOT_LOADED != semantic.MALFORMED


@pytest.mark.parametrize("caller", [{}, {"CUDA_VISIBLE_DEVICES": "0"}, {"CUDA_VISIBLE_DEVICES": "-1"}])
def test_the_query_server_is_started_without_hiding_the_gpu(monkeypatch, caller):
    """The start environment is the caller's with OLLAMA_HOST set to the query address: no ``CUDA_VISIBLE_DEVICES=-1``
    is added, and whatever the caller has is passed on unchanged."""
    seen = []
    monkeypatch.setattr(ollama, "ensure_available", lambda **kwargs: seen.append(kwargs) or {"available": True})
    env = {"OLLAMA_HOST": "127.0.0.1:11434", "GOV_QUERY_OLLAMA_HOST": "127.0.0.1:7", "PATH": "/bin", **caller}
    assert ollama.ensure_query_available(timeout_s=3, env=env) == {"available": True}
    assert seen == [{"timeout_s": 3, "env": {**env, "OLLAMA_HOST": "127.0.0.1:7"}}]
    assert seen[0]["env"].get("CUDA_VISIBLE_DEVICES") == caller.get("CUDA_VISIBLE_DEVICES")
    assert not hasattr(ollama, "NO_GPU")
