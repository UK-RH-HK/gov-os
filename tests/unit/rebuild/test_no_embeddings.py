"""``gov rebuild --no-embeddings`` builds everything but the semantic vectors (DEC-530)."""
from __future__ import annotations

import argparse

import pytest

from gov.rebuild.command import add_arguments, run


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


@pytest.fixture()
def asked(monkeypatch):
    """What a rebuild asked for, with stand-ins for every store it builds."""
    asked = []
    monkeypatch.setattr("gov.store.load", lambda root: asked.append("record") or {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: asked.append("lexical"))
    monkeypatch.setattr("gov.retrieval.semantic.refresh",
                        lambda root: asked.append("semantic") or {"available": True})
    monkeypatch.setattr("gov.codeintel.index", lambda root: asked.append("codeintel"))
    return asked


def test_the_mode_asks_for_no_vectors_and_says_why(tmp_path, asked):
    result = run(tmp_path, _args("--no-embeddings"), {"path-map.yaml": {}})
    assert asked == ["record", "lexical", "codeintel"]
    semantic = result["stores"].pop("semantic")
    assert (semantic["status"], semantic["requested"]) == ("not_recreated", False)
    assert "--no-embeddings" in semantic["reason"]
    assert result["digest"] == "d" and result["stores"] == {"lexical": {"status": "recreated"},
                                                            "codeintel": {"status": "recreated"}}


def test_a_full_rebuild_is_the_default(tmp_path, asked):
    result = run(tmp_path, _args(), {"path-map.yaml": {}})
    assert asked == ["record", "lexical", "semantic", "codeintel"]
    assert result["stores"]["semantic"] == {"status": "recreated"}
