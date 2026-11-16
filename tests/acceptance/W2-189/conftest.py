"""Fixtures of the W2-189 acceptance tests (README): the stand-ins, and the semantic endpoint for the cases that run
the semantic facet's own status gate.

No embedder, reranker or model request of any kind. By default the semantic route is a stand-in with no hit
(available, so a bundle's stopping reason is the lexical store's own), the file route is off, the reranker is the
identity. A case that asks for ``semantic_endpoint`` runs ``gov.retrieval.semantic`` itself, unpatched (its status
gate, its ``_vectors``, ``query_vector``), with only the model calls replaced: ``_ask`` (the embedding request, the
model list, the device listing) and ``_ready`` (``sqlite_vec`` replaced by a Python distance function), as
``tests/unit/retrieval/test_w2_32_pin.py`` does. ``GOV_ROLE``, ``GOV_TICKET`` and ``GOV_STORE`` are cleared and each
case runs in an empty folder, so nothing of the session running the tests shapes a result.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_189_support as support  # noqa: E402, F401

from gov.config import models  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52


def _distance(left, right):
    count = len(left) // 4
    return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))


@pytest.fixture(autouse=True)
def stand_ins(request, monkeypatch, tmp_path):
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_STORE"):
        monkeypatch.delenv(name, raising=False)
    nowhere = tmp_path / "elsewhere"
    nowhere.mkdir()
    monkeypatch.chdir(nowhere)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # the secret filter replaced
    if "semantic_endpoint" not in request.fixturenames:
        monkeypatch.setattr(semantic, "search",
                            lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
        monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)
    monkeypatch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture()
def semantic_endpoint(monkeypatch, tmp_path):
    """The model calls of the semantic facet replaced: a two-number embedding of each text (does it hold *pelican*,
    does it hold *marmalade*), the model listed at the pinned digest on the GPU. ``endpoint["sent"]`` is every text
    embedded."""
    endpoint = {"sent": [], "models": {semantic.MODEL: PINNED}}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": name, "digest": digest} for name, digest in endpoint["models"].items()]}
        if path == "/api/ps":
            return {"models": [{"name": name, "size": 1, "size_vram": 1} for name in endpoint["models"]]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float("pelican" in text), float("marmalade" in text)] for text in body["input"]]}

    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None:
                        connection.create_function("vec_distance_cosine", 2, _distance))
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))
    return endpoint
