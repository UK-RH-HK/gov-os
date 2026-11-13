"""Fixtures for the W2-135 acceptance tests: the two planted repositories per session, and the stand-ins of every test.

No embedder, reranker or model: the semantic route answers no hit (a stand-in), the file route and the routing
settings are off (absent in the planted repositories), and every ``retrieve`` is given a stand-in reranker
(``w2_135_support.Scorer``) that keeps the texts it is sent and scores them by a hash. No question names a symbol or
a record, so neither the code route nor a closure is asked. ``GOV_ROLE`` and ``GOV_TICKET`` are cleared, so no role
filter of the session running the tests shapes a bundle.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_135_support as support  # noqa: E402

from gov.decisions import register as register_module  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402


@pytest.fixture(scope="session")
def project(tmp_path_factory):
    """The planted repository, built once; a retrieval only reads, so the tests share it."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # the secret filter replaced
        return support.build(tmp_path_factory.mktemp("w2-135") / "repo")


@pytest.fixture(scope="session")
def register_project(tmp_path_factory):
    """The planted register's repository (``docs/DECISION_REGISTER.txt``), built once."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))
        return support.build_register(tmp_path_factory.mktemp("w2-135-register") / "repo")


@pytest.fixture(scope="session")
def today():
    """``retrieve`` as ``w2/integrate`` held it before the fix (``support.TODAY_BLOBS``)."""
    return support.today()


@pytest.fixture(scope="session")
def today_register():
    """``register`` as ``w2/integrate`` held it before the fix (``support.TODAY_BLOBS``)."""
    return support.today_register()


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch):
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)


@pytest.fixture()
def ask(project, register_project, today, today_register):
    """``ask(query, module=None, scorer=None, repo="planted", pipeline=False, **kwargs)``: ``retrieve``'s bundle, of
    the running tree (or ``module``, today's), with a stand-in reranker (``scorer``, else a fresh one).

    ``repo="register"`` asks the planted register's repository. ``pipeline=True`` is ``gov retrieve``'s pipeline
    (``gov.retrieve.command.run``): ``retrieve``, then the register's ``leave_out`` over the evidence, its record kept
    as ``left_out``; the register module is today's when ``module`` is today's, else the running tree's."""
    def asked(query, module=None, scorer=None, repo="planted", pipeline=False, **kwargs):
        scorer = scorer or support.Scorer()
        root = register_project if repo == "register" else project
        bundle = (module or retrieve_module).retrieve(root, query, reranker=scorer.loader, **kwargs)
        if pipeline:
            register = today_register if module is today else register_module
            bundle["evidence"], left_out = register.leave_out(root, bundle["evidence"])
            if left_out:
                bundle["left_out"] = left_out
        return bundle
    return asked
