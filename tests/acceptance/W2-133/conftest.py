"""Fixtures for the W2-133 acceptance tests: one planted repository per session, and the stand-ins of every test.

No embedder, reranker or model: the semantic route answers no hit (a stand-in), the file route and the routing
settings are off (absent in the planted repository), every ``retrieve`` is given ``reranker=lambda: None``, no
question names a symbol or a record, so neither the code route nor a closure is asked. ``GOV_ROLE`` and
``GOV_TICKET`` are cleared, so no role filter of the session running the tests shapes a bundle.

``ask`` is ``gov retrieve``'s pipeline (``gov.retrieve.command.run``, lines 104-113 on integrate): ``retrieve``, then
the register's ``leave_out`` over the evidence, its record kept as ``left_out``. ``raw`` is ``retrieve`` alone.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_133_support as support  # noqa: E402

from gov.decisions import register as register_module  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402


@pytest.fixture(scope="session")
def project(tmp_path_factory):
    """The planted repository, built once; a retrieval only reads, so the tests share it."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # the secret filter replaced
        return support.build(tmp_path_factory.mktemp("w2-133") / "repo")


@pytest.fixture(scope="session")
def today():
    """``(retrieve, register)`` as ``w2/integrate`` held them before the fix (``support.TODAY_BLOBS``)."""
    return support.today()


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch):
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)


@pytest.fixture()
def raw(project):
    """``raw(query, modules=None, **kwargs)``: ``retrieve``'s bundle, of the running tree (or ``modules``)."""
    def asked(query, modules=None, **kwargs):
        retrieval = (modules or (retrieve_module, register_module))[0]
        return retrieval.retrieve(project, query, reranker=lambda: None, **kwargs)
    return asked


@pytest.fixture()
def ask(project):
    """``ask(query, modules=None, **kwargs)``: the bundle ``gov retrieve`` gives: ``retrieve``, then ``leave_out``."""
    def asked(query, modules=None, **kwargs):
        retrieval, register = modules or (retrieve_module, register_module)
        bundle = retrieval.retrieve(project, query, reranker=lambda: None, **kwargs)
        bundle["evidence"], left_out = register.leave_out(project, bundle["evidence"])
        if left_out:
            bundle["left_out"] = left_out
        return bundle
    return asked
