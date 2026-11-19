"""Fixtures of the W2-203 acceptance tests (README).

No embedder, reranker or model: the semantic route is a stand-in with no hit, the file route is off, the reranker is
the identity, the secret filter is replaced (as W2-197's conftest), and the code index knows no symbol. ``GOV_ROLE``,
``GOV_TICKET``, ``GOV_STORE`` and ``GOV_SESSION`` are cleared and every case runs in an empty folder, so nothing of
the session running the tests shapes a result, and no store of a real worktree is opened or written.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_203_support as support  # noqa: E402

from gov import codeintel  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402


def _stand_ins(patch) -> None:
    patch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    patch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    patch.setattr(semantic, "file_level_on", lambda _root: False)
    patch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    patch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})
    patch.setattr(codeintel, "definitions", lambda _root, _name: [])


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch, tmp_path):
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_STORE", "GOV_SESSION"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GOV_MEMORY_LOG", str(tmp_path / "memory-use.jsonl"))
    nowhere = tmp_path / "elsewhere"
    nowhere.mkdir()
    monkeypatch.chdir(nowhere)
    _stand_ins(monkeypatch)


@pytest.fixture(scope="session")
def planted(tmp_path_factory):
    """The planted project, its keyword index and record store built once; the cases only read it."""
    with pytest.MonkeyPatch.context() as patch:
        _stand_ins(patch)
        return support.plant(tmp_path_factory.mktemp("w2-203-planted") / "repo")


@pytest.fixture
def plant(tmp_path):
    """A planted project of the case's own: ``plant(name, **how)``."""
    return lambda name, **how: support.plant(tmp_path / name / "repo", **how)


@pytest.fixture(scope="session")
def home(tmp_path_factory):
    return tmp_path_factory.mktemp("w2-203-home")


@pytest.fixture(scope="session")
def base_clone(tmp_path_factory):
    """The base commit's tree and history, in a temporary folder."""
    return support.clone_at(tmp_path_factory.mktemp("w2-203-base") / "repo", support.BASE)


@pytest.fixture(scope="session")
def head_clone(tmp_path_factory):
    """This repository's HEAD, in a temporary folder: the committed state is what the clone cases judge."""
    return support.clone_at(tmp_path_factory.mktemp("w2-203-head") / "repo", support.head_of())


@pytest.fixture(scope="session")
def moved(head_clone):
    """HEAD's archive and kept register as entries: ``{"archive": [(id, text)], "register": [...], "only": ids the
    archive alone holds}``; the case fails here where HEAD holds no archive."""
    archive = head_clone / support.ARCHIVE_REL
    assert archive.is_file(), f"HEAD holds no {support.ARCHIVE_REL}: the old register is not archived"
    old = support.entries(archive.read_text(encoding="utf-8"))
    new = support.entries((head_clone / support.REGISTER_REL).read_text(encoding="utf-8"))
    only = {record_id for record_id, _ in old} - {record_id for record_id, _ in new}
    assert only, f"{support.REGISTER_REL} at HEAD still holds every entry of the archive"
    return {"archive": old, "register": new, "only": only}
