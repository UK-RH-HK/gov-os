"""Fixtures of the W2-138 acceptance tests (README): the two planted stores, once per session, and the stand-ins.

No embedder, reranker or model: the semantic route is a stand-in with no hit (available, so a bundle's stopping
reason is the store's own), the file route is off, the reranker is the identity (``retrieve.rerank`` and
``retrieve.last_outcome`` replaced, as W2-131's unit tests do), no question names a symbol, so the code route is not
asked. ``GOV_ROLE``, ``GOV_TICKET`` and ``GOV_STORE`` are cleared, and every case runs in an empty folder, so nothing
of the session running the tests (its role filter, its store, its working tree's configuration) shapes a result.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_138_support as support  # noqa: E402

from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402


@pytest.fixture(scope="session")
def stores(tmp_path_factory):
    """``a`` at C1 and ``b`` at C2, built once; a search only reads, so the cases share them."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # the secret filter replaced
        return support.make_stores(tmp_path_factory.mktemp("w2-138"))


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch, tmp_path):
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_STORE"):
        monkeypatch.delenv(name, raising=False)
    nowhere = tmp_path / "elsewhere"
    nowhere.mkdir()
    monkeypatch.chdir(nowhere)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)
    monkeypatch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})
