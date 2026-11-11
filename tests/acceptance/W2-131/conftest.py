"""Fixtures for the W2-131 acceptance tests: one planted repository per session, and the stand-ins of every test.

No embedder, reranker or model: the semantic route answers no hit (a stand-in), the file route and the routing
settings are off (absent in the planted repository), every ``retrieve`` is given ``reranker=lambda: None``, the code
route is never asked (no question names a symbol) and the closure starts from records only (no code index asked).
``GOV_ROLE`` and ``GOV_TICKET`` are cleared, so no role filter of the session running the tests shapes a bundle.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_131_support as support  # noqa: E402

from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieval  # noqa: E402


@pytest.fixture(scope="session")
def project(tmp_path_factory):
    """The planted repository, built once; a retrieval only reads, so the tests share it."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # the secret filter replaced
        return support.build(tmp_path_factory.mktemp("w2-131") / "repo")


@pytest.fixture(scope="session")
def today():
    """``retrieve.py`` as ``w2/integrate`` held it before the fix (``support.TODAY_BLOB``)."""
    return support.today()


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch):
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)


@pytest.fixture()
def ask(project):
    """``ask(query, module=None, **kwargs)``: the bundle of the running tree's ``retrieve`` (or ``module``'s)."""
    def asked(query, module=None, **kwargs):
        return (module or retrieval).retrieve(project, query, reranker=lambda: None, **kwargs)
    return asked
