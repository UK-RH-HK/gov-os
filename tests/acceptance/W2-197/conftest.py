"""Fixtures of the W2-197 acceptance tests (README): the planted store, once per session, and the stand-ins.

No embedder, reranker or model, as W2-138's conftest: the semantic route is a stand-in with no hit (available), the file
route is off, the reranker is the identity (``retrieve.rerank`` and ``retrieve.last_outcome`` replaced), the secret
filter is replaced. ``GOV_ROLE``, ``GOV_TICKET``, ``GOV_STORE`` and ``GOV_SESSION`` are cleared, ``GOV_MEMORY_LOG``
names a file in the case's own folder (a case that tests the default unsets it), and every case runs in an empty
folder, so nothing of the session running the tests (its role, its store, its log) shapes a result or is written.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_197_support as support  # noqa: E402

from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402


@pytest.fixture(scope="session")
def store(tmp_path_factory):
    """The planted store, built once; a search only reads it."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))
        return support.plant_store(tmp_path_factory.mktemp("w2-197"))


@pytest.fixture
def repo(tmp_path):
    """A repository for gov brief: this tree's templates and facts, the READY ticket."""
    return support.BriefRepo(tmp_path / "brief-repo")


@pytest.fixture
def log(tmp_path):
    return tmp_path / "memory-use.jsonl"


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch, tmp_path):
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_STORE", "GOV_SESSION", "GOV_MEMORY_LOG"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GOV_MEMORY_LOG", str(tmp_path / "memory-use.jsonl"))
    nowhere = tmp_path / "elsewhere"
    nowhere.mkdir()
    monkeypatch.chdir(nowhere)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)
    monkeypatch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})
